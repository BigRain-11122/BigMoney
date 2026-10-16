import io, sys, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
spec = importlib.util.spec_from_file_location("p", r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\JAY-REDO-PACK-v1.py")
pack = importlib.util.module_from_spec(spec); spec.loader.exec_module(pack)
m = {s[0]: s for s in pack.SHOTS}
print("I2V_TAIL >>>", pack.I2V_TAIL)
print()
for n in ("E01c_first_line.mp4", "SING1_torch_song_v2_s9013.mp4"):
    iv = m[n][3]
    print("=====", n, "len", len(iv))
    print(iv)
    print()
