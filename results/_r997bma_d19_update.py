import subprocess
# r997 D19 update: orders delta (3 rows, group/BigStream domain, zero BigMoney directives) consumed + acked
r = subprocess.run(["python","scripts\\d19_watermark.py","update","--advance","--receipt","results/_r997bma_d19_receipt.json"], capture_output=True)
print("rc=", r.returncode)
print(r.stdout.decode("utf-8","replace")[-1500:])
print(r.stderr.decode("utf-8","replace")[-500:])
