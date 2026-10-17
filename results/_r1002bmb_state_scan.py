import json, glob, os, io
REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
out = io.StringIO()
# 1) inbox unread
for p in sorted(glob.glob(REPO + r"\fleet\inbox\*.md") + glob.glob(REPO + r"\fleet\inbox\*.json")):
    out.write("INBOX_UNPROC: %s\n" % os.path.basename(p))
# 2) idle trigger state
try:
    it = json.loads(open(REPO + r"\results\idle_trigger_state.bm-b.json", "rb").read().decode("utf-8-sig"))
    out.write("IDLE_TRIGGER: %s\n" % json.dumps({k: it.get(k) for k in ("green_idle","claimable_pool_lines","idle_rounds","verdict","ram_free_pct","ts")}, ensure_ascii=False))
except Exception as e:
    out.write("IDLE_TRIGGER_ERR %s\n" % e)
# 3) py_watermark last verdict + next_pick
try:
    lines = open(REPO + r"\results\watermark.jsonl", "rb").read().decode("utf-8", "replace").strip().splitlines()
    last = json.loads(lines[-1])
    out.write("WM_LAST: %s\n" % json.dumps({k: last.get(k) for k in ("verdict","ts","next_pick","reason")}, ensure_ascii=False)[:600])
except Exception as e:
    out.write("WM_ERR %s\n" % e)
try:
    wr = json.loads(open(REPO + r"\results\watermark_red.json", "rb").read().decode("utf-8-sig"))
    out.write("WM_RED: red=%s next_pick=%s\n" % (wr.get("red"), str(wr.get("next_pick"))[:200]))
except Exception as e:
    out.write("WM_RED_ERR %s\n" % e)
# 4) saturation engine state (wave chain)
try:
    se = json.loads(open(REPO + r"\results\saturation_engine\state_bm-b.json", "rb").read().decode("utf-8-sig"))
    out.write("SAT_ENGINE: %s\n" % json.dumps({k: se.get(k) for k in ("current_wave","queue_depth","verdict","last_action","round","status")}, ensure_ascii=False)[:500])
except Exception as e:
    out.write("SAT_ERR %s\n" % e)
# 5) backlog claimable lines
try:
    txt = open(REPO + r"\fleet\backlog.md", "rb").read().decode("utf-8", "replace")
    cl = [l for l in txt.splitlines() if l.strip() and "claimed@" not in l and l.startswith(("-", "*"))]
    out.write("BACKLOG_CLAIMABLE=%d\n" % len(cl))
    for l in cl[:8]:
        out.write("  BL: %s\n" % l.strip()[:150])
except Exception as e:
    out.write("BACKLOG_ERR %s\n" % e)
print(out.getvalue())
