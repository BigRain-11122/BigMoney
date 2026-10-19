# -*- coding: utf-8 -*-
# r1121 bm-c: CAS surgical edit -- DAILY-OUTPUT-REPORT.md BigMoney row (16:26 daily-report law,
# each-division 22:0x deadline; landed early per CEO immediate law). Read origin blob -> split the
# merged row -> insert BigMoney row -> CAS push (r705 + r1020 40hex law).
import subprocess, sys, os, tempfile
sys.stdout.reconfigure(encoding="utf-8")
GRP = r"K:\Fluxgroup\FluxGroup"
PATH = "cph4/fleet/DAILY-OUTPUT-REPORT.md"
env = dict(os.environ, GIT_INDEX_FILE=os.path.join(GRP, ".git", "cas-index-r1121b"))

def g(*args, env_extra=None, check=True):
    r = subprocess.run(["git", "-C", GRP] + list(args), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env_extra or os.environ)
    if check and r.returncode != 0:
        raise SystemExit("GIT FAIL %s: %s" % (args[:3], (r.stderr or "")[:300]))
    return r.stdout.strip()

base = g("rev-parse", "origin/main")
print("base:", base)
blob = subprocess.run(["git", "-C", GRP, "show", "origin/main:" + PATH], capture_output=True).stdout
text = blob.decode("utf-8")
lines = text.split("\n")
idx = -1
for i, l in enumerate(lines):
    if "Biggame/BigMoney/BigHouse/CPH4 Labs" in l:
        idx = i
        break
if idx < 0:
    raise SystemExit("merged row not found -- file structure changed")
merged = lines[idx]
print("merged row:", merged[:120])
new_merged = merged.replace("Biggame/BigMoney/BigHouse/CPH4 Labs", "Biggame/BigHouse/CPH4 Labs")
bm_row = ("| BigMoney | **0 件**（如实·诚实延续） | "
          "NATS 机队总线 bm-c 节点上线+回执上链（cph4/fleet/inbox/MSG-1653-bmc-natsbus.md @ e0409120·心跳任务 every:1m 在役·三机行全绿）"
          "+ W278 引擎周期闭环（finalize 账 1,035,935 / K=609,520 EXACT·五钥 6/6·results/perpetual_faces/n1_w278_results.json）"
          "+ W279 prereg PREP 锚件机冻（results/_w279bmc_prep_facts.json + T0 冻结面字节验 99001d3d3f337942）"
          "+ T0 针脚楼层实测收据（results/_w279bmc_needle_floors.json） | "
          "W279 prereg derive 冻结上链（r1122 首动作·builder 一代滚动→ALL GATES→banned ADMIT→freeze push）；引擎波链常设全速（W279=第 269 波·席位已立）"
          " 〔bm-c r1121 落行 17:0x〕 |")
lines[idx] = bm_row + "\n" + new_merged
text2 = "\n".join(lines)
assert "BigMoney |" in text2 and text2.count("BigMoney |") == 1, "row insert failed"
tmp = os.path.join(tempfile.gettempdir(), "daily-output-bmc-r1121.md")
open(tmp, "w", encoding="utf-8", newline="").write(text2)
g("read-tree", base, env_extra=env)
h = subprocess.run(["git", "-C", GRP, "hash-object", "-w", tmp], capture_output=True, text=True).stdout.strip()
assert len(h) == 40, "blob not 40hex"
print("blob:", h)
g("update-index", "--add", "--cacheinfo", "100644,%s,%s" % (h, PATH), env_extra=env)
tree = g("write-tree", env_extra=env)
assert len(tree) == 40, "tree not 40hex"
newc = subprocess.run(["git", "-C", GRP, "commit-tree", tree, "-p", base, "-m",
                       "DAILY-OUTPUT-REPORT: BigMoney 2026-10-19 行落 (对外0件如实+NATS总线节点上链回执+W278周期闭环+T0针脚实测·bm-c r1121) [16:26 每日产出汇报令·各司22:0x·提前落行]"],
                      capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()
assert len(newc) == 40, "commit not 40hex"
print("commit:", newc)
r = subprocess.run(["git", "-C", GRP, "push", "origin", newc + ":refs/heads/main"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
out = r.stdout + r.stderr
print("push rc:", r.returncode, out[:200])
if r.returncode != 0 or any(k in out.lower() for k in ("fatal", "rejected", "non-fast-forward")):
    raise SystemExit("PUSH FAILED")
subprocess.run(["git", "-C", GRP, "fetch", "origin"], capture_output=True)
after = g("rev-parse", "origin/main")
print("origin/main:", after, "LANDED" if after == newc else "RACED?")
os.remove(env["GIT_INDEX_FILE"])
