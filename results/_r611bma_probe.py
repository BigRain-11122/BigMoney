import io, re
dom = io.open(r"results/_r611bma_dom_dump.html", encoding="utf-8").read()
i = dom.find("家族判决图")
seg = dom[i - 100:i + 700]
print(seg)
