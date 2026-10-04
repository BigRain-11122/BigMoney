src = open("results/_r698bma_s6_chain.py", encoding="utf-8").read()
src = src.replace("_r698bma", "_r699bma").replace("r698 bm-a", "r699 bm-a")
open("results/_r699bma_s6_chain.py", "w", encoding="utf-8", newline="").write(src)
print("written bytes:", len(src))
