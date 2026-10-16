import io, sys, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
spec = importlib.util.spec_from_file_location("mfs", r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\30s-reel-v1\mv_full_shots.py")
mfs = importlib.util.module_from_spec(spec); spec.loader.exec_module(mfs)
names = {"C01_carver_face", "B01_weary", "D01_carver_words"}
found = {}
def walk(obj, path="root"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, path + "/" + str(k))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            walk(v, path + "[%d]" % i)
    elif isinstance(obj, str):
        for n in names:
            if n in obj:
                found.setdefault(n, []).append((path, obj[:300]))
for attr in dir(mfs):
    if attr.startswith("_"):
        continue
    walk(getattr(mfs, attr), attr)
for n in names:
    print("=====", n)
    for p, s in found.get(n, [])[:3]:
        print("  @", p, "::", s.replace("\n", " ")[:280])
