# -*- coding: utf-8 -*-
"""r326 bm-a S4: append asi8 unit-trap pitlaw to CODELY.md (one entry)."""
import io
import os

p = "CODELY.md"
entry = ("- [2026-09-27 13:4x r326 bm-a] 坑律：**pandas 3.x DatetimeIndex.asi8 返回索引"
         "自身分辨率单位（微秒常见）非恒 ns——日历匹配/searchsorted 整数比较静默错位**——"
         "r326 实弹（W2-A runner LHB 面 selftest）：合成 idx 由 Timestamp 集合重建后单位=微秒，"
         "`idx.asi8` 得 1.42e15（微秒）而 `pd.to_datetime(...).values.astype('datetime64[ns]')"
         "'.astype('int64')` 得 1.42e18（ns）→searchsorted+相等比较全 miss→事件 placed=0 静默"
         "（幸 selftest first-signal 断言当场拦）。正典=日期匹配一律走 `datetime64[ns]` 值域"
         "（`idx.values.astype('datetime64[ns]')` vs 事件同铸）单位无关比较；序列化日历用 ISO "
         "字符串勿用 asi8 裸整数（`pd.DatetimeIndex(int64)` 按数组单位解释=再炸一次）。"
         "指针=scripts/census_fusion_s2_w2.py lhb_count_face + meta idx_iso 字段。\r\n")
with io.open(p, "a", encoding="utf-8", newline="") as f:
    f.write(entry)
s = io.open(p, encoding="utf-8").read()
assert "asi8" in s and "r326 bm-a" in s
size = os.path.getsize(p)
print("appended; new size:", size, "bytes; <10KB:", size < 10240)
