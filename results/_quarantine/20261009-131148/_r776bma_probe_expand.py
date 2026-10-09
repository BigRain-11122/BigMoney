# -*- coding: utf-8 -*-
"""T-173 face-1 expansion probe: candidate proxy data availability (read-only)."""
import os
import pandas as pd

CANDS = [
    ("sh515220", "coal_2021"),
    ("sh512400", "nonfer_2021"),
    ("sh515210", "steel_2021"),
    ("sh512980", "media_metaverse_2021"),
    ("sz159992", "innopharma_2025"),
    ("sh562500", "robot_2025"),
    ("sh512800", "bank_div_2024"),
    ("sh560080", "tcm_2022"),
    ("sz159997", "electronics_2019"),
    ("sh510230", "fin_broker_2014"),
    ("sz159825", "agri_hog_2019"),
    ("sh515030", "ev_check"),
    ("sh513100", "nasdaq_check"),
    ("sh516010", "game_ai_2023"),
    ("sh512480", "semic_check"),
]

for code, tag in CANDS:
    p = f"data/daily/{code}.csv"
    if not os.path.exists(p):
        print(f"{code} {tag}: MISSING")
        continue
    df = pd.read_csv(p)
    dcol = df.columns[0]
    print(f"{code} {tag}: {len(df)} rows, {df[dcol].min()}..{df[dcol].max()}")
