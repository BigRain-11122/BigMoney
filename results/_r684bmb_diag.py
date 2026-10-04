# r684 bm-b: diagnose needle counts in pool file
import io

FP = r"results/runnable_pool.json"
NEEDLE = b"O-202601002-2150"
FIX = b"O-20261002-2150"
raw = io.open(FP, "rb").read()
print("raw needle count:", raw.count(NEEDLE))
print("raw fix count:", raw.count(FIX))
patched = raw.replace(NEEDLE, FIX)
print("patched needle count:", patched.count(NEEDLE))
print("patched fix count:", patched.count(FIX))
i = raw.find(NEEDLE)
print("context:", raw[max(0, i - 80):i + 60])
# any second occurrence in patched?
j = patched.find(NEEDLE)
print("patched first needle pos:", j)
