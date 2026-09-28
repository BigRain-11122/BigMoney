t = open("results/_r404bmb_cls2.txt", encoding="utf-8", errors="replace").read()
i = t.find("unknown")
print(t[i - 5:] if i >= 0 else t[-1500:])
