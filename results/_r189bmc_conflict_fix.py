import io, re, sys

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\pool_worker.py"
src = io.open(P, encoding="utf-8").read()

# union resolution: origin (r404-cont) S14/S15 + r188 guard legs renumbered S16-S19
union = '''        # S14/S15 origin-blob read face (O-2210 item-3, r404-cont):
        # bogus ref degrades to local-file fallback without crash;
        # real origin/main blob readable as pool face.
        pool_fb = _load_pool(ref="refs/heads/__pw_selftest_bogus__")
        ok("S14 bogus ref -> local-file fallback returns pool",
           isinstance(pool_fb, dict) and len(pool_fb.get("entries", [])) > 0)
        pool_or = _load_pool()
        ok("S15 origin-main blob readable (post-fetch face)",
           isinstance(pool_or, dict) and "entries" in pool_or)
        # S16-S19 D-20260928-02 mid-git-op guard (hermetic fake roots)
        # (renumbered from r188 S14-S17 post-union with r404-cont S14/S15)
        fake = os.path.join(tmp, "fake_repo")
        ok("S16 clean tree -> no marker", _mid_git_op(fake) is None)
        os.makedirs(os.path.join(fake, ".git", "rebase-merge"))
        ok("S17 rebase-merge marker detected",
           _mid_git_op(fake) == "rebase-merge")
        shutil.rmtree(os.path.join(fake, ".git", "rebase-merge"))
        with open(os.path.join(fake, ".git", "MERGE_HEAD"), "w") as fh:
            fh.write("x")
        ok("S18 MERGE_HEAD marker detected",
           _mid_git_op(fake) == "MERGE_HEAD")
        os.remove(os.path.join(fake, ".git", "MERGE_HEAD"))
        with open(os.path.join(fake, ".git", "index.lock"), "w") as fh:
            fh.write("x")
        ok("S19 index.lock detected (live git op -> defer)",
           _mid_git_op(fake) == "index.lock")
'''

pat = re.compile(r"<<<<<<< HEAD\n.*?=======\n.*?>>>>>>> ec5e6839[^\n]*\n", re.DOTALL)
n = len(pat.findall(src))
if n != 1:
    print(f"ABORT: expected 1 conflict block, found {n}")
    sys.exit(2)
src = pat.sub(lambda m: union, src)
for marker in ("<<<<<<<", ">>>>>>>", "|||||||"):
    if marker in src:
        print(f"ABORT: residual marker {marker}")
        sys.exit(2)
io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print("RESOLVED: union applied, zero residual markers")
