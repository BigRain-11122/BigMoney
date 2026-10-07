import io, re
entry = io.open(r"results\_r822bma_w173_probe_n1_entry.txt", encoding="utf-8", newline="").read()
print("W171 count:", entry.count("W171"))
for m in re.finditer(r".{0,45}W171.{0,35}", entry):
    print(repr(m.group(0)))
