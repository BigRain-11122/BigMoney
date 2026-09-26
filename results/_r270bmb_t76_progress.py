"""r270 bm-b -- T-76 progress_r270 field write-back (R254/R255/R257 five-face probing law)."""
import json
import subprocess

TICKET = "fleet/tasks/T-2026-09-26-76-P1.json"
PROGRESS = (
    "R270 bm-b face (a) DELIVERED (standing channels weekly machine-diff, wave-10 five-face closure): "
    "hibor run-5 3 new / 3 rolled (three 260925 weekly periodicals = in-corpus families, zero deep-capture; "
    "jin-gong daily absence r182 pointer stays open -> 09-28 first post-holiday daily verify at run-6), "
    "jisilu run-9 1 new / 1 rolled (516978 futures live-journal = zero methodology, no deep-capture per "
    "anti-padding law), guorn run-3 0 new / 0 rolled (11-URL set identity, byte-stable page, third consecutive "
    "zero-roll = low-frequency channel read; bm-b guorn fetch face = schannel after python urllib SSL "
    "self-signed-chain fail, one-retry channel-switch honest note); runner results/_r270bmb_facea_channels.py "
    "+ _r270bmb_guorn_roll.py; digest research/digests/DIGEST-20260926-wave10-facea-channels.md (funnel 3 "
    "harvest faces / 0 pass); wave-10 faces (a)+(b)+(c)+(d)+(e) ALL CLOSED -> ticket now awaits GM closure "
    "discretion"
)


def main():
    blob = subprocess.run(["git", "cat-file", "blob", "HEAD:" + TICKET.replace("\\", "/")],
                          capture_output=True, check=True).stdout
    bom = blob.startswith(b"\xef\xbb\xbf")
    crlf = b"\r\n" in blob
    trailing = blob.endswith(b"\n")
    txt = blob.decode("utf-8-sig")
    t = json.loads(txt)
    lines = txt.rstrip("\n").split("\n")
    indent = len(lines[1]) - len(lines[1].lstrip(" "))
    ascii_esc = "\\u" in txt.split('"claim"')[0] if '"claim"' in txt else False
    print("faces: bom=%s crlf=%s trailing_nl=%s indent=%s ensure_ascii_escaped_sample=%s"
          % (bom, crlf, trailing, indent, ascii_esc))
    t["progress_r270"] = PROGRESS
    out = json.dumps(t, ensure_ascii=False, indent=indent)
    if crlf:
        out = out.replace("\n", "\r\n")
    if trailing:
        out += "\r\n" if crlf else "\n"
    if bom:
        out = "\xef\xbb\xbf" + out
    with open(TICKET, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)
    print("written; progress_r270 len:", len(PROGRESS))


if __name__ == "__main__":
    main()
