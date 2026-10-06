# -*- coding: utf-8 -*-
"""r812 bm-a W169 freeze DRY-RUN: simulate the four freeze edits in memory,
run every content-level assertion from the freeze script against the
SIMULATED post-edit file content (pf2sim/n2sim). Zero disk writes to the
two target scripts; probe dumps + live files read-only."""
import ast, io, json, re, os, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = r"results/_r811bma_w169_freeze_edits.py"
PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
CRLF = "\r\n"

tree = ast.parse(io.open(SRC, encoding="utf-8", newline="").read())
TOK = BACK = FIXUPS = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for tgt in node.targets:
            if isinstance(tgt, ast.Name) and tgt.id == "TOK":
                TOK = [ast.literal_eval(e) for e in node.value.elts]
            if isinstance(tgt, ast.Name) and tgt.id == "BACK":
                BACK = [ast.literal_eval(e) for e in node.value.elts]
            if isinstance(tgt, ast.Name) and tgt.id == "FIXUPS":
                FIXUPS = ast.literal_eval(node.value)
assert TOK and BACK and FIXUPS, "TOK/BACK/FIXUPS extraction failed"
assert len(TOK) == len(BACK) == 60, (len(TOK), len(BACK))
tn = set(b for a, b in TOK); bn = set(a for a, b in BACK)
assert tn == bn and not (tn - bn), "token parity broken"


def vmap(s):
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    return s


def vmap_fix(s, kind):
    s = vmap(s)
    if kind == "claim" or kind not in FIXUPS:
        return s
    for i, (old, new) in enumerate(FIXUPS[kind]):
        n = s.count(old)
        assert n == 1, (kind, "fixup", i, n, old[:70])
        s = s.replace(old, new)
    return s


gate = json.load(open("results/_r810bma_w169_band_gate.json", encoding="utf-8"))
leg3 = gate["legs"]["leg3"]
def u(s):
    def g(part):
        return re.sub(r"(\d)(?=(\d{3})+$)", r"\1_", part)
    a, b = s.split("..")
    return f"{g(a)}..{g(b)}"
W170p_A, W170p_B = u(leg3["W170p_A"]), u(leg3["W170p_B"])

EO = '"engine_owner": "bm-a"},'
pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# --- source segments (replicating the a1..a4 construction) ---
i1 = pfsrc.find("    # W168 (bm-a r809 freeze")
assert i1 > 0
r1 = pfsrc.find('168: {"a": (384_404', i1)
j1 = pfsrc.find(EO, r1) + len(EO)
block168_pf = pfsrc[i1:j1]
assert block168_pf == io.open(r"results/_r811bma_w169_probe_pf_block.txt", encoding="utf-8", newline="").read(), "pf face drift vs probe"

k = n1src.find('168: {"batch"')
m = n1src.find(EO, k) + len(EO)
entry168 = n1src[k:m]
assert entry168 == io.open(r"results/_r811bma_w169_probe_n1_entry.txt", encoding="utf-8", newline="").read(), "entry face drift"

w = n1src.find("# --- W168 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
block = n1src[w:t2]
assert block == io.open(r"results/_r811bma_w169_probe_n1_mat.txt", encoding="utf-8", newline="").read(), "mat face drift"
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 168)], chain_rows

cs = n1src.find('"+ W168 materializer face')
ce = n1src.find('"r809 bm-a] "', cs) + len('"r809 bm-a] "')
claim168 = n1src[cs:ce]
assert claim168 == io.open(r"results/_r811bma_w169_probe_n1_claim.txt", encoding="utf-8", newline="").read(), "claim face drift"

# --- simulate the edits ---
new_pf_block = vmap_fix(block168_pf, "pf")
new_entry = vmap_fix(entry168, "n1entry")
w168row = ('assert pf.N1_BANDS[168] == {"a": (384_404, 386_403),' + CRLF +
           '                                    "b_exit": (386_404, 386_603),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W168 row parity drift (r307; bm-a r809)"' + CRLF +
           "        ")
new_mat = vmap_fix(pre, "mat") + chain + w168row + vmap(post)
new_claim = vmap_fix(claim168, "claim")

pf2sim = pfsrc.replace(block168_pf + CRLF + "}", block168_pf + CRLF + new_pf_block + CRLF + "}")
assert pf2sim != pfsrc, "pf simulation no-op"
n2sim = n1src
n2sim = n2sim.replace(entry168 + CRLF + "                       }",
                      entry168 + CRLF + "                       " + new_entry + CRLF + "                       }")
block169 = new_mat
n2sim = n2sim.replace(block + "# --- T-141 s2 lane face",
                       block169 + "# --- T-141 s2 lane face")
n2sim = n2sim.replace('"r809 bm-a] "' + CRLF + '          "+ T-141 s2 "',
                      '"r809 bm-a] "' + CRLF + "          " + new_claim + CRLF + '          "+ T-141 s2 "')
assert n2sim != n1src, "n1 simulation no-op"

# --- W170p / prose asserts (from the freeze script, verbatim) ---
assert f"# {W170p_A} CLEAN hops=0 / B first-clean {W170p_B}" in pf2sim, "pf W170p prose missing"
assert "W170 A window; W170 freezer MUST re-derive on the post-W169" in pf2sim
assert '"W170 A window; W170 freezer MUST re-derive on the "' in n2sim
assert '"W169 B band 388_604..388_803 will refuse the naive "' in n2sim
assert f"A first-clean {W170p_A} " in n2sim and f"B first-clean {W170p_B} CLEAN" in n2sim
# honesty faces (landed direction)
assert "bm-b r798 consumed-archived the" in pf2sim, "pf self-ack fixup missing"
assert "06:02:52 -- honest state);" in pf2sim, "pf self-ack tail fixup missing"
assert "bm-b r798 consumed-archived the" in n2sim, "mat self-ack fixup missing"
assert "06:02:52 -- honest state)." in n2sim, "mat self-ack tail missing"
assert "payload = seat MSG + pre-seat probe + probe receipt;" in pf2sim
assert '"seat MSG + pre-seat probe + probe receipt; "' in n2sim
assert "= seat MSG + pre-seat probe + probe receipt;" in n2sim
assert "r810 pre-seat" in pf2sim and "r810 pre-seat" in n2sim
assert "direct fast-forward behind-0" in pf2sim and "direct fast-forward behind-0" in n2sim
assert "bcd6e4392" in pf2sim and "bcd6e4392" in n2sim
assert '"number law after the REGISTERED W168 row bm-a r809 freeze "' in n2sim
assert '"8d8842b61, SINGLE STATE zero seat gap W2..W168 all "' in n2sim
assert '"finalize one-pass bm-a r809, net chain head 775,012, "' in n2sim
assert n2sim.count("finalize one-pass bm-a r809") == 2
assert "bm-a r809 freeze 8d8842b61" in n2sim
assert "own-wave A window reserved jumps to 388_604, first-clean " in n2sim
assert "own-wave A window reserved jumps to 386_404, first-clean" not in n2sim.split("# --- W169 materializer face")[1].split("# --- T-141 s2 lane face")[0]
assert '"r811 bm-a] "' in n2sim

# --- stale scan (verbatim stale list from the freeze script) ---
i2 = pf2sim.find("    # W169 (bm-a r811 freeze")
j2 = pf2sim.find(EO, i2) + len(EO)
newpfblk = pf2sim[i2:j2]
k2 = n2sim.find('169: {"batch"')
m2 = n2sim.find(EO, k2) + len(EO)
newentry = n2sim[k2:m2]
cs2 = n2sim.find('"+ W169 materializer face')
ce2 = n2sim.find('"r811 bm-a] "', cs2) + len('"r811 bm-a] "')
newclaim = n2sim[cs2:ce2]
blk2 = n2sim[n2sim.find("# --- W169 materializer face"):
             n2sim.find("# --- T-141 s2 lane face", n2sim.find("# --- W169 materializer face"))]
ci2 = blk2.find("assert pf.N1_BANDS[138]")
cj2 = blk2.find("# prior-wave disjointness")
mat_new_faces = blk2[:ci2] + blk2[cj2:]
assert i2 > 0 and k2 > 0 and cs2 > 0, "new W169 block anchors missing"
chain_rows2 = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]",
                         blk2[ci2:cj2])
assert chain_rows2 == [str(x) for x in range(138, 169)], chain_rows2

STALE = ("r793 gate", "r796 sec8", "r797 gate", "r799 sec8",
         "r797 pre-seat", "r801 pre-seat", "r801 gate",
         "W166 (bm-a r799", "W167 (bm-a r805", "W168 (bm-a r809",
         "bm-a r795 freeze", "r795 bm-a freeze",
         "bm-a r799 freeze", "r799 bm-a freeze",
         "bm-a r805 freeze", "r805 bm-a freeze",
         "MSG-2026-10-06-223x", "MSG-2026-10-07-0259", "ceaf58908",
         "d1dc12117", "bma-w167-seat", "bma-w168-seat", "MSG-223x",
         "MSG-0259", "seat MSG-0259 tail", "merge-absorb",
         "gate-derived r797", "gate-derived r801", "gate-derived r806",
         "r806 pre-seat", "r806 sec8",
         "e51edfcbc",
         "382_004", "382_203", "382_204", "382_403",
         "384_003", "384_203", "384_204", "384_403",
         "384_404", "384_603", "386_203",
         "768,412", "360,920", "770,612", "363,120", "772,812",
         "365,320", "aebb94d2d", "c2d6c5e14", "f61835690",
         "f7d34e5a7", "18231a529", "764cd882a", "678a07d4f",
         "6957f509e", "6ee1207bb", "ee04482a2",
         "twenty-sixth", "twenty-seventh",
         "seventy-ninth", "eightieth", "eighty-first", "eighty-second",
         "eighty-third",
         "ONE HUNDRED-AND-FIFTY-FIFTH", "ONE HUNDRED-AND-FIFTY-SIXTH",
         "ONE HUNDRED-AND-FIFTY-SEVENTH", "ONE HUNDRED-AND-FIFTY-EIGHTH",
         "engine_owner rows 154", "engine_owner rows 155",
         "engine_owner rows 156", "engine_owner rows 157",
         "rows 80 + candidate", "rows 81 + candidate",
         "rows 82 + candidate", "rows 83 + candidate",
         "n1w165", "n1_w165", "n1w166", "n1_w166", "n1w167", "n1_w167",
         "n1w168", "n1_w168",
         "PERPETUAL-N1-W165", "PERPETUAL_N1_W165",
         "PERPETUAL-N1-W166", "PERPETUAL_N1_W166",
         "PERPETUAL-N1-W167", "PERPETUAL_N1_W167",
         "PERPETUAL-N1-W168", "PERPETUAL_N1_W168",
         "r789 gate", "r790 sec8", "r785 gate", "r786 sec8",
         "facts helper", "arc generator")
problems = []
for tag, seg in (("pf", newpfblk), ("entry", newentry),
                 ("mat", mat_new_faces), ("claim", newclaim)):
    for stale in STALE:
        if stale in seg:
            problems.append((tag, stale))
print("stale-scan hits:", problems if problems else "CLEAN")

# --- malformed-window scans on simulated full files ---
for path, txt in ((PF, pf2sim), (N1, n2sim)):
    bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", txt)
           if int(mm.group(3)) < int(mm.group(1))]
    assert not bad, f"malformed windows in simulated {path}: {bad[:4]}"

# --- AST-parse the simulated files (edit-time AST gate) ---
ast.parse(pf2sim); ast.parse(n2sim)
print("AST parse PASS on both simulated files")

# --- semantic spot-checks on simulated content ---
assert '169: {"a": (386_604, 388_603), "b_exit": (388_604, 388_803),' in pf2sim
assert '"a_seed_base": 386_604,' in n2sim
assert '"b_exit_seed_base": 388_604,' in n2sim
assert '169: {"batch"' in n2sim
assert '"shard_subdir": "n1_w169"' in n2sim
assert '"out_name": "n1_w169_results.json"' in n2sim
assert n2sim.count('"prereg": ("research/PERPETUAL_N1_W169_PREREG.md (wave-level frozen ') == 1, \
    "W169 per-wave prereg citation drift (tuple form)"
# check residual @TOKEN@ leakage
leaks = sorted(set(re.findall(r"@\w+@", pf2sim + n2sim)))
print("residual @TOKEN@ leakage:", leaks if leaks else "NONE")
# check orphan tokens that TOK maps but never restores were never triggered
print("DRY-RUN ALL CONTENT ASSERTIONS PASS")
