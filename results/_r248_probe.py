# -*- coding: utf-8 -*-
import io
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
src = io.open('Tools/post_review.py', encoding='utf-8', errors='replace').read()
i = src.find('def _check')
j = src.find('def _scan') if 'def _scan' in src else src.find('def main')
print(src[i:i+ (j-i) if j>i else 2600])
