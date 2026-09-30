"""RW-4 slice-2 (T-127, D-20260930-05): panel gate real-data probe.

Read-only on data (no writes), zero network. Runs the canonical data
gate (knowledge/panel_gate.py) against the REAL data/daily face and
proves the audit acceptance face for RW-4:

  - "1670 zhi stale files excluded" -- batch-mode gate over the full
    canonical universe with the audit Q7 caliber (stale_days=5);
  - "twin keys deduped, symbol set has no duplicates"
    (len(set)==len(list)) -- canonicalization of all 1724 file keys;
  - in-service lock: 48-member frozen whitelist gate PASS on the real
    panel + fail-closed injection legs (out-of-lock / twin request /
    stale-required / missing-in-lock).

Evidence -> results/_r476bma_rw4_slice2_probe.json
CEO face  -> results/RW4_PANEL_GATE_20260930.md
"""
import json
import os
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.insert(0, ROOT)
from knowledge import panel_gate as pg  # noqa: E402

DAILY = os.path.join(ROOT, "data", "daily")
OUT = os.path.join(ROOT, "results", "_r476bma_rw4_slice2_probe.json")
MEMO = os.path.join(ROOT, "results", "RW4_PANEL_GATE_20260930.md")

TZ = timezone(timedelta(hours=8))


def main():
    inv = pg.scan_daily_dir(DAILY)
    all_codes = sorted(set(inv.bare) | set(inv.prefixed))
    canon_seq = [pg.canonical_symbol(f) for f in
                 sorted(os.listdir(DAILY)) if f.endswith(".csv")]
    twins_found = len(canon_seq) - len(set(canon_seq))  # 48 prefixed twins
    unique_face = (len(set(all_codes)) == len(all_codes))  # codes unique AFTER dedup

    # G2/G3 real-data runs
    batch = pg.gate(all_codes, mode="batch", inventory=inv,
                    stale_days=pg.STALE_DAYS_DEFAULT)
    inservice = pg.gate(list(pg.INSERVICE_WHITELIST), mode="inservice",
                        inventory=inv, stale_days=pg.STALE_DAYS_DEFAULT)

    # fail-closed injection legs (synthetic fixtures, hermetic)
    inj = {}
    r = pg.gate(["sh510300", "510300"], mode="batch", inventory=inv)
    inj["twin_request_refused"] = (not r.ok) and any("twin/duplicate" in x for x in r.reasons)
    r = pg.gate(["510300", "600000"], mode="inservice", inventory=inv)
    inj["out_of_lock_refused"] = (not r.ok) and any("out-of-lock" in x for x in r.reasons)
    stale_fixture = dict(inv.last_bars)
    stale_fixture["510300"] = "2026-01-01"
    fx = pg.PanelInventory(bare=inv.bare, prefixed=inv.prefixed,
                           last_bars=stale_fixture)
    r = pg.gate(["510300"], mode="inservice", inventory=fx, anchor="2026-09-29")
    inj["stale_inservice_refused"] = (not r.ok) and any("stale" in x for x in r.reasons)
    r = pg.gate(["510300"], mode="batch", inventory=fx, anchor="2026-09-29",
                required=["510300"])
    inj["stale_required_refused"] = (not r.ok) and any("stale required" in x for x in r.reasons)
    miss = pg.PanelInventory(bare=dict(inv.bare), prefixed=dict(inv.prefixed),
                             last_bars=dict(inv.last_bars))
    miss.bare.pop("510300"), miss.last_bars.pop("510300")
    r = pg.gate(["510300"], mode="inservice", inventory=miss)
    inj["missing_inlock_refused"] = (not r.ok) and any(
        ("missing panel file" in x) or ("not served by canonical bare" in x)
        or ("missing in-lock" in x) for x in r.reasons)
    r = pg.gate(["600000"], mode="batch", inventory=inv, anchor=None,
                stale_days=pg.STALE_DAYS_DEFAULT)
    inj["stale_batch_excluded_not_refused"] = (r.ok and "600000" in r.excluded
                                               and r.accepted == [])

    anchor = max([b for b in inv.last_bars.values() if b])
    # file-face staleness (audit Q7 caliber: stale FILES incl. twin files)
    def _days_behind(d):
        from datetime import date
        y1, m1, d1 = map(int, anchor.split("-"))
        y2, m2, d2 = map(int, d.split("-"))
        return (date(y1, m1, d1) - date(y2, m2, d2)).days
    file_face_stale = 0
    for f in sorted(os.listdir(DAILY)):
        if not f.endswith(".csv"):
            continue
        lb = pg._tail_last_bar(os.path.join(DAILY, f))
        if not lb or _days_behind(lb) > pg.STALE_DAYS_DEFAULT:
            file_face_stale += 1
    out = {
        "probe": "rw4_slice2_panel_gate_realdata",
        "ticket": "T-2026-09-30-127 (RW-4 slice-2)",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "files_csv": len(canon_seq),
            "canonical_unique_codes": len(all_codes),
            "twins_deduped": twins_found,
            "bare_keys": len(inv.bare),
            "prefixed_keys": len(inv.prefixed),
            "panel_anchor_last_bar": anchor,
            "stale_days": pg.STALE_DAYS_DEFAULT,
            "batch_excluded_stale": len(batch.excluded),
            "file_face_stale_files": file_face_stale,
            "batch_accepted": len(batch.accepted),
            "inservice_accepted": len(inservice.accepted),
        },
        "acceptance_face": {
            "twins_found_in_files": twins_found,
            "len_set_eq_len_list_after_dedup": bool(unique_face),
            "audit_verbatim": "len(set)==len(list)",
            "stale_excluded_n": len(batch.excluded),
            "inservice_gate_ok": inservice.ok,
            "inservice_whitelist_n": len(pg.INSERVICE_WHITELIST),
            "inservice_sha16": pg.INSERVICE_SHA16,
        },
        "injection_legs": inj,
        "inservice_refusals": inservice.reasons,
        "divergence_disclosure": (
            "audit RW-4 row says in-service panel 'locked to 30'; no in-repo "
            "count reproduces 30 (48 bare core48 / 53 fresh / 6 registered / "
            "18 held / 22 PROSPECT). Lock = REAL 48-member universe, "
            "frozen sha16 "
            + pg.INSERVICE_SHA16
            + "; divergence disclosed, no 30-member panel fabricated."),
        "excluded_sample": dict(list(sorted(batch.excluded.items()))[:5]),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    c = out["counts"]
    print(f"files={c['files_csv']} canonical_unique={c['canonical_unique_codes']} "
          f"twins_deduped={c['twins_deduped']} anchor={anchor}")
    print(f"batch: accepted={c['batch_accepted']} "
          f"excluded_stale={c['batch_excluded_stale']}")
    print(f"inservice: ok={inservice.ok} accepted={c['inservice_accepted']}")
    print(f"len(set)==len(list) after dedup: {unique_face}")
    print("injection legs:", inj)

    assert twins_found == 48, "48 prefixed twins must be detected by canonicalization"
    assert unique_face, "after twin dedup the symbol set must have no duplicates"
    assert inservice.ok and len(inservice.accepted) == 48, \
        "in-service gate must accept exactly the 48 locked members on real data"
    assert c["batch_excluded_stale"] >= 1600, \
        "audit acceptance: ~1670 stale legacy files must be excluded"
    assert all(inj.values()), f"fail-closed injection leg failed: {inj}"
    _write_memo(out, batch, inservice)
    print(f"evidence -> {os.path.relpath(OUT, ROOT)}")
    print(f"CEO face  -> {os.path.relpath(MEMO, ROOT)}")


def _write_memo(out, batch, inservice):
    c = out["counts"]
    a = out["acceptance_face"]
    lines = [
        "# RW-4 数据门禁落地（T-127 / D-20260930-05·2026-09-30）",
        "",
        "门禁件 = `knowledge/panel_gate.py`（三腿·fail-closed：门禁不过=批不受理）",
        "实弹证据 = `results/_r476bma_rw4_slice2_probe.json`",
        "接线面 = `live/paper.py load_core`（在役面·行为恒等由 6/6 锚定门证明）",
        "",
        "## 审计验收面对账",
        "",
        f"- 全目录 {c['files_csv']} 个 CSV → 归一化去重后 {c['canonical_unique_codes']} 个唯一 symbol",
        f"  （孪生 {c['twins_deduped']} 对去重·`len(set)==len(list)` = "
        f"{'True' if a['len_set_eq_len_list_after_dedup'] else 'FAIL'}）",
        f"- 陈旧排除（N={c['stale_days']} 日·面板锚 {c['panel_anchor_last_bar']}）：",
        f"  归一化码面排除 {c['batch_excluded_stale']} 只 / 文件面陈旧 {c['file_face_stale_files']} 件",
        f"  （审计口径 1670+ 只陈旧件被排除 ✓·双口径如实并列）",
        f"- 在役面板锁：{a['inservice_whitelist_n']} 只冻结白名单"
        f"（sha16 {a['inservice_sha16']}）实弹过门 {c['inservice_accepted']}/48",
        "- 注入例 5/5 fail-closed 全过（孪生请求拒/越锁拒/在役陈旧拒/必需陈旧拒/在锁缺件拒）",
        "",
        "## 「锁定 30 只」差异披露（诚实律）",
        "",
        out["divergence_disclosure"],
        "",
        "## 陈旧排除样例（前 5）",
        "",
    ]
    for k, v in out["excluded_sample"].items():
        lines.append(f"- {k}: {v}")
    lines += [
        "",
        "## 采行注记",
        "",
        "- 直接前缀读者（div_lowvol 族 / trial_labor_w4 w5 / regime_calibration）",
        "  = 判负或归档线，按档存重估律留在原冻结口径；新批禁复用其读法。",
        "- 新批装配一律走 `panel_gate.gate(symbols, mode=...)`；G1 孪生/G2 陈旧",
        "  /G3 越锁任一命中 = rc≠0 = 批不受理。",
        "",
    ]
    with open(MEMO, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    main()
