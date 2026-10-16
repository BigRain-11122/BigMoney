import io, sys, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
spec = importlib.util.spec_from_file_location("mfs", r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\30s-reel-v1\mv_full_shots.py")
mfs = importlib.util.module_from_spec(spec); spec.loader.exec_module(mfs)
row = None
for idx in (12, 27, 35):
    r = mfs.NEW[idx]
    print("===== NEW[%d] len=%d" % (idx, len(r)))
    for j, x in enumerate(r):
        print("  [%d]" % j, str(x)[:600].replace("\n", " "))
