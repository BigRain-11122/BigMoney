# r700 bm-b: decisions.md regression forensics (r639 family): diff blob at 53804aa (12:06) vs 06e9a1a (23:08)
import subprocess, tempfile, shutil, os, sys, hashlib

URLS = ["git@github.com:BigRain-11122/FluxGroup.git",
        "https://github.com/BigRain-11122/FluxGroup.git"]
d = tempfile.mkdtemp(prefix="d19fore_")
try:
    ok = False
    for url in URLS:
        r = subprocess.run(["git","clone","--filter=blob:none","--sparse",url,d],
                           capture_output=True, timeout=240)
        if r.returncode == 0:
            ok = True; break
        shutil.rmtree(d, ignore_errors=True)
        try: os.makedirs(d)
        except OSError: pass
    if not ok:
        print("CLONE_FAIL"); sys.exit(2)
    res = {}
    for rev in ["53804aa","06e9a1a","997a052"]:
        out = subprocess.run(["git","-C",d,"show",rev+":docs/decisions.md"], capture_output=True, timeout=120)
        b = out.stdout
        res[rev] = (len(b), hashlib.sha256(b).hexdigest().upper()[:16])
        # count key markers
        m104 = b.count(b"D-20261004-")
        m103 = b.count(b"D-20261003-")
        tail = b[-600:].decode("utf-8","replace").replace("\r","")
        res[rev] += (m103, m104)
        # save 53804aa copy for row diff
        if rev == "53804aa":
            open(os.path.join("results","_r700bmb_decisions_1206.bin"),"wb").write(b)
    lines = []
    for k,v in res.items():
        lines.append(f"{k}: len={v[0]} sha16={v[1]} D20261003count={v[2]} D20261004count={v[3]}")
    open(os.path.join("results","_r700bmb_d19_forensics.txt"),"w",encoding="utf-8").write("\n".join(lines)+"\n")
    print("\n".join(lines))
finally:
    shutil.rmtree(d, ignore_errors=True)
