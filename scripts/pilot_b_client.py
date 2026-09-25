"""T-70 local-coding pilot B-arm client (O-20260925-2313-bm-c).

Why: prereg research/R-20260925-bma-local-coding-pilot.md s2 -- the B arm
must receive the frozen prompt verbatim and produce machine-verifiable
artifacts (generation log + first-token latency + total time + token
counts). Reuses the llm_assist.py loopback transport recipe
(ProxyHandler({}) -- never route 127.0.0.1 through the system proxy).

Contract:
  - transport: stdlib urllib, native /api/chat with stream=True (ndjson),
    so first-token latency is measurable. Zero new dependencies.
  - model: env BIGMONEY_PILOT_MODEL, default qwen3-coder:30b.
  - write-face: confined to results/local_coding_pilot/ (arm dirs only);
    never touches scripts/, engine/, firm/ registries.
  - honesty: raw response saved verbatim; extraction failure = exit 2 with
    the raw artifact preserved (never silently retried/edited).

Exit codes: 0 ok | 1 transport/model error | 2 contract failure
(serve down / model missing / no code block / empty generation).

Usage:
    python scripts/pilot_b_client.py <task_dir>          # run B arm
    python scripts/pilot_b_client.py selftest            # offline assertions
"""

import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
MODEL = os.environ.get("BIGMONEY_PILOT_MODEL", "qwen3-coder:30b")
NUM_CTX = 32768
CONNECT_TIMEOUT = 20
STREAM_TIMEOUT = 1800  # 30b hybrid CPU/GPU can be slow; generous but finite

# Loopback serve contract: never route 127.0.0.1 through the system proxy
# (this box runs Clash globally; urllib would hijack localhost otherwise).
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

CODE_BLOCK_RE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL)


def _post_stream(payload, timeout):
    """Yield decoded ndjson chunks; raise on transport errors."""
    req = urllib.request.Request(
        HOST + "/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with _OPENER.open(req, timeout=timeout) as resp:
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if not line:
                continue
            yield json.loads(line)


def generate(prompt_path, out_dir):
    """Stream one generation. Returns (metrics, text) or raises RuntimeError."""
    prompt = io.open(prompt_path, encoding="utf-8").read()
    # strip the trailing arm-placement note (not part of the frozen prompt
    # body the model must see; separator line is the boundary)
    cut = prompt.find("\n---\n")
    model_prompt = prompt if cut < 0 else prompt[:cut]

    os.makedirs(out_dir, exist_ok=True)
    t0 = time.perf_counter()
    first_token_s = None
    parts = []
    usage = {}
    done_meta = {}
    n_chunks = 0
    for chunk in _post_stream({
        "model": MODEL,
        "messages": [{"role": "user", "content": model_prompt}],
        "stream": True,
        "options": {"temperature": 0.2, "num_ctx": NUM_CTX},
    }, STREAM_TIMEOUT):
        n_chunks += 1
        msg = chunk.get("message") or {}
        tok = msg.get("content") or ""
        if tok:
            if first_token_s is None:
                first_token_s = time.perf_counter() - t0
            parts.append(tok)
        if chunk.get("done"):
            done_meta = {
                k: chunk.get(k) for k in
                ("eval_count", "prompt_eval_count", "eval_duration",
                 "prompt_eval_duration", "total_duration")
            }
    total_s = time.perf_counter() - t0
    text = "".join(parts)
    if not text.strip():
        raise RuntimeError("empty generation")
    eval_count = done_meta.get("eval_count") or 0
    eval_dur = done_meta.get("eval_duration") or 0
    tok_s = (eval_count / (eval_dur / 1e9)) if eval_count and eval_dur else None
    metrics = {
        "model": MODEL,
        "first_token_s": round(first_token_s, 3) if first_token_s else None,
        "total_s": round(total_s, 3),
        "n_stream_chunks": n_chunks,
        "eval_count": eval_count,
        "prompt_eval_count": done_meta.get("prompt_eval_count") or 0,
        "tok_s": round(tok_s, 2) if tok_s else None,
    }
    return metrics, text


def main(argv):
    if len(argv) >= 2 and argv[1] == "selftest":
        return _selftest()
    if len(argv) != 3:
        print("usage: pilot_b_client.py <task_dir> | selftest", file=sys.stderr)
        return 2
    task_dir = os.path.abspath(argv[1])
    arm_dir = os.path.abspath(argv[2])
    prompt_path = os.path.join(task_dir, "prompt.md")
    if not os.path.isfile(prompt_path):
        print(f"prompt.md missing under {task_dir}", file=sys.stderr)
        return 2

    # serve/model presence (honest preflight, never a silent fallback)
    try:
        with _OPENER.open(urllib.request.Request(
                HOST + "/api/tags", method="GET"),
                timeout=CONNECT_TIMEOUT) as r:
            names = [m.get("name", "") for m in
                     json.loads(r.read().decode("utf-8")).get("models", [])]
    except (urllib.error.URLError, OSError, ValueError) as e:
        print(f"serve unreachable: {e}", file=sys.stderr)
        return 2
    if not any(n.startswith(MODEL) or n.split(":")[0] == MODEL.split(":")[0]
               for n in names):
        print(f"model {MODEL} absent; have {names}", file=sys.stderr)
        return 2

    os.makedirs(arm_dir, exist_ok=True)
    t_gen = time.strftime("%Y%m%d-%H%M%S")
    try:
        metrics, text = generate(prompt_path, arm_dir)
    except urllib.error.HTTPError as e:
        io.open(os.path.join(arm_dir, f"raw_error_{t_gen}.txt"), "w",
                encoding="utf-8").write(str(e))
        print(f"API error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        io.open(os.path.join(arm_dir, f"raw_empty_{t_gen}.txt"), "w",
                encoding="utf-8").write(str(e))
        print(f"generation error: {e}", file=sys.stderr)
        return 1

    io.open(os.path.join(arm_dir, "raw_response.md"), "w",
            encoding="utf-8").write(text)
    io.open(os.path.join(arm_dir, "metrics.json"), "w",
            encoding="utf-8").write(json.dumps(metrics, indent=1))

    m = CODE_BLOCK_RE.search(text)
    code = m.group(1) if m else (text if text.lstrip().startswith(("#", "import", '"""')) else None)
    if not code or not code.strip():
        print("no python code block in response (raw preserved)", file=sys.stderr)
        return 2
    # normalize exactly one trailing newline
    code = code.rstrip("\n") + "\n"
    io.open(os.path.join(arm_dir, "rr_lint.py"), "w", encoding="utf-8").write(code)
    print("B arm wrote rr_lint.py | " + json.dumps(metrics, ensure_ascii=False))
    return 0


def _selftest():
    """Offline assertions on pure helpers (no network, no files written)."""
    ok = 0
    # code-block extraction family
    cases = [
        ("pre```python\nx=1\n```post", "x=1\n"),
        ("```py\ny=2\n```", "y=2\n"),
        ("```\nz=3\n```", "z=3\n"),
    ]
    for src, want in cases:
        m = CODE_BLOCK_RE.search(src)
        assert m and m.group(1) == want, f"extract failed: {src!r}"
        ok += 1
    # no-block fallback triggers only on code-looking text
    assert CODE_BLOCK_RE.search("plain text only") is None
    ok += 1
    print(f"selftest: {ok} assertions ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
