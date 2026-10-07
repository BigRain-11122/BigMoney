import io
m = io.open(r"results\_r830bma_w175_probe_n1_mat.txt", encoding="utf-8", newline="").read()
print("mat len:", len(m))
print("HEAD:", repr(m[:200]))
print("TAIL:", repr(m[-260:]))
NL = "\r\n"
print("endswith _set_wave(2)+NL+4sp:", m.endswith("_set_wave(2)" + NL + "    "))
print("endswith _set_wave(174):", m.endswith("_set_wave(174)"))
print("endswith _set_wave(2):", m.endswith("_set_wave(2)"))
i = m.rfind("_set_wave(")
print("last _set_wave ctx:", repr(m[i-60:i+40]))
c = io.open(r"results\_r830bma_w175_probe_n1_claim.txt", encoding="utf-8", newline="").read()
print("CLAIM:", repr(c[-200:]))
