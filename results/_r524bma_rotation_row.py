# r524 bm-a: land the corrected sovereignty-rotation law row (yield addendum).
# Anchored on ACTUAL state: W13=bm-b (bm-b r512 first-push wins; my unpushed
# r524 suite yielded per r239). Cycle from the real anchor:
# W14=bm-c / W15=bm-a / W16=bm-b (matches bm-c's own F-20261001-01 example).
path = "research/PERPETUAL_FACES.md"
raw = open(path, encoding="utf-8", newline="").read()
anchor = "仍照例 prereg 时机验（含引擎队列面与语法登记簿对账防重烧）。"
assert raw.count(anchor) == 1, f"anchor count {raw.count(anchor)} != 1"
row = anchor + "\n" + (
    "- **引擎波主权预分区轮值律（r524 bm-a 落法·F-20261001-01 根治步·当日双撞实证**："
    "W12 三机同窗三冻〔bm-a r523/bm-b r511/bm-c r323〕+W13 双机同窗双冻〔bm-b r512 先推胜出·"
    "bm-a r524 未推让路·两机带闸确定性同谳 A=70_001..72_000——同窗独立扫描恒同带=撞面在冻结权"
    "不在带位〕）：N1 引擎波自 W14 起按轮值预分配冻结权——**W13=bm-b〔实锚·先推实况〕/"
    "W14=bm-c / W15=bm-a / W16=bm-b 循环**（模 3 轮转自实锚续行）；每机 never-dry 触发面"
    "（队列空=供给断流）在冻结动作前必读本表轮值——**本波不属己=零冻结动作**（属己=照常冻结）；"
    "构造性零同号撞面（fetch 墙盲窗对其免疫）；r239 让路律退役为异常兜底；轮值表变更=GM 署名面。"
    "配套观察：轮值落地窗内已在飞的双烧由 engine_owner 闸自限（本例 bm-a 引擎 16:39 起 W13 "
    "foreign 不可见=队列清零自停·重复 7 片产物全量弃置留痕）"
)
open(path, "w", encoding="utf-8", newline="").write(raw.replace(anchor, row))
print("rotation row landed after bm-b W13 row")
