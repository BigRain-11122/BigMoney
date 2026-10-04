import subprocess
CREAT = 0x08000000
for name, ref in [("r677_bmb_240df7e9d", "240df7e9d"),
                  ("bmc_r480_3fbfb4ed0", "3fbfb4ed0"),
                  ("autofill_e8173b2a0", "e8173b2a0"),
                  ("origin_main_now", "origin/main"),
                  ("worktree_now", None)]:
    if ref:
        b = subprocess.run(["git", "show", f"{ref}:results/runnable_pool.json"],
                           capture_output=True, creationflags=CREAT).stdout
    else:
        b = open(r"results\runnable_pool.json", "rb").read()
    crlf = b.count(b"\r\n")
    lf = b.count(b"\n")
    print(f"{name}: bytes={len(b)} CRLF={crlf} LF={lf} crlf_face={crlf >= max(1, lf) // 2}")
