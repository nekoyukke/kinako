$now = Get-Date -Format "yyyyMMdd-HHmm"
git switch -c "branch-$now"
git commit --allow-empty -m "新しいブランチ作成: $(Get-Date -Format 'yyyy/MM/dd HH:mm:ss')"
git push kinako "branch-$now"
git add .
git commit -m $args[0]
git push kinako "branch-$now"