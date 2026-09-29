# r422 bm-a yield kit: TSTATE re-berth + inbox archive + CODELY 10KB archival
# All moves byte-exact via python (no PS redirection on CJK faces, r209 law).
# Zero-loss verification: every migrated CODELY line must exist verbatim in
# the archive file after append (line-level zero-loss law).
import shutil
import subprocess
import sys

# 1) TSTATE re-berth: blob from pre-second-rebase commit e18aa4599
r = subprocess.run(["git", "show", "e18aa4599:research/TRIAL_LABOR_W7_PREREG.md"],
                  capture_output=True)
assert r.returncode == 0, "blob read failed"
orig = r.stdout.decode("utf-8")
banner = """# TRIAL_LABOR_W8_CANDIDATE_TSTATE_PREREG_DRAFT —— TSTATE 时序态门 wave-8 候选泊位（转泊收执 2026-09-29 09:4x·bm-a r422）

> **【转泊收执（collision yield receipt·fleet/README.md §4 commit 时间序）】**本件原为 bm-a r421 起草+冻结的 TRIAL_LABOR_W7_PREREG（TSTATE 时序态门·本地 commit 2026-09-29 09:07:52·SEED 三键 20305000/20305500/20306000 同 commit 登记·T-118 开票认领·F-04 MSG-0905 声明——推送被拒未及上链）。W7 泊位三机同窗撞车：bm-c STREAK 稿 ba2653539 @09:07:05 先落 origin（r207 冻结上链 5de79413b）+bm-b AMP 稿 r417a 已让路转 W8 候选 → 本机后到让路：**W7=STREAK 版正典**（research/TRIAL_LABOR_W7_PREREG.md 现挂 bm-c 冻结版），本 TSTATE 版 **W7 冻结失效**——wave 号/SEED 三键/T-118 票全归 W7-STREAK；TSTATE 若立 W8 须另开票+种子撞带重取（三步律复验）+重走冻结四件套（prereg 冻结+SEED 同 commit+票同轮认领+F-04 MSG）。转泊后状态=**W8 候选备货泊位**（与 bm-b AMP 并列·W8 起草窗=W7 全链消费落地后·任何健康机可认领起草·起草面无门禁）。**供给侧事实全部保值有效**：TSTATE census 正信号主证（O-1855④ MAD60_q10 中位 t=+2.255·60% 工具 |t|>2 / RSV60_low<0.2 中位 t=+2.201·58%·20 日前瞻窗）+探针件 results/_r421bma_tstate_probe.py + _r421bma_tstate_probe_facts.json（含 pandas NaN 比较/bool first_valid_index 双伪影坑律修正面·九十五批）+§1-§9 全部冻结文语义。以下原文逐字保留（标题行 wave-7 字样=历史原貌不追改）。

"""
with open("research/TRIAL_LABOR_W8_CANDIDATE_TSTATE_PREREG_DRAFT.md", "wb") as fh:
    fh.write((banner + orig).encode("utf-8"))
back = open("research/TRIAL_LABOR_W8_CANDIDATE_TSTATE_PREREG_DRAFT.md", "rb").read()
assert back.decode("utf-8").endswith(orig), "verbatim tail check failed"
print("[re-berth] TSTATE W8 candidate file written, %dB (orig %dB + banner %dB)"
      % (len(back), len(orig.encode("utf-8")), len(banner.encode("utf-8"))))

# 2) inbox: process both W7 declaration MSGs (ours 0905 superseded by 0945;
#    bm-c 0930 answered by the 0945 yield receipt)
for f in ("MSG-20260929-0905-bma-ALL-W7-prereg-freeze.md",
          "MSG-20260929-0930-bmc-ALL-W7-prereg-freeze.md"):
    shutil.move("fleet/inbox/" + f, "fleet/inbox/processed/" + f)
    print("[inbox] processed <-", f)

# 3) CODELY.md 10KB hot-cold archival (water-line law, same-window):
#    migrate the three 九十五批-family hot entries verbatim to the monthly
#    archive, replace with ONE consolidated pointer line; append r422 entry.
ARCHIVE = "research/memory-archive/202609.md"
CODELY = "CODELY.md"
text = open(CODELY, "rb").read().decode("utf-8")
lines = text.splitlines(keepends=True)
targets = []
for ln in lines:
    s = ln.strip()
    if s.startswith("- [2026-09-29 08:5x] 九十五批"):
        targets.append(ln)
    elif s.startswith("- [2026-09-29 09:1x r206 bm-c] 坑律九十五批"):
        targets.append(ln)
    elif s.startswith("- [2026-09-29 09:0x r421 bm-a] 坑律"):
        targets.append(ln)
assert len(targets) == 3, "expected 3 migration targets, got %d" % len(targets)

new_entry = "- [2026-09-29 09:47 r422 bm-a] 坑律九十六批（常设线同波三稿撞车·泊位声明缺位=W7 窗三机烧两仪式）：TRIAL_LABOR 常供线触发器（W6 落地+池空）同窗同拍三机（bm-c STREAK/bm-b AMP/bm-a TSTATE）各自按 §1 起草 wave-7，零泊位声明机制→bm-b r417a 让路（commit-time 律 origin 先到 ba2653539 @09:07:05）、bm-a r421 冻结后被裁定让路（本机 commit 09:07:52 后到·推送被拒未及上链）：两机冻结仪式白烧（SEED 复验+票+MSG 重做·TSTATE/AMP 转 W8 候选泊位·种子撞带重取）。How to apply：任何「板空默认起草下一波」型常设线触发→先 fetch+查 origin 有无同波 draft 泊位声明→有=让路转候选备货、无=先落轻量泊位声明（一行 commit/MSG 落 origin）再开起草；裁定基准=fleet/README §4 commit 时间序（origin 先到者胜·本地 commit 时间戳不算在位证据）。指针=TRIAL_LABOR_W8_CANDIDATE_TSTATE_PREREG_DRAFT.md 转泊收执+MSG-20260929-0945。\n"
pointer = "冷层指针：坑律正典 2026-09-29 九十五批三连（r416 bm-b 波级预注册 §7/§8 跑后回填纪律五波静默漂移坑·r206 bm-c 孤儿 finalize 已落地链重跑 append 同批双计坑·r421 bm-a pandas 门探针 NaN 比较产 False 非 NaN+bool first_valid_index 全真双伪影）全文 verbatim=archive 202609.md『坑律归档 2026-09-29 r422 bm-a 窗批』节（r422 bm-a 窗水位律当窗整编·行级零丢失校验）。\n"

out = []
for ln in lines:
    s = ln.strip()
    if s.startswith("- [2026-09-29 08:5x] 九十五批"):
        out.append(new_entry)  # replace in place under ### Project
    elif s.startswith("- [2026-09-29 09:1x r206 bm-c] 坑律九十五批") or \
         s.startswith("- [2026-09-29 09:0x r421 bm-a] 坑律"):
        if not any(x is ln for x in [l for l in out if "r206 bm-c" in l]):
            pass
        continue  # dropped; consolidated pointer appended below instead
    else:
        out.append(ln)
# append consolidated pointer at file end (Reference area)
out.append(pointer)
new_text = "".join(out)
with open(CODELY, "wb") as fh:
    fh.write(new_text.encode("utf-8"))

# archive append (verbatim, zero-loss)
with open(ARCHIVE, "ab") as fh:
    fh.write(("\n## 坑律归档 2026-09-29 r422 bm-a 窗批（水位律当窗整编：CODELY 并集 11.07KB 超线→九十五批三连迁此·行级零丢失校验）\n").encode("utf-8"))
    for ln in targets:
        fh.write(ln.encode("utf-8"))
    fh.write(("『r422 bm-a 窗行级零丢失校验：以上三条自 CODELY.md 热层 verbatim 迁移，条目内容零删零改动。』\n").encode("utf-8"))

# zero-loss verification: each migrated line exists verbatim in archive
arch_text = open(ARCHIVE, "rb").read().decode("utf-8")
for ln in targets:
    assert ln in arch_text, "zero-loss check failed"
print("[archival] 3 entries migrated verbatim; archive OK")
size = len(open(CODELY, "rb").read())
print("[archival] CODELY.md now %dB (was 11067B)" % size)
assert size <= 10240, "CODELY.md still over 10KB hard line"
print("[yield-kit] ALL OK")
