"""explore.md conflict union (rebase UU): bm-b r823 primary + bm-a r947 convergent secondary."""
import io
import subprocess

G = "C:/Program Files/Git/cmd/git.exe"


def stage(st, path):
    out = subprocess.run([G, "show", f":{st}:{path}"], capture_output=True)
    assert out.returncode == 0, out.stderr[:200]
    return out.stdout.decode("utf-8")


path = "state/queue/explore.md"
origin = stage(2, path)  # bm-b side (primary, earlier commit)
mine = stage(3, path)

old_row = "| E3 | 北向资金数据源可达性扫描（akshare/东财源·情绪面因子候选） | 外源扫描两源交叉律 | done |"
new_row = ("| E3 | 北向资金数据源可达性扫描（akshare/东财源·情绪面因子候选）——r823 bm-b 判负收口"
           "（northbound_probe 12 面）+r947 bm-a 双源收敛判负（流量面 2024-08-16 政策死亡·"
           "季度持股 8 点快照+南向旁系登记不开发） | 外源扫描两源交叉律 | done |")
assert old_row in origin, "E3 origin row anchor missing"

my_line = (
    "> r947 消耗记录（bm-a）：E3 后到让路注记（撞头：bm-b r823 先手收口 E3=primary〔northbound_probe 12 面探针+results/northbound_probe.json+"
    "research/shortline/NORTHBOUND_DATA_REACHABILITY.md〕·bm-a r947 同窗独立完成=convergent secondary 让路——"
    "双机独立同判负：北向流量面 2024-08-16 政策死亡双源收敛〔bm-a 证据=scripts/hsgt_source_probe.py〔selftest 7/7·6 接口 8 请求〕+"
    "results/shortline/hsgt_source_probe.json+research/digests/DIGEST-20261010-e3-hsgt-source-probe.md〕；"
    "bm-a 增补证据面=same-endpoint 南向对照实验〔北向 0 vs 南向 -23.31/+26.22 亿真值=零填系政策非损坏〕+"
    "季度持股快照 8 点存活〔2024-09-30..2026-06-30 季度末 2.41→3.10 万亿〕+南向旁系日度真值登记不开发；"
    "判负判词以 bm-b r823 复活门三选一为准〔披露恢复/两源新渠道/CEO 新令+GM 署名票+T-67 §2 前向窗〕；双探针双判词件并档）\n"
)

txt = origin.replace(old_row, new_row)
txt = txt.rstrip("\n") + "\n" + my_line
io.open(path, "w", encoding="utf-8", newline="").write(txt)
print("union written:", len(txt.encode("utf-8")), "bytes (origin", len(origin.encode("utf-8")), "+ my line", len(my_line.encode("utf-8")), ")")
# zero-loss assertions
for anchor in ("r823 消耗记录", "r947 处理记录", "r821 消耗记录", "r822 消耗记录", "r946 消耗记录"):
    assert anchor in txt, anchor
assert "hsgt_source_probe.py" in txt and "northbound_probe" in txt
print("all consumption lines preserved; dual probes annotated")
