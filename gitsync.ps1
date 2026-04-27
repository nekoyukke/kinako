$now = Get-Date -Format "yyyyMMdd-HHmm"
git switch -c "branch-$now"
git commit --allow-empty -m "new branch!!!: $(Get-Date -Format 'yyyy/MM/dd HH:mm:ss')"
git push kinako "branch-$now"
git add .
git commit -m $args[0]
git push kinako "branch-$now"
git switch main
# 戻ったとき、もし「作業中の残骸」があれば消して真っさらにする
git checkout .  # ← 変更を全部捨てて、最後に成功したコミットの状態に戻す（※注意：未保存は消えます）
# GitHub上の最新（合体後のmain）を取り込んで、常に自分を最新にする
git pull kinako main --rebase
echo "remote:"
git remote
echo "branch:"
git branch