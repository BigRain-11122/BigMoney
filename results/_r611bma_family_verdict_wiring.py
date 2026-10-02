"""r611 bm-a surgical wiring: (A) iteration_prompt S0 reland shared-pool-face
max-merge law (MSG-2026-10-03-0612 proposal-1, bm-a face); (B) build_status
_family_verdict_state derive + main wiring; (C) dashboard.html family
verdict map chainRow. Byte-level edits, CRLF-preserving, anchors asserted
unique (r530 law). Read-only idempotence: skips faces already present."""

import sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def rd(p):
    with open(p, "rb") as f:
        return f.read()


def wr(p, data):
    with open(p, "wb") as f:
        f.write(data)


def edit(path, anchor, insert, insert_before=False, expect=1, tag=""):
    data = rd(path)
    n = data.count(anchor)
    if n != expect:
        print("FAIL anchor %r count=%d expect=%d" % (tag, n, expect))
        sys.exit(1)
    new = anchor + insert if not insert_before else insert + anchor
    data = data.replace(anchor, new)
    wr(path, data)
    print("OK %s (+%d bytes)" % (tag, len(insert)))


def crlf(text):
    return text.replace(b"\n", b"\r\n")


# --- (A) iteration_prompt.txt S0 reland law (MSG-0612 proposal-1) ---
ip = ROOT + r"\Tools\iteration_prompt.txt"
LAW = crlf(
    "S0 集成/收口 reland 环律（MSG-2026-10-03-0612 实弹·bm-a r611 立法）：撤-FF-重落/外科重放环 payload 含共享池面（runnable_pool.json/crash_fuse.json/pool 车道镜像族）时禁整文件重放——重放前对该面 per-face max-merge vs origin blob（owner_since/cleared_ts 等时间戳 newer-wins），或重放后立刻 python scripts\\merge_lane_views.py sync_face 幂等补 settle（实弹：陈旧 settle 快照整文件重放致 NULLS owner_since 回退 20min 破接管门→假接管评估窗 7.6min·crash fuse 侥幸拦截零双烧）；".encode("utf-8")
)
ip_anchor = "禁强推禁擅自解冲突；无远端/失败非阻塞）；".encode("utf-8")
data = rd(ip)
if "S0 集成/收口 reland 环律".encode("utf-8") in data:
    print("SKIP A (law already present)")
else:
    edit(ip, ip_anchor, LAW, tag="A-iteration-prompt")

# --- (B1) build_status.py: _family_verdict_state after _fund_family_state ---
bs = ROOT + r"\monitor\build_status.py"
FUNC = crlf(b'''

def _family_verdict_state() -> dict:
    """Deep-axis family verdict map (J10 lane, r611 bm-a): one-stop
    read-only derive of the judged/closed family lines -- the
    O-20261002-2115 speed-window verdict (LOWAMP-DEEP-P1) and the
    perpetual family faces (N4 pooled window closed at terminal wave
    B3, N3-R2 judged round). Single sources only:
      - results/lowamp_deep_p1/lowamp_deep_p1_results.json
      - results/perpetual_faces/n4_b3_results.json (terminal pooled wave)
      - results/perpetual_faces/n3_r2_results.json
    Missing sources degrade to honest None/empty, never fabricated."""
    out = {"present": False, "verdicts": []}

    def _add(name, **kw):
        row = {"family": name}
        for k, v in kw.items():
            if v is not None:
                row[k] = v
        out["verdicts"].append(row)

    p = os.path.join(PATHS.results_dir, "lowamp_deep_p1",
                     "lowamp_deep_p1_results.json")
    d = _read_json(p)
    if d:
        head = d.get("headline") or {}
        dsr = (d.get("gates") or {}).get("dsr") or {}
        led = d.get("trials_ledger") or {}
        _add("LOWAMP-DEEP-P1", verdict=d.get("verdict"),
             headline_sharpe=head.get("sharpe_full"),
             headline_trades=head.get("n_trades"),
             dsr=dsr.get("dsr"), n_trials=dsr.get("n_trials"),
             ledger_total=led.get("total"),
             evidence_cutoff=d.get("evidence_cutoff"))
    p = os.path.join(PATHS.results_dir, "perpetual_faces",
                     "n4_b3_results.json")
    d = _read_json(p)
    if d:
        members = d.get("members") or {}
        pos = 0
        for v in members.values():
            ci = ((v or {}).get("bootstrap_ci_sharpe") or {})
            if ci.get("ci_lower_bound_positive"):
                pos += 1
        waves = "+".join([str(w) for w in (d.get("pool_waves") or [])]
                         + [str(d.get("wave"))])
        _add("N4 (%s pooled)" % waves, verdict="window-closed",
             k_eff=d.get("k_eff"), members=len(members),
             ci95_lb_positive=pos)
    p = os.path.join(PATHS.results_dir, "perpetual_faces",
                     "n3_r2_results.json")
    d = _read_json(p)
    if d:
        packs = d.get("packs") or []
        judged = sum(1 for x in packs if x.get("status") == "judged")
        _add("N3-R2", verdict="judged",
             members=len(packs), members_judged=judged,
             window_cells=d.get("window_cells"),
             ledger_total=(d.get("trials_ledger") or {}).get("total"))
    out["present"] = bool(out["verdicts"])
    return out

''')
data = rd(bs)
if b"def _family_verdict_state" in data:
    print("SKIP B1 (function already present)")
else:
    anchor = b"def _token_state"
    edit(bs, anchor, FUNC, insert_before=True, tag="B1-build-status-func")

# --- (B2) build_status.py main wiring ---
data = rd(bs)
WIRE = crlf(b'    data["family_verdicts"] = _family_verdict_state()\n')
if b'data["family_verdicts"]' in data:
    print("SKIP B2 (wiring already present)")
else:
    anchor = b'    data["fund_family"] = _fund_family_state()\r\n'
    edit(bs, anchor, WIRE, tag="B2-build-status-wire")

# --- (C) dashboard.html family verdict chainRow ---
dh = ROOT + r"\dashboard.html"
JS = crlf(('''  const fv = D.data.family_verdicts;
  if (fv && fv.present) {
    const vtxt = (fv.verdicts || []).map(v => {
      let s = esc(v.family);
      if (v.verdict) s += `[${esc(v.verdict)}]`;
      if (v.headline_sharpe != null) s += ` S ${fnum(v.headline_sharpe, 3)}`;
      if (v.dsr != null) s += ` DSR ${fnum(v.dsr, 3)}`;
      if (v.k_eff != null) s += ` K_eff ${n2(v.k_eff)}`;
      if (v.members != null) s += ` ${n2(v.members)}员`;
      if (v.ci95_lb_positive != null) s += ` CI95下界>0 ${n2(v.ci95_lb_positive)}/${n2(v.members || 0)}`;
      if (v.window_cells != null) s += ` ${n2(v.window_cells)}窗`;
      if (v.ledger_total != null) s += ` 账 ${n2(v.ledger_total)}`;
      return s;
    }).join(" · ");
    rows.push(chainRow("家族判决图 · 深轴战役",
      vtxt, "dim", "judged/closed"));
  }
''').encode("utf-8"))
data = rd(dh)
if "D.data.family_verdicts".encode("utf-8") in data:
    print("SKIP C (render already present)")
else:
    anchor = crlf('排程/前置门")));\n  }\n'.encode("utf-8"))
    edit(dh, anchor, JS, tag="C-dashboard-render")

print("ALL EDITS DONE")
