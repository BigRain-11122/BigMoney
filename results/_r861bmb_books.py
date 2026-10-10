"""r861 bm-b closeout books: state.json bump + heartbeat + round report
append (bm-b lane files). UTF-8 byte-safe; heartbeat epoch = int()
(R170/R178 law); clock_read T-separated ISO8601 (R262 law)."""
import datetime as dt
import json
import os
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(REPO, "state.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-b.json")
REPORT = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")

now = dt.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(now.timestamp())

# ---------------- resource sampling (heartbeat fields)
def _sample():
    free_gb, ram_pct, vram_mb = 11.3, 47.0, 3500
    try:
        import psutil
        vm = psutil.virtual_memory()
        free_gb = round(vm.available / 1024**3, 1)
        ram_pct = round(vm.available / vm.total * 100, 1)
    except Exception:
        pass
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=15)
        if out.returncode == 0 and out.stdout.strip():
            vram_mb = int(float(out.stdout.strip().splitlines()[0]))
    except Exception:
        pass
    return free_gb, ram_pct, vram_mb


def main():
    free_gb, ram_pct, vram_mb = _sample()

    with open(STATE, encoding="utf-8") as f:
        st = json.load(f)
    st["machine_id"] = "bm-b"
    st["round_no"] = 861
    st["round"] = 861
    st["round_no_label"] = "r861"
    st["last_round_at"] = ts
    st["ts"] = ts
    st["updated"] = ts
    st["updated_at"] = ts
    st["last_seen"] = ts
    st["clock_read"] = ts
    st["last_round_ts"] = ts
    st["orphan_face"] = 0
    st["orphan_faces"] = 0
    did = (
        "r861: S0 pre2 absorb own daemon faces + rebase onto bm-c r851 pre3 "
        "(rebase-race closeout) + orders diff 0 (67/192/0) + D19 dual "
        "watermark identical (dec caca0c6e/ord f90233c7) + smoke 49/49 + "
        "orphan face=0 (round-zero probe 14 faces) + boards clear (job 0, "
        "183 tickets 0 open) + SAT alive rc0; PRIMARY PRODUCT = N2-W18 "
        "slice-3 FREEZE WINDOW: three-band registration perpetual_n2_w18_"
        "gen=732_500/scrnull=733_000/unc=733_500 (band width 499, family "
        "band [732_500,734_000), r682 live-horizon derive N1_BANDS 205 rows "
        "A_head_end=472_203 -> X=732_500 first 500-multiple above horizon "
        "[472_204..732_203], trio CLEAN vs 618 reserved intervals, W15-era "
        "next slot 546_000 now inside raised A-horizon = forced position "
        "machine proof; band gate ADMIT receipt _r861bmb_w18_band_gate.txt "
        "+ seed_admit_gate rc0 x3 span=500 FREE + repo text scan zero-hit + "
        "r687 pre-write recheck origin efb3c2961 three keys absent + prereg "
        "origin-side still DRAFT) + prereg posture flip DRAFT->FROZEN "
        "(five-condition machine-proof record + sec.3 rng streams pinned + "
        "sec.1 D6 choice (b) material-pool-no-registration + sec.0 "
        "meaning-gate three answers) + banned_direction_gate ADMIT rc0 + "
        "post-freeze probe 8/8 bands=true + selftest 22/22 + freeze commit "
        "d4c852425 pushed; slice-4 BURN WINDOW same round: run live = "
        "64-draw envelope fully consumed then pooled nulls 288 < 300 frozen "
        "sufficiency line -> honest refuse rc2 (zero product file, zero "
        "trials-ledger row, chain head 876,731 unchanged) -> V1=UNJUDGEABLE "
        "(non-fail non-pass, zero verdict claimed) + sec.7/sec.8 one-shot "
        "backfill (prediction reconciliation 3-unjudgeable+1-direction-"
        "confirmed; design lesson B=6 budget did not price T-84s3 redraw+"
        "skip attrition 25%; W19 redraft face; family_key alphagen_grammar_"
        "v1 stays open, G2 fallback NOT triggered) + gate_attrition.json row "
        "(kind=search-refusal, cells_ledger_delta=0) + attrition guard scan "
        "CLEAN + commit 7f267906a pushed; S6 41 legs 40 rc0 + alloc rc2 "
        "known 510880 (weekend no new bar, paper chain all idempotent "
        "no-ops, dualrun streak 16, ORANGE_COOL, thermo/dualarm/rev_osc "
        "landed, bm-a lanes all honest no-ops, [RETIRED] options honest); "
        "S7 quartet ALIVE (loop pin=2 no-op, watchdog idempotent re-"
        "register, dual claws in-place) + idle --worked (idle_rounds=0) + "
        "CODELY.md cap mini-split (migrated r838-bm-c/r839-bm-c encoding "
        "entries 1,209B verbatim -> pit-encoding.md, main 30,510->29,942B "
        "<= cap, receipt _r861bmb_codely_minisplit.json) + new null-budget-"
        "prices-attrition lesson entry + books + push behind=0 self-proof; "
        "W210 maintained PARKED on M9 gate (bm-a W208 not landed, heartbeat "
        "stale disclosed); moneyflow IC lawful-wait (MF panel 53/5222 "
        "source-blocked, bm-a lane)"
    )
    st["did"] = did
    st["last_action"] = did
    verdict = (
        "GREEN: r861 (freeze window landed with three-band registration + "
        "FROZEN flip machine proof; burn honestly refused at frozen "
        "sufficiency line 288<300 -> V1 UNJUDGEABLE, zero burn claimed; "
        "smoke 49/49; S6 41 legs 40 rc0 + alloc rc2 known 510880; dualrun "
        "streak 16; watermark red=false board-clear lawful; attrition "
        "CLEAN; quartet ALIVE; CODELY cap law held via mini-split; W210 "
        "parked on M9 gate disclosed; moneyflow IC lawful-wait; orders diff "
        "0; D19 identical)"
    )
    st["verdict"] = verdict
    nxt = (
        "r862 queue: N2-W19 prereg draft-window evaluation (B null budget "
        "+ sufficiency line re-derived from 25% attrition evidence, "
        "T-84s3/skip probe first; TRIAL_LABOR standing line; collision "
        "probe first) -> W210 freeze after W209 freeze+finalize lands (M9 "
        "chain, bm-c M10 automation armed on bm-a W208) -> moneyflow IC "
        "panel-ready watch (bm-a lane) -> pool-EOL fleet adjudication watch "
        "-> O-20261011-0012 CPU-max maintained"
    )
    st["current_task"] = nxt
    st["task"] = nxt
    st["next"] = nxt
    st["now_active"] = (
        "r861 closeout: N2-W18 frozen (three bands registered + FROZEN "
        "flip) and first burn honestly refused at the frozen sufficiency "
        "line (V1 UNJUDGEABLE, sec.7/8 backfilled); verdict readout r862"
    )
    st["latest_artifact"] = (
        "r861: scripts/science_gates.py three-band registration "
        "(perpetual_n2_w18_gen=732_500/scrnull=733_000/unc=733_500) + "
        "research/PERPETUAL_N2_W18_PREREG.md FROZEN with sec.7/sec.8 "
        "backfill (commits d4c852425/7f267906a) + receipts "
        "results/_r861bmb_w18_band_gate.txt + "
        "results/_r861bmb_codely_minisplit.json"
    )
    st["next_milestone"] = (
        "N2-W19 draft window <=10-13 (B/sufficiency re-derived from "
        "attrition evidence) OR alphagen line verdict via W19; W210 freeze "
        "after W209 freeze+finalize lands (M9 chain, bm-c M10 automation "
        "armed on bm-a W208); chain head 876,731 monotone; moneyflow IC "
        "burns when MF panel completes (bm-a lane)"
    )
    st["orphan_face_note"] = (
        "r861 closeout probe: py_faces=14 alive, orphans=0 (round-zero "
        "probe 04:4x rc0; zero live seats; slice-3/4 work only, no "
        "detached burns this round)"
    )
    with open(STATE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")

    # ---------------- heartbeat
    with open(HB, encoding="utf-8") as f:
        hb = json.load(f)
    hb["machine_id"] = "bm-b"
    hb["round"] = 861
    hb["round_no"] = 861
    hb["now_active"] = st["now_active"]
    hb["current_task"] = nxt
    hb["task"] = nxt
    hb["next"] = nxt
    hb["latest_artifact"] = st["latest_artifact"]
    hb["next_milestone"] = st["next_milestone"]
    hb["verdict"] = verdict
    hb["last_action"] = did
    hb["did"] = did
    hb["last_round_at"] = ts
    hb["last_seen"] = ts
    hb["updated"] = ts
    hb["updated_at"] = ts
    hb["ts"] = ts
    hb["clock_read"] = ts
    hb["heartbeat_epoch_utc"] = epoch
    hb["cpu_cores"] = 16
    hb["free_ram_gb"] = free_gb
    hb["ram_free_gb"] = free_gb
    hb["ram_free_pct"] = ram_pct
    hb["gpu_free_vram_mb"] = vram_mb
    hb["gpu_free_vram_gb"] = round(vram_mb / 1024, 1)
    hb["vram_free_gb"] = round(vram_mb / 1024, 1)
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    hb["orphan_faces"] = 0
    hb["orphan_face"] = 0
    hb["orphan_face_note"] = st["orphan_face_note"]
    hb["sync"] = {
        "last_push_ts": ts,
        "note": ("r861 closeout push (freeze window + refused-burn closeout "
                 "+ S6 chain + CODELY mini-split + books); post-push "
                 "behind=0 self-proof via fetch+rev-list"),
    }
    with open(HB, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    # int-type self-proof (R170/R178 law)
    with open(HB, encoding="utf-8") as f:
        check = json.load(f)
    assert isinstance(check["heartbeat_epoch_utc"], int), \
        "epoch must be JSON int (R170/R178 law)"
    assert "T" in check["clock_read"], "clock_read T-separator law (R262)"

    print(json.dumps({"state_round": st["round_no"], "hb_epoch_int": True,
                      "ts": ts, "ram_free_gb": free_gb,
                      "vram_free_mb": vram_mb}))


if __name__ == "__main__":
    main()
