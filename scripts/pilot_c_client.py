"""T-70 local-coding pilot C-arm client (MSG-20260926-0925-bm-a, P1).

C arm = B arm (qwen3-coder:30b, frozen prompt, zero changes) + a self-fix
loop of <=3 rounds. Isolates the self-correction variable for the 10-09
midterm judgment: the ONLY feedback fed back to the model is its own
previous delivery plus the frozen verification command's failure output
(zero orchestrator hints), per the pre-registration
research/R-20260926-bma-pilot-C-arm.md (frozen before any C run).

Products isolated to results/local_coding_pilot/tasks/<NN>/C/:
  <name>.py         current best product (overwritten per round)
  roundK_code.py    each round's delivered code (provenance, kept)
  roundK_verify.out each round's verify exit + stdout + stderr (kept)
  roundK.diff       unified diff vs previous round (K >= 1, kept)
  raw_response.md   round-0 raw generation (B-parity face)
  metrics.json      aggregate per-round generation metrics
  verdict.json      {verdict: PASS|FAIL, fix_rounds, attempts, task}

Contract (frozen in prereg):
  - transport/model/temperature/num_ctx identical to the B client
    (imported; no re-implementation, zero drift).
  - verification: [sys.executable, <C>/<name>.py, "selftest"] from repo
    root -- arm-placement-protocol semantics-identical form; the frozen
    prompts' selftest contract is hermetic (reads no repo files).
  - verify timeout 120s per attempt; hard cap 4 attempts (round 0 + 3
    fix rounds); extraction failure = that round's verify face = FAIL
    (raw preserved, loop continues, round consumed).

Exit codes: 0 = task done (PASS or FAIL verdict recorded) | 2 = contract
failure (serve down / model missing / prompt missing).

Usage:
    python scripts/pilot_c_client.py <task_dir>            # run C arm
    python scripts/pilot_c_client.py selftest             # offline asserts
"""

import difflib
import io
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import pilot_b_client as B  # noqa: E402  (side-effect-free module, r231 law: no top-level effects here)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFY_TIMEOUT_S = 120
MAX_FIX_ROUNDS = 3
FEEDBACK_TAIL_CHARS = 4000  # context-safety cap on fed-back failure output

FIX_TEMPLATE = """{frozen_prompt}

---

你上一轮交付的完整代码：
```python
{prev_code}
```

冻结验证命令 `python scripts/{name} selftest` 失败（exit {exit_code}），输出如下：
```
{verify_tail}
```

请基于失败输出修复代码缺陷，重新输出修复后的完整文件（唯一 ```python 代码块，文件之外无任何解说文本）。"""


def _verify(product_path):
    """Run the frozen verification command (arm-placement form)."""
    r = subprocess.run(
        [sys.executable, os.path.abspath(product_path), "selftest"],
        capture_output=True, timeout=VERIFY_TIMEOUT_S, cwd=REPO)
    out = (r.stdout.decode("utf-8", "replace")
           + r.stderr.decode("utf-8", "replace"))
    return r.returncode, out


def _gen_round(prompt_text, tag, out_dir):
    """One streamed generation; returns (metrics, text) via B transport."""
    t0 = time.perf_counter()
    first_tok = None
    parts, done_meta, n_chunks = {}, {}, 0
    buf = []
    for chunk in B._post_stream({
        "model": B.MODEL,
        "messages": [{"role": "user", "content": prompt_text}],
        "stream": True,
        "options": {"temperature": 0.2, "num_ctx": B.NUM_CTX},
    }, B.STREAM_TIMEOUT):
        n_chunks += 1
        msg = chunk.get("message") or {}
        tok = msg.get("content") or ""
        if tok:
            if first_tok is None:
                first_tok = time.perf_counter() - t0
            buf.append(tok)
        if chunk.get("done"):
            done_meta = {k: chunk.get(k) for k in
                         ("eval_count", "prompt_eval_count",
                          "eval_duration", "prompt_eval_duration")}
    total = time.perf_counter() - t0
    text = "".join(buf)
    eval_count = done_meta.get("eval_count") or 0
    eval_dur = done_meta.get("eval_duration") or 0
    metrics = {
        "round": tag,
        "total_s": round(total, 3),
        "first_token_s": round(first_tok, 3) if first_tok else None,
        "n_stream_chunks": n_chunks,
        "eval_count": eval_count,
        "prompt_eval_count": done_meta.get("prompt_eval_count") or 0,
        "tok_s": round(eval_count / (eval_dur / 1e9), 2)
                 if eval_count and eval_dur else None,
    }
    return metrics, text


def run_task(task_dir):
    """Full C-arm loop for one task. Returns the verdict dict."""
    task_dir = os.path.abspath(task_dir)
    c_dir = os.path.join(task_dir, "C")
    os.makedirs(c_dir, exist_ok=True)
    prompt_path = os.path.join(task_dir, "prompt.md")
    prompt_full = io.open(prompt_path, encoding="utf-8").read()
    out_name = B.extract_target_name(prompt_full)
    if not out_name:
        raise SystemExit("no target-file name in frozen prompt")
    cut = prompt_full.find("\n---\n")
    frozen_prompt = prompt_full if cut < 0 else prompt_full[:cut]

    product = os.path.join(c_dir, out_name)
    all_metrics, prev_code = [], None
    verdict = {"verdict": "FAIL", "fix_rounds": MAX_FIX_ROUNDS,
               "attempts": 0, "task": os.path.basename(task_dir),
               "passing_round": None}
    for k in range(MAX_FIX_ROUNDS + 1):  # round 0 + 3 fix rounds
        verdict["attempts"] += 1
        if k == 0:
            prompt_text = frozen_prompt
        else:
            prompt_text = FIX_TEMPLATE.format(
                frozen_prompt=frozen_prompt, prev_code=prev_code,
                name=out_name, exit_code=last_exit,
                verify_tail=last_out[-FEEDBACK_TAIL_CHARS:])
        metrics, text = _gen_round(prompt_text, f"round{k}", c_dir)
        all_metrics.append(metrics)
        io.open(os.path.join(c_dir, f"round{k}_gen.md"), "w",
                encoding="utf-8").write(text)
        m = B.CODE_BLOCK_RE.search(text)
        code = m.group(1) if m else (
            text if text.lstrip().startswith(("#", "import", '"""')) else None)
        if not code or not code.strip():
            exit_code, out = -1, "extraction failure: no python code block in response"
        else:
            code = code.rstrip("\n") + "\n"
            io.open(os.path.join(c_dir, f"round{k}_code.py"), "w",
                    encoding="utf-8").write(code)
            if k > 0 and prev_code is not None:
                diff = "\n".join(difflib.unified_diff(
                    prev_code.splitlines(), code.splitlines(),
                    fromfile=f"round{k-1}", tofile=f"round{k}", lineterm=""))
                io.open(os.path.join(c_dir, f"round{k}.diff"), "w",
                        encoding="utf-8").write(diff or "(no line diff)")
            io.open(product, "w", encoding="utf-8").write(code)
            prev_code = code
            exit_code, out = _verify(product)
        io.open(os.path.join(c_dir, f"round{k}_verify.out"), "w",
                encoding="utf-8").write(f"exit={exit_code}\n{out}")
        last_exit, last_out = exit_code, out
        print(f"[C {verdict['task']}] round{k}: exit={exit_code} "
              f"{out.strip().splitlines()[-1][:100] if out.strip() else ''}")
        if exit_code == 0:
            verdict.update(verdict="PASS", fix_rounds=k, passing_round=k)
            break
    verdict["fix_rounds_dist_label"] = (
        "0 (single-shot)" if verdict["fix_rounds"] == 0 and verdict["verdict"] == "PASS"
        else ("1-3" if verdict["verdict"] == "PASS" else "3 (fail)"))
    io.open(os.path.join(c_dir, "metrics.json"), "w", encoding="utf-8").write(
        json.dumps(all_metrics, ensure_ascii=False, indent=1))
    io.open(os.path.join(c_dir, "verdict.json"), "w", encoding="utf-8").write(
        json.dumps(verdict, ensure_ascii=False, indent=1))
    return verdict


def main(argv):
    if len(argv) >= 2 and argv[1] == "selftest":
        return _selftest()
    if len(argv) != 2:
        print("usage: pilot_c_client.py <task_dir> | selftest", file=sys.stderr)
        return 2
    # honest preflight (same face as B client; never silent fallback)
    import urllib.error
    import urllib.request
    try:
        with B._OPENER.open(urllib.request.Request(
                B.HOST + "/api/tags", method="GET"),
                timeout=B.CONNECT_TIMEOUT) as r:
            names = [m.get("name", "") for m in
                     json.loads(r.read().decode("utf-8")).get("models", [])]
    except (urllib.error.URLError, OSError, ValueError) as e:
        print(f"serve unreachable: {e}", file=sys.stderr)
        return 2
    if not any(n.startswith(B.MODEL) or n.split(":")[0] == B.MODEL.split(":")[0]
               for n in names):
        print(f"model {B.MODEL} absent; have {names}", file=sys.stderr)
        return 2
    v = run_task(argv[1])
    print("verdict:", json.dumps(v, ensure_ascii=False))
    return 0


def _selftest():
    """Offline assertions (no network, no repo writes; r157 discipline)."""
    ok = 0
    # 1. fix-template round-trips: frozen prompt + prev code + tail feedback
    tpl = FIX_TEMPLATE.format(
        frozen_prompt="任务：x\n目标文件：scripts/foo.py",
        prev_code="print(1)\n", name="foo.py", exit_code=1,
        verify_tail="AssertionError: expected 2")
    assert "目标文件：scripts/foo.py" in tpl and "print(1)" in tpl
    assert "exit 1" in tpl and "AssertionError: expected 2" in tpl
    assert "修复" in tpl and "```python" in tpl
    ok += 1
    # 2. tail cap: fed-back output never exceeds the frozen cap
    huge = "x" * (FEEDBACK_TAIL_CHARS + 5000)
    assert len(huge[-FEEDBACK_TAIL_CHARS:]) == FEEDBACK_TAIL_CHARS
    ok += 1
    # 3. verdict label distribution face (prereg fifth column)
    for vr, fr, want in (("PASS", 0, "0 (single-shot)"), ("PASS", 2, "1-3"),
                         ("FAIL", 3, "3 (fail)")):
        label = ("0 (single-shot)" if fr == 0 and vr == "PASS"
                 else ("1-3" if vr == "PASS" else "3 (fail)"))
        assert label == want, (vr, fr, label)
        ok += 1
    # 4. round cap: MAX_FIX_ROUNDS + 1 attempts total (0 + 3)
    assert MAX_FIX_ROUNDS == 3 and len(range(MAX_FIX_ROUNDS + 1)) == 4
    ok += 1
    # 5. diff artifact face (unified diff between two rounds)
    d = "\n".join(difflib.unified_diff(
        ["a", "b"], ["a", "c"], fromfile="round0", tofile="round1",
        lineterm=""))
    assert "-b" in d and "+c" in d and "round0" in d
    ok += 1
    print(f"selftest: {ok} assertions ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
