# -*- coding: utf-8 -*-
"""Audio work-order runner (T-92 s3 intake lane, bm-b standing production lane).

Consumes ONE work-order JSON (audio-queue incoming face, art-queue precedent
adapted to audio) and renders all jobs through the X989 mastered-audio chain
(14-hao L0 law; chain functions are the r316-proven recipe, verbatim).

Order schema (fields per T-92 ticket: kind/n_seeds/out_dir/style adapted):
  id          order id (required, unique)
  project     free text (required)
  out_dir     target dir for rendered assets + manifest (required)
  style       order-level default class: sfx|bgm|amb|voice (optional)
  n_seeds     order-level default take count for voice jobs (optional, default 1)
  jobs[]:
    voice   {name, kind="voice", text, voice?, style?, n_seeds?}
            -> piper TTS render x n_seeds takes -> mastered chain
    master  {name, kind="master", input_file, style?}
            -> existing audio file -> mastered chain

Class loudness targets (14-hao L0-1 verbatim): sfx=-16 bgm=-18 amb=-20
voice=-16 LUFS, tol +-1.0 LU; TP window [-14,-3] dBTP (L0-2); carrier
44100 Hz mono s16 (L0-4). Job names SHOULD carry the class prefix
(sfx_/bgm_/amb_) for AudioGateCheck class-window compliance.

Evidence (L0-8): per-order manifest.json in out_dir with tool/LUFS/TP/
bytes/MD5/lineage per clip. Exit codes: 0 = all jobs in-spec; 2 = any job
out-of-spec or mechanism failure (worker then moves the order to failed/
-- honest red, per the r316 case-B law: unattainable material is remade on
the L3/L4 human track, NOT forced through).

Machine-direct law U187/U240: engines are local installs (piper/ffmpeg),
no git, no cross-machine transfer.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

PIPER = r"E:\Minigame\Tools\tts\piper\piper\piper.exe"
VOICES = Path(r"E:\Minigame\Tools\tts\voices")
FFMPEG = r"E:\Minigame\Tools\ffmpeg\bin\ffmpeg.exe"
FFPROBE = r"E:\Minigame\Tools\ffmpeg\bin\ffprobe.exe"
DEFAULT_VOICE = "zh_CN-huayan-medium"

TARGETS = {"sfx": -16.0, "bgm": -18.0, "amb": -20.0, "voice": -16.0}  # 14-hao L0-1 verbatim
TOL_LU = 1.0
TP_MAX, TP_MIN = -3.0, -14.0


def run(cmd, inp=None, timeout=300):
    p = subprocess.run(cmd, input=inp, capture_output=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def measure(path):
    """pass-1 mono-first measure via loudnorm print_format=json (r315/r316 proven)."""
    rc, _, err = run([FFMPEG, "-hide_banner", "-i", str(path),
                      "-af", "aformat=channel_layouts=mono,loudnorm=print_format=json",
                      "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", err.decode("utf-8", "replace"), re.S)
    if not m:
        raise RuntimeError(f"loudnorm json not found for {path}: {err[-500:]!r}")
    j = json.loads(m.group(0))
    return float(j["input_i"]), float(j["input_tp"]), float(j["input_lra"])


def apply_master(src, dst, target_i, measured_i, measured_tp, measured_lra):
    """pass-2 mono-first + loudnorm linear to class target, 44.1k mono s16 wav."""
    af = (f"aformat=channel_layouts=mono,"
          f"loudnorm=I={target_i}:TP=-3:LRA=11:"
          f"measured_I={measured_i}:measured_TP={measured_tp}:measured_LRA={measured_lra}:linear=true")
    rc, _, err = run([FFMPEG, "-hide_banner", "-y", "-i", str(src),
                      "-af", af, "-ar", "44100", "-sample_fmt", "s16", str(dst)])
    if rc != 0:
        raise RuntimeError(f"master apply failed: {err[-500:]!r}")


def iterate_master(src, dst, target_i, max_iters=3):
    """Crest-conflict re-normalization loop (r316 case-A live-fire proven):
    each loudnorm pass limiter-trims the crest, re-measure+re-apply converges;
    honest red after max_iters (unattainable material -> remake track)."""
    iters = []
    cur = Path(str(dst) + ".it0")
    cur.write_bytes(Path(src).read_bytes())
    for it in range(1, max_iters + 1):
        mi, mtp, mlra = measure(cur)
        apply_master(cur, dst, target_i, mi, mtp, mlra)
        i, tp = ebur128(dst)
        ok = abs(i - target_i) <= TOL_LU and TP_MIN <= tp <= TP_MAX
        iters.append({"iter": it, "in_i": round(mi, 2), "in_tp": round(mtp, 2),
                      "out_i": round(i, 2), "out_tp": round(tp, 2), "ok": ok})
        if ok:
            break
        cur = Path(str(dst) + f".it{it}")
        cur.write_bytes(Path(dst).read_bytes())
    for p in dst.parent.glob(dst.name + ".it*"):
        p.unlink(missing_ok=True)
    return iters


def ebur128(path):
    """ebur128 integrated + true peak (same instrument face as AudioGateCheck L0-1/L0-2)."""
    rc, _, err = run([FFMPEG, "-hide_banner", "-i", str(path),
                      "-af", "ebur128=peak=true", "-f", "null", "-"])
    s = err.decode("utf-8", "replace")
    i = re.search(r"Integrated loudness:\s*I:\s*(-?[0-9.]+) LUFS", s)
    tp = re.search(r"True peak:\s*Peak:\s*(-?[0-9.]+) dBFS", s)
    if not i or not tp:
        raise RuntimeError(f"ebur128 parse failed for {path}")
    return float(i.group(1)), float(tp.group(1))


def probe(path):
    rc, out, _ = run([FFPROBE, "-v", "error",
                      "-show_entries", "stream=sample_rate,channels",
                      "-show_entries", "format=duration",
                      "-of", "default=nw=1:nk=1", str(path)])
    lines = [l for l in out.decode().splitlines() if l.strip()]
    return int(lines[0]), int(lines[1]), float(lines[-1])


def class_target(style, order_default):
    cls = style or order_default
    if cls not in TARGETS:
        raise ValueError(f"unknown style/class {cls!r} (valid: {sorted(TARGETS)})")
    return cls, TARGETS[cls]


def render_voice(job, order_default_style, order_default_seeds, workdir):
    """piper TTS render x n_seeds takes (per-render verdicts; piper is
    non-deterministic run-to-run -- r316 finding f1, md5 is the record)."""
    text = job.get("text")
    if not text:
        raise ValueError(f"voice job {job.get('name')!r}: 'text' required")
    voice = job.get("voice") or DEFAULT_VOICE
    onnx = VOICES / (voice + ".onnx")
    if not onnx.exists():
        raise ValueError(f"voice model not found: {onnx}")
    n_seeds = int(job.get("n_seeds", order_default_seeds))
    raws = []
    for k in range(1, n_seeds + 1):
        raw = workdir / f"{job['name']}_take{k}.raw.wav"
        rc, _, err = run([PIPER, "--model", str(onnx), "--output_file", str(raw)],
                         inp=text.encode("utf-8"), timeout=180)
        if rc != 0 or not raw.exists():
            raise RuntimeError(f"piper render failed (take {k}): {err[-400:]!r}")
        raws.append((k, raw))
    return raws


def main():
    if len(sys.argv) != 2:
        print("usage: audio_render_order.py <order.json>")
        return 3
    order_path = Path(sys.argv[1])
    order = json.loads(order_path.read_text(encoding="utf-8-sig"))

    for f in ("id", "project", "out_dir"):
        if not order.get(f):
            print(f"order validation FAIL: field {f!r} required")
            return 2
    jobs = order.get("jobs") or []
    if not jobs:
        print("order validation FAIL: jobs[] empty")
        return 2
    seen = set()
    for j in jobs:
        if j.get("name") in seen:
            print(f"order validation FAIL: duplicate job name {j.get('name')!r}")
            return 2
        seen.add(j.get("name"))

    out_dir = Path(order["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    workdir = out_dir / "_work"
    workdir.mkdir(exist_ok=True)
    default_style = order.get("style", "sfx")
    default_seeds = int(order.get("n_seeds", 1))

    recs, all_pass = [], True
    for job in jobs:
        kind = job.get("kind")
        name = job["name"]
        cls, target_i = class_target(job.get("style"), default_style)
        try:
            if kind == "voice":
                raws = render_voice(job, default_style, default_seeds, workdir)
                multi = len(raws) > 1
                for k, raw in raws:
                    stem = f"{name}_seed{k}" if multi else name
                    dst = out_dir / f"{stem}.wav"
                    iters = iterate_master(raw, dst, target_i)
                    i, tp = ebur128(dst)
                    r, c, d = probe(dst)
                    ok = abs(i - target_i) <= TOL_LU and TP_MIN <= tp <= TP_MAX and r == 44100 and c == 1
                    all_pass &= ok
                    recs.append({"job": name, "take": k, "kind": "voice", "class": cls,
                                 "target_lufs": target_i, "measured_lufs": round(i, 2),
                                 "measured_tp": round(tp, 2), "sample_rate": r, "channels": c,
                                 "duration_sec": round(d, 3), "bytes": dst.stat().st_size,
                                 "md5": md5_of(dst), "chain_iterations": iters,
                                 "file": str(dst), "verdict": "PASS" if ok else "FAIL"})
                    print(f"{stem}: I={i:.2f} (t={target_i}) TP={tp:.2f} {r}Hz ch{c} "
                          f"iters={len(iters)} -> {'PASS' if ok else 'FAIL'}")
                    raw.unlink(missing_ok=True)
            elif kind == "master":
                src = Path(job["input_file"])
                if not src.exists():
                    raise ValueError(f"master job {name!r}: input_file not found: {src}")
                dst = out_dir / f"{name}.wav"
                iters = iterate_master(src, dst, target_i)
                i, tp = ebur128(dst)
                r, c, d = probe(dst)
                ok = abs(i - target_i) <= TOL_LU and TP_MIN <= tp <= TP_MAX and r == 44100 and c == 1
                all_pass &= ok
                recs.append({"job": name, "kind": "master", "class": cls,
                             "source": str(src), "source_md5": md5_of(src),
                             "target_lufs": target_i, "measured_lufs": round(i, 2),
                             "measured_tp": round(tp, 2), "sample_rate": r, "channels": c,
                             "duration_sec": round(d, 3), "bytes": dst.stat().st_size,
                             "md5": md5_of(dst), "chain_iterations": iters,
                             "file": str(dst), "verdict": "PASS" if ok else "FAIL"})
                print(f"{name}: I={i:.2f} (t={target_i}) TP={tp:.2f} {r}Hz ch{c} "
                      f"iters={len(iters)} -> {'PASS' if ok else 'FAIL'}")
            else:
                raise ValueError(f"job {name!r}: unknown kind {kind!r} (valid: voice|master)")
        except Exception as e:  # honest red: order goes to failed/ with the reason recorded
            all_pass = False
            recs.append({"job": name, "kind": kind, "error": str(e)[:400], "verdict": "FAIL"})
            print(f"{name}: ERROR {e}")

    manifest = {
        "order_id": order["id"], "project": order.get("project"),
        "order_file": order_path.name, "date": order.get("date"),
        "law": "X989 mastered-audio (14-hao L0-1/-2/-4/-8 verbatim): "
               "sfx=-16 bgm=-18 amb=-20 voice=-16 LUFS tol+-1.0, TP in [-14,-3], 44100Hz mono s16",
        "chain": "piper TTS (voice jobs) / source file (master jobs) -> ffmpeg mono-first "
                 "(kenglu #212) + loudnorm two-pass linear (I=<class target> TP=-3 LRA=11) "
                 "-> -ar 44100 -sample_fmt s16; crest-conflict re-normalization loop <=3 iters",
        "jobs": recs,
        "all_pass": bool(all_pass),
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"MANIFEST: {out_dir / 'manifest.json'}")
    print(f"ALL_PASS: {manifest['all_pass']}")
    return 0 if all_pass else 2


if __name__ == "__main__":
    sys.exit(main())
