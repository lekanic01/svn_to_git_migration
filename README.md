# svn_to_git_migration
[svn repository] to [git local repositoy] migration python script

svn repositoy를 git local repository 로 migration 하는 python script 입니다.
특정 폴더에서 svn checkout을 통해 사용 중인 directory를 입력으로 사용합니다.
현재 svn 의 A(추가), M(수정), D(삭제) 인 경우만 지원합니다.
생성된 git local repository를 확인 후 
(몇 번의 조작으로 가능하므로)
필요 시, git remote repository pull 작업은 수동으로 진행합니다.
script 결과 svn의 log 기록들이 모두 git log로 이관됩니다.

git log는
svn commit 시점
commit author
commit log
가 저장됩니다.

필요 시, scirpt를 수정해서 사용하세요.
