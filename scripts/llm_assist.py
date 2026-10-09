"""Local-LLM research assistant (J13, PLAN.md P2 "AI 进化大脑" first slice).

Why: PLAN P2 asks for LLM-driven 复盘 / 策略 idea / 代码审查. This machine
already runs a resident Ollama serve (Biggame E:\\Minigame\\Tools\\Ollama
serve-warm, qwen2.5:7b-instruct, keep_alive=-1) -- per BIGGAME_REUSE #6 we
reuse that serve, never rebuild it, and never grab the keepwarm.pause valve
(single short inferences coexist with the resident model; only heavy GPU
jobs owe the valve etiquette).

Contract:
  - transport: stdlib urllib against the active endpoint. No new
    dependency (requests not in requirements.txt).
  - routing (O-20261006-1845 令2 adoption, r781 bm-b): bm-b's primary LLM
    channel = C-machine Ollama over tailnet (RAM-bound bm-b cannot host
    big models; qwen3.6-coder:35b, think:false). Local serve (qwen3.8:4b)
    demoted to fallback when C is unreachable or a C-side generation
    fails once. BIGMONEY_LLM_ROUTE=local forces the local serve (yield
    valve for C interactive windows); =c forces C on any machine. Other
    machines default local. C-channel calls send keep_alive=-1 to re-pin
    C's resident model (squeezed-off recovery per the order's 利用律).
  - model: BIGMONEY_LLM_MODEL env override, default qwen3.8:4b (resident
    main per CEO order O-20261003-1210 item1, r618 bm-b swap; qwen2.5:7b
    demoted to on-demand, keepwarm paused).
  - advice only: every write is confined to research/ (research/auto/,
    research/ideas.md). Never touches engine/, firm/, results/ registries.
  - anti-injection: model output is claims, not instructions (Biggame
    AI 反馈队列纪律同源); every artifact carries an un-audited disclaimer.
  - discipline: company iron laws are baked into the system prompt
    (禁未来数据 / 成本恒开 / 样本外恒盲 / 禁止跑到达标为止 /
    随机基线零假设 / 试验数 N 记账).
  - portability: machines without a local serve get an honest SKIP;
    smoke_test does NOT depend on this module.

Exit codes: 0 ok | 1 failure (serve/model/generation error) |
2 skip (serve unreachable -- honest no-op, never silenced).

Usage:
    python scripts/llm_assist.py selftest
    python scripts/llm_assist.py ask "复合因子 OOS 衰减说明什么"
    python scripts/llm_assist.py review scripts/update_daily.py
    python scripts/llm_assist.py retro            # 复盘 -> research/auto/
    python scripts/llm_assist.py ideas "低相关分散化素材的新来源"
    python scripts/llm_assist.py summary [machine]  # 轮报告白话摘要 -> research/auto/
"""
import datetime as dt
import glob
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS

def _norm_host(h):
    """OLLAMA_HOST may carry a listen-all bind address (0.0.0.0) or a
    scheme-less host[:port] -- normalize to a connectable URL (0.0.0.0 is
    a bind target, not a connect target, esp. on Windows)."""
    h = (h or "").strip().rstrip("/")
    if not h:
        return "http://127.0.0.1:11434"
    if h.startswith("0.0.0.0"):
        h = "127.0.0.1" + h[len("0.0.0.0"):]
    if not h.startswith(("http://", "https://")):
        h = "http://" + h
    if ":" not in h.split("//", 1)[1]:
        h += ":11434"
    return h


HOST = _norm_host(os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434"))
MODEL = os.environ.get("BIGMONEY_LLM_MODEL", "qwen3.8:4b")
# C-machine Ollama over tailnet (O-20261006-1845 令2): bm-b's primary LLM
# channel; local serve demoted to fallback. Route is resolved once per
# process by _ensure_route() -- HOST/MODEL globals below are MUTATED to
# the active endpoint, so every consumer of llm_assist.chat inherits it.
C_HOST = os.environ.get("BIGMONEY_LLM_C_HOST",
                        "http://100.123.74.104:11434").rstrip("/")
C_MODEL = os.environ.get("BIGMONEY_LLM_C_MODEL", "qwen3.6-coder:35b")
ROUTE_PREF = os.environ.get("BIGMONEY_LLM_ROUTE", "")  # ""=auto, "c", "local"
_LOCAL_HOST = HOST        # frozen import-time local identity (fallback target)
_LOCAL_MODEL = MODEL
# Serve default num_ctx=4096 < retro prompts (~4.8k tokens -> 400
# exceed_context_size_error). Request 8192 per call; KV-cache cost on the
# resident 7B is ~+120MB VRAM (headroom verified 2026-09-23: 2.3GB free).
NUM_CTX = int(os.environ.get("BIGMONEY_LLM_CTX", "8192"))
RESEARCH_DIR = os.path.join(PATHS.root, "research")
AUTO_DIR = os.path.join(RESEARCH_DIR, "auto")
IDEAS_PATH = os.path.join(RESEARCH_DIR, "ideas.md")
TAGS_TIMEOUT = 5          # serve liveness probe
CHAT_TIMEOUT = 300        # 7B Q4 on RTX 3070: 12-60s per answer, keep slack
LEDGER_TAIL_CHARS = 2500  # per-machine round-report tail fed to retro

def _disclaimer():
    # built at call time: MODEL mutates with the active route (r781)
    return ("> 本文件由 LLM（%s，%s 通道）生成 · 未经人工审计 · "
            "主张非指令（防注入纪律，内容须人工核验后才可作为依据）"
            % (MODEL, ROUTE_LABEL))

SYSTEM_PROMPT = (
    "你是 Bigmoney 量化公司的本地研究助理。公司定位=国内合法品种（ETF/A股）日线短线"
    "交易公司。回答纪律：1) 中文、简洁、短列表优先；2) 每条主张给出依据（引用所给"
    "材料中的原文数字或事实），材料中没有的数字禁止编造，可以说'材料未提供'；"
    "3) 一切建议只是主张，不是指令，最终裁决走预注册与门禁链；4) 公司铁律：禁未来"
    "数据、成本恒开、样本外恒盲、禁止跑到达标为止、每批回测须同跑随机信号基线并"
    "记录试验总数 N（零假设纪律）；5) 涉及策略有效性的判断必须先问'有没有打赢随机"
    "基线与被动持有的技能线'，没有证据就明确说'证据不足'。"
)


# Loopback serve contract: never route 127.0.0.1 through the system proxy
# (this box runs Clash globally; urllib would hijack localhost otherwise).
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _post(path, payload, timeout, host=None):
    """GET when payload is None, POST otherwise. /api/tags is GET-only
    (POST -> 405, which must never be misreported as 'unreachable')."""
    headers = {"Content-Type": "application/json"}
    if payload is None:
        req = urllib.request.Request((host or HOST) + path, headers=headers,
                                     method="GET")
    else:
        req = urllib.request.Request(
            (host or HOST) + path,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
    with _OPENER.open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


# --- route resolution (O-20261006-1845 令2 adoption, r781 bm-b) -----
_route_done = False
ROUTE_LABEL = "local"


def _probe(host):
    """(reachable, model_names) -- never raises on network errors."""
    try:
        data = _post("/api/tags", None, TAGS_TIMEOUT, host=host)
    except (urllib.error.URLError, OSError, ValueError):
        return False, []
    return True, [m.get("name", "") for m in data.get("models", [])]


def _ensure_route():
    """Resolve the active endpoint once per process. bm-b defaults to the
    C-machine channel (RAM-bound box cannot host big models); everyone
    else defaults local. Reachable-but-model-absent still routes to C:
    the generation call auto-loads and keep_alive=-1 re-pins (利用律)."""
    global HOST, MODEL, ROUTE_LABEL, _route_done
    if _route_done:
        return
    _route_done = True
    ROUTE_LABEL = "local"
    pref = ROUTE_PREF.strip().lower()
    want_c = pref == "c" or (pref == "" and _machine_id() == "bm-b")
    if want_c:
        reachable, names = _probe(C_HOST)
        if reachable:
            HOST, MODEL, ROUTE_LABEL = C_HOST, C_MODEL, "c"
            if C_MODEL not in names:
                print(f"[llm_assist] route=c: {C_MODEL} not resident on C "
                      f"(squeezed off) -> generation will re-pin "
                      f"(keep_alive=-1)")
        else:
            print(f"[llm_assist] C endpoint {C_HOST} unreachable "
                  f"-> local fallback")


def check_serve():
    """(reachable, model_present, names) -- never raises on network errors."""
    _ensure_route()
    try:
        data = _post("/api/tags", None, TAGS_TIMEOUT)
    except (urllib.error.URLError, OSError, ValueError):
        return False, False, []
    names = [m.get("name", "") for m in data.get("models", [])]
    return True, MODEL in names, names


# --- L2 consumption ledger (O-20260926-0947 slice-3: every routine-doc
# leg routed to the local LLM is accounted leg-by-leg so token_meter can
# report the L2 share; est by the same bytes/3.5 proxy, honest rough).
USAGE_PATH = os.path.join(PATHS.results_dir, "llm2_usage.jsonl")
USAGE_KEEP = 500          # compact to last N legs (append-only + compaction)
BPE_PROXY = 3.5


def _machine_id():
    try:
        with open(os.path.join(PATHS.root, "fleet", "machine.json"),
                  encoding="utf-8") as fh:
            return json.load(fh).get("machine_id", "")
    except Exception:
        return ""


def _log_usage(cmd, prompt_bytes, response_bytes, out_path=None):
    """One ledger line per SUCCESSFUL L2 leg (skip/fail legs burn zero)."""
    try:
        rec = {"ts": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "machine": _machine_id(), "cmd": cmd, "model": MODEL,
               "prompt_bytes": int(prompt_bytes),
               "response_bytes": int(response_bytes),
               "tokens_est": int((prompt_bytes + response_bytes)
                                  / BPE_PROXY)}
        if out_path:
            rec["out_path"] = out_path
        os.makedirs(os.path.dirname(USAGE_PATH), exist_ok=True)
        with open(USAGE_PATH, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        # compaction (r225-family: shared append files must not grow
        # unbounded; keep-last rewrite is deterministic)
        try:
            with open(USAGE_PATH, encoding="utf-8") as f:
                lines = f.readlines()
            if len(lines) > USAGE_KEEP:
                tmp = USAGE_PATH + ".tmp"
                with open(tmp, "w", encoding="utf-8", newline="\n") as f:
                    f.writelines(lines[-USAGE_KEEP:])
                os.replace(tmp, USAGE_PATH)
        except OSError:
            pass
    except OSError:
        pass               # ledger failure must never fail the leg itself


def chat(messages, temperature=0.4, num_predict=900, usage_cmd=None):
    """One round-trip generation. Raises RuntimeError on API/model errors
    (HTTP body surfaced -- API errors must never read as 'unreachable').
    usage_cmd: when set, a successful generation is ledgered as one L2
    consumption leg (O-0947 slice-3).
    Routing (r781): a C-channel failure (HTTP/network/empty) falls back
    to the local serve once -- C interactive windows must not block the
    leg (错峰让路); a local failure raises as before."""
    global HOST, MODEL, ROUTE_LABEL
    _ensure_route()

    def _gen():
        payload = {
            "model": MODEL,
            "messages": messages,
            "stream": False,
            # thinking-capable models must not burn the num_predict budget
            # on chain-of-thought: advisory lane wants the answer only
            # (empirical: think default ate all 12 selftest tokens ->
            # empty content -> FAIL)
            "think": False,
            "options": {"temperature": temperature,
                        "num_predict": num_predict,
                        "num_ctx": NUM_CTX},
        }
        if ROUTE_LABEL == "c":
            payload["keep_alive"] = -1   # re-pin C's resident model (O-1845)
        try:
            return _post("/api/chat", payload, CHAT_TIMEOUT)
        except urllib.error.HTTPError as e:
            try:
                detail = e.read().decode("utf-8", "replace")[:300]
            except Exception:
                detail = "(no body)"
            raise RuntimeError(f"API {e}: {detail}") from e

    def _content(data):
        c = (data.get("message") or {}).get("content")
        if not c:
            raise RuntimeError(f"empty generation: {json.dumps(data)[:200]}")
        return c

    try:
        content = _content(_gen())
    except (RuntimeError, urllib.error.URLError, OSError) as e:
        if ROUTE_LABEL != "c":
            raise
        print(f"[llm_assist] C-channel generation failed ({e}) "
              f"-> local fallback (错峰让路)")
        HOST, MODEL, ROUTE_LABEL = _LOCAL_HOST, _LOCAL_MODEL, "local"
        content = _content(_gen())
    if usage_cmd:
        _log_usage(usage_cmd,
                   len(json.dumps(messages, ensure_ascii=False)
                       .encode("utf-8")),
                   len(content.encode("utf-8")))
    return content.strip()


def _research_path(*parts):
    """Resolve a path strictly under research/ (write-confined there)."""
    p = os.path.abspath(os.path.join(RESEARCH_DIR, *parts))
    if not p.startswith(RESEARCH_DIR + os.sep):
        raise RuntimeError(f"write outside research/ refused: {p}")
    return p


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def _stamp(title, body):
    return (f"# {title}\n\n{_disclaimer()}\n"
            f"生成时间：{dt.date.today().isoformat()}\n\n{body.strip()}\n")


def _gather_retro_context():
    """Dashboard truth + per-machine round-ledger tails (facts only)."""
    chunks = []
    dash = os.path.join(PATHS.results_dir, "dashboard_status.json")
    if os.path.exists(dash):
        with open(dash, encoding="utf-8") as f:
            d = json.load(f)
        for key in ("trading", "research", "events"):
            if key in d:
                s = json.dumps(d[key], ensure_ascii=False)
                # 1800 (was 3000): ledgers grew past NUM_CTX=8192 -> the
                # retro leg went red with exceed_context_size_error; keep
                # prompt+gen <= ctx (r655 bm-b fix, dashboards+3x2500 tails)
                chunks.append(f"[dashboard_status.{key}]\n{s[:1800]}")
    for ledger in sorted(glob.glob(
            os.path.join(PATHS.logs_dir, "iteration-loop", "round_reports*.md"))):
        with open(ledger, encoding="utf-8", errors="replace") as f:
            tail = f.read()[-LEDGER_TAIL_CHARS:]
        chunks.append(f"[{os.path.basename(ledger)} 尾部]\n{tail}")
    return "\n\n".join(chunks) if chunks else "(无可用材料)"


def cmd_selftest():
    reachable, present, names = check_serve()
    if not reachable:
        print(f"[selftest] serve {HOST} unreachable -> SKIP (exit 2)")
        return 2
    if not present:
        print(f"[selftest] FAIL model {MODEL} absent; serve has: {names}")
        return 1
    reply = chat([{"role": "user",
                   "content": "自检：只回复四个字：自检通过"}],
                 temperature=0.0, num_predict=12, usage_cmd="selftest")
    guard = _research_path("auto", "guardtest.md")
    ok = guard.startswith(RESEARCH_DIR + os.sep)
    try:
        escape = _research_path("..", "engine", "x.md")
        refused = not escape.startswith(RESEARCH_DIR + os.sep)
    except RuntimeError:
        refused = True
    print(f"[selftest] serve OK, model OK, gen={reply!r}, "
          f"write-guard under research/ = {ok and refused}")
    print(f"[selftest] active route = {ROUTE_LABEL} ({MODEL} @ {HOST})")
    return 0 if (reply and ok and refused) else 1


def cmd_ask(question):
    answer = chat([{"role": "system", "content": SYSTEM_PROMPT},
                   {"role": "user", "content": question}],
                  temperature=0.5, usage_cmd="ask")
    print(answer)
    return 0


def cmd_review(target):
    if not os.path.isfile(target):
        print(f"[review] no such file: {target}")
        return 1
    with open(target, encoding="utf-8", errors="replace") as f:
        code = f.read()[:24000]
    prompt = (
        "审查以下代码。输出最多5条按严重度排序的问题，每条一行："
        "[严重度] 问题（含行号或函数名线索）+ 一句修复方向。重点：正确性、"
        "未来数据（look-ahead）风险、成本/复杂度、可测性。没有问题就明确说通过。"
        f"\n\n文件：{os.path.basename(target)}\n```python\n{code}\n```"
    )
    body = chat([{"role": "system", "content": SYSTEM_PROMPT},
                 {"role": "user", "content": prompt}], temperature=0.3,
                usage_cmd="review")
    stem = os.path.splitext(os.path.basename(target))[0]
    out = _research_path("auto", f"review-{stem}-{dt.date.today():%Y%m%d}.md")
    _write(out, _stamp(f"代码审查：{os.path.basename(target)}",
                       f"审查对象：`{target}`\n\n{body}"))
    print(f"[review] saved {out}\n\n{body}")
    return 0


def cmd_retro():
    ctx = _gather_retro_context()
    prompt = (
        "基于以下真实运行材料做今日复盘。输出三节：①今天做得对的（引用原文证据）；"
        "②风险与隐患（只依据材料，每条给原文依据）；③下轮建议（3-5条，每条一句话，"
        "标注优先级）。材料：\n\n" + ctx
    )
    body = chat([{"role": "system", "content": SYSTEM_PROMPT},
                 {"role": "user", "content": prompt}], temperature=0.3,
                usage_cmd="retro")
    out = _research_path("auto", f"retro-{dt.date.today():%Y%m%d}.md")
    _write(out, _stamp(f"自动复盘 {dt.date.today().isoformat()}", body))
    print(f"[retro] saved {out}\n\n{body}")
    return 0


def _ledger_path(mid):
    """Per-machine round ledger (fleet/README sec.6 file-split: bm-b keeps
    the legacy round_reports.md, every other machine uses the -<id> suffix;
    self-drive T1 consumes the OWN-machine ledger by default)."""
    name = "round_reports.md" if mid == "bm-b" else f"round_reports-{mid}.md"
    return os.path.join(PATHS.logs_dir, "iteration-loop", name)


def cmd_summary(machine=None):
    """Round-ledger tail -> plain-language summary (T1, O-20261009-1246 P2
    queue head). CEO 白话律 (O-20260927-2244): no jargon, numbers up front,
    one-line verdicts. Advisory artifact only (claims, never instructions)."""
    mid = machine or _machine_id() or "bm-c"
    ledger = _ledger_path(mid)
    if not os.path.isfile(ledger):
        print(f"[summary] no such ledger: {ledger}")
        return 1
    with open(ledger, encoding="utf-8", errors="replace") as f:
        tail = f.read()[-LEDGER_TAIL_CHARS:]
    prompt = (
        "把下面这份机器轮账本尾部（最新一轮）压成给外行 CEO 看的白话摘要。"
        "纪律（CEO 白话律）：①禁行话术语，术语要么翻译成人话要么不用；"
        "②数字直给；③每问一句话结论。固定三问，每问一行：本轮做了什么"
        "（含最关键的 1-2 个数字）/最强的验证证据是什么/下轮要干什么。"
        "总共不超过 6 行。材料：\n\n" + tail
    )
    body = chat([{"role": "system", "content": SYSTEM_PROMPT},
                 {"role": "user", "content": prompt}], temperature=0.2,
                num_predict=400, usage_cmd="summary")
    out = _research_path(
        "auto", f"summary-{mid}-{dt.date.today():%Y%m%d}.md")
    _write(out, _stamp(f"轮报告白话摘要 {mid} {dt.date.today().isoformat()}",
                       f"材料：`{ledger}` 尾部 {LEDGER_TAIL_CHARS} 字符\n\n{body}"))
    print(f"[summary] saved {out}\n\n{body}")
    return 0


def cmd_ideas(topic):
    prompt = (
        f"围绕主题「{topic}」为 Bigmoney 提出 3 个可验证的研究/工程 idea。"
        "每个 idea 三行：一句话假设 / 为什么值得测（依据公司现状）/ 最小验证路径"
        "（先过哪道门：随机基线技能线、成本×2、G1'/G2 门禁链）。提醒：策略类 idea "
        "必须先过有效性门才许扫参数。"
    )
    body = chat([{"role": "system", "content": SYSTEM_PROMPT},
                 {"role": "user", "content": prompt}], temperature=0.8,
                usage_cmd="ideas")
    section = _stamp(f"idea：{topic}", body)
    if os.path.exists(IDEAS_PATH):
        with open(IDEAS_PATH, encoding="utf-8") as f:
            old = f.read()
    else:
        old = "# research ideas（J13 本地 LLM 研究助理产出，逐条追加）\n"
        _write(IDEAS_PATH, old)
    with open(IDEAS_PATH, "a", encoding="utf-8", newline="\n") as f:
        f.write("\n" + section)
    print(f"[ideas] appended to {IDEAS_PATH}\n\n{body}")
    return 0


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "selftest":
        return cmd_selftest()
    if cmd == "ask":
        return cmd_ask(" ".join(rest)) if rest else 1
    if cmd == "review":
        return cmd_review(rest[0]) if rest else 1
    if cmd == "retro":
        return cmd_retro()
    if cmd == "summary":
        return cmd_summary(rest[0] if rest else None)
    if cmd == "ideas":
        return cmd_ideas(" ".join(rest)) if rest else 1
    print(f"unknown command: {cmd}\n{__doc__}")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except urllib.error.URLError as e:
        print(f"[llm_assist] serve unreachable ({e}) -> SKIP")
        sys.exit(2)
    except (RuntimeError, OSError, ValueError) as e:
        print(f"[llm_assist] FAIL: {e}")
        sys.exit(1)
