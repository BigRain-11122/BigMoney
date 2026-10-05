# -*- coding: utf-8 -*-
"""r555 bm-c S7-close row append (post-push tail, r714 family steady-state:
this row lands AFTER delivery; r556 churn-absorb collects it + this
script). EOL-preserving bytes append (bookkeeping lineage)."""
import os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
RR = os.path.join(ROOT, "round_reports-bm-c.md")

row = ("2026-10-05T16:18:42+08:00 | r555 bm-c S7-close | dept:工程 | 本地未达 origin commit 数=0"
       "（DELIVERED 三跳+absorb2 收口 per r524/r620/r704-1 律：round commit 217b0127a〔44 面=簿记三写+CODELY S4 条目+"
       "HANDOVER 5x 核对行+qa 证据包 r555 双件+S6 log/legdiff 收据+Tools/_r555bmc_* 脚本族+S6 再生面族+daemon lane churn〕"
       "首试 push_verify rc1=落后 origin 信号〔窗内 origin 前进 7=bm-a/bm-b 波〕→close 窗 merge rc2 零 UU=21 个 "
       "post-commit S6/daemon 脏面挡道〔r620 律〕→churn-absorb-2 007de9953〔22 面=确定性 pre-add 3〔daily_scorecard/"
       "dashboard twins=close#1 REGEN 清单漏网面〕+union 19〔paper 六员+paper_export+prospect 双 summary+runnable_pool+"
       "scorecard_v1+strategy_scorecard+t35_open_fill+x2_watch_log+daemon lane+close2/por_probe 脚本〕〕→merge 单停 "
       "1-UU〔attrition scan 同日双写：theirs 16:13:21>ours 16:13:17 机器探针定谳取 theirs·r554 血统 resolver "
       "ts-newer-wins 定向键〕→merge commit f06f29b1d→push#3 rc0 DELIVERED 0/0 tip f06f29b1d1 remote_match=True→ls-tree "
       "终探针 13/13 PASS〔含 HANDOVER.md+CODELY+legdiff 真门收据+簿记三写〕→orders 复扫 154/154 零未回执+inbox 0"
       "（S0.5/S7 双扫合规）→close_facts tail-defer 实测值落盘〔r532/r533 律〕〕| 零清扫/归档/删除/恢复类动作轮：登记册"
       "零命中断言 N/A-无此类动作（O-2030 §二.3 自证面）| 轮产品计分：2（HANDOVER 5x 核对行=产物清单刷新实物+qa/ 证据包 "
       "r555=能跑/能看实物〔93 trades·sharpe 0.1586·determinism=True·二十八连证〕+S6 38 面 CEO 再生面）| 本窗新坑 2 条="
       "①血统 git() helper 携带 .strip() 与 porcelain 消费面组合（r548 族复发新面·'esults/...' 路径首字符被吃 rc128 "
       "fail-fast 拦截·CODELY 行级 append 新律〔先查 strip 面必须审 helper 本体〕）②close#1 REGEN 清单漏 3 个 S6 再生面"
       "（daily_scorecard/dashboard twins·union backstop 过滤器不含→漏网为 absorb2 尾面·close v2 确定性 add 律已覆盖类"
       "不入册）| close 尾行滞后一拍机制注记（r714 族稳定态：本行 push 后落盘·r556 churn-absorb 收编）")

rr_raw = open(RR, "rb").read()
eol = b"\r\n" if b"\r\n" in rr_raw[-2000:] else b"\n"
row_b = row.encode("utf-8")
if eol == b"\r\n":
    row_b = row_b.replace(b"\n", b"\r\n")
if not rr_raw.endswith(eol):
    open(RR, "ab").write(eol)
open(RR, "ab").write(row_b + eol)
txt = open(RR, "rb").read().decode("utf-8", errors="replace")
cnt = txt.count("| r555 bm-c S7-close |")
assert cnt == 1, "r555 close row count != 1: %d" % cnt
print("CLOSE-ROW appended, count=%d" % cnt)
