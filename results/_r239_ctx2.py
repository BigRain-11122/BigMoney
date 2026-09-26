# -*- coding: utf-8 -*-
src = open("Tools/iteration_prompt.txt", encoding="utf-8", newline="").read()
i = src.find("monitor.build_status")
print("before build_status:", repr(src[i - 40: i + 30]))
print("n arrow-space legs:", src.count(" → "), "| n arrow-no-space:", src.count("→"))
k = src.find("token_meter.py")
print("before token_meter:", repr(src[k - 40: k + 20]))
