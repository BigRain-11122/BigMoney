import io
p = 'CODELY.md'
row = "- [2026-10-19 10:5x r1077 bm-a] **append-only 账本 NUL 全蚀三步正法（死窗遗产吸收实弹）**：死窗写中断把 results/pool_dualrun.bm-a.jsonl 写成 15,597B 全 \\x00（ps 缓冲未落盘击杀态）→ 轮首 git add -A 基线**误携腐蚀面入 commit**（add -A 前无 NUL 扫描面）→ 下轮 S6 dualrun 腿 rc=2 MECHANISM FAULT（json.loads 首行即炸）。三步正法=①treasure_guard restore 必先跑（本例 rc3 硬拒=append-only-ledger 类禁 blob origin-restore）②唯一合法路=行级 union（origin 行 ∪ 盘面有效 JSON 行·零 NUL 断言+行数不减断言）③复跑原腿自证（本例 ZERO-DRIFT streak 51 rc0）。姊妹判例：同窗双机水位探针同秒 ts 平手（双机 10:39:03）newer-wins 不可判 → tie-break 取重放侧（后续 commit 携新 ts 自然覆写即愈·零信息损失）。How to apply：S6 腿报 MECHANISM FAULT Expecting value 先查文件 NUL 字节面；add -A 前遇死窗遗产必 NUL 扫描。"
with io.open(p, 'a', encoding='utf-8', newline='\n') as f:
    f.write(row + "\n")
lines = io.open(p, encoding='utf-8').read().splitlines()
print('appended; total lines:', len(lines))
print('last:', lines[-1][:80])
