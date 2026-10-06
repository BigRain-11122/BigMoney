# r770 bm-a probe: exact byte forms in the W155 freeze template + live tails
import io

T = open("results/_r768bma_w155_freeze_edits.py", "rb").read()
print("template bytes:", len(T))
print("CRLF count:", T.count(b"\r\n"), "LF-only count:", T.count(b"\n") - T.count(b"\r\n"))
s = T.decode("utf-8")

def show(tag, needle, span=200):
    i = s.find(needle)
    print(f"--- {tag}: find@{i}")
    if i >= 0:
        print(repr(s[i:i + span]))

# a1/a2/a3/a4 definitions
show("a1-def", "a1 = (")
show("a2-def", 'a2 = (')
show("a3-def", "a3 = ")
show("a4-def", "a4 = (")
# docstring precedent line
show("docstring-precedent", "Rev.B lesson")
# post-survived assert
show("post-survived", "row survived")
# parity block boundaries
show("parity-start", "registered row parity")
show("parity-end", "W154 row parity drift")
# sec8 / delivery texts
show("sec8", "sec8 succession")
show("delivery1", "delivery window")
show("deliv-pre", "probe receipt + W155 finalize")
show("deliv-leg", "probe receipt + W155 finalize\r")
# global-count markers
print("count '155':", s.count("155"))
print("count '153':", s.count("153"))
print("count 'len(pf.N1_BANDS) == 153':", s.count("len(pf.N1_BANDS) == 153"))
print("count 'N1_BANDS 153 rows':", s.count("N1_BANDS 153 rows"))

# live pf.py W155 row block (the a1 anchor for W156)
pf = open("scripts/perpetual_faces.py", "r", encoding="utf-8", newline="").read()
i = pf.find('    155: {"a": (355_804, 357_803), "b_exit": (357_804, 358_003),')
print("--- pf W155 row @", i)
print(repr(pf[i:i + 130]))
# live n1.py W155 shard_subdir line (a2 anchor for W156)
n1 = open("scripts/perpetual_faces_n1.py", "r", encoding="utf-8", newline="").read()
j = n1.find('"shard_subdir": "n1_w155", "out_name": "n1_w155_results.json",')
print("--- n1 W155 shard line @", j)
print(repr(n1[j - 40:j + 130]))
# live n1.py PASS snippet tail (a4 anchor region for W156)
k = n1.find('"results/_r768bma_w155_band_gate.json, law sec.4 W155 row, "')
print("--- n1 W155 PASS gate line @", k)
print(repr(n1[k - 20:k + 240]))
