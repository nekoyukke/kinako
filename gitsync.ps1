$now = Get-Date -Format "yyyyMMdd-HHmm"
git switch -c "branch-$now"
git commit --allow-empty -m "new branch!!!: $(Get-Date -Format 'yyyy/MM/dd HH:mm:ss')"

git push kinako "branch-$now"
git add .
git commit -m $args[0]
git push kinako "branch-$now"

git switch main
Read-Host "Do marge!!!"
git checkout .
git pull kinako main --rebase
git branch -D "branch-$now"

echo "remote:"
git remote
echo "branch:"
git branch