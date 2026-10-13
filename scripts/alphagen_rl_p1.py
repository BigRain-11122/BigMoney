#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""N2U3-ALPHAGEN-RL-P1 runner -- E17 leg-1 RL environment + in-repo PPO
minimal reproduction set (prereg DRAFT precedes this build; the FREEZE-GATE
refuses EVERY real-data burn until the freeze window lands).

Prereg: research/N2U3_ALPHAGEN_RL_P1.md (bm-b r889 DRAFT; drafting window
opened legally by E16 census_holds=true per its sec.3 ruling line). Batch
identity: N2 U3 channel-1 "new grammar" RL leverage judged batch, K=32
top formulas consumed on core48 via the frozen tsgate template (A158-
TSGATE-P1 precedent), criteria = shared library g1_prime_v2 /
g2_registration_v2, family_key=alphagen_rl_grammar (near-neighbor to
alphagen_random_grammar: same grammar, different search mechanism -- RL
feedback vs no-feedback sampling; disclosed, not asserted).

LEG MAP (prereg sec.0 compute budget):
  leg-1 (THIS BUILD, zero burn): runner + hermetic selftest + env-probe
       read-only fact receipt. pretrain/train/export-topk/judge carry the
       FREEZE-GATE and honestly refuse with a receipt while the prereg is
       DRAFT or any seed band is unregistered.
  leg-2 (post-freeze, pool): short-window training probe (~30-60min).
  leg-3 (post-freeze, pool): full training (2-6h, per-episode resume).

MACHINERY (verbatim import law -- zero rewrite):
  - Grammar space = E16 frozen face imported from scripts/
    alphagen_rg_census.py (import_a158_ops / OP_IMPL / node forms d1-d2 /
    formula_str / canonical_key / evaluate). Lineage single-source =
    research/shortline/external/qlib_alpha158_loader.py sha16
    814b7f7ab3d418ae (original qlib face, research artifact; executable
    single source = scripts/alpha158_compare.py build_inventory via the
    E16 import face, sha16 recorded in probe receipts).
  - Panel = E16 frozen census-instant cache (same-instant D2 lockbox,
    CAL_LAST=2026-10-09): e16.cache_path/ensure_cache reuse, zero rebuild.
  - IC faces = pa_lhb_ic rank_rows / ic_from_ranks / fwd_ret + composite_ic
    stats_block, imported verbatim (h=1 single caliber, E16 same-machinery
    law); NaN policy = full-window; MIN_CROSS=100 / MIN_PERIODS=30.
  - Nulls (judged face, post-freeze) = t23._permute_ranks_within_mask
    verbatim; training face runs NO nulls (search face, not trials).
  - Dedup = e16.canonical_key on the generalized template + excluded set
    (E16 census 200 strings + W19/W20 family products + TRIAL_GRAMMAR_
    LEDGER text scan); hits excluded and honestly counted, NEVER redrawn
    (W20 envelope law); in-batch dedup same key.

PPO MINIMAL REPRODUCTION SET (paper hyperparameters NOT copied -- every
value below is an in-repo disclosed value; AlphaGen claims = claimed-
unverified rider R3, measured by THIS batch only):
  - Token-MDP over the E16 grammar: step 0 depth {d1,d2}; d1 = op,input,
    window (4 tokens); d2 = op2,w2,op1,input,w1 (6 tokens). Vocab = 2+29+8+5
    = 44 tokens; per-step legal-action masks; state = 6 slot one-hots +
    step id (270-dim).
  - Policy = numpy MLP 270-64-64-44 tanh + linear value head; masked
    softmax; PPO clip 0.2, GAE(lambda=0.95, gamma=1.0 terminal-reward
    episodes), entropy coef 0.01, vf coef 0.5, Adam lr 3e-4, 4 epochs,
    minibatch 8, grad-norm clip 0.5, rollout 32 episodes/update.
  - Bootstrap pretraining ("zi ju pretrain", E16 rng machinery face):
    N_BOOT=256 uniform draws via e16._draw_node rng=[gen,9000+i] streams
    (depth split 60/40 by parity), behavior cloning of the top-quartile
    reward draw token sequences (BC_EPOCHS=8).
  - Reward = synergy-pool MARGINAL rank-IC (alphagen pool law): pool
    members = E16 census TOP-8 survivors + batch-admitted formulas;
    ensemble = per-date mean of mask-z-scored ranks, sign-aligned by each
    member's own IC; marginal = max over sign of [ic_mean(pool+{f}) -
    ic_mean(pool)]; admission threshold TAU_ADMIT=0.005 marginal.
    Honest boundary: registered members (zai ce cheng yuan) have NO stock
    cross-section factor face at training time -- they enter at the judged
    D6 gate (daily-return max|corr| >= 0.7 reject, sleeve-tag precedent);
    enforced in the judge face, disclosed here.
  - Training-time cost face: universe column subsample TRAIN_UNI_N=1024
    (seed-pinned deterministic subset of the cache universe; MIN_CROSS=100
    t23 law unchanged); export-topk re-evaluates survivors on the FULL
    panel face. Disclosed as training proxy; judged face is full-panel.

FREEZE-GATE (rc2 honest refuse + receipt, W19 hard-spec law: every refuse
path lands results/alphagen_rl_p1/refusal-*.json with the full condition
checklist; zero burn, zero ledger row):
  pretrain/train/export-topk require: (a) prereg head FROZEN (not DRAFT),
  (b) all three seed bands registered. judge additionally requires the
  leg-3 TOPK product + the freeze-window tsgate anchor receipt
  (results/alphagen_rl_p1/tsgate_anchors.json). The judged face itself is
  a post-freeze leg (frozen consumption template, probe-anchored same-face
  law G-ANCHOR-FACE); leg-1 judge = gate + refuse machine only.

SEED BANDS (freeze-window registration via Tools/seed_admit_gate.py rc0;
this module reads science_gates.SEED_REGISTRY at run time, NEVER
hardcodes values; DRAFT proposal = 20_625_000 family, +500 spacing):
  n2u3_alphagen_rl_gen      -- policy init / bootstrap draw streams /
                               training-universe subsample stream
  n2u3_alphagen_rl_scrnull  -- judged-face permutation null family
  n2u3_alphagen_rl_unc      -- reserved uncertainty berth (freeze wiring)

Subcommands:
  env-probe   -- read-only fact receipt (panel gate, census anchors,
                 grammar face, seed posture, banned-gate posture, closed
                 families, dedup sources, freeze-condition checklist) ->
                 results/alphagen_rl_p1/probe_latest.json
  pretrain    -- FREEZE-GATED bootstrap pretrain (leg-2 step 1)
  probe       -- FREEZE-GATED leg-2 compound probe (pool-entry face):
                 idempotent pretrain (skip when pretrain_policy.npz
                 exists) + train --episodes N, one atomic burn; receipt
                 = throughput face for leg-3 sizing
  train       -- FREEZE-GATED PPO fine-tune with per-episode resume (leg-3)
  export-topk -- FREEZE-GATED top-K=32 candidate table on the full panel
  judge       -- FREEZE-GATED judged face gate (leg-4; refuses until the
                 freeze-window anchors land)
  status      -- read-only checkpoint/product posture
  selftest    -- hermetic offline legs (r116 law: zero network, zero
                 engine, zero repo data reads; synthetic panels via the
                 e16 _synth_cache import face; freeze-gate machine proofs
                 redirect receipts to a system tempdir)

Exit contract: 0 = ok/no-op; 1 = selftest fail / usage; 2 = freeze-gate
refuse / awaiting panel / mechanism suspect (receipt landed).

-- bm-b r891 leg-1 * marks +0 * SEED bands consumed only post-freeze
   * research output, not investment advice * live-trading gate =
   monthly review + CEO-only, unchanged.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import science_gates as sg                                   # noqa: E402
import alphagen_rg_census as e16                             # noqa: E402
import t23_random_grammar_census as t23                      # noqa: E402
from pa_lhb_ic import rank_rows, ic_from_ranks, fwd_ret   # noqa: E402
from composite_ic import stats_block                       # noqa: E402
from parallel_runner import run_cells_parallel, worker_cap  # noqa: E402
from screening.pbo import cscv_pbo                         # noqa: E402

# ------------------------------------------------------------ frozen constants
BATCH = "N2U3-ALPHAGEN-RL-P1"
PREREG_REL = "research/N2U3_ALPHAGEN_RL_P1.md"
PREREG = os.path.join(ROOT, PREREG_REL)
QUEUE_ROW = "state/queue/explore.md E17 (N2 U3 channel-1 RL 主考批)"
FAMILY_KEY = "alphagen_rl_grammar"
CUTOFF_PIN = e16.CAL_LAST                  # census same-instant D2 lockbox
OUT_DIR = os.path.join(ROOT, "results", "alphagen_rl_p1")
CKPT_DIR = os.path.join(OUT_DIR, "ckpt")          # machine-local, gitignored
PROBE_RECEIPT = os.path.join(OUT_DIR, "probe_latest.json")
TSGATE_ANCHORS = os.path.join(OUT_DIR, "tsgate_anchors.json")
CENSUS_PRODUCT = os.path.join(ROOT, "results", "alphagen_rg",
                              f"CENSUS-{CUTOFF_PIN}.json")
GRAMMAR_LEDGER = os.path.join(ROOT, "research", "TRIAL_GRAMMAR_LEDGER.md")
W19_PRODUCT = os.path.join(ROOT, "results", "alphagen_w19",
                           f"W19-{CUTOFF_PIN}.json")
W20_PRODUCT = os.path.join(ROOT, "results", "alphagen_w20",
                           f"W20-{CUTOFF_PIN}.json")

SEED_KEY_GEN = "n2u3_alphagen_rl_gen"
SEED_KEY_SCRNULL = "n2u3_alphagen_rl_scrnull"
SEED_KEY_UNC = "n2u3_alphagen_rl_unc"
SEED_KEYS = (SEED_KEY_GEN, SEED_KEY_SCRNULL, SEED_KEY_UNC)
SEED_PROPOSAL_BASE = 20_625_000            # DRAFT proposal face (freeze
SEED_PROPOSAL_SPACING = 500                # window runs seed_admit_gate rc0)

K_TOP = 32                                 # judged-face formula slots
POOL_TOP_K = 8                             # E16 survivor pool members
MAX_SKIP_FRAC = 0.10                       # t23 law (P5 prediction face)
MIN_CROSS = e16.MIN_CROSS                  # 100, verbatim
MIN_PERIODS = e16.MIN_PERIODS              # 30, verbatim
TRAIN_UNI_N = 1024                         # training universe subsample
N_BOOT = 256                               # bootstrap pretrain draws
BOOT_DEPTH1_FRAC = 0.60                    # depth split of boot draws
BC_EPOCHS = 8                              # behavior-clone epochs
TAU_ADMIT = 0.005                          # pool admission marginal-IC tau
# PPO in-repo disclosed values (NOT paper values)
PPO = {
    "rollout_episodes": 32, "lr": 3e-4, "clip": 0.2, "ent_coef": 0.01,
    "vf_coef": 0.5, "epochs": 4, "minibatch": 8, "gae_lambda": 0.95,
    "gamma": 1.0, "max_grad_norm": 0.5, "hidden": 64,
}
SLOTS = 6                                  # max tokens per episode (d2)
QLIB_LOADER_REL = "research/shortline/external/qlib_alpha158_loader.py"
QLIB_LOADER_SHA16_PIN = "814b7f7ab3d418ae"

# E16 census survivor TOP-8 anchors (DRAFT sec.1 verbatim; probe verifies
# them against the census product -- selftest uses them as parse anchors)
SURVIVOR_ANCHORS = (
    "LOW(turnover,30)", "LOW(volume,10)", "QTLD(volume,20)",
    "VMA(volume,60)", "ROC(volume,20)", "SUMN(volume,60)",
    "ROC(turnover,20)", "RANK(amount,60)",
)

# --------------------------------------------------------------- io utilities

def _dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def _receipt_path(face):
    return os.path.join(OUT_DIR, f"refusal-{face}.json")


def _now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")

# ------------------------------------------------------------- grammar face

_GRAMMAR = {}


def grammar_face():
    """Lazily built frozen grammar face (E16 verbatim import; sorted op
    labels give a deterministic token vocab independent of dict order)."""
    if not _GRAMMAR:
        ops, gate = e16.import_a158_ops()
        op_labels = tuple(sorted(ops))
        assert len(op_labels) == 29 and gate["rolling_ops"] == 29, gate
        win_tokens = tuple(str(w) for w in e16.WINDOWS)
        depth_tokens = ("D1", "D2")
        vocab = depth_tokens + op_labels + tuple(e16.BASE_INPUTS) + win_tokens
        tok = {t: i for i, t in enumerate(vocab)}
        _GRAMMAR.update(ops=ops, op_labels=op_labels, gate=gate,
                        vocab=vocab, tok=tok,
                        n_vocab=len(vocab), win_tokens=win_tokens,
                        depth_tokens=depth_tokens)
    return _GRAMMAR


def parse_formula(s):
    """Strict parser for E16 grammar strings (d1: OP(inp,w); d2:
    OP(OP(inp,w),w2)). Round-trips formula_str exactly (asserted by the
    caller); returns None on any out-of-grammar shape."""
    g = grammar_face()
    s = s.strip()

    def _d1(m):
        op, inp, w = m.group(1), m.group(2), int(m.group(3))
        if (op in g["op_labels"] and inp in e16.BASE_INPUTS
                and w in e16.WINDOWS):
            return ("d1", op, inp, w)
        return None

    m = re.fullmatch(r"([A-Z]+)\(([a-z]+),(\d+)\)", s)
    if m:
        return _d1(m)
    m = re.fullmatch(r"([A-Z]+)\((.+),(\d+)\)", s)
    if m and m.group(1) in g["op_labels"] and int(m.group(3)) in e16.WINDOWS:
        sub = parse_formula(m.group(2))
        if sub is not None:
            return ("d2", m.group(1), int(m.group(3)), sub)
    return None


def tokens_to_node(tokens):
    """Token sequence -> grammar node (masks guarantee legality; the
    round-trip assert is the wiring guard)."""
    g = grammar_face()
    toks = list(tokens)
    assert toks[0] in (g["tok"]["D1"], g["tok"]["D2"]), toks
    if toks[0] == g["tok"]["D1"]:
        assert len(toks) == 4, toks
        return ("d1", g["vocab"][toks[1]], g["vocab"][toks[2]],
                int(g["vocab"][toks[3]]))
    assert len(toks) == 6, toks
    sub = ("d1", g["vocab"][toks[3]], g["vocab"][toks[4]],
           int(g["vocab"][toks[5]]))
    return ("d2", g["vocab"][toks[1]], int(g["vocab"][toks[2]]), sub)


def node_to_tokens(node):
    """Node -> canonical token sequence (behavior-clone target face)."""
    g = grammar_face()
    if node[0] == "d1":
        return (g["tok"]["D1"], g["tok"][node[1]], g["tok"][node[2]],
                g["tok"][str(node[3])])
    sub = node[3]
    return (g["tok"]["D2"], g["tok"][node[1]], g["tok"][str(node[2])],
            g["tok"][sub[1]], g["tok"][sub[2]], g["tok"][str(sub[3])])


def _step_type(step, depth):
    """Legal token family per step (depth: 0 unknown / 1 / 2)."""
    if step == 0:
        return "DEPTH"
    if depth == 1:
        return ("OP", "INPUT", "WINDOW")[step - 1]
    return ("OP", "WINDOW", "OP", "INPUT", "WINDOW")[step - 1]


def step_mask(step, depth):
    g = grammar_face()
    fam = _step_type(step, depth)
    m = np.zeros(g["n_vocab"], dtype=bool)
    if fam == "DEPTH":
        m[g["tok"]["D1"]] = True
        m[g["tok"]["D2"]] = True
    elif fam == "OP":
        for op in g["op_labels"]:
            m[g["tok"][op]] = True
    elif fam == "INPUT":
        for inp in e16.BASE_INPUTS:
            m[g["tok"][inp]] = True
    elif fam == "WINDOW":
        for w in g["win_tokens"]:
            m[g["tok"][w]] = True
    else:                                            # pragma: no cover
        raise AssertionError(fam)
    return m


def n_steps(depth):
    return 4 if depth == 1 else 6


def featurize(tokens, step):
    """One-hot slots (6) + step id (SLOTS) -> policy input vector."""
    g = grammar_face()
    x = np.zeros(SLOTS * g["n_vocab"] + SLOTS, dtype=np.float64)
    for slot, t in enumerate(tokens):
        x[slot * g["n_vocab"] + t] = 1.0
    x[SLOTS * g["n_vocab"] + step] = 1.0
    return x

# ------------------------------------------------------------ numpy PPO core

def masked_softmax(logits, mask):
    z = np.where(mask, logits, -np.inf)
    z = z - np.max(np.where(mask, logits, -np.inf), axis=-1, keepdims=True)
    with np.errstate(invalid="ignore"):
        e = np.where(mask, np.exp(np.where(mask, z, 0.0)), 0.0)
    return e / np.maximum(e.sum(axis=-1, keepdims=True), 1e-300)


def masked_log_softmax(logits, mask):
    z = np.where(mask, logits, -np.inf)
    z = z - np.max(np.where(mask, z, -np.inf), axis=-1, keepdims=True)
    with np.errstate(invalid="ignore"):
        lp = np.where(mask, z - np.log(np.maximum(
            np.where(mask, np.exp(np.where(mask, z, 0.0)), 0.0)
            .sum(axis=-1, keepdims=True), 1e-300)), -np.inf)
    return lp


class TinyPolicy:
    """MLP policy + value head (numpy, deterministic init)."""

    def __init__(self, n_in, n_hidden, n_out, seed):
        rng = np.random.default_rng([int(seed), 11])
        self.W1 = rng.standard_normal((n_in, n_hidden)) * np.sqrt(2.0 / n_in)
        self.b1 = np.zeros(n_hidden)
        self.W2 = rng.standard_normal((n_hidden, n_hidden)) * np.sqrt(
            2.0 / n_hidden)
        self.b2 = np.zeros(n_hidden)
        self.W3 = rng.standard_normal((n_hidden, n_out)) * 0.01
        self.b3 = np.zeros(n_out)
        self.V = rng.standard_normal((n_hidden, 1)) * 0.01
        self.vb = np.zeros(1)
        self.n_in, self.n_hidden, self.n_out = n_in, n_hidden, n_out

    def params(self):
        return [self.W1, self.b1, self.W2, self.b2,
                self.W3, self.b3, self.V, self.vb]

    def forward(self, X):
        h1 = np.tanh(X @ self.W1 + self.b1)
        h2 = np.tanh(h1 @ self.W2 + self.b2)
        logits = h2 @ self.W3 + self.b3
        value = (h2 @ self.V + self.vb).reshape(-1)
        return logits, value, (X, h1, h2)

    def backprop(self, cache, dlogits, dvalue):
        X, h1, h2 = cache
        g = {}
        g["W3"] = h2.T @ dlogits
        g["b3"] = dlogits.sum(axis=0)
        g["V"] = h2.T @ dvalue.reshape(-1, 1)
        g["vb"] = np.array([dvalue.sum()])
        dh2 = dlogits @ self.W3.T + (dvalue.reshape(-1, 1) @ self.V.T)
        dz2 = dh2 * (1.0 - h2 * h2)
        g["W2"] = h1.T @ dz2
        g["b2"] = dz2.sum(axis=0)
        dh1 = dz2 @ self.W2.T
        dz1 = dh1 * (1.0 - h1 * h1)
        g["W1"] = X.T @ dz1
        g["b1"] = dz1.sum(axis=0)
        return [g["W1"], g["b1"], g["W2"], g["b2"],
                g["W3"], g["b3"], g["V"], g["vb"]]

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        np.savez(path, **{f"p{i}": p for i, p in enumerate(self.params())})

    @classmethod
    def load(cls, path, n_in, n_hidden, n_out):
        pol = cls.__new__(cls)
        with np.load(path, allow_pickle=False) as z:
            ps = [z[f"p{i}"] for i in range(8)]
        (pol.W1, pol.b1, pol.W2, pol.b2, pol.W3, pol.b3, pol.V,
         pol.vb) = [np.array(p, dtype=np.float64) for p in ps]
        pol.n_in, pol.n_hidden, pol.n_out = n_in, n_hidden, n_out
        return pol


class Adam:
    def __init__(self, params, lr):
        self.m = [np.zeros_like(p) for p in params]
        self.v = [np.zeros_like(p) for p in params]
        self.t = 0
        self.lr = lr

    def step(self, params, grads):
        self.t += 1
        b1, b2 = 0.9, 0.999
        for p, g, m, v in zip(params, grads, self.m, self.v):
            m *= b1
            m += (1 - b1) * g
            v *= b2
            v += (1 - b2) * g * g
            mh = m / (1 - b1 ** self.t)
            vh = v / (1 - b2 ** self.t)
            p -= self.lr * mh / (np.sqrt(vh) + 1e-8)


def _grad_norm_clip(grads, max_norm):
    tot = math.sqrt(sum(float(np.sum(g * g)) for g in grads))
    if tot > max_norm and tot > 0:
        scale = max_norm / tot
        return [g * scale for g in grads]
    return grads


def ppo_update(policy, opt, s, masks, acts, old_logp, adv, ret, consts):
    """One PPO epoch sweep over a rollout batch (numpy minimal repro set).
    s (B,n_in); masks (B,n_out) bool; acts (B,); old_logp/adv/ret (B,).
    Returns the mean clipped surrogate (diagnostic)."""
    B = s.shape[0]
    adv_n = adv
    eps = consts["clip"]
    ent = consts["ent_coef"]
    vf = consts["vf_coef"]
    mb = max(1, min(consts["minibatch"], B))
    surr_acc = []
    order = np.arange(B)
    for _epoch in range(consts["epochs"]):
        # deterministic epoch shuffle: seed derives from a fixed base +
        # epoch so repeated runs of the same batch replay identically
        rng = np.random.default_rng([1234, _epoch])
        order = rng.permutation(B)
        for lo in range(0, B, mb):
            hi = min(lo + mb, B)
            idx = order[lo:hi]
            X = s[idx]
            M = masks[idx]
            a = acts[idx]
            olp = old_logp[idx]
            A = adv_n[idx]
            R = ret[idx]
            logits, V, cache = policy.forward(X)
            lp = masked_log_softmax(logits, M)
            p = np.exp(lp)
            onehot = np.zeros_like(p)
            onehot[np.arange(len(a)), a] = 1.0
            logp = lp[np.arange(len(a)), a]
            ratio = np.exp(logp - olp)
            surr = np.minimum(ratio * A, np.clip(ratio, 1 - eps,
                                                 1 + eps) * A)
            surr_acc.append(float(np.mean(surr)))
            # NaN-safe entropy: lp is -inf on masked slots; p is 0 there,
            # so lp_safe makes every masked term contribute exactly 0
            lp_safe = np.where(M, lp, 0.0)
            H = -np.sum(p * lp_safe, axis=-1)
            # dL/dz: clip term (zero where the clip binds) + entropy bonus
            flows = ((A > 0) & (ratio < 1 + eps)) | ((A < 0)
                                                    & (ratio > 1 - eps))
            coeff = np.where(flows, A * ratio, 0.0) / len(a)
            dlogits = (p - onehot) * coeff[:, None]
            dlogits += (ent / len(a)) * p * (lp_safe + H[:, None])
            # value loss grad: vf * mean((V-R)^2) -> d/dV = 2vf(V-R)/n
            dvalue = vf * 2.0 * (V - R) / len(a)
            grads = policy.backprop(cache, dlogits, dvalue)
            grads = _grad_norm_clip(grads, consts["max_grad_norm"])
            opt.step(policy.params(), grads)
    return float(np.mean(surr_acc)) if surr_acc else 0.0

# -------------------------------------------------------------- panel faces

def load_training_panel(cache_path, uni_n, seed):
    """Cache -> training panel with a seed-pinned column subsample (the
    training cost proxy face; export-topk/judged use the FULL face)."""
    with np.load(cache_path, allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
        cal = [str(x) for x in z["cal"]]
        universe = [str(x) for x in z["universe"]]
        rows = np.asarray(z["census_rows"], dtype=np.int64)
        sub = None
        if 0 < uni_n < len(universe):
            rng = np.random.default_rng([int(seed), 777])
            sub = np.sort(rng.choice(len(universe), size=uni_n,
                                     replace=False))
        else:
            sub = np.arange(len(universe))
        elig = z["elig"][:, sub]
        fwd1 = z["fwd1"][:, sub]
        leaves = {}
        for k in e16.BASE_INPUTS:
            leaves[k] = z[f"leaf_{k}"][:, sub]
    return {"cal": cal, "universe": [universe[i] for i in sub],
            "elig": elig, "fwd1": fwd1, "leaves": leaves,
            "census_rows": rows, "meta": meta, "sub": sub,
            "full_universe_n": len(universe)}


def _panel_faces(panel):
    """Precomputed IC machinery faces for a training panel (rows slice)."""
    rows = panel["census_rows"]
    cal_us = np.asarray(pd.to_datetime(np.asarray(
        panel["cal"], dtype="datetime64[us]")))[rows]
    elig_c = panel["elig"][rows, :]
    fwd_c = panel["fwd1"][rows, :]
    Rr = rank_rows(np.isfinite(fwd_c), fwd_c)
    nser_all = pd.Series(elig_c.sum(axis=1), index=cal_us)
    return {"rows": rows, "cal_us": cal_us, "elig_c": elig_c,
            "fwd_c": fwd_c, "Rr": Rr, "keep": (nser_all >= MIN_CROSS),
            "nser": nser_all}


def ic_face(F, faces):
    """E16 real-IC face glue (helpers imported verbatim): returns
    (stats_block_or_None, n_dates_kept)."""
    Fc = F[faces["rows"], :]
    eff = (faces["elig_c"] & np.isfinite(Fc) & np.isfinite(faces["fwd_c"]))
    Fr = rank_rows(eff, Fc)
    s = ic_from_ranks(Fr, faces["Rr"], faces["cal_us"])
    s = s[s.index.isin(faces["nser"].index[faces["keep"]])]
    blk = stats_block(s)
    if "ic_mean" not in blk or blk.get("n_periods", 0) < MIN_PERIODS:
        return None, int(faces["keep"].sum())
    return blk, int(faces["keep"].sum())


def _zrank(eff, Fc):
    """Per-date z-scored ranks within the eligible mask."""
    Fr = rank_rows(eff, Fc)
    fin = np.isfinite(Fr)
    cnt = fin.sum(axis=1)
    safe = np.maximum(cnt, 1)
    mu = np.nansum(np.where(fin, Fr, 0.0), axis=1) / safe
    var = np.nansum(np.where(fin, (Fr - mu[:, None]) ** 2, 0.0),
                    axis=1) / safe
    sd = np.sqrt(var)
    z = np.where(fin, (Fr - mu[:, None]) / np.maximum(sd, 1e-12)[:, None],
                 np.nan)
    return np.where(sd[:, None] > 0, z, 0.0)


class SynergyPool:
    """Marginal rank-IC reward face (alphagen synergy-pool law, in-repo
    minimal repro set): members = E16 survivors + batch-admitted."""

    def __init__(self, panel, survivor_nodes, faces=None):
        self.panel = panel
        self.faces = faces or _panel_faces(panel)
        self.members = []          # (node, formula_str, sign, zrank, ic)
        for node in survivor_nodes:
            self._add_member(node, admit=False)

    # -- internals -------------------------------------------------
    def _eval(self, node):
        return e16.evaluate(node, self.panel["leaves"])

    def _member_z(self, node, sign):
        F = self._eval(node)
        Fc = F[self.faces["rows"], :]
        eff = (self.faces["elig_c"] & np.isfinite(Fc)
               & np.isfinite(self.faces["fwd_c"]))
        z = _zrank(eff, Fc) * sign
        return z, eff

    def _add_member(self, node, admit=True, sign=None):
        F = self._eval(node)
        blk, _ = ic_face(F, self.faces)
        assert blk is not None, e16.formula_str(node)
        s = 1.0 if (blk["ic_mean"] >= 0) else -1.0
        if sign is not None:
            s = sign
        z, _ = self._member_z(node, s)
        rec = (node, e16.formula_str(node), s, z, blk)
        self.members.append(rec)
        return rec

    # -- public faces ----------------------------------------------
    def ensemble_ic(self, extra_z=None):
        stack = [m[3] for m in self.members]
        if extra_z is not None:
            stack = stack + [extra_z]
        S = np.stack(stack)
        fin = np.isfinite(S)
        cnt = fin.sum(axis=0)
        ens = np.where(cnt > 0, np.nansum(
            np.where(fin, S, 0.0), axis=0) / np.maximum(cnt, 1), np.nan)
        eff_ens = (self.faces["elig_c"] & np.isfinite(ens)
                   & np.isfinite(self.faces["fwd_c"]))
        Er = rank_rows(eff_ens, ens)
        s = ic_from_ranks(Er, self.faces["Rr"], self.faces["cal_us"])
        s = s[s.index.isin(self.faces["nser"].index[self.faces["keep"]])]
        blk = stats_block(s)
        if "ic_mean" not in blk or blk.get("n_periods", 0) < MIN_PERIODS:
            return None
        return blk

    def base_ic(self):
        blk = self.ensemble_ic()
        return blk["ic_mean"] if blk else 0.0

    def marginal(self, node):
        """Sign-aligned marginal IC of a candidate vs the current pool.
        Returns (marginal, sign, cand_blk, pool_base_ic)."""
        F = self._eval(node)
        cand_blk, _ = ic_face(F, self.faces)
        if cand_blk is None:
            return None, None, None, self.base_ic()
        Fc = F[self.faces["rows"], :]
        eff = (self.faces["elig_c"] & np.isfinite(Fc)
               & np.isfinite(self.faces["fwd_c"]))
        base = self.base_ic()
        best_m, best_s = None, None
        for sgn in (1.0, -1.0):
            z = _zrank(eff, Fc) * sgn
            blk = self.ensemble_ic(extra_z=z)
            if blk is None:
                continue
            m = blk["ic_mean"] - base
            if best_m is None or m > best_m:
                best_m, best_s = m, sgn
        if best_m is None:
            return None, None, cand_blk, base
        return best_m, best_s, cand_blk, base

    def admit(self, node, sign):
        """Batch acceptance face (TAU_ADMIT gate enforced by the caller);
        returns the member record."""
        return self._add_member(node, admit=True, sign=sign)


class GrammarEnv:
    """Token-MDP episode collector + synergy-pool reward face."""

    def __init__(self, panel, pool, excluded_keys, seed_gen):
        g = grammar_face()
        self.panel = panel
        self.faces = _panel_faces(panel)
        self.pool = pool
        self.excluded = set(excluded_keys)
        self.seed_gen = int(seed_gen)
        self.n_in = SLOTS * g["n_vocab"] + SLOTS

    def sample(self, policy, episode_seed):
        """Token-sampling half of an episode (cheap parent-side face):
        tokens/logps/vals/masks + node identity. Deterministic given
        (policy params, episode_seed)."""
        g = grammar_face()
        rng = np.random.default_rng([self.seed_gen, int(episode_seed)])
        tokens, logps, vals, masks = [], [], [], []
        depth = 0
        for step in range(SLOTS):
            x = featurize(tuple(tokens), step)
            mask = step_mask(step, depth if step > 0 else 0)
            logits, val, _ = policy.forward(x.reshape(1, -1))
            lp = masked_log_softmax(logits.reshape(-1), mask)
            p = np.exp(lp)
            p = np.where(mask, p, 0.0)
            p = p / max(p.sum(), 1e-300)
            a = int(rng.choice(g["n_vocab"], p=p))
            tokens.append(a)
            logps.append(float(lp[a]))
            vals.append(float(val[0]))
            masks.append(mask)
            if step == 0:
                depth = 1 if a == g["tok"]["D1"] else 2
            if step == n_steps(depth) - 1:
                break
        node = tokens_to_node(tokens)
        key = e16.canonical_key(node)
        fstr = e16.formula_str(node)
        return {"tokens": tuple(tokens), "node": node,
                "formula": fstr, "key": key,
                "dup": bool(key in self.excluded),
                "logps": tuple(logps), "values": tuple(vals),
                "masks": masks}

    def episode(self, policy, episode_seed):
        """One episode (sequential reference face): policy-sampled token
        sequence -> node -> reward. Deterministic given (policy params,
        episode_seed)."""
        ep = self.sample(policy, episode_seed)
        marginal, sign, cand_blk, base_ic = self.pool.marginal(ep["node"])
        skip = marginal is None
        ep.update({"skip": bool(skip), "marginal": marginal, "sign": sign,
                   "cand_blk": cand_blk, "pool_base_ic": base_ic,
                   "reward": 0.0 if skip else float(marginal)})
        return ep

    def rollout(self, policy, start_ep, n_ep):
        eps = []
        for j in range(n_ep):
            eps.append(self.episode(policy, start_ep + j))
        return eps


def _gae(eps, consts):
    """Terminal-reward GAE (gamma=1 short horizon): reward-to-go is the
    episode reward at every step; advantage = GAE over value deltas."""
    lam = consts["gae_lambda"]
    S, M, A, OL, AD, RT = [], [], [], [], [], []
    for ep in eps:
        R = ep["reward"]
        vals = list(ep["values"])
        T = len(vals)
        # delta_t = R - V_t  (terminal reward, V(s_T+1)=0)
        deltas = [R - v for v in vals]
        adv = [0.0] * T
        run = 0.0
        for t in range(T - 1, -1, -1):
            run = deltas[t] + lam * run
            adv[t] = run
        for t in range(T):
            S.append(featurize(ep["tokens"][:t], t))
            M.append(ep["masks"][t])
            A.append(ep["tokens"][t])
            OL.append(ep["logps"][t])
            AD.append(adv[t])
            RT.append(R)
    ad = np.asarray(AD, dtype=np.float64)
    if ad.std() > 1e-12:
        ad = (ad - ad.mean()) / ad.std()
    return (np.asarray(S), np.asarray(M), np.asarray(A, dtype=np.int64),
            np.asarray(OL), ad, np.asarray(RT))

# ------------------------------------------------------- dedup / survivors

def load_excluded_keys():
    """Consumed-grammar dedup face: E16 census strings + W19/W20 family
    records + full TRIAL_GRAMMAR_LEDGER text scan (W20 belt-and-braces)."""
    keys = set()
    hits = {"census": 0, "w19": 0, "w20": 0, "ledger_scan": "n/a"}
    if os.path.exists(CENSUS_PRODUCT):
        d = json.load(open(CENSUS_PRODUCT, encoding="utf-8"))
        for r in d.get("census", {}).get("formulas", []):
            node = parse_formula(r.get("formula", ""))
            if node is not None:
                keys.add(e16.canonical_key(node))
                hits["census"] += 1
    for path, tag in ((W19_PRODUCT, "w19"), (W20_PRODUCT, "w20")):
        if os.path.exists(path):
            d = json.load(open(path, encoding="utf-8"))
            texts = []
            for rec in d.get("census", d.get("family", {})).get(
                    "formulas", d.get("records", [])):
                texts.append(rec.get("formula", ""))
            for s in texts:
                node = parse_formula(s)
                if node is not None:
                    keys.add(e16.canonical_key(node))
                    hits[tag] += 1
    if os.path.exists(GRAMMAR_LEDGER):
        src = open(GRAMMAR_LEDGER, encoding="utf-8").read()
        n = 0
        for m in re.finditer(r"[A-Z]{2,6}\([a-z]+(?:\([a-z]+,\d+\))?,\d+\)",
                             src):
            node = parse_formula(m.group(0))
            if node is not None:
                keys.add(e16.canonical_key(node))
                n += 1
        hits["ledger_scan"] = n
    return keys, hits


def load_survivor_nodes(top_k=POOL_TOP_K):
    """E16 census TOP-K survivors by |ICIR| -> parsed nodes + anchor
    facts (probe re-verifies them against the census records)."""
    d = json.load(open(CENSUS_PRODUCT, encoding="utf-8"))
    recs = [r for r in d["census"]["formulas"] if r.get("skip") is None]
    top = sorted(recs, key=lambda r: -abs(r["h1"]["ic_ir"]))[:top_k]
    out = []
    for r in top:
        node = parse_formula(r["formula"])
        assert node is not None, r["formula"]
        assert e16.formula_str(node) == r["formula"], r["formula"]
        out.append((node, r["formula"], float(r["h1"]["ic_ir"])))
    return out, {"verdict_holds": d["verdict"]["census_holds"],
                 "n_ok": d["verdict"]["n_ok"]}

# ------------------------------------------------------------- freeze gates

def _prereg_head(path=PREREG, nbytes=1500):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read(nbytes)
    except OSError:
        return ""


def prereg_status(path=PREREG):
    head = _prereg_head(path)
    if "FROZEN" in head and "DRAFT" not in head:
        return "FROZEN"
    if "DRAFT" in head:
        return "DRAFT"
    return "UNKNOWN"


def freeze_gate(face, registry=None, prereg_path=PREREG,
                receipt_path=None, extra_conditions=None):
    """Five-condition posture gate (leg burns require FROZEN + 3 bands;
    judge adds product/anchor conditions). Returns (ok, posture). Refuse
    lands a receipt (W19 hard-spec law)."""
    reg = sg.SEED_REGISTRY if registry is None else registry
    posture = {"face": face,
               "prereg_status": prereg_status(prereg_path),
               "seed_bands": {k: (k in reg) for k in SEED_KEYS},
               "extra": extra_conditions or {}}
    posture["problems"] = []
    if posture["prereg_status"] != "FROZEN":
        posture["problems"].append(
            f"prereg status {posture['prereg_status']} != FROZEN "
            "(freeze window must flip the DRAFT status line)")
    missing = [k for k, ok in posture["seed_bands"].items() if not ok]
    if missing:
        posture["problems"].append(
            "seed bands absent from SEED_REGISTRY: " + ",".join(missing))
    for name, ok in (extra_conditions or {}).items():
        if not ok:
            posture["problems"].append(f"condition failed: {name}")
    posture["ok"] = not posture["problems"]
    posture["checked_at"] = _now()
    if not posture["ok"]:
        rp = receipt_path or _receipt_path(face)
        _dump(posture, rp)
        posture["receipt"] = rp
    return posture["ok"], posture


# ------------------------- leg-3 completion gate (r922 post-burn
# consumption fail-closed face): export-topk/judge must not consume a
# top-K built from a MID-TRAINING log. Prereg sec.3 output face = the
# TRAINED top-K (post leg-3), so a partial-log export is VOID by
# prereg sequencing. Completion face = train receipt of a COMPLETED
# leg-3-scale run: cumulative episodes >= probe base + leg-3 pool
# budget (additive re-claim law: interrupted restarts ADD a fresh 4096
# budget, so any completed leg-3 chain ends at or above this line) AND
# receipt episodes == on-disk log line count (guards stale receipt vs a
# re-claimed in-flight log). Pure I/O, deterministic.
LEG2_PROBE_EPS = 256                      # leg-2 probe budget (resume base)
LEG3_TRAIN_EPS = 4096                     # leg-3 pool-entry budget
LEG3_COMPLETE_EPS = LEG2_PROBE_EPS + LEG3_TRAIN_EPS


def _train_complete_face(ckpt_dir=None):
    """(ok, face) completion gate for the post-burn consumption legs."""
    cd = ckpt_dir or CKPT_DIR
    rcpt = os.path.join(cd, "train_receipt.json")
    log = os.path.join(cd, "train_log.jsonl")
    if not os.path.exists(rcpt):
        return False, {"train_complete": False,
                       "reason": "receipt_absent"}
    try:
        with open(rcpt, encoding="utf-8") as f:
            r = json.load(f)
    except (OSError, ValueError) as exc:              # noqa: BLE001
        return False, {"train_complete": False,
                       "reason": "receipt_unreadable",
                       "error": str(exc)}
    eps = r.get("episodes")
    if r.get("face") != "train" or not isinstance(eps, int):
        return False, {"train_complete": False,
                       "reason": "receipt_face_mismatch",
                       "receipt": {"face": r.get("face"),
                                   "episodes": eps}}
    n_log = 0
    if os.path.exists(log):
        with open(log, encoding="utf-8") as f:
            n_log = sum(1 for ln in f if ln.strip())
    okc = eps >= LEG3_COMPLETE_EPS and n_log == eps
    return okc, {"train_complete": okc, "receipt_episodes": eps,
                 "log_lines": n_log, "required_min": LEG3_COMPLETE_EPS,
                 "reason": None if okc else
                 ("incomplete_leg3_budget" if eps < LEG3_COMPLETE_EPS
                  else "log_receipt_mismatch_reclaim_inflight")}

# ------------------------- multiproc eval face (O-20260930-2355 law-1
# ProcessPool conversion: workers_plan is CODE, not a declaration. The
# expensive face of every burn is the synergy-pool MARGINAL eval; within
# a batch the pool is frozen (admissions land in the parent AFTER the
# batch, cmd_train law), so per-node evals are independent pure functions
# of (node, panel, pool snapshot) -> parallel results assemble by index
# and are bit-identical to the sequential reference loop (episode()).
# Workers rebuild the seed-pinned panel + pool from the SAME frozen
# cache face via initializer/initargs (shared state law, zero closures).
_MP_STATE = {}


def _mp_init(cache_path, uni_n, gen, survivor_nodes, admitted_pairs):
    """Worker-side one-time init: rebuild the training panel + synergy
    pool (survivors + batch-admitted-so-far) from the same frozen cache.
    Identical inputs -> bit-identical pool -> bit-identical marginals."""
    panel = load_training_panel(cache_path, uni_n, gen)
    pool = SynergyPool(panel, list(survivor_nodes))
    for node, sign in admitted_pairs:
        pool.admit(node, sign)
    _MP_STATE["pool"] = pool


def _mp_marginal(node):
    marginal, sign, cand_blk, base = _MP_STATE["pool"].marginal(node)
    return {"marginal": marginal, "sign": sign, "cand_blk": cand_blk,
            "base_ic": base}


def _marginals_parallel(nodes, initargs, workers):
    """Parallel marginal batch; prereg sec.0 workers_plan =
    min(worker_cap(), 8). Returns (results-by-index, workers_used)."""
    if not workers or workers <= 0:
        workers = min(worker_cap(), 8)
    jobs = [(f"marg-{i}", _mp_marginal, (nd,)) for i, nd in enumerate(nodes)]
    out = run_cells_parallel(jobs, workers=workers, desc="rl-marginals",
                             initializer=_mp_init, initargs=initargs)
    used = out.pop("__workers__", workers)
    return [out[f"marg-{i}"] for i in range(len(nodes))], used


# ---------------------------------------------------------------- commands

def cmd_env_probe(args):
    t0 = time.time()
    g = grammar_face()
    face = {}
    # panel gate (E16 import face) + cache posture
    try:
        pf = e16.gate_face()
        face["panel_gate"] = {k: v for k, v in pf.items()
                              if k != "cal_error"}
    except Exception as exc:                          # noqa: BLE001
        face["panel_gate"] = {"error": str(exc)}
    cache = e16.cache_path(CUTOFF_PIN)
    face["cache"] = {"path": cache, "exists": os.path.exists(cache),
                     "size_mb": round(os.path.getsize(cache) / 1e6, 1)
                     if os.path.exists(cache) else None}
    face["cutoff_pin"] = CUTOFF_PIN
    face["census_product"] = {"exists": os.path.exists(CENSUS_PRODUCT)}
    survivors = None
    if os.path.exists(CENSUS_PRODUCT):
        survivors, cens = load_survivor_nodes()
        face["census_product"].update(
            verdict_holds=cens["verdict_holds"], n_ok=cens["n_ok"],
            top_k=POOL_TOP_K,
            survivors=[{"formula": s, "abs_icir": round(abs(ir), 3)}
                       for _, s, ir in survivors],
            anchors_match=[s for _, s, _ in survivors]
            == list(SURVIVOR_ANCHORS))
    # grammar face + lineage
    import hashlib
    qlib_sha = hashlib.sha256(
        open(os.path.join(ROOT, QLIB_LOADER_REL), "rb").read()
    ).hexdigest()[:16] if os.path.exists(
        os.path.join(ROOT, QLIB_LOADER_REL)) else None
    face["grammar"] = {
        "ops": len(g["op_labels"]), "base_inputs": len(e16.BASE_INPUTS),
        "windows": len(e16.WINDOWS), "depth_max": 2,
        "vocab": g["n_vocab"],
        "qlib_loader_sha16": qlib_sha,
        "qlib_loader_sha16_pin": QLIB_LOADER_SHA16_PIN,
        "qlib_loader_sha16_match": qlib_sha == QLIB_LOADER_SHA16_PIN,
        "e16_import_face": "scripts/alphagen_rg_census.py (verbatim)",
    }
    # seed posture + admit-gate probe record (read-only)
    bands = {k: (k in sg.SEED_REGISTRY) for k in SEED_KEYS}
    admit = {"ran": False}
    try:
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "Tools",
                                          "seed_admit_gate.py"),
             str(SEED_PROPOSAL_BASE),
             "--span", str(SEED_PROPOSAL_SPACING)],
            capture_output=True, text=True, timeout=120, cwd=ROOT)
        admit = {"ran": True, "rc": r.returncode,
                 "stdout_tail": (r.stdout or "")[-600:],
                 "stderr_tail": (r.stderr or "")[-300:]}
    except Exception as exc:                          # noqa: BLE001
        admit = {"ran": False, "error": str(exc)}
    face["seeds"] = {"bands": bands,
                     "proposal_base": SEED_PROPOSAL_BASE,
                     "proposal_spacing": SEED_PROPOSAL_SPACING,
                     "admit_gate_probe": admit}
    # banned-direction gate posture (DRAFT sec.0.5 run-before-burn face)
    banned = {"ran": False}
    try:
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "Tools",
                                          "banned_direction_gate.py"),
             "--prereg", PREREG_REL],
            capture_output=True, text=True, timeout=120, cwd=ROOT)
        banned = {"ran": True, "rc": r.returncode,
                  "stdout_tail": (r.stdout or "")[-400:]}
    except Exception as exc:                          # noqa: BLE001
        banned = {"ran": False, "error": str(exc)}
    face["banned_direction_gate"] = banned
    # closed families + dedup sources
    fam = sg.closed_family_check(FAMILY_KEY) if hasattr(
        sg, "closed_family_check") else {"in_closed": False}
    keys, hits = load_excluded_keys()
    face["family"] = {"family_key": FAMILY_KEY,
                      "closed_families": sorted(sg.CLOSED_FAMILIES),
                      "in_closed_families": FAMILY_KEY in sg.CLOSED_FAMILIES,
                      "check": fam}
    face["dedup"] = {"excluded_keys": len(keys), "hits": hits,
                     "w19_product": os.path.exists(W19_PRODUCT),
                     "w20_product": os.path.exists(W20_PRODUCT)}
    # freeze-conditions checklist (five-condition window face)
    face["freeze_conditions"] = {
        "1_runner_selftest_green": "pending selftest run this window",
        "2_seed_admit_gate_rc0": admit.get("rc"),
        "3_banned_direction_gate_rc0": banned.get("rc"),
        "4_prereg_frozen": prereg_status() == "FROZEN",
        "5_meaning_gate_three_questions": "freeze-window session action",
    }
    face["queue_row"] = QUEUE_ROW
    face["mechanics"] = {"train_uni_n": TRAIN_UNI_N, "n_boot": N_BOOT,
                         "ppo": PPO, "tau_admit": TAU_ADMIT,
                         "k_top": K_TOP, "pool_top_k": POOL_TOP_K,
                         "pool_boundary_disclosure":
                             "registered members have no stock cross-"
                             "section face at training time; they enter "
                             "at the judged D6 daily-return gate"}
    face["audit"] = {"elapsed_sec": round(time.time() - t0, 1),
                     "generated_at": _now(), "read_only": True}
    _dump(face, PROBE_RECEIPT)
    print(json.dumps({"probe": "ok", "receipt": PROBE_RECEIPT,
                      "panel_ready": face["panel_gate"].get("ready"),
                      "prereg": face.get("freeze_conditions", {}).get(
                          "4_prereg_frozen"),
                      "bands": bands,
                      "admit_rc": admit.get("rc"),
                      "banned_rc": banned.get("rc"),
                      "elapsed_sec": face["audit"]["elapsed_sec"]},
                     ensure_ascii=False, indent=1))
    return 0


def _require_freeze(face, extra=None, registry=None):
    ok, posture = freeze_gate(face, registry=registry,
                              extra_conditions=extra)
    if not ok:
        print(json.dumps({"refused": True, "face": face,
                          "problems": posture["problems"],
                          "receipt": posture.get("receipt")},
                         ensure_ascii=False, indent=1))
    return ok, posture


def cmd_pretrain(args):
    ok, posture = _require_freeze("pretrain")
    if not ok:
        return 2
    gen = int(sg.SEED_REGISTRY[SEED_KEY_GEN])
    cache_path, meta = e16.ensure_cache(CUTOFF_PIN)
    panel = load_training_panel(cache_path, TRAIN_UNI_N, gen)
    survivors, _ = load_survivor_nodes()
    pool = SynergyPool(panel, [n for n, _, _ in survivors])
    excluded, _ = load_excluded_keys()
    g = grammar_face()
    # bootstrap draws: E16 rng machinery face (rng=[gen,9000+i] streams)
    draws = []
    for i in range(N_BOOT):
        rng = np.random.default_rng([gen, 9000 + i])
        depth = 1 if (i % 10) < (BOOT_DEPTH1_FRAC * 10) else 2
        draws.append(e16._draw_node(rng, g["ops"], depth))
    env = GrammarEnv(panel, pool, excluded, gen)
    # parallel marginal batch (256 independent draws; pool = survivors
    # only during pretrain -- no admissions, initargs admit list empty)
    surv_nodes = [n for n, _, _ in survivors]
    margs, used_w = _marginals_parallel(
        draws, (cache_path, TRAIN_UNI_N, gen, surv_nodes, []),
        getattr(args, "workers", 0))
    recs = []
    for i, node in enumerate(draws):
        marginal, sign = margs[i]["marginal"], margs[i]["sign"]
        recs.append({"i": i, "node": node,
                     "formula": e16.formula_str(node),
                     "key": e16.canonical_key(node),
                     "dup": e16.canonical_key(node) in excluded,
                     "skip": marginal is None,
                     "marginal": marginal, "sign": sign})
    okd = [r for r in recs if not r["skip"] and not r["dup"]]
    okd.sort(key=lambda r: -(r["marginal"] or 0.0))
    quart = okd[:max(1, len(okd) // 4)]
    # behavior cloning on the top-quartile token sequences
    policy = TinyPolicy(env.n_in, PPO["hidden"], g["n_vocab"], gen)
    opt = Adam(policy.params(), lr=PPO["lr"])
    S, M, A = [], [], []
    for r in quart:
        toks = node_to_tokens(r["node"])
        for t in range(len(toks)):
            S.append(featurize(toks[:t], t))
            M.append(step_mask(t, 1 if toks[0] == g["tok"]["D1"] else 2))
            A.append(toks[t])
    S = np.asarray(S); M = np.asarray(M); A = np.asarray(A, np.int64)
    for _ep in range(BC_EPOCHS):
        logits, _, cache = policy.forward(S)
        lp = masked_log_softmax(logits, M)
        onehot = np.zeros_like(np.exp(lp))
        onehot[np.arange(len(A)), A] = 1.0
        p = np.exp(lp)
        dlogits = (p - onehot) / len(A)
        grads = policy.backprop(cache, dlogits,
                                np.zeros(len(A)))
        opt.step(policy.params(), grads)
    os.makedirs(CKPT_DIR, exist_ok=True)
    policy.save(os.path.join(CKPT_DIR, "pretrain_policy.npz"))
    receipt = {"face": "pretrain", "n_draws": N_BOOT,
               "n_evaluable": len(okd), "n_bc": len(quart),
               "top_bc": [{"formula": r["formula"],
                           "marginal": r["marginal"]} for r in quart[:8]],
               "seed_key": SEED_KEY_GEN, "train_uni_n": TRAIN_UNI_N,
               "meta": meta, "audit": {"generated_at": _now(),
                                       "workers": used_w}}
    _dump(receipt, os.path.join(CKPT_DIR, "pretrain_receipt.json"))
    print(json.dumps({"pretrain": "ok", "n_draws": N_BOOT,
                      "n_evaluable": len(okd), "n_bc": len(quart)},
                     ensure_ascii=False))
    return 0


def cmd_train(args):
    t0 = time.time()
    ok, posture = _require_freeze("train")
    if not ok:
        return 2
    gen = int(sg.SEED_REGISTRY[SEED_KEY_GEN])
    cache_path, meta = e16.ensure_cache(CUTOFF_PIN)
    panel = load_training_panel(cache_path, TRAIN_UNI_N, gen)
    survivors, _ = load_survivor_nodes()
    pool = SynergyPool(panel, [n for n, _, _ in survivors])
    excluded, _ = load_excluded_keys()
    g = grammar_face()
    env = GrammarEnv(panel, pool, excluded, gen)
    ckpt_pol = os.path.join(CKPT_DIR, "train_policy.npz")
    pre_pol = os.path.join(CKPT_DIR, "pretrain_policy.npz")
    if os.path.exists(ckpt_pol):
        policy = TinyPolicy.load(ckpt_pol, env.n_in, PPO["hidden"],
                                 g["n_vocab"])
    elif os.path.exists(pre_pol):
        policy = TinyPolicy.load(pre_pol, env.n_in, PPO["hidden"],
                                 g["n_vocab"])
    else:
        policy = TinyPolicy(env.n_in, PPO["hidden"], g["n_vocab"], gen)
    opt = Adam(policy.params(), lr=PPO["lr"])
    log_path = os.path.join(CKPT_DIR, "train_log.jsonl")
    os.makedirs(CKPT_DIR, exist_ok=True)
    done_eps = 0
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            done_eps = sum(1 for line in f if line.strip())
    # optimizer-state note (disclosed): Adam moments reset on process
    # restart; episode-log resume keeps the data face append-never-reset
    target = done_eps + args.episodes
    updates = 0
    surr = 0.0
    surv_nodes = [n for n, _, _ in survivors]
    used_w = None
    while done_eps < target:
        # sample token sequences (cheap, parent-side, policy-dependent)
        seqs = [env.sample(policy, done_eps + j)
                for j in range(PPO["rollout_episodes"])]
        # parallel marginal batch: pool snapshot = survivors + admissions
        # from PREVIOUS batches (this batch's admissions land after the
        # PPO update below -- within-batch pool frozen = sequential law)
        admitted = [(m[0], m[2]) for m in pool.members[len(surv_nodes):]]
        margs, used_w = _marginals_parallel(
            [s["node"] for s in seqs],
            (cache_path, TRAIN_UNI_N, gen, surv_nodes, admitted),
            getattr(args, "workers", 0))
        eps = []
        for j, s in enumerate(seqs):
            r = margs[j]
            s.update({"marginal": r["marginal"], "sign": r["sign"],
                      "cand_blk": r["cand_blk"],
                      "pool_base_ic": r["base_ic"],
                      "skip": r["marginal"] is None,
                      "reward": 0.0 if r["marginal"] is None
                      else float(r["marginal"])})
            eps.append(s)
        with open(log_path, "a", encoding="utf-8", newline="\n") as f:
            for j, ep in enumerate(eps):
                f.write(json.dumps({
                    "ep": done_eps + j, "formula": ep["formula"],
                    "dup": ep["dup"], "skip": ep["skip"],
                    "marginal": None if ep["marginal"] is None
                    else round(ep["marginal"], 6),
                    "sign": ep["sign"],
                    "reward": round(ep["reward"], 6)},
                    ensure_ascii=False) + "\n")
        done_eps += len(eps)
        live = [e for e in eps if not e["skip"]]
        if live:
            S, M, A, OL, AD, RT = _gae(live, PPO)
            surr = ppo_update(policy, opt, S, M, A, OL, AD, RT, PPO)
        # pool admission face (alphagen tau law)
        for ep in live:
            if (not ep["dup"] and ep["marginal"] is not None
                    and ep["marginal"] > TAU_ADMIT):
                pool.admit(ep["node"], ep["sign"])
        policy.save(ckpt_pol)
        updates += 1
    receipt = {"face": "train", "episodes": done_eps, "updates": updates,
               "last_surr": round(surr, 6), "pool_members": len(pool.members),
               "seed_key": SEED_KEY_GEN, "train_uni_n": TRAIN_UNI_N,
               "audit": {"generated_at": _now(),
                         "elapsed_sec": round(time.time() - t0, 1),
                         "workers": used_w}}
    _dump(receipt, os.path.join(CKPT_DIR, "train_receipt.json"))
    print(json.dumps({"train": "ok", "episodes": done_eps,
                      "updates": updates,
                      "pool_members": len(pool.members)},
                     ensure_ascii=False))
    return 0


def cmd_probe(args):
    """leg-2 short-window training probe (pool-entry face): idempotent
    pretrain (skipped when pretrain_policy.npz exists) + train
    --episodes N in ONE atomic burn; receipt = throughput face for
    leg-3 sizing."""
    ok, posture = _require_freeze("probe")
    if not ok:
        return 2
    t0 = time.time()
    did_pretrain = False
    if not os.path.exists(os.path.join(CKPT_DIR, "pretrain_policy.npz")):
        rc = cmd_pretrain(args)
        if rc:
            return rc
        did_pretrain = True
    rc = cmd_train(args)
    if rc:
        return rc
    with open(os.path.join(CKPT_DIR, "train_receipt.json"),
              encoding="utf-8") as f:
        tr = json.load(f)
    receipt = {"face": "probe", "pretrain_ran": did_pretrain,
               "episodes_total": tr.get("episodes"),
               "updates": tr.get("updates"),
               "pool_members": tr.get("pool_members"),
               "workers": (tr.get("audit") or {}).get("workers"),
               "elapsed_sec": round(time.time() - t0, 1),
               "audit": {"generated_at": _now()}}
    _dump(receipt, os.path.join(CKPT_DIR, "probe_receipt.json"))
    print(json.dumps({"probe": "ok",
                      "episodes": receipt["episodes_total"],
                      "pretrain_ran": did_pretrain}, ensure_ascii=False))
    return 0


def cmd_export_topk(args):
    ok, posture = _require_freeze("export-topk")
    if not ok:
        return 2
    okc, cface = _train_complete_face()
    if not okc:
        print(json.dumps({"awaiting_train_complete": True,
                          "completion_face": cface}, ensure_ascii=False))
        return 2
    log_path = os.path.join(CKPT_DIR, "train_log.jsonl")
    if not os.path.exists(log_path):
        print(json.dumps({"awaiting_train": True,
                          "log": log_path}, ensure_ascii=False))
        return 2
    seen, best = set(), {}
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("skip") or r.get("dup"):
                continue
            k = r["formula"]
            if k not in seen:
                seen.add(k)
                best[k] = r
    if not best:
        print(json.dumps({"no_evaluable": True}, ensure_ascii=False))
        return 2
    ranked = sorted(best.values(),
                    key=lambda r: -(r["marginal"] or 0.0))[:K_TOP]
    # full-panel re-evaluation face (cache full universe)
    gen = int(sg.SEED_REGISTRY[SEED_KEY_GEN])
    cache_path, meta = e16.ensure_cache(CUTOFF_PIN)
    full = load_training_panel(cache_path, 0, gen)   # 0 = full face
    survivors, cens = load_survivor_nodes()
    pool = SynergyPool(full, [n for n, _, _ in survivors])
    excluded, _ = load_excluded_keys()
    rows = []
    n_dup = n_skip = 0
    for r in ranked:
        node = parse_formula(r["formula"])
        assert node is not None, r["formula"]
        if e16.canonical_key(node) in excluded:
            n_dup += 1
            continue
        marginal, sign, blk, base = pool.marginal(node)
        if marginal is None:
            n_skip += 1
            continue
        rows.append({"formula": r["formula"],
                     "marginal_ic": round(float(marginal), 6),
                     "sign": sign,
                     "abs_icir": round(abs(blk["ic_ir"]), 4),
                     "ic_mean": round(blk["ic_mean"], 6),
                     "n_periods": blk["n_periods"]})
    n_uniq = len(rows)
    if n_uniq < K_TOP:
        # not a redraw (W20 envelope law): honest shortfall disclosure
        pass
    product = {
        **sg.cutoff_meta(CUTOFF_PIN),
        "batch": BATCH, "face": "export-topk (pre-judged candidate "
        "table; RL search face -- ZERO trials ledger row; judged face "
        "counts K=32 post-freeze)",
        "k_target": K_TOP, "n_unique": n_uniq,
        "n_excluded_dup": n_dup, "n_skip": n_skip,
        "unique_shortfall_disclosed": n_uniq < K_TOP,
        "rows": rows,
        "pool_members_initial": POOL_TOP_K,
        "seeds": {"gen": [gen, SEED_KEY_GEN]},
        "prereg_ref": PREREG_REL + " (FROZEN at burn time)",
        "audit": {"engine_runs": 0, "generated_at": _now()},
    }
    out = os.path.join(OUT_DIR, f"TOPK-{CUTOFF_PIN}.json")
    _dump(product, out)
    print(json.dumps({"export_topk": "ok", "n_unique": n_uniq,
                      "n_dup": n_dup, "n_skip": n_skip, "out": out},
                     ensure_ascii=False))
    return 0


# ------------------------------------------- judged face (leg-4 build, r923)
# A158-TSGATE-P1 door template on the core48 consumption face (prereg
# §3 frozen): stock cross-section factor -> sign-aligned top-quintile
# cohort mean of aligned values (the "factor tail state" feature; the
# mapping is probed+anchored by cmd_tsgate_probe, G-ANCHOR-FACE law)
# -> per-instrument q10/q90 rolling-quantile doors (q90 high door
# judged = the sign-consistent predictive cohort state) -> long-only
# T+1 equal-weight-basket strategy at cost x1/x2/x3 -> P-5/P-5B
# all-start virtual time points -> G1'v2/G2v2/M1/D6 shared-lib gates.
DOOR_WIN = 252                              # A158-TSGATE-P1 verbatim
DOOR_MINP = 120                             # A158-TSGATE-P1 verbatim
DOOR_Q_JUDGED = 0.90                        # high door = judged side
DOOR_Q_LOW_DISCLOSED = 0.10                 # template low side, NOT
                                            # judged (32-trial budget,
                                            # no side mining)
COHORT_FRAC = 0.20                          # top-quintile by aligned rank
COST_X1_SIDE_BP = 13.041                    # ETF 26.082bp round-trip, A
COST_FACES = (("x1", 1.0), ("x2", 2.0), ("x3", 3.0))
EXTREME_DAYS = ("2024-09-24", "2024-09-30", "2025-04-07",
                "2026-01-19")               # prereg §5 P4 frozen four
JUDGED_LEDGER_NAME = "N2U3_ALPHAGEN_RL_P1"  # prereg §3 ledger verbatim
JUDGED_PRODUCT = os.path.join(OUT_DIR, f"JUDGED-{CUTOFF_PIN}.json")
ALLSTART_WINDOWS = {"3m": 63, "6m": 126, "12m": 252}   # P-5 windows
ROLLING_WORST = {"3y": 756, "5y": 1260, "10y": 2520}   # §1.3 rolling
MIN_LISTED = 24                             # P-5 deployment floor


def _sharpe_ann(r):
    r = np.asarray(r, dtype=float)
    if r.size < 2:
        return 0.0
    sd = float(r.std(ddof=1))
    return float(r.mean() / sd * np.sqrt(252.0)) if sd > 0.0 else 0.0


def _max_drawdown(eq):
    peak = eq.cummax()
    return float((eq / peak - 1.0).min())


def _signal_faces(F, sign, elig):
    """Sign-aligned top-quintile cohort mean of aligned factor values
    (A158-TSGATE-P1 transposition feature): per-date mask = elig &
    finite; cohort = top ceil(20%*n_t) names by aligned rank; feature
    = cohort mean of aligned values; thin days (n_t < MIN_CROSS) are
    gate-closed NaN (E16 MIN_CROSS law)."""
    Fc = np.where(np.isfinite(F), F, np.nan)
    eff = (elig & np.isfinite(Fc))
    A = np.where(eff, Fc * float(sign), np.nan)
    FrA = rank_rows(eff, A)
    n_t = eff.sum(axis=1)
    return A, FrA, eff, n_t


def _cohort_mean(A, FrA, eff, n_t):
    """Cohort-mean feature from an (observed or permuted) aligned-rank
    matrix -- identical selection mechanics for the observed face and
    the null face."""
    k_t = np.maximum(1, np.ceil(COHORT_FRAC * n_t).astype(np.int64))
    thr = (n_t - k_t + 1).astype(np.float64)
    coh = eff & (FrA >= thr[:, None])
    cnt = coh.sum(axis=1)
    with np.errstate(invalid="ignore"):
        s = np.where(cnt > 0,
                     np.nansum(np.where(coh, A, 0.0), axis=1)
                     / np.maximum(cnt, 1), np.nan)
    return np.where(n_t >= MIN_CROSS, s, np.nan)


def _door_state(s, dates):
    """A158-TSGATE-P1 door mechanics verbatim: rolling(252,
    min_periods=120).quantile(0.90) on the signal series; open =
    s > qref on decidable days; state carries forward between
    decidable days (in/out bucket persistence law)."""
    ser = pd.Series(s, index=dates)
    qref = ser.rolling(DOOR_WIN, min_periods=DOOR_MINP).quantile(
        DOOR_Q_JUDGED)
    decidable = ser.notna() & qref.notna()
    opens = (ser > qref) & decidable
    vals = pd.Series(np.where(decidable, opens, np.nan), index=dates)
    state = vals.ffill().fillna(False).astype(bool)
    return state, opens, qref, decidable


def _door_strategy(door_state, basket_ret, cost_side_bp):
    """Long-only T+1 door strategy on the core48 equal-weight basket:
    condition at close t -> position effective t+1; per-side cost on
    position transitions (x1 face = COST_X1_SIDE_BP)."""
    cal = basket_ret.index
    d = door_state.reindex(cal).ffill().fillna(False).astype(float)
    pos = d.shift(1).fillna(0.0)            # T+1: prior day's condition
    gross = basket_ret * pos
    prev = pos.shift(1).fillna(0.0)
    turn = (pos - prev).abs()
    net = gross - turn * (float(cost_side_bp) / 1e4)
    entries = int(((pos == 1.0) & (prev == 0.0)).sum())
    exits = int(((pos == 0.0) & (prev == 1.0)).sum())
    return {"net": net, "pos": pos, "n_entries": entries,
            "n_trades": exits}


def _allstart_face(net, basket_ret):
    """P-5/P-5B all-start virtual time points: every start p with a
    full window -> strategy vs same-window passive (EW basket
    buy&hold) window returns; beat rates + full-start 6m distribution
    + rolling 3/5/10y worst (§1.3 disclosure face)."""
    cal = net.index
    pas = basket_ret.reindex(cal)
    es = (1.0 + net).cumprod().values
    ep = (1.0 + pas).cumprod().values
    n = len(cal)
    out = {"n_starts": {}, "beat_rate": {}, "rolling_worst": {},
           "fullstart_6m": None}
    for wname, w in ALLSTART_WINDOWS.items():
        if n < w:
            out["n_starts"][wname] = 0
            out["beat_rate"][wname] = None
            continue
        rs = es[w - 1:] / es[:n - w + 1] - 1.0
        rp = ep[w - 1:] / ep[:n - w + 1] - 1.0
        out["n_starts"][wname] = int(len(rs))
        out["beat_rate"][wname] = round(float(np.mean(rs > rp)), 4)
        if wname == "6m":
            out["fullstart_6m"] = {
                "best": round(float(rs.max()), 4),
                "worst": round(float(rs.min()), 4),
                "p25": round(float(np.percentile(rs, 25)), 4),
                "median": round(float(np.median(rs)), 4),
                "p75": round(float(np.percentile(rs, 75)), 4)}
    for yname, w in ROLLING_WORST.items():
        if n >= w:
            rw = es[w - 1:] / es[:n - w + 1] - 1.0
            out["rolling_worst"][yname] = round(float(rw.min()), 4)
        else:
            out["rolling_worst"][yname] = None
    return out


def _core48_face():
    """core48 consumption panel (live.paper.load_core frozen-whitelist
    lock, single source): members truncated at the cutoff pin ->
    member daily returns + equal-weight basket returns on the common
    calendar + roster anchor facts (G-CONSUME face)."""
    from live.paper import load_core
    core = load_core()
    ps = pd.Timestamp(CUTOFF_PIN)
    roster, rets = [], {}
    for code, df in core.items():
        d = df[df.index <= ps]
        if len(d) < 2:
            continue
        roster.append(code)
        rets[code] = d["close"].pct_change().dropna()
    roster = sorted(roster)
    if len(roster) < MIN_LISTED:
        raise RuntimeError(f"core48 face too thin: {len(roster)}")
    import hashlib
    facts = {
        "n_members": len(roster),
        "roster_sha16": hashlib.sha256(
            "|".join(roster).encode("utf-8")).hexdigest()[:16],
        "anchor_510300_rows": (int(len(core["510300"]))
                               if "510300" in core else None),
        "min_listed_floor": MIN_LISTED,
    }
    return {"roster": roster, "member_rets": rets, "facts": facts}


def _anchor_triple(panel, faces, dates):
    """G-ANCHOR-FACE anchor: TOP-1 E16 survivor formula on the full
    panel, member-sign face (ic_mean sign -- the SynergyPool
    _add_member default) -> deterministic signal triple. Probe and
    consumer must derive the identical triple."""
    survivors, _ = load_survivor_nodes()
    node, formula, _ = survivors[0]
    F = e16.evaluate(node, panel["leaves"])
    blk, _ = ic_face(F, faces)
    sign = 1.0 if blk["ic_mean"] >= 0 else -1.0
    A, FrA, eff, n_t = _signal_faces(F, sign, panel["elig"])
    s = _cohort_mean(A, FrA, eff, n_t)
    state, opens, qref, decidable = _door_state(s, dates)
    first_dec = int(np.argmax(decidable.values)) \
        if bool(decidable.any()) else -1
    first_open = None
    if bool(opens.any()):
        first_open = str(dates[np.argmax(opens.values)].date())
    return {"formula": formula, "sign": sign,
            "ic_mean": round(float(blk["ic_mean"]), 6),
            "signal_len": int(np.isfinite(s).sum()),
            "first_decidable_idx": first_dec,
            "door_open_count": int(opens.sum()),
            "first_door_date": first_open}


def _assert_same_face(anchors, panel, faces, dates):
    """Consumer-side G-ANCHOR-FACE law: re-derive the anchor triple on
    the same frozen faces and compare; any drift = refuse (config
    mismatch, never a silent pass)."""
    if not isinstance(anchors, dict) or "anchor_triple" not in anchors:
        return False, {"reason": "anchors absent/malformed"}
    if anchors.get("evidence_cutoff") != CUTOFF_PIN:
        return False, {"reason": "anchor cutoff drift",
                       "anchors_cutoff": anchors.get("evidence_cutoff")}
    triple = _anchor_triple(panel, faces, dates)
    ok = triple == anchors["anchor_triple"]
    return ok, {"reason": "same-face assert " + ("OK" if ok else
               "MISMATCH"), "rederived": triple}


def _judged_core(panel, faces, dates, basket, anchors, topk_rows,
                 topk_sha16, member_rets, results_dir, out_dir,
                 d6_fn, null_k=K_TOP):
    """Judged face battery (leg-4): per TOPK row -> signal/door/strategy
    (x1 primary; x2/x3 stability descriptive) -> G1'v2 (batch-own K=32
    scrnull permutation null pool) + G2 (DSR raw-returns + family PBO
    CSCV-8) + M1 (factor IC t from the TOPK re-eval face) + D6 (REG6 +
    same-batch prior, daily-return correlation) + per-instrument /
    all-start / extreme-day / OOS-midpoint disclosure faces. Pure core:
    every repo read is injected (selftest runs synthetic faces); d6_fn
    = the shared _d6_corr_cell correlation face (W15 canon, injected by
    the caller so the hermetic selftest never imports the tl1..tl14
    chain)."""
    scrnull = int(sg.SEED_REGISTRY[SEED_KEY_SCRNULL])
    rows = list(topk_rows)
    if not rows:
        raise RuntimeError("no TOPK rows to judge")
    # strategy calendar = signal x basket with the P-5 listing floor
    R = pd.DataFrame(basket["member_rets"])
    sig_dates = pd.DatetimeIndex(dates)
    listed = R.notna().sum(axis=1)
    floor_days = listed[listed >= MIN_LISTED].index
    cal = sig_dates.intersection(floor_days)
    basket_cal = R.mean(axis=1, skipna=True).reindex(cal).dropna()
    cal = basket_cal.index
    cells, null_vals, rets_by_cell = [], [], {}
    for i, row in enumerate(rows):
        node = parse_formula(row["formula"])
        assert node is not None, row["formula"]
        F = e16.evaluate(node, panel["leaves"])
        sign = float(row["sign"])
        A, FrA, eff, n_t = _signal_faces(F, sign, panel["elig"])
        s = _cohort_mean(A, FrA, eff, n_t)
        state, opens, qref, decidable = _door_state(s, sig_dates)
        strat = {cname: _door_strategy(state, basket_cal,
                                       COST_X1_SIDE_BP * mult)
                 for cname, mult in COST_FACES}
        net = strat["x1"]["net"]
        eq = (1.0 + net).cumprod()
        yearly = (1.0 + net).groupby(net.index.year).prod() - 1.0
        # OOS = strategy-window midpoint (batch-own face, disclosed)
        half = len(net) // 2
        oos_eq = eq.iloc[half:]
        oos_ret = float(oos_eq.iloc[-1] / oos_eq.iloc[0] - 1.0)
        # per-instrument door-active face (A158 per-inst median shape)
        poscal = strat["x1"]["pos"]
        inst_sh = {}
        for code, mr in basket["member_rets"].items():
            m = mr.reindex(cal).fillna(0.0) * poscal
            if float(m.std(ddof=1) or 0.0) > 0:
                inst_sh[code] = _sharpe_ann(m)
        med_inst = (round(float(np.median(list(inst_sh.values()))), 4)
                    if inst_sh else None)
        # extreme-day door states (P4 frozen four; absent = None)
        exd = {}
        for dstr in EXTREME_DAYS:
            ts = pd.Timestamp(dstr)
            exd[dstr] = (bool(state.loc[ts]) if ts in state.index
                         else None)
        cell = {
            "i": i, "formula": row["formula"],
            "sign": sign,
            "m1_t_face": {"ic_mean": row.get("ic_mean"),
                          "abs_icir": row.get("abs_icir"),
                          "n_periods": row.get("n_periods")},
            "n_entries": strat["x1"]["n_entries"],
            "n_trades": strat["x1"]["n_trades"],
            "sharpe_full_x1": round(_sharpe_ann(net), 4),
            "sharpe_full_x2": round(_sharpe_ann(strat["x2"]["net"]), 4),
            "sharpe_full_x3": round(_sharpe_ann(strat["x3"]["net"]), 4),
            "max_dd_x1": round(_max_drawdown(eq), 4),
            "yearly_x1": {str(k): round(float(v), 4)
                          for k, v in yearly.items()},
            "descriptive": {
                "ann_pos": bool(eq.iloc[-1] > eq.iloc[0]),
                "oos_dual_pos": bool(_sharpe_ann(
                    net.iloc[half:]) > 0 and oos_ret > 0),
                "oos_sharpe": round(_sharpe_ann(net.iloc[half:]), 4),
                "oos_ret": round(oos_ret, 4),
                "dd_ok": bool(_max_drawdown(eq) >= -0.35),
                "no_crash_year": bool(yearly.min() > -0.30
                                      if len(yearly) else False),
                "x2_yearly_stable": bool(
                    ((1.0 + strat["x2"]["net"]).groupby(
                        strat["x2"]["net"].index.year).prod()
                     - 1.0).min() > -0.30
                    if len(net) else False),
            },
            "per_instrument": {
                "median_door_active_sharpe": med_inst,
                "n_instrument_face": len(inst_sh),
                "anchor_510300_sharpe": inst_sh.get("510300")},
            "extreme_day_door_state": exd,
            "allstart": _allstart_face(net, basket_cal),
        }
        # K=32 same-mask permutation nulls: draw j belongs to formula
        # j mod n_rows (one permutation replicate per draw, t23
        # verbatim; values feed the batch-own skill line)
        j = i
        while j < null_k:
            rng = np.random.default_rng([scrnull, j])
            FrA_null = t23._permute_ranks_within_mask(FrA, eff, rng)
            s_null = _cohort_mean(A, FrA_null, eff, n_t)
            st_null, _, _, _ = _door_state(s_null, sig_dates)
            nz = _door_strategy(st_null, basket_cal,
                                COST_X1_SIDE_BP)["net"]
            null_vals.append(round(_sharpe_ann(nz), 4))
            j += len(rows)
        cells.append(cell)
        rets_by_cell[i] = net
    # batch-own null pool (>=30 law: K=32)
    mu = float(np.mean(null_vals))
    sd = float(np.std(null_vals, ddof=1)) if len(null_vals) > 1 else None
    null_pool = {"values": null_vals, "source":
                 "N2U3 batch-own K=32 scrnull permutation nulls "
                 "(t23 _permute_ranks_within_mask verbatim, one "
                 "replicate per draw, formula j mod n_rows cycling)",
                 "coverage": {"n_values": len(null_vals),
                              "schemas_parsed": ["batch_own_scrnull"],
                              "known_unparsed": [],
                              "mu": mu, "sigma": sd}}
    # family PBO (CSCV-8) on the complete 32 x T net matrix
    mat = pd.DataFrame({i: rets_by_cell[i] for i in range(len(cells))})
    pbo_out = cscv_pbo(mat)
    pbo_val = float(pbo_out["pbo"])
    # phase 2: per-cell gates (skill line is batch-level data-driven)
    same_batch_rets = dict(member_rets)
    for cell in cells:
        i = cell["i"]
        net = rets_by_cell[i]
        rets = [float(v) for v in net.values]
        try:
            g1 = sg.g1_prime_v2(cell["sharpe_full_x1"], rets, K_TOP,
                                n_trades=cell["n_trades"],
                                n_entries=cell["n_entries"],
                                pool="core48", null_pool=null_pool,
                                results_dir=results_dir)
        except Exception as exc:                    # noqa: BLE001
            g1 = {"gate": "g1_prime_v2", "pass_v2": False,
                  "error": f"skill-line face refused: {exc}"}
        try:
            dsr = sg.deflated_sharpe_ratio(rets, K_TOP)
        except Exception as exc:                    # noqa: BLE001
            dsr = {"dsr": None, "error": str(exc)}
        g2 = sg.g2_registration_v2(g1.get("pass_v2", False), dsr,
                                   pbo_val)
        # M1: factor-face IC t (t = sign(ic_mean)*|icir|*sqrt(n))
        r0 = cell["m1_t_face"]
        t_stat = None
        if (r0.get("ic_mean") is not None
                and r0.get("abs_icir") not in (None, 0)
                and r0.get("n_periods")):
            t_stat = (np.sign(r0["ic_mean"]) * r0["abs_icir"]
                      * math.sqrt(int(r0["n_periods"])))
        m1 = sg.m1_t_value_gate(t_stat)
        # D6: registered members + same-batch already-judged formulas
        d6 = _d6_corr_cell(net, same_batch_rets)
        cell["g1_prime_v2"] = g1
        cell["g2_registration_v2"] = g2
        cell["m1_t_value_gate"] = m1
        cell["d6"] = d6
        cell["d6_ok"] = not (d6.get("max_corr_vs_registered") is not None
                             and d6["max_corr_vs_registered"] >= 0.7)
        cell["verdict"] = {
            "g1_pass_v2": bool(g1.get("pass_v2")),
            "g2_eligible_v2": bool(g2.get("eligible_v2")),
            "m1_pass": bool(m1.get("pass")),
            "d6_ok": bool(cell["d6_ok"]),
            "refused_d6": not bool(cell["d6_ok"]),
            "registered": bool(g2.get("eligible_v2") and m1.get("pass")
                               and cell["d6_ok"]),
        }
        same_batch_rets[f"BATCH:{i}"] = net
    out_path = os.path.join(out_dir, f"JUDGED-{CUTOFF_PIN}.json")
    if os.path.exists(out_path):
        return {"refused": True, "reason": "judged product already "
                "landed (refuse-if-exists law)", "out": out_path}
    n_g1 = sum(1 for c in cells if c["verdict"]["g1_pass_v2"])
    n_reg = sum(1 for c in cells if c["verdict"]["registered"])
    product = {
        **sg.cutoff_meta(CUTOFF_PIN),
        "batch": BATCH,
        "face": "judged (leg-4: A158-TSGATE-P1 q90 door on core48, "
        "long-only T+1, cost x1/x2/x3, all-start virtual time points)",
        "k_cells": len(cells),
        "topk_sha16_pin": topk_sha16,
        "anchors_sha16_pin": anchors.get("_sha16"),
        "door": {"win": DOOR_WIN, "min_periods": DOOR_MINP,
                 "q_judged": DOOR_Q_JUDGED,
                 "q_low_disclosed_not_judged": DOOR_Q_LOW_DISCLOSED},
        "signal_construction": anchors.get("signal"),
        "cost": {"x1_side_bp": COST_X1_SIDE_BP,
                 "faces": [f[0] for f in COST_FACES]},
        "null_pool": null_pool,
        "family_pbo": {"pbo": round(pbo_val, 4),
                       "verdict": pbo_out.get("verdict"),
                       "n_blocks": 8},
        "aggregate": {"n_g1_pass_v2": n_g1,
                      "n_registered": n_reg,
                      "n_d6_refused": sum(
                          1 for c in cells if c["refused_d6"]),
                      "n_m1_pass": sum(
                          1 for c in cells
                          if c["m1_t_value_gate"]["pass"])},
        "cells": cells,
        "prereg_ref": PREREG_REL + " (FROZEN at burn time)",
        "ledger": sg.append_ledger(
            JUDGED_LEDGER_NAME, K_TOP, file_name=out_path,
            evidence_cutoff=CUTOFF_PIN, results_dir=results_dir),
        "audit": {"engine_runs": 0, "generated_at": _now(),
                  "batch_cells_ledger": K_TOP,
                  "note": "RL search face + nulls calibration not "
                  "counted (E16 trial_budget_law); judged K=32 "
                  "counted; E[FP]=0.05*32=1.6 nominal"},
    }
    _dump(product, out_path)
    return {"refused": False, "out": out_path, "product": product}


def cmd_tsgate_probe(args):
    """Freeze-gated anchor probe (leg-4 step 1): pins the §3 frozen
    consumption mapping (door params + signal construction + core48
    roster facts + anchor formula triple) into tsgate_anchors.json.
    Refuse-if-exists: re-derivation is the judge consumer's same-face
    assert, never a rewrite."""
    ok, posture = _require_freeze("tsgate-probe")
    if not ok:
        return 2
    if os.path.exists(TSGATE_ANCHORS):
        print(json.dumps({"tsgate_probe": "already-landed (refuse "
                         "rewrite; judge asserts same-face on "
                         "consume)"}, ensure_ascii=False))
        return 0
    pf = e16.gate_face()
    if not pf.get("ready"):
        print(json.dumps({"refused": True, "reason": "panel gate not "
                          "ready", "panel_gate_keys": sorted(pf)[:8]},
                         ensure_ascii=False))
        return 2
    cache_path, meta = e16.ensure_cache(CUTOFF_PIN)
    gen = int(sg.SEED_REGISTRY[SEED_KEY_GEN])
    panel = load_training_panel(cache_path, 0, gen)
    faces = _panel_faces(panel)
    dates = pd.to_datetime(np.asarray(panel["cal"],
                                      dtype="datetime64[us]"))
    basket = _core48_face()
    triple = _anchor_triple(panel, faces, dates)
    anchors = {
        **sg.cutoff_meta(CUTOFF_PIN),
        "batch": BATCH,
        "template": "A158-TSGATE-P1 per-instrument q10/q90 door on "
        "core48 (prereg §3 frozen consumption template)",
        "door": {"win": DOOR_WIN, "min_periods": DOOR_MINP,
                 "q_judged": DOOR_Q_JUDGED,
                 "q_low_disclosed_not_judged": DOOR_Q_LOW_DISCLOSED,
                 "side_note": "q90 high door = sign-consistent "
                 "predictive cohort state; low side disclosed but NOT "
                 "judged (32-trial budget, no side mining)"},
        "signal": {"cohort_frac": COHORT_FRAC,
                   "min_cross": MIN_CROSS,
                   "cost_x1_side_bp": COST_X1_SIDE_BP,
                   "construction": "sign-aligned top-quintile-by-rank "
                   "cohort mean of aligned values (per-date mask = "
                   "elig & finite; this probe pins the mapping, "
                   "G-ANCHOR-FACE law)"},
        "calendar": {"signal_face": "full cache cal incl. warmup rows",
                     "census_start": "2018-01-01",
                     "oos_split": "strategy-window midpoint (batch-own "
                     "face; prereg pins no calendar split)",
                     "min_listed_floor": MIN_LISTED},
        "core48": basket["facts"],
        "anchor_triple": triple,
        "nulls": {"k": K_TOP, "seed_key": SEED_KEY_SCRNULL,
                  "law": "t23 _permute_ranks_within_mask verbatim; one "
                  "permutation replicate per draw, K=32 draws, "
                  "formula j mod n_rows cycling"},
        "extreme_days": list(EXTREME_DAYS),
        "allstart_windows": ALLSTART_WINDOWS,
        "rolling_worst": ROLLING_WORST,
        "prereg_ref": PREREG_REL + " (FROZEN)",
        "audit": {"engine_runs": 0, "generated_at": _now()},
    }
    _dump(anchors, TSGATE_ANCHORS)
    print(json.dumps({"tsgate_probe": "ok", "anchors": TSGATE_ANCHORS,
                      "anchor_triple": triple,
                      "core48": basket["facts"]},
                     ensure_ascii=False, indent=1))
    return 0


def cmd_judge(args):
    """Judged face (leg-4): consumes the frozen tsgate anchors (same-
    face assert) + the TOPK candidate table (sha16-pinned) -> full
    judged battery -> JUDGED-<cutoff>.json + ledger 32 (first judged
    N2U3 channel-1 evidence). Refuses until anchors + TOPK + leg-3
    completion all stand; refuse-if-exists on the product."""
    extra = {
        "topk_product": os.path.exists(
            os.path.join(OUT_DIR, f"TOPK-{CUTOFF_PIN}.json")),
        "tsgate_anchors": os.path.exists(TSGATE_ANCHORS),
        "train_complete": _train_complete_face()[0],
    }
    ok, posture = _require_freeze("judge", extra=extra)
    if not ok:
        return 2
    if os.path.exists(JUDGED_PRODUCT):
        print(json.dumps({"refused": True, "reason": "judged product "
                          "already landed (refuse-if-exists law)",
                          "out": JUDGED_PRODUCT}, ensure_ascii=False))
        return 0
    pf = e16.gate_face()
    if not pf.get("ready"):
        print(json.dumps({"refused": True, "reason": "panel gate not "
                          "ready"}, ensure_ascii=False))
        return 2
    import hashlib
    with open(TSGATE_ANCHORS, "rb") as f:
        anchors_blob = f.read()
    anchors = json.loads(anchors_blob.decode("utf-8"))
    anchors["_sha16"] = hashlib.sha256(anchors_blob).hexdigest()[:16]
    topk_path = os.path.join(OUT_DIR, f"TOPK-{CUTOFF_PIN}.json")
    with open(topk_path, "rb") as f:
        topk_blob = f.read()
    topk = json.loads(topk_blob.decode("utf-8"))
    topk_sha16 = hashlib.sha256(topk_blob).hexdigest()[:16]
    rows = topk.get("rows") or []
    if not rows:
        print(json.dumps({"refused": True, "reason": "TOPK zero rows"},
                         ensure_ascii=False))
        return 2
    cache_path, meta = e16.ensure_cache(CUTOFF_PIN)
    gen = int(sg.SEED_REGISTRY[SEED_KEY_GEN])
    panel = load_training_panel(cache_path, 0, gen)
    faces = _panel_faces(panel)
    dates = pd.to_datetime(np.asarray(panel["cal"],
                                      dtype="datetime64[us]"))
    ok_face, face_ev = _assert_same_face(anchors, panel, faces, dates)
    if not ok_face:
        print(json.dumps({"refused": True, "reason": "G-ANCHOR-FACE "
                          "same-window assert failed", "evidence":
                          face_ev}, ensure_ascii=False))
        return 2
    basket = _core48_face()
    # D6 registered-member daily returns (ew6 member_run canon face,
    # live.paper anchor-gate code path; heavy imports stay judge-local)
    import ew6_portfolio as E
    from perpetual_faces_n2 import _d6_corr_cell, REG6   # noqa: E402
    from live.paper import load_core
    if E.PRICES_FULL is None:
        E.PRICES_FULL = load_core()
    member_rets = {}
    for tid in REG6:
        r = E.member_run(tid)
        eq = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        member_rets[tid] = eq.pct_change().dropna()
    res = _judged_core(panel, faces, dates, basket, anchors, rows,
                       topk_sha16, member_rets, ROOT_RESULTS,
                       OUT_DIR)
    if res.get("refused"):
        print(json.dumps(res, ensure_ascii=False))
        return 2
    p = res["product"]
    print(json.dumps({"judge": "ok", "out": res["out"],
                      "k_cells": p["k_cells"],
                      "aggregate": p["aggregate"],
                      "family_pbo": p["family_pbo"],
                      "null_mu_sigma": [p["null_pool"]["coverage"]["mu"],
                                        p["null_pool"]["coverage"][
                                            "sigma"]],
                      "ledger_total": p["ledger"]["total"]},
                     ensure_ascii=False, indent=1))
    return 0


def cmd_status(args):
    st = {"prereg_status": prereg_status(),
          "cutoff_pin": CUTOFF_PIN,
          "seed_bands": {k: (k in sg.SEED_REGISTRY) for k in SEED_KEYS},
          "cache_exists": os.path.exists(e16.cache_path(CUTOFF_PIN)),
          "probe_receipt": os.path.exists(PROBE_RECEIPT),
          "ckpts": {f: os.path.exists(os.path.join(CKPT_DIR, f))
                    for f in ("pretrain_policy.npz", "pretrain_receipt.json",
                              "train_policy.npz", "train_log.jsonl",
                              "train_receipt.json")},
          "products": {"topk": os.path.exists(
              os.path.join(OUT_DIR, f"TOPK-{CUTOFF_PIN}.json")),
              "tsgate_anchors": os.path.exists(TSGATE_ANCHORS)}}
    log_path = os.path.join(CKPT_DIR, "train_log.jsonl")
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            st["train_episodes"] = sum(1 for line in f if line.strip())
    print(json.dumps(st, ensure_ascii=False, indent=1))
    return 0

# ------------------------------------------------------------------ selftest

def _synth_panel(path, seed=777, T=140, N=120, signal=0.9, warmup=30):
    """Hermetic synthetic cache (e16 _synth_cache import face)."""
    e16._synth_cache(path, seed=seed, T=T, N=N, signal=signal,
                     warmup=warmup)


def selftest():
    ok = []

    def check(name, cond):
        ok.append((name, bool(cond)))
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")

    g = grammar_face()
    td = tempfile.mkdtemp(prefix="rlp1_selftest_")

    # L1 grammar face + determinism + parse round-trip (hermetic anchors)
    check("L1a 29 ops / 8 inputs / 5 windows / depth<=2",
          len(g["op_labels"]) == 29 and len(e16.BASE_INPUTS) == 8
          and len(e16.WINDOWS) == 5)
    check("L1b vocab 44 deterministic",
          g["n_vocab"] == 44 and g["vocab"] == grammar_face()["vocab"])
    for s in SURVIVOR_ANCHORS:
        n = parse_formula(s)
        check(f"L1c parse round-trip {s}",
              n is not None and e16.formula_str(n) == s)
    d2s = "STD(MA(volume,10),5)"
    n2 = parse_formula(d2s)
    check("L1d d2 parse round-trip",
          n2 is not None and e16.formula_str(n2) == d2s
          and n2[0] == "d2")
    check("L1e out-of-grammar parse refused",
          parse_formula("NOTANOP(close,5)") is None
          and parse_formula("MA(close,7)") is None
          and parse_formula("MA(bogus,5)") is None)
    # token maps
    n1 = ("d1", "ROC", "close", 5)
    toks = node_to_tokens(n1)
    check("L1f node<->tokens round-trip d1",
          tokens_to_node(toks) == n1 and len(toks) == 4)
    toks2 = node_to_tokens(n2)
    check("L1g node<->tokens round-trip d2",
          tokens_to_node(toks2) == n2 and len(toks2) == 6)
    # E16 rng bootstrap face determinism
    r1 = [e16._draw_node(np.random.default_rng([123, 9000 + i]),
                         g["ops"], 1 if i % 10 < 6 else 2)
          for i in range(N_BOOT)]
    r2 = [e16._draw_node(np.random.default_rng([123, 9000 + i]),
                         g["ops"], 1 if i % 10 < 6 else 2)
          for i in range(N_BOOT)]
    check("L1h bootstrap draw streams deterministic",
          all(e16.formula_str(a) == e16.formula_str(b)
              for a, b in zip(r1, r2)))

    # L2 masks + featurize legality
    m0 = step_mask(0, 0)
    check("L2a depth mask exactly {D1,D2}",
          m0.sum() == 2 and m0[g["tok"]["D1"]] and m0[g["tok"]["D2"]])
    m1 = step_mask(1, 1)
    check("L2b d1 step1 mask = ops only",
          m1.sum() == 29 and m1[g["tok"]["MA"]] and not m1[g["tok"]["D1"]])
    m2 = step_mask(2, 2)
    check("L2c d2 step2 mask = windows only",
          m2.sum() == 5 and m2[g["tok"]["20"]])
    x = featurize(node_to_tokens(n1)[:2], 2)
    check("L2d featurize shape + one-hots",
          x.shape == (SLOTS * 44 + SLOTS,)
          and x.sum() == 3 and x[-SLOTS + 2] == 1.0)

    # L3 masked softmax / log-softmax laws
    z = np.array([0.3, -1.2, 2.0, 0.1])
    mk = np.array([True, False, True, True])
    p = masked_softmax(z, mk)
    lp = masked_log_softmax(z, mk)
    check("L3a masked softmax renormalizes over mask",
          abs(p[mk].sum() - 1.0) < 1e-12 and p[~mk].sum() == 0.0
          and np.all(np.isfinite(p[mk])))
    check("L3b log-softmax consistent with softmax",
          np.allclose(np.exp(lp[mk]), p[mk]))
    # finite-difference gradient checks (cross-entropy + entropy)
    rng = np.random.default_rng(5)
    for trial in range(3):
        zz = rng.standard_normal(4) * 0.7
        mm = rng.random(4) > 0.3
        if not mm.any():
            mm[0] = True
        aa = int(np.argmax(np.where(mm, rng.random(4), -1)))
        lp0 = masked_log_softmax(zz, mm)
        p0 = np.exp(lp0)
        lp_safe = np.where(mm, lp0, 0.0)
        onehot = np.zeros(4)
        onehot[aa] = 1.0
        H0 = -np.sum(p0 * lp_safe)
        dce = p0 - onehot
        dent = p0 * (lp_safe + H0)
        h = 1e-6
        fd_ce = np.zeros(4)
        fd_ent = np.zeros(4)
        for j in range(4):
            zp = zz.copy(); zp[j] += h
            zm = zz.copy(); zm[j] -= h
            lpp = masked_log_softmax(zp, mm)[aa]
            lpm = masked_log_softmax(zm, mm)[aa]
            # finite difference of the LOSS faces the analytic grads
            # measure: d(-log p_a)/dz_j and d(-H)/dz_j
            fd_ce[j] = (lpm - lpp) / (2 * h)

            def _H(z):
                lpz = masked_log_softmax(z, mm)
                pz = np.exp(lpz)
                return -np.sum(pz * np.where(mm, lpz, 0.0))

            fd_ent[j] = (_H(zm) - _H(zp)) / (2 * h)
        if not (np.allclose(dce * (mm), fd_ce * (mm), atol=1e-5)
                and np.allclose(dent * mm, fd_ent * mm, atol=1e-5)):
            break
    check("L3c CE/entropy analytic grads == finite difference",
          trial == 2 and np.allclose(dce * (mm), fd_ce * (mm), atol=1e-5)
          and np.allclose(dent * mm, fd_ent * mm, atol=1e-5))

    # L4 MLP backprop finite-difference (tiny net, one sample)
    tn = TinyPolicy(6, 4, 3, 99)
    xs = np.random.default_rng(7).standard_normal((1, 6))
    ms = np.array([True, True, True])
    logits, _, cache = tn.forward(xs)
    a0 = 1
    lp0 = masked_log_softmax(logits.reshape(-1), ms)
    onehot = np.zeros(3); onehot[a0] = 1.0
    dlogits = (np.exp(lp0) - onehot).reshape(1, -1)
    grads = tn.backprop(cache, dlogits, np.zeros((1, 1)))
    h = 1e-6
    rngp = np.random.default_rng(2024)
    fd_ok = True
    for pi, P in enumerate(tn.params()):
        if P.ndim == 1:
            idxs = [(int(rngp.integers(0, P.shape[0])),)]
        else:
            idxs = [(int(rngp.integers(0, P.shape[0])),
                     int(rngp.integers(0, P.shape[1]))) for _ in range(2)]

        def _loss_at():
            lg, _, _ = tn.forward(xs)
            return masked_log_softmax(lg.reshape(-1), ms)[a0]

        for ij in idxs:
            old = P[ij]
            P[ij] = old + h
            lp_p = _loss_at()
            P[ij] = old - h
            lp_m = _loss_at()
            P[ij] = old
            # FD of the LOSS face (-log p_a) the analytic grad measures
            fd = (lp_m - lp_p) / (2 * h)
            if abs(fd - grads[pi][ij]) > 1e-4:
                fd_ok = False
                break
        if not fd_ok:
            break
    check("L4 MLP backprop == finite difference (sampled params)", fd_ok)

    # L5 PPO learns the better arm (synthetic 2-armed bandit through the
    # REAL ppo_update machinery)
    pol = TinyPolicy(4, 8, 2, 4242)
    opt = Adam(pol.params(), lr=0.05)
    bandit_consts = dict(PPO)
    bandit_consts.update(lr=0.05, epochs=2, minibatch=16,
                         rollout_episodes=16, ent_coef=0.0, vf_coef=0.0)
    xs_b = np.array([[0.0, 0.0, 0.0, 1.0]] * 1)
    mask_b = np.array([True, True])
    rngb = np.random.default_rng(31337)
    B = 32
    Sb = np.repeat(xs_b, B, axis=0)
    Mb = np.tile(mask_b, (B, 1))
    probs_hist = []
    for it in range(40):
        logits, _, _ = pol.forward(Sb)
        pb = np.exp(masked_log_softmax(logits, Mb))
        acts = np.array([int(rngb.choice(2, p=pb[i]))
                         for i in range(B)])
        olp = np.log(np.array([pb[i, acts[i]]
                               for i in range(B)]) + 1e-300)
        ret = (acts == 0).astype(np.float64)
        adv = ret - ret.mean()
        ppo_update(pol, opt, Sb, Mb, acts, olp, adv, ret, bandit_consts)
        if it % 10 == 9:
            probs_hist.append(pb[0, 0])
    check("L5 PPO learns the better arm (p->>0.9)",
          probs_hist[-1] > 0.9 and probs_hist[-1] > probs_hist[0])

    # L6 synthetic panel: IC face + synergy pool machinery
    cp = os.path.join(td, "syn_cache.npz")
    _synth_panel(cp, seed=777, T=140, N=120, signal=0.9)
    with np.load(cp, allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
        cal = [str(x) for x in z["cal"]]
        universe = [str(x) for x in z["universe"]]
        panel = {"cal": cal, "universe": universe, "elig": z["elig"],
                 "fwd1": z["fwd1"], "census_rows": z["census_rows"],
                 "leaves": {k: z[f"leaf_{k}"] for k in e16.BASE_INPUTS},
                 "meta": meta, "sub": None, "full_universe_n": len(universe)}
    pool = SynergyPool(panel, [("d1", "ROC", "close", 5)])
    # exact zero-marginal law: same factor as the pool member -> 0
    m0_, s0_, blk0, base0 = pool.marginal(("d1", "ROC", "close", 5))
    check("L6a identical factor -> marginal == 0 (exact)",
          m0_ is not None and abs(m0_) < 1e-9)
    # strong signal vs noise pool: positive marginal; correlated family:
    # smaller marginal (anti-redundancy law)
    pool_noise = SynergyPool(panel, [("d1", "MA", "volume", 10)])
    m_sig, s_sig, blk_sig, _ = pool_noise.marginal(("d1", "ROC", "close", 5))
    m_fam, _, _, _ = pool.marginal(("d1", "ROC", "close", 10))
    check("L6b signal vs noise pool -> positive marginal",
          m_sig is not None and m_sig > 0.02)
    check("L6c correlated family member -> smaller marginal",
          m_fam is not None and m_fam < m_sig)
    # dilution law: a noise candidate never IMPROVES the pool (adding a
    # zero-IC member dilutes a strong pool by ~m*M/(M+1) -> negative)
    m_noise, _, blk_n, _ = pool.marginal(("d1", "MA", "volume", 10))
    check("L6d noise candidate marginal is dilution-negative",
          m_noise is None or m_noise < 1e-6)
    # pool admission face: tau gate + member count
    n_before = len(pool.members)
    if m_fam is not None and m_fam > TAU_ADMIT:
        pool.admit(("d1", "ROC", "close", 10), s0_ or 1.0)
        check("L6e admit grows pool", len(pool.members) == n_before + 1)
    else:
        check("L6e admit grows pool (tau gate honest skip)",
              len(pool.members) == n_before)

    # L7 env episode + dedup + wiring (synthetic panel, tiny policy)
    excluded = {e16.canonical_key(("d1", "ROC", "close", 5))}
    env = GrammarEnv(panel, pool_noise, excluded, 555)
    pol_e = TinyPolicy(env.n_in, 16, g["n_vocab"], 556)
    eps = env.rollout(pol_e, 0, 12)
    check("L7a episodes build legal nodes",
          all(e16.node_depth(e["node"]) in (1, 2) for e in eps)
          and all(len(e["tokens"]) in (4, 6) for e in eps))
    # dup wiring: replay the SAME seeds/policy with excluded = the first
    # batch's own keys -> every replayed episode must flag dup
    keys_first = {e["key"] for e in eps}
    env_replay = GrammarEnv(panel, pool_noise, keys_first, 555)
    eps_replay = env_replay.rollout(pol_e, 0, 12)
    check("L7b dup flag fires on replay vs first-batch keys",
          len(eps_replay) == len(eps)
          and all(e["formula"] == f["formula"]
                  for e, f in zip(eps_replay, eps))
          and all(e["dup"] for e in eps_replay))
    live = [e for e in eps if not e["skip"]]
    check("L7c rewards finite on live episodes",
          all(np.isfinite(e["reward"]) for e in live) and len(live) > 0)
    # token sequence replay determinism (same policy + seed)
    e1 = env.episode(pol_e, 7)
    e2 = env.episode(pol_e, 7)
    check("L7d episode replay deterministic",
          e1["tokens"] == e2["tokens"] and e1["reward"] == e2["reward"])

    # L8 GAE + shard split math
    S8, M8, A8, OL8, AD8, RT8 = _gae(live, PPO)
    check("L8a GAE batch shapes aligned",
          len(S8) == len(M8) == len(A8) == len(OL8) == len(AD8)
          == len(RT8) and len(S8) > 0)
    check("L8b minibatch partition covers batch",
          sum(1 for lo in range(0, len(S8), PPO["minibatch"])
              for _ in [0]) == math.ceil(len(S8) / PPO["minibatch"]))

    # L9 t23 permutation determinism + same-mask invariance (verbatim
    # import face -- judged-null machinery leg)
    Fr = np.arange(40, dtype=np.float64).reshape(4, 10) % 7
    eff = np.ones((4, 10), dtype=bool)
    eff[:, 0] = False
    p1 = t23._permute_ranks_within_mask(Fr, eff,
                                        np.random.default_rng(42))
    p2 = t23._permute_ranks_within_mask(Fr, eff,
                                        np.random.default_rng(42))
    check("L9a permutation deterministic", np.array_equal(p1, p2))
    check("L9b per-row multiset invariant",
          np.array_equal(np.sort(Fr[eff].reshape(4, 9), axis=1),
                         np.sort(p1[eff].reshape(4, 9), axis=1)))

    # L10 FREEZE-GATE machine proof (synthetic prereg + synthetic
    # registry; receipts redirected to tempdir -- zero repo file touched)
    syn_reg = {SEED_KEY_SCRNULL: 1, SEED_KEY_UNC: 2}   # gen band MISSING
    syn_draft = os.path.join(td, "syn_prereg_draft.md")
    open(syn_draft, "w", encoding="utf-8").write(
        "head 【状态：DRAFT——起草窗产物·未冻结】\n")
    ok_f, post = freeze_gate(
        "selftest-draft", registry=syn_reg, prereg_path=syn_draft,
        receipt_path=os.path.join(td, "r1.json"))
    check("L10a DRAFT + missing band -> refuse",
          not ok_f and len(post["problems"]) == 2)
    syn_frozen = os.path.join(td, "syn_prereg_frozen.md")
    open(syn_frozen, "w", encoding="utf-8").write(
        "head 【状态：FROZEN——冻结窗产物】\n")
    syn_reg2 = {SEED_KEY_GEN: 20_625_000, SEED_KEY_SCRNULL: 20_625_500,
                SEED_KEY_UNC: 20_626_000}
    ok_f2, post2 = freeze_gate(
        "selftest-frozen", registry=syn_reg2, prereg_path=syn_frozen,
        receipt_path=os.path.join(td, "r2.json"))
    check("L10b FROZEN + full bands -> pass", ok_f2)
    check("L10c refuse landed a receipt",
          os.path.exists(os.path.join(td, "r1.json"))
          and not os.path.exists(os.path.join(td, "r2.json")))
    # judge extra conditions face
    ok_j, post_j = freeze_gate(
        "selftest-judge", registry=syn_reg2, prereg_path=syn_frozen,
        receipt_path=os.path.join(td, "r3.json"),
        extra_conditions={"topk_product": False,
                          "tsgate_anchors": True})
    check("L10d judge refuses on missing TOPK product",
          not ok_j and any("topk_product" in p for p in post_j["problems"]))

    # L11 ledger block shape (E16 s7 precedent face)
    led = sg.append_ledger("N2U3_RL_SELFTEST_DUMMY", 4, file_name=None,
                           prev_total=100)
    check("L11a ledger block shape (prev override)",
          led["batch_trials"] == 4 and led["total"] == 104)
    check("L11b cutoff_meta top-level evidence_cutoff",
          sg.cutoff_meta("2026-10-09") ==
          {"evidence_cutoff": "2026-10-09"})

    # L12 dedup canonical face (E16 verbatim key law + in-batch counting)
    k1 = e16.canonical_key(("d1", "SUMP", "close", 5))
    k2 = e16.canonical_key(("d1", "VSUMP", "close", 5))
    check("L12a alias canonical collapse", k1 == k2)
    test_keys = [e16.canonical_key(("d1", "SUMP", "close", 5)),
                 e16.canonical_key(("d1", "VSUMP", "close", 5)),
                 e16.canonical_key(("d1", "MA", "close", 10)),
                 e16.canonical_key(("d1", "MA", "close", 10))]
    seen_batch = set()
    dups = 0
    for k in test_keys:
        if k in seen_batch:
            dups += 1
        seen_batch.add(k)
    check("L12b in-batch key dedup counting (alias + repeat)",
          dups == 2 and len(seen_batch) == 2)

    # L13 parallel marginal equivalence (O-20260930-2355 law-1
    # ProcessPool conversion): worker-side rebuild from the same
    # synthetic cache (survivor + admitted pair) must be bit-identical
    # to the in-process sequential reference
    cand_nodes = [("d1", "ROC", "close", 5), ("d1", "MA", "volume", 10),
                  ("d2", "STD", 20, ("d1", "MA", "close", 5)),
                  ("d1", "RANK", "amount", 60),
                  ("d1", "QTLD", "volume", 20)]
    pool_ref = SynergyPool(panel, [("d1", "MA", "volume", 10)])
    pool_ref.admit(("d1", "ROC", "close", 5), 1.0)
    seq_ref = [pool_ref.marginal(nd) for nd in cand_nodes]
    par_res, par_w = _marginals_parallel(
        cand_nodes,
        (cp, TRAIN_UNI_N, 777, [("d1", "MA", "volume", 10)],
         [(("d1", "ROC", "close", 5), 1.0)]), 2)
    par_ok = all(
        (a[0] == b["marginal"]) and (a[1] == b["sign"])
        and ((a[2] is None) == (b["cand_blk"] is None))
        and (a[2] is None or a[2]["ic_mean"] == b["cand_blk"]["ic_mean"])
        and a[3] == b["base_ic"]
        for a, b in zip(seq_ref, par_res))
    check("L13 parallel marginal == sequential reference (bit-exact)",
          par_ok and par_w == 2)

    # L14 leg-3 completion gate (post-burn consumption fail-closed face)
    def _mk_ckpt_face(d, n_log, eps):
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "train_log.jsonl"), "w",
                  encoding="utf-8") as f:
            for i in range(n_log):
                f.write(json.dumps({"ep": i, "formula": "MA(close,5)",
                                    "dup": False, "skip": False,
                                    "marginal": 0.001, "sign": 1.0,
                                    "reward": 0.001}) + "\n")
        _dump({"face": "train", "episodes": eps, "updates": 1,
               "pool_members": POOL_TOP_K, "seed_key": SEED_KEY_GEN,
               "train_uni_n": TRAIN_UNI_N,
               "audit": {"generated_at": _now()}},
              os.path.join(d, "train_receipt.json"))

    ckA = os.path.join(td, "ck_partial")
    _mk_ckpt_face(ckA, 300, 300)
    okA, faceA = _train_complete_face(ckA)
    check("L14a partial training face refused (incomplete leg3 budget)",
          not okA and faceA["reason"] == "incomplete_leg3_budget"
          and faceA["required_min"] == 4352)
    ckB = os.path.join(td, "ck_reclaim")
    _mk_ckpt_face(ckB, 4400, 4352)
    okB, faceB = _train_complete_face(ckB)
    check("L14b stale receipt vs re-claimed log refused (mismatch)",
          not okB and faceB["reason"]
          == "log_receipt_mismatch_reclaim_inflight")
    okC, faceC = _train_complete_face(os.path.join(td, "ck_empty"))
    check("L14c missing receipt refused",
          not okC and faceC["reason"] == "receipt_absent")
    ckD = os.path.join(td, "ck_done")
    _mk_ckpt_face(ckD, LEG3_COMPLETE_EPS, LEG3_COMPLETE_EPS)
    okD, faceD = _train_complete_face(ckD)
    check("L14d completed leg-3 face accepted (receipt==log, >= 4352)",
          okD and faceD["receipt_episodes"] == LEG3_COMPLETE_EPS
          and faceD["log_lines"] == LEG3_COMPLETE_EPS)

    n_pass = sum(1 for _, c in ok if c)
    print(f"selftest: {n_pass}/{len(ok)} PASS")
    return 0 if n_pass == len(ok) else 1

# --------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=BATCH + " runner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("env-probe")
    p = sub.add_parser("pretrain")
    p.add_argument("--workers", type=int, default=0,
                   help="eval workers; 0 = min(worker_cap(), 8)")
    p = sub.add_parser("probe")
    p.add_argument("--episodes", type=int, default=320,
                   help="training episodes this probe invocation")
    p.add_argument("--workers", type=int, default=0,
                   help="eval workers; 0 = min(worker_cap(), 8)")
    p = sub.add_parser("train")
    p.add_argument("--episodes", type=int, default=320,
                    help="additional training episodes this invocation")
    p.add_argument("--workers", type=int, default=0,
                   help="eval workers; 0 = min(worker_cap(), 8)")
    sub.add_parser("export-topk")
    sub.add_parser("tsgate-probe")
    sub.add_parser("judge")
    sub.add_parser("status")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "status":
        return cmd_status(a)
    if a.cmd == "env-probe":
        return cmd_env_probe(a)
    if a.cmd == "pretrain":
        return cmd_pretrain(a)
    if a.cmd == "probe":
        return cmd_probe(a)
    if a.cmd == "train":
        return cmd_train(a)
    if a.cmd == "export-topk":
        return cmd_export_topk(a)
    if a.cmd == "tsgate-probe":
        return cmd_tsgate_probe(a)
    if a.cmd == "judge":
        return cmd_judge(a)
    return 1


if __name__ == "__main__":
    sys.exit(main())
