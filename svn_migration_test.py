import os, re, subprocess, random, shutil
from distutils.dir_util import copy_tree

## user settings --------------------------------------------------------

# 본 script는 [svn 특정 repository]를 [git local repository]에 migration 한다.
# 즉 [git local repository]에 svn log 및 파일들이 정상적으로 migration 되었는 지
# 확인한 후 수동으로 [git remote repository] 에 업로드하도록 한다.
# 현재 svn 명령 중 Modification, Add, Delete 만 지원한다.

# 아래는 진행 예시
# - github, gitbucket 등의 사이트에서 [git remote reposotory] 생성
# - git pull origin master
# - 해당 스크립트 실행 및 확인
# - git push origin master

svn_user_name = "*******"  # svn ID 입력
svn_password = "*******"   # svn 비밀번호 입력    

# migration svn source root repository 선택(absolute path로 입력)
svn_repos = "G:\\svn_test\\trunk\\src\\input\\ypur\\dir"

# -----------------------------------------------------------------------


# svn infomation read
svn_info = subprocess.check_output(f"svn info {svn_repos}", shell=True)
svn_info = svn_info.decode('euc-kr')
revision_num = re.search("Revision: \d+", svn_info)
revision_num = revision_num.group().split(":")[1]
revision_num = revision_num.strip()
revision_int = int(revision_num)
# debuggin point - revision number 받아오기 확인
print("svn revision number: " + str(revision_int))

repos_url = re.search("URL: [\w:/.]+", svn_info)
repos_url = repos_url.group().split(" ")[1].strip()
# debuggin point - 현재 경로의 URL 확인
print("svn repository of input path: " + repos_url)

repos_relativ_url = re.search("Relative URL: \^[\w:/.]+", svn_info)
repos_relativ_url = repos_relativ_url.group().split(" ")[2].strip()[1:]
# debuggin point - 현재 경로의 relative URL 확인
print("svn relative repository of input path: " + repos_relativ_url)

svn_cmd = f"svn log {svn_repos} -l {revision_int} -v"
svn_info = subprocess.check_output(svn_cmd, shell=True)
svn_info = svn_info.decode('euc-kr')
svn_info_list = svn_info.split("\n")
svn_info_list = list(info for info in svn_info_list if (0 != len(info.strip())))

# svn info parsing
rev_num_list = list()
date_list = list()
log_list = list()
add_del_list = list()
author_list = list()

index = 0
while index <= len(svn_info_list):
    svn_str = svn_info_list[index].strip()
    if(svn_str.startswith("----")):
        # revision number and date info
        index += 1
        if index >= len(svn_info_list):
            break
        rev_num = svn_info_list[index].strip().split("|")[0].strip()[1:]
        tmp_author = svn_info_list[index].strip().split("|")[1].strip()
        rev_date = svn_info_list[index].strip().split("|")[2].strip()
        rev_num_list.append(int(rev_num))
        date_list.append(rev_date)
        author_list.append(tmp_author)
        # add/delete log
        index += 2
        if index >= len(svn_info_list):
            break
        temp_list = list()
        while True:
            svn_str = svn_info_list[index]
            if(svn_str.startswith("   ")):
                temp_list.append(svn_str)
                index += 1
            else:
                break
        add_del_list.append(temp_list)
        # log string info
        if index >= len(svn_info_list):
            break
        temp_list = list()
        while True:
            svn_str = svn_info_list[index].strip()
            if(svn_str.startswith("----")):
                break
            else:
                temp_list.append(svn_str)
                index += 1
        log_list.append(temp_list)
rev_num_list.reverse()
date_list.reverse()
add_del_list.reverse() 
log_list.reverse() 
author_list.reverse()
# debuggin point - rev_num_list, date_list, add_del_list, log_list 가 제대로 받아왔는 지 확인
# list 길이가 같아야함
print("number of svn log: [revision number: %d], [date: %d], [changed path: %d], [commit log: %d], [author: %d]"
      %(len(rev_num_list), len(date_list), len(add_del_list), len(log_list), len(author_list)))


# test로 다른 svn repository에 저장한다.
randum_num = random.randrange(1, 10000)
file_root_path = os.path.dirname(os.path.realpath(__file__))
tmp_dir_name_from = f"temp_dir_{revision_num}_{randum_num}"
tmp_dir_name_to = f"temp_dir_{revision_num}_{randum_num + 1}"
full_src_path = os.path.join(file_root_path, tmp_dir_name_from)
full_dest_path = os.path.join(file_root_path, tmp_dir_name_to)
os.mkdir(full_src_path)
os.mkdir(full_dest_path)


svn_checkout_cmd = f"svn checkout {repos_url} {full_src_path} --username {svn_user_name} --password {svn_password} -r {rev_num_list[0]}"
subprocess.check_output(svn_checkout_cmd, shell=True)
os.chdir(full_dest_path)
git_cmd = "git init"
subprocess.check_output(git_cmd, shell=True)
#git_cmd = f"git remote add origin {dest_repos_url}"
#subprocess.check_output(git_cmd, shell=True)
os.chdir("..")

for rev_idx in range(len(rev_num_list)):
    print("in progress...[%d/%d]" % (rev_idx + 1, len(rev_num_list)))
    
    # svn update
    svn_update_cmd = f"svn update {full_src_path} -r {rev_num_list[rev_idx]}"
    subprocess.check_output(svn_update_cmd, shell=True)
    
    # file copy from source to dest
    file_list = os.listdir(full_src_path)
    file_list = [name for name in file_list if name[0] != "." ] # 숨김파일 제외

    for f_idx in file_list:
        src_file_path = os.path.join(full_src_path, f_idx)
        dest_file_path = os.path.join(full_dest_path, f_idx)
        if os.path.isdir(src_file_path):
            copy_tree(src_file_path, dest_file_path)
        else:
            shutil.copyfile(src_file_path, dest_file_path)

    # add 및 delete 정보를 받아서 처리
    os.chdir(full_dest_path)
    for add_del_str in add_del_list[rev_idx]:
        add_del_str = add_del_str.strip()
        
        if repos_relativ_url in add_del_str and not add_del_str.endswith(repos_relativ_url) :
            file_cmd = add_del_str.split(" ")[1]
            file_cmd = file_cmd.replace((repos_relativ_url + "/"), "")
            if "M" == add_del_str[0] or "A" == add_del_str[0]:
                #print("[A or M] " + add_del_str)
                git_add_cmd = f"git add \"{file_cmd}\""
                subprocess.check_output(git_add_cmd, shell=True)
            elif "D" == add_del_str[0]:
                #print("[D] " + add_del_str)
                git_add_cmd = f"git rm -r \"{file_cmd}\""
                subprocess.check_output(git_add_cmd, shell=True)
            else:
                print("[NOT SUPPORT CMD] " + add_del_str)
    
    # svn commit to dest
    data_str = date_list[rev_idx]
    author_str = author_list[rev_idx]
    msg = "-m \""  + data_str + "\""
    msg += " -m \"author: "  + author_str + "\""
    for log_str in log_list[rev_idx]:
        msg += " -m \""
        msg += log_str
        msg += "\""
        
    git_commit_cmd = f"git commit {msg}"
    subprocess.check_output(git_commit_cmd, shell=True)
    os.chdir("..")
        
if os.path.isdir(full_src_path):
    shutil.rmtree(full_src_path)

