# -*- coding: utf-8 -*-
# _r1010bmc_wave2_harvest.py -- O-20261014-1855 wave2 harvest face (post-runner window)
# Gates: (0) all 39 SAVED else exit 2; (1) canonical URL per slot (prefer _w2r1010/_w2r1008/exact tag rows,
#   HEAD Content-Length == local bytes); (2) repair slots with no canonical (raw file_upload+PUT under
#   <sid>_w2r1010, byte-verify, append INDEX row) -- INDEX-SKIP law: byte-level URL-local identity is
#   the only delivery proof; (3) final verify 39/39 byte-identical -> receipt with canonical map for
#   bm-a assembly; (4) q88 contact board (ffmpeg mid-frame x39 -> PIL grid).
# Race-safety: NEVER touches wave2_r998_progress.json (runner owns it while alive).
import io, json, os, re, ssl, subprocess, sys, time, urllib.request

HERE = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012"
sys.path.insert(0, HERE)
sys.path.insert(0, r"K:\Fluxgroup\FluxGroup\quant\bigmoney\.codely-cli\scratch\meme_v1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

BMC = os.path.join(HERE, "bmc")
I2V = os.path.join(BMC, "i2v")
IDX = os.path.join(BMC, "I2V-URL-INDEX.md")
PROG = os.path.join(BMC, "wave2_r998_progress.json")
OUT = os.path.join(BMC, "wave2_harvest_r1010.json")
BOARD = os.path.join(BMC, "wave2_qc_sheet_r1010.jpg")
TAG = "_w2r1010"

ssl_ctx = ssl.create_default_context()

def head_len(url, timeout=30):
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as r:
        return int(r.headers.get("Content-Length", "-1"))

def index_rows():
    """Return list of (tag, url) in file order (later rows win on same tag)."""
    rows = []
    rx = re.compile(r"^\|\s*([^|]+?)\s*\|\s*[^|]*?\s*\|\s*(https?://\S+?)\s*\|")
    for line in io.open(IDX, encoding="utf-8"):
        m = rx.match(line)
        if m:
            rows.append((m.group(1).strip(), m.group(2).strip()))
    return rows

def main():
    prog = json.load(io.open(PROG, encoding="utf-8"))
    shots = prog["shots"]
    not_saved = sorted(k for k, v in shots.items() if not (isinstance(v, dict) and v.get("status") == "SAVED"))
    if not_saved:
        print("GATE-FAIL pending=%d: %s" % (len(not_saved), ",".join(not_saved)))
        sys.exit(2)

    rows = index_rows()
    by_tag = {}
    for tag, url in rows:
        by_tag[tag] = url

    report = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "total": len(shots),
              "canonical": {}, "repaired": {}, "failed": {}, "verify_all": {}}

    # Phase 1: canonical resolution
    need_repair = []
    for sid in sorted(shots):
        p = os.path.join(I2V, sid + ".mp4")
        local = os.path.getsize(p)
        canon = None
        for cand in (sid + TAG, sid + "_w2r1008", sid):
            url = by_tag.get(cand)
            if not url:
                continue
            try:
                if head_len(url) == local:
                    canon = url
                    break
            except Exception:
                continue
        if canon:
            report["canonical"][sid] = {"url": canon, "bytes": local}
        else:
            need_repair.append(sid)
    print("phase1 canonical=%d need_repair=%d -> %s" % (len(report["canonical"]), len(need_repair), ",".join(need_repair)))

    # Phase 2: repair (raw upload under fresh tag)
    if need_repair:
        import tj_mcp
        if not getattr(tj_mcp, "session_id", None):
            tj_mcp.initialize()
        for sid in need_repair:
            p = os.path.join(I2V, sid + ".mp4")
            local = os.path.getsize(p)
            tag = sid + TAG
            ok_url = None
            for attempt in (1, 2, 3):
                try:
                    res = tj_mcp.call_tool("file_upload", {"file_path": p}, timeout=120)
                    rec = None
                    for c in res.get("content", []):
                        if c.get("type") == "resource":
                            try:
                                rec = json.loads(c["resource"]["text"])
                            except Exception:
                                rec = None
                    if not rec or not rec.get("upload_url"):
                        if rec and rec.get("already_uploaded") and rec.get("file_url"):
                            ok_url = rec["file_url"]
                            break
                        print("[%s] no upload_url a%d: %s" % (tag, attempt, json.dumps(res)[:120]))
                        time.sleep(3)
                        continue
                    data = io.open(p, "rb").read()
                    req = urllib.request.Request(rec["upload_url"], data=data,
                                                 headers={"Content-Type": "application/octet-stream"}, method="PUT")
                    with urllib.request.urlopen(req, timeout=300) as r:
                        if r.status != 200:
                            print("[%s] PUT %d" % (tag, r.status))
                            time.sleep(2)
                            continue
                    ok_url = rec.get("file_url")
                    break
                except Exception as ex:
                    if "session" in str(ex).lower():
                        tj_mcp.session_id = None
                        try:
                            tj_mcp.initialize()
                        except Exception:
                            pass
                    print("[%s] exc a%d: %r" % (tag, attempt, ex))
                    time.sleep(3)
            if not ok_url:
                report["failed"][sid] = "upload failed after retries"
                continue
            try:
                if head_len(ok_url) != local:
                    report["failed"][sid] = "byte mismatch after put"
                    continue
            except Exception as ex:
                report["failed"][sid] = "HEAD exc: %r" % ex
                continue
            with io.open(IDX, "a", encoding="utf-8") as f:
                f.write("| %s | %.1fMB | %s |\n" % (tag, local / 1048576.0, ok_url))
            report["repaired"][sid] = {"url": ok_url, "bytes": local, "tag": tag}
            report["canonical"][sid] = {"url": ok_url, "bytes": local}
            print("[%s] REPAIRED %d bytes" % (tag, local))

    if report["failed"]:
        print("REPAIR-FAIL: %s" % ",".join(report["failed"]))
        tmp = OUT + ".tmp"
        io.open(tmp, "w", encoding="utf-8").write(json.dumps(report, ensure_ascii=False, indent=1))
        os.replace(tmp, OUT)
        sys.exit(3)

    # Phase 3: final verify all 39 canonical URLs byte-identical
    vm = 0
    bad = []
    for sid, c in sorted(report["canonical"].items()):
        try:
            if head_len(c["url"]) == c["bytes"]:
                vm += 1
                report["verify_all"][sid] = "OK"
            else:
                bad.append(sid)
                report["verify_all"][sid] = "LEN-MISMATCH"
        except Exception as ex:
            bad.append(sid)
            report["verify_all"][sid] = "HEAD-EXC %r" % ex
    report["verified_count"] = vm
    tmp = OUT + ".tmp"
    io.open(tmp, "w", encoding="utf-8").write(json.dumps(report, ensure_ascii=False, indent=1))
    os.replace(tmp, OUT)
    print("phase3 verify %d/%d" % (vm, len(report["canonical"])))
    if vm != len(shots):
        print("VERIFY-FAIL: %s" % ",".join(bad))
        sys.exit(4)

    # Phase 4: q88 contact board (mid-frame of each clip, 7-col grid)
    from PIL import Image, ImageDraw
    sids = sorted(shots)
    cols, tw, th, pad = 7, 266, 150, 14
    rows_n = (len(sids) + cols - 1) // cols
    W = cols * (tw + pad) + pad
    H = rows_n * (th + 22 + pad) + pad + 30
    board = Image.new("RGB", (W, H), (18, 16, 14))
    d = ImageDraw.Draw(board)
    d.text((pad, 6), "wave2 harvest 39/39 byte-verified -- r1010 bm-c -- %s" % report["ts"], fill=(240, 200, 120))
    tmpd = os.path.join(BMC, "_thumb_tmp_r1010")
    os.makedirs(tmpd, exist_ok=True)
    for i, sid in enumerate(sids):
        r_, c_ = divmod(i, cols)
        x = pad + c_ * (tw + pad)
        y = pad + 30 + r_ * (th + 22 + pad)
        tf = os.path.join(tmpd, sid + ".png")
        if not os.path.isfile(tf):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "2.5", "-i",
                            os.path.join(I2V, sid + ".mp4"), "-frames:v", "1", "-vf",
                            "scale=%d:%d,setsar=1" % (tw, th), tf], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.isfile(tf):
            try:
                im = Image.open(tf).convert("RGB")
                board.paste(im, (x, y))
            except Exception:
                pass
        d.text((x, y + th + 3), sid, fill=(200, 200, 200))
    board.save(BOARD, "JPEG", quality=88)
    print("phase4 board -> %s" % BOARD)
    print("HARVEST-DONE 39/39 verified=%d repaired=%d board=%s" %
          (vm, len(report["repaired"]), os.path.basename(BOARD)))

if __name__ == "__main__":
    main()
