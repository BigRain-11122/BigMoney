"""ETF asset-class tagging for panel decomposition.

Name-keyword classifier over data/basic/etf_list.csv (code, name), with a code-prefix
fallback. Ordered rules: bond/cash and commodity beat the equity default because their
names carry explicit markers (债 / 国开 / 货币 / 黄金 / 期货 ...).

Why not code prefixes alone: bond ETFs are NOT all 511xxx -- 159395/159396 (SZ) and
551900/551510 (SSE) are bond/money-market too, and prefix-only tagging silently pushed
them into the equity bucket.

Usage: python -c "from scripts.etf_asset_class import classify; print(classify())"
"""
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIST_PATH = os.path.join(BASE, "data", "basic", "etf_list.csv")

BOND_KW = ("债", "国债", "政金", "国开", "短融", "信用", "城投", "货币", "现金",
           "存单", "同业", "理财", "利率",
           # money-market funds whose names carry no "货币" marker at all:
           # 511880 银华日利 / 511990 华宝添益 / 159003 招商快线 were reaching
           # the equity book (r1257 live ticket: 2 of 5 picks were cash funds)
           "日利", "添益", "添利", "快线", "保证金", "日日", "天天金", "财富宝")
COMMOD_KW = ("黄金", "白银", "豆粕", "期货", "能源化工", "有色期货")
CROSS_KW = ("恒生", "港股", "纳指", "纳斯达克", "标普", "美国", "日经", "德国",
            "法国", "亚太", "中概", "海外", "东南亚", "沙特", "越南", "中韩",
            "中日", "新兴市场", "全球")
CONV_KW = ("转债", "可转债")

PREFIX_CLASS = (("511", "bond"), ("551", "bond"), ("518", "commodity"),
                ("513", "crossborder"))


def bare(sym):
    s = str(sym)
    return s[2:] if s[:2] in ("sh", "sz") else s


def class_from_name(name):
    """Class from a fund name, or None when no keyword fires.

    Returning None (rather than defaulting to "equity") is load-bearing: the
    old default made the prefix fallback unreachable, so 511880 银华日利 /
    511990 华宝添益 / 159003 招商快线 were tagged equity and the composite
    book bought money-market funds as if they were stocks (r1257 live ticket
    2/5).  Prefixes now decide when the name says nothing.
    """
    n = str(name)
    for kw in CONV_KW:
        if kw in n:
            return "convertible"
    for kw in BOND_KW:
        if kw in n:
            return "bond"
    for kw in COMMOD_KW:
        if kw in n:
            return "commodity"
    for kw in CROSS_KW:
        if kw in n:
            return "crossborder"
    return None


def class_from_prefix(code):
    c = bare(code)
    for pre, cls in PREFIX_CLASS:
        if c.startswith(pre):
            return cls
    return None


def load_map():
    """symbol (bare 6-digit) -> class, from the ETF list plus prefix fallback."""
    out = {}
    if os.path.exists(LIST_PATH):
        df = pd.read_csv(LIST_PATH, dtype=str)
        if {"代码", "名称"}.issubset(df.columns):
            for code, name in zip(df["代码"], df["名称"]):
                out[bare(code)] = class_from_name(name)
    return out


def classify(symbols=None):
    """symbol -> class for the given panel columns (name first, then prefix)."""
    m = load_map()
    out = {}
    for s in (symbols or []):
        b = bare(s)
        cls = m.get(b) or class_from_prefix(b) or "equity"
        out[s] = cls
    return out


if __name__ == "__main__":
    m = load_map()
    print("etf_list tagged:", len(m))
    print({k: v for k, v in pd.Series(list(m.values())).value_counts().items()})
    for c in ("159395", "159396", "511190", "551900", "551510", "518880", "510300"):
        print(c, m.get(c), class_from_prefix(c))