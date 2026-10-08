import pathlib

p = pathlib.Path(r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
                 r"\logs\iteration-loop\round_reports-bm-c.md")
row = (pathlib.Path(r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
                    r"\results\_r780bmc_s7close_row.txt")
       .read_bytes().rstrip(b"\n") + b"\n")
before = p.stat().st_size
with open(p, "ab") as f:
    f.write(row)
after = p.stat().st_size
print("appended_bytes=", after - before,
      "endswith_row=", p.read_bytes().endswith(row))
