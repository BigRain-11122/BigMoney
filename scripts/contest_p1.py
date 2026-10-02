"""CONTEST_P1 survivor-king contest enumeration -- T-2026-10-02-148 (O-20261002-2150 CEO direct).

Round-1 slice: ADMISSION ENUMERATION ONLY (deterministic, zero burn, pure
assembly -- T-146 precedent). Burn leg (YTD backtests, sharded pool units)
and assembly leg (contest table) land in later slices; this file freezes
the WHO-IS-IN face so burns can start.

Admission philosophy (O-2150 sec.1): contest face is GENEROUS --
any face with (a) a frozen runnable grammar AND (b) at least one positive
honest measurement signal enters. Science faces (judged/DSR/E1) stay
untouched; winners will carry 'contest-selected' labels, never
'scientifically proven'.

Sources (all on-tree, deterministic):
  S1 MASS_TRIAL_W1_SURVIVORS   -- full 166 judge-cell set (T-94), grammar
     joined from results/mass_trial/w1_candidates.json; ticket verbatim
     "full 166 set"; each row carries its best honest evidence line.
  S2 REV_CENSUS_POSITIVE       -- results/refine_bench_stock/rev_census/
     census_ranking.json top10_independent rows with sharpe_full > 0.
  S3 REV_P2_REFINE_POSITIVE    -- rev_p2/cells_summary.csv rows with
     sharpe_full > 0 (positive honest refine-bench signal).
  S4 LOWAMP_DEEP_EXPLORATION   -- lowamp_p3/s1_evidence_extract.json
     deep_axis_faces: judged-negative line BUT exploration-positive
     faces admitted per O-2150 verbatim (deep-axis +55~60% pair).
  S5 T146_LIVE_MEMBERS         -- 41 already-measured members
     (results/ytd_track_record/ytd_summary.json) join the SAME table;
     they include six employees + 27 accounts + SYSTEM-V1 + REV-OSC +
     watchlist members + grid/aggr sleeves.

Dedup: grammar fingerprint set (signal_sha256 for S1; face-name for
S2/S3/S4; member name for S5). No duplicate entrants (ticket mandate).

Output: results/contest_p1/entrants.json (+ ENTRANTS.md admission table).
Determinism: sorted sources, no wall-clock in payload; byte-identical
rerun. Subcommands: enumerate | selftest.
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "contest_p1")


def _read_json(path):
    with io.open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


def _iter_jsonl(path):
    with io.open(os.path.join(ROOT, path), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def _fmt_pct(x):
    return ("%+.2f%%" % (x * 100)) if isinstance(x, (int, float)) else str(x)


# --- source S1: mass-trial W1 survivors (full 166 set) -----------------------
def _src_mass_trial():
    cands = _read_json("results/mass_trial/w1_candidates.json")["candidates"]
    by_id = {c["id"]: c for c in cands}
    rows = []
    for shard in ("judge_shard_0of4.jsonl", "judge_shard_1of4.jsonl",
                  "judge_shard_2of4.jsonl", "judge_shard_3of4.jsonl"):
        for row in _iter_jsonl(os.path.join("results/mass_trial", shard)):
            rows.append(row)
    entrants = []
    for row in sorted(rows, key=lambda r: r["candidate_id"]):
        cid = row["candidate_id"]
        cand = by_id.get(cid)
        if cand is None:
            continue  # honest skip: grammar missing -> not frozen-runnable
        # best honest evidence line across legs/costs
        evid = []
        for leg, lr in sorted((row.get("legs") or {}).items()):
            for cost, cr in sorted((lr or {}).items()):
                if isinstance(cr, dict) and isinstance(cr.get("sharpe_full"), (int, float)):
                    evid.append((cr["sharpe_full"], leg, cost))
        best = max(evid) if evid else (None, None, None)
        entrants.append({
            "contest_id": "MT-W1-" + cid,
            "source": "MASS_TRIAL_W1_SURVIVORS",
            "face_name": "%s|%s" % (cand["family"], cand["id"]),
            "grammar": {"family": cand["family"], "kind": cand["kind"],
                        "params": cand["params"], "axes": cand.get("axes", {}),
                        "signal_sha256": cand.get("signal_sha256")},
            "grammar_ref": "results/mass_trial/w1_candidates.json#" + cid,
            "evidence": "stage-1 survivor (T-94 full 166 set); best judged "
                        "sharpe_full %s (%s %s)" % (
                            ("%+.4f" % best[0]) if best[0] is not None else "n/a",
                            best[1] or "-", best[2] or "-"),
            "ytd_legs": ["backtest"],  # candidates have no paper leg
        })
    return entrants


# --- source S2: rev census positive faces -----------------------------------
def _src_rev_census():
    rank = _read_json("results/refine_bench_stock/rev_census/census_ranking.json")
    entrants = []
    for row in sorted(rank.get("top10_independent") or [], key=lambda r: r.get("name", "")):
        sharpe = row.get("sharpe_full")
        if not isinstance(sharpe, (int, float)) or sharpe <= 0:
            continue  # honesty: positive-signal-only admission
        entrants.append({
            "contest_id": "RC-" + row["name"].replace("|", "-"),
            "source": "REV_CENSUS_POSITIVE",
            "face_name": row["name"],
            "grammar": {"depth": row.get("depth"), "entry": row.get("entry"),
                        "liq": row.get("liq"), "exit": row.get("exit"),
                        "H": row.get("H")},
            "grammar_ref": "results/refine_bench_stock/rev_census/census_ranking.json#top10_independent",
            "evidence": "census ranked independent: sharpe_full %+.4f, ann_ret %s, "
                        "entries %s" % (sharpe, _fmt_pct(row.get("ann_ret")),
                                        row.get("entries")),
            "ytd_legs": ["backtest"],
        })
    return entrants


# --- source S3: rev_p2 refine-bench positive cells --------------------------
def _src_rev_p2():
    import csv
    entrants = []
    path = os.path.join(ROOT, "results/refine_bench_stock/rev_p2/cells_summary.csv")
    with io.open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                sharpe = float(row.get("sharpe_full") or "nan")
            except ValueError:
                continue
            if sharpe <= 0:
                continue
            name = row.get("cell") or row.get("face") or "?"
            entrants.append({
                "contest_id": "RP2-" + name.replace("|", "-") + "-" + row.get("face", "x1"),
                "source": "REV_P2_REFINE_POSITIVE",
                "face_name": name,
                "grammar": {"face": row.get("face")},
                "grammar_ref": "results/refine_bench_stock/rev_p2/cells_summary.csv",
                "evidence": "refine-bench positive: sharpe_full %+.4f, ann_ret %s"
                            % (sharpe, row.get("ann_ret")),
                "ytd_legs": ["backtest"],
            })
    return entrants


# --- source S4: lowamp deep-axis exploration positives ----------------------
def _src_lowamp_deep():
    e = _read_json("results/lowamp_p3/s1_evidence_extract.json")
    entrants = []
    faces = e.get("deep_axis_faces") or {}
    for name in sorted(faces):
        row = faces[name] or {}
        # O-2150 verbatim: judged-negative line, exploration-positive faces
        # admitted (deep-axis +55~60% pair carried by LA-EDGE faces)
        if not name.startswith("LA-EDGE"):
            continue
        entrants.append({
            "contest_id": "LX-" + name.replace("|", "-"),
            "source": "LOWAMP_DEEP_EXPLORATION",
            "face_name": name,
            "grammar": {"face": name},
            "grammar_ref": "results/lowamp_p3/s1_evidence_extract.json#deep_axis_faces",
            "evidence": "O-2150 verbatim admission: judged-negative line, "
                        "exploration-positive deep-axis +55~60%% pair (%s)"
                        % json.dumps({k: row.get(k) for k in list(row)[:4]},
                                     ensure_ascii=False),
            "ytd_legs": ["backtest"],
        })
    return entrants


# --- source S5: T-146 live members (join the same table) ---------------------
def _src_live():
    s = _read_json("results/ytd_track_record/ytd_summary.json")
    entrants = []
    for m in sorted(s.get("members") or [], key=lambda x: x.get("member", "")):
        ytd = m.get("ytd_ret")
        if not isinstance(ytd, (int, float)):
            continue
        entrants.append({
            "contest_id": "LIVE-" + str(m.get("member", "")).replace(" ", "-"),
            "source": "T146_LIVE_MEMBERS",
            "face_name": str(m.get("member", "")),
            "grammar": {"member": m.get("member")},
            "grammar_ref": "results/ytd_track_record/ytd_summary.json",
            "evidence": "already-live member; YTD %s (T-146 measured, spliced "
                        "backtest+paper legs)" % _fmt_pct(ytd),
            "ytd_legs": ["backtest", "paper"],
        })
    return entrants


def _dedup_key(e):
    if e["source"] == "MASS_TRIAL_W1_SURVIVORS":
        return "sha:" + str(e["grammar"].get("signal_sha256"))
    if e["source"] == "T146_LIVE_MEMBERS":
        return "member:" + e["face_name"]
    return "face:" + e["face_name"]


def enumerate_entrants():
    sources = [
        ("MASS_TRIAL_W1_SURVIVORS", _src_mass_trial),
        ("REV_CENSUS_POSITIVE", _src_rev_census),
        ("REV_P2_REFINE_POSITIVE", _src_rev_p2),
        ("LOWAMP_DEEP_EXPLORATION", _src_lowamp_deep),
        ("T146_LIVE_MEMBERS", _src_live),
    ]
    entrants, seen, dup_dropped = [], set(), 0
    for src_name, fn in sources:
        for e in fn():
            e["_src_order"] = src_name
            k = _dedup_key(e)
            if k in seen:
                dup_dropped += 1
                continue
            seen.add(k)
            e.pop("_src_order")
            entrants.append(e)
    by_src = {}
    for e in entrants:
        by_src[e["source"]] = by_src.get(e["source"], 0) + 1
    payload = {
        "schema": "contest_p1_entrants_v1",
        "ticket": "T-2026-10-02-148 (O-20261002-2150 survivor-king contest)",
        "slice": "admission enumeration (deterministic, zero burn)",
        "dedup": "grammar fingerprint (signal_sha256 / face name / member name); "
                 "duplicates dropped: %d" % dup_dropped,
        "dedup_disclosure": "REV_P2_REFINE_POSITIVE rows are cost-x1/x2 refine "
                            "re-measurements of the same REV faces already "
                            "admitted via REV_CENSUS_POSITIVE (same grammar "
                            "fingerprint) -- dedup collapses them into the "
                            "census entrants by design; their refine evidence "
                            "travels with the census rows' source artifacts",
        "n_entrants": len(entrants),
        "n_by_source": dict(sorted(by_src.items())),
        "burn_note": "YTD backtest leg runner + pool shards = next slice; live "
                     "members carry T-146 measured YTD already",
        "entrants": entrants,
    }
    return payload


def _write_outputs(payload):
    os.makedirs(OUT_DIR, exist_ok=True)
    body = json.dumps(payload, ensure_ascii=False, indent=1) + "\n"
    with io.open(os.path.join(OUT_DIR, "entrants.json"), "w",
                 encoding="utf-8", newline="") as f:
        f.write(body)
    lines = [
        "# 胜者为王大赛（T-148·O-2150）· 准入枚举表 v1",
        "",
        "- 枚举律：确定性源枚举+语法指纹去重·禁人工挑（dup dropped: %s）"
        % payload["dedup"].rsplit(":", 1)[-1].strip(),
        "- 准入哲学：有冻结可跑语法+任一诚实正信号即入；judged 判负但探索面正信号者照入（O-2150）",
        "- 胜者标注律：竞赛选拔≠科学证明——晋升时如实注明 contest-selected",
        "- 本表=准入面；YTD 烧录段（01-05→09-23+纸盘腿拼接）=下一切片，已在跑成员直接同表（T-146 实测）",
        "",
        "| 源 | 入赛数 |",
        "|---|---:|",
    ]
    for src, n in payload["n_by_source"].items():
        lines.append("| %s | %d |" % (src, n))
    lines += ["", "总入赛面：**%d**" % payload["n_entrants"], ""]
    with io.open(os.path.join(OUT_DIR, "ENTRANTS.md"), "w",
                 encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))
    return body


def cmd_enumerate():
    payload = enumerate_entrants()
    body = _write_outputs(payload)
    print("entrants: %d | by source: %s" % (payload["n_entrants"],
                                            payload["n_by_source"]))
    _ = body
    return 0


def cmd_selftest():
    p1 = enumerate_entrants()
    b1 = json.dumps(p1, ensure_ascii=False, sort_keys=True)
    p2 = enumerate_entrants()
    b2 = json.dumps(p2, ensure_ascii=False, sort_keys=True)
    assert b1 == b2, "S1 determinism: two enumerations must be byte-identical"
    print("[PASS] S1 determinism (byte-identical double enumerate)")

    by_src = p1["n_by_source"]
    assert by_src.get("MASS_TRIAL_W1_SURVIVORS") == 166, \
        "S2 mass-trial full-166-set verbatim: %s" % by_src
    print("[PASS] S2 mass-trial survivors = full 166 set (ticket verbatim)")

    assert by_src.get("T146_LIVE_MEMBERS") == 41, \
        "S3 live members join same table: %s" % by_src
    print("[PASS] S3 T-146 live members = 41 join same table")

    assert by_src.get("LOWAMP_DEEP_EXPLORATION", 0) >= 1, \
        "S4 O-2150 verbatim: judged-negative exploration-positive LA-EDGE pair must be admitted"
    print("[PASS] S4 exploration-positive admission (O-2150 verbatim)")

    keys = [_dedup_key(e) for e in p1["entrants"]]
    assert len(keys) == len(set(keys)), "S5 dedup: no duplicate grammar fingerprints"
    print("[PASS] S5 grammar-fingerprint dedup zero duplicates")

    for e in p1["entrants"]:
        assert e.get("grammar") and e.get("evidence") and e.get("ytd_legs"), \
            "S6 entrant contract: %s" % e["contest_id"]
        if e["source"] in ("REV_CENSUS_POSITIVE", "REV_P2_REFINE_POSITIVE"):
            assert "sharpe_full" in e["evidence"], "S7 positive-signal line: %s" % e["contest_id"]
    print("[PASS] S6 entrant contract (grammar+evidence+legs)")
    print("[PASS] S7 positive-signal evidence lines on ranked sources")

    print("selftest: ALL PASS")
    return 0


def main(argv):
    if len(argv) < 2:
        print("usage: contest_p1.py enumerate|selftest")
        return 2
    if argv[1] == "enumerate":
        return cmd_enumerate()
    if argv[1] == "selftest":
        return cmd_selftest()
    print("unknown subcommand:", argv[1])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
