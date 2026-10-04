import subprocess
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
def show(ref, path):
    r = subprocess.run(["git","-C",REPO,"show",f"{ref}:{path}"], capture_output=True)
    return r.stdout
for ref in ("HEAD","MERGE_HEAD"):
    b = show(ref, "CODELY.md")
    lines = b.splitlines()
    print("====", ref, "total lines:", len(lines))
    for l in lines[-12:]:
        print(repr(l.decode("utf-8","replace")[:120]))
