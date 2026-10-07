import subprocess, re
b = subprocess.run(["git", "show", "59fde9319:results/_r819bma_w172_freeze_edits.py"],
                   capture_output=True).stdout
t = b.decode("utf-8")
i = t.find("# r773 pit law leg 3")
print(t[i:i + 1600])
