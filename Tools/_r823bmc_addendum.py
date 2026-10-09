# r823 addendum append (UTF-8 clean, LF)
line = ("2026-10-10T01:44+08:00 | r823 补记：push 正道 3 连试=SSH reset 窗转 origin 移动拒"
        "（behind 6·他机在推进）→按协议推 origin machine/bm-c-r823 备份分支"
        "（本地未达 origin commit 数=6〔前驱 r822 absorb 面未推件+本轮收口+daemon keepalive〕"
        "·r824 S0 absorb-reconcile 收口·跨两轮红旗自警面）")
with open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\round_reports-bm-c.md", "a", encoding="utf-8", newline="") as f:
    f.write(line + "\n")
print("ADDENDUM_APPENDED")
