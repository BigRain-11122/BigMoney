# r237 (bm-a): text-level minimal insert of progress_r237 into T-39 ticket
# (r230 law: probe indent/EOL, text-level insert, no json rewrite; BOM+CRLF preserved)
import io

PATH = "fleet/tasks/T-2026-09-25-39-P1.json"
raw = open(PATH, "rb").read()
assert b"progress_r237" not in raw, "already inserted (idempotent guard)"

anchor = b'next window ~03:41."\r\n}\r\n'
assert raw.count(anchor) == 1, "anchor not unique/found"
val = ("R237 bm-a hardening amendment (R236 family port, spec MF_COLLECTOR.md sec9): "
       "stale-repull dead-code + zero-symbol None-cutoff latent defects confirmed isomorphic "
       "(armed only after first pull completes +20td, ~2026-10-27 window) and fixed pre-arm -- "
       "_is_repull/_todo_for(done-reset, attempts cumulative per isolation law)/"
       "_panel_cutoff_from_bytes(512B tail derive)/_terminal_cutoff(zero-symbol round never "
       "writes None over live panel) + gate spawn_mode disclosure + refresh-repull subcommand "
       "dispatch; selftest 20/20->21/21 green (S21 dead-code fixture per r157 law); zero "
       "behavior change on first-pull/continuation faces (mirror still first-pull incomplete "
       "53/5222, source-blocked in flight per sec7 live-fire)")
import json
ins = (b'",\r\n  "progress_r237": ' + json.dumps(val, ensure_ascii=False).encode("utf-8") + b"\r\n}\r\n")
patched = raw.replace(anchor, ins)
open(PATH, "wb").write(patched)

# verify: CRLF counts, valid json, new key parses, old tail intact
raw2 = open(PATH, "rb").read()
t = raw2.decode("utf-8")
obj = json.loads(t)
assert obj["progress_r237"].startswith("R237 bm-a")
assert obj["progress_r116"].endswith("next window ~03:41.")
assert "03:41.\"," in t  # comma added to prior tail member
crlf, lf = raw2.count(b"\r\n"), raw2.count(b"\n")
print("insert OK: crlf=%d lf=%d (pure CRLF=%s) keys=%d" % (
    crlf, lf, crlf == lf, len(obj)))
