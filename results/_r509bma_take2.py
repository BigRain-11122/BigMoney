import subprocess

R = "C:/Users/sjs20/Desktop/FluxGroup/quant/bmoney".replace("bmoney", "bigmoney")
raw = subprocess.check_output(["git", "-C", R, "show",
                               ":2:scripts/perpetual_faces.py"])
open(R + "/scripts/perpetual_faces.py", "wb").write(raw)
print("wrote", len(raw), "bytes")
t = raw.decode("utf-8")
print("W5 band present:", "21_900" in t)
print("N3 runner referenced:", "perpetual_faces_n3" in t)
