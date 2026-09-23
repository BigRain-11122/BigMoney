"""Token meter: L1 zero-token proxy accounting (CEO order O-20260923-2325).

Measures what can be measured LOCALLY (byte-level context loads that drive
round-by-round token spend), with an HONEST rough-estimate disclosure:
no exact CLI usage API exists today, so tokens ~ bytes / 3.5 (mixed
CN/EN BPE proxy rate) -- labeled rough, never presented as exact.

Sources measured per machine ledger:
  - Tools/iteration_prompt.txt   (fixed mandate context read every round)
  - logs/iteration-loop/state-<id>.json  "did" field (round-report write)
  - logs/iteration-loop/round_reports*.md size (ledger growth)
  - CODELY.md size (project-memory read load per round)
Snapshot-to-snapshot delta gives the trend line for the evolution ledger.

Products: results/token_usage.json (snapshot + delta vs previous).
Usage: python scripts/token_meter.py   (exit 0; zero network, zero API)
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS  # noqa: E402

BPE_PROXY = 3.5          # bytes/token rough proxy for mixed CN/EN text
OUT_PATH = os.path.join(PATHS.results_dir, "token_usage.json")
LOOP_DIR = os.path.join(PATHS.root, "logs", "iteration-loop")


def _tokens(nbytes: int) -> int:
    return int(nbytes / BPE_PROXY)


def _fsize(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def _states_and_reports():
    states, reports = {}, {}
    if not os.path.isdir(LOOP_DIR):
        return states, reports
    for name in os.listdir(LOOP_DIR):
        p = os.path.join(LOOP_DIR, name)
        if name.startswith("state") and name.endswith(".json"):
            machine = name[6:-5] or "default"
            did_bytes = 0
            try:
                with open(p, encoding="utf-8") as fh:
                    did_bytes = len(fh.read().encode("utf-8"))
            except Exception:
                pass
            states[machine] = {"file": name, "bytes": did_bytes}
        elif name.startswith("round_reports") and name.endswith(".md"):
            machine = (name.replace("round_reports", "").replace(".md", "")
                       or "default")
            reports[machine] = {"file": name, "bytes": _fsize(p)}
    return states, reports


def main() -> int:
    mandate_bytes = _fsize(os.path.join(PATHS.root, "Tools",
                                       "iteration_prompt.txt"))
    codely_bytes = _fsize(os.path.join(PATHS.root, "CODELY.md"))
    states, reports = _states_and_reports()

    machines = {}
    for machine in sorted(set(states) | set(reports)):
        st = states.get(machine, {})
        rp = reports.get(machine, {})
        machines[machine] = {
            "state_bytes": st.get("bytes", 0),
            "state_tokens_est": _tokens(st.get("bytes", 0)),
            "report_bytes": rp.get("bytes", 0),
            "report_tokens_est": _tokens(rp.get("bytes", 0)),
        }

    per_round_context = {
        "mandate_read_tokens_est": _tokens(mandate_bytes),
        "codely_read_tokens_est": _tokens(codely_bytes),
        "note": "per-round fixed context load (rough proxy bytes/3.5); "
                "CLI exact usage API unavailable -- honest rough estimate",
    }

    out = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "order": "O-20260923-2325",
        "method": {"bpe_proxy": BPE_PROXY, "disclosure":
                   "ROUGH ESTIMATE -- byte/3.5 proxy; never presented as "
                   "exact; exactness upgrade path = future CLI usage API"},
        "per_round_context": per_round_context,
        "machines": machines,
        "total_state_tokens_est": sum(
            m["state_tokens_est"] for m in machines.values()),
        "total_report_tokens_est": sum(
            m["report_tokens_est"] for m in machines.values()),
    }

    delta = None
    if os.path.exists(OUT_PATH):
        try:
            with open(OUT_PATH, encoding="utf-8") as fh:
                prev = json.load(fh)
            delta = {
                "prev_generated": prev.get("generated"),
                "state_tokens_growth": out["total_state_tokens_est"]
                - prev.get("total_state_tokens_est", 0),
                "report_tokens_growth": out["total_report_tokens_est"]
                - prev.get("total_report_tokens_est", 0),
                "mandate_growth": per_round_context[
                    "mandate_read_tokens_est"]
                - prev.get("per_round_context", {}).get(
                    "mandate_read_tokens_est", 0),
            }
        except Exception:
            delta = None
    out["delta_vs_prev"] = delta

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"saved: {OUT_PATH}")
    print(f"per-round fixed context ~ {per_round_context['mandate_read_tokens_est']}"
          f" + {per_round_context['codely_read_tokens_est']} tokens (rough); "
          f"ledger cumulative ~ {out['total_state_tokens_est']} state + "
          f"{out['total_report_tokens_est']} report tokens; "
          f"delta={None if delta is None else delta['state_tokens_growth']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
