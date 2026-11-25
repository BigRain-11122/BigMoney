# 一个 pp，两把尺子：r2073 噪声带的换算与它自己的差额不一致

独立席复算（只读，第二双眼睛）。对象=`results/etf_book_cap_trim_toll.json`（r2073）。

## 一句话

同一张面上，**差额**（19,543 元）用 `÷β` 折成钱，**噪声带**（58,920 元）却用 `×NAV` 折成钱。两者都是 exposure-β 单位的 pp，换算必须同法。噪声带被低估了 `1/β ≈ 2.08` 倍——正确值约 **122,386 元**。

## 三行对比

| 项 | 面里印的 | 正确算法 | 正确值 |
|---|---|---|---|
| 差额（over 0.941pp） | 19,543.03 | `over_pp/100/β·nav` | 19,547.39（差 4.36，舍入） |
| 噪声带（5.892pp） | **58,920.00** | `band_pp/100/β·nav` | **122,394.51** |
| 恒等式校核 | — | `k_noise_sd·nav` | 122,386.05 |

`ratio = 122,394.51 / 58,920.00 = 2.0773`，与 `1/β_now = 1/0.481394 = 2.0773` 逐位相等。

## 为什么

上游 `scripts/etf_book_cap_beta_units.py`：
- `band_units = k_noise_sd * beta` → `ruler_band_pp = 100*k_noise_sd*beta`，**是 exposure-β 单位**；
- `trim_cny = (k*beta-cap)/beta*nav`，**÷β** 折钱。

下游 `scripts/etf_book_cap_trim_toll.py` L219：
```python
band_cny = band_pp / 100.0 * nav        # ×NAV，漏了 ÷beta
```
于是同一个 exposure-β 的 pp，在同一页上有两个价：1pp≈2.08万元（差额侧）vs 1pp≈1万元（带侧）。

## 判词翻不翻

**不翻。** 19,543 元 < 122,386 元，`TRIM_IS_INSIDE_THE_RULER` 照旧成立——而且更成立。错的只是印出来的噪声带这一个数，以及它与同页差额的口径一致性。

## 修法（给主腿）

`band_cny = band_pp / 100.0 / beta_now * nav`，或更直接 `= k_noise_sd * nav`（恒等式，避开 band_pp 的 3 位舍入）。修后本页「差额 vs 噪声带」两数同尺。

## 复跑

```
python results/_unattended_bmc_band_audit_20261125.py
```
读 `results/etf_book_cap_beta_units.json` + `results/etf_book_cap_trim_toll.json`，不写任何共享面。
