import io

LINE = (
    " - [2026-09-26 17:1x] 坑律（bm-a R258·T-73 s2 slice-D·bars osh 血统面·E1 侧车期自捕）：**bars `outstanding_share` 列=当前股本截面 ffilled 回填（000001/300750/600519 全史 ~0 次变动、仅末日 1 次微调实证）非逐行历史股本——任何「×osh」派生面（市值/换手率）历史段皆代理非真值：高送转/增发名历史值被 osh_today/osh_t 畸变，OOS 近末日段近真**；连带教训=**末 bar 单点对账门（turnover_derived 先例）对「截面 ffilled 回填」型源病零捕获力——派生侧车的对账门必须含历史变动性探针（逐 gate 名数全史 osh 变动次数，本轮 t73_mktcap_sidecar 门[5] 已立）**；波及披露：turnover_derived 侧车同病（slice-C IS 段换手率水平带反向畸变、其判读不翻案=OOS 近真+定律双面活，digest §5 留痕）。指针=Money02/data/cache/p1c_stock/mktcap_raw.meta.json honesty_face+osh_provenance_probe_gate_syms+scripts/t73_mktcap_sidecar.py 门[5]\r\n"
)
with io.open('CODELY.md', 'a', encoding='utf-8', newline='') as f:
    f.write(LINE)
print('appended')
