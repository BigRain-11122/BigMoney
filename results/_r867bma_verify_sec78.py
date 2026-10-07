# -*- coding: utf-8 -*-
import io, subprocess
wt = io.open(r"research\PERPETUAL_N1_W181_PREREG.md", encoding="utf-8", newline="").read()
blob = subprocess.run(["git", "show", "de699e8cd:research/PERPETUAL_N1_W181_PREREG.md"],
                      capture_output=True).stdout.decode("utf-8")
i7 = wt.find("## \u00a77")
iF = wt.find("- **\u8dd1\u524d\u51bb\u7ed3")
j7 = blob.find("## \u00a77")
jF = blob.find("- **\u8dd1\u524d\u51bb\u7ed3")
head_w = wt[:i7].replace("\r\n", "\n")
head_b = blob[:j7]
tail_w = wt[iF:].replace("\r\n", "\n")
tail_b = blob[jF:]
print("positions wt:", i7, iF, "| blob:", j7, jF)
print("head equal:", head_w == head_b)
print("tail equal:", tail_w == tail_b)
if head_w != head_b:
    for k, (a, b) in enumerate(zip(head_w, head_b)):
        if a != b:
            print("first head diff at", k, repr(a), repr(b), "| ctx wt:", repr(head_w[k-20:k+20]), "| ctx blob:", repr(head_b[k-20:k+20]))
            break
    else:
        print("len diff:", len(head_w), len(head_b), "| extra wt:", repr(head_w[min(len(head_w),len(head_b)):][:80]))
print("sec78 region wt:", repr(wt[i7:iF][:80]))
print("OK" if (head_w == head_b and tail_w == tail_b) else "MISMATCH")
