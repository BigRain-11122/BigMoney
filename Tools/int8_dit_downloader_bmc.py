# -*- coding: utf-8 -*-
# int8 DiT parallel downloader for bm-c (ModelScope channel, 8-segment ranged, resume-capable)
# CEO order O-20261010-11xx: install minimax_h3_fl2va_pruned_int8_convrot.safetensors (~21GB)
import os, sys, time, threading, urllib.request, struct

URL = 'https://modelscope.cn/models/Comfy-Org/MiniMax-H3/resolve/master/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors'
TOTAL = 20970379616  # bytes (verified via Content-Range probe 2026-10-10)
PARTS_DIR = r'D:\ComfyUI\ComfyUI\models\_h3_parts\int8'
FINAL = r'D:\ComfyUI\ComfyUI\models\diffusion_models\minimax_h3_fl2va_pruned_int8_convrot.safetensors'
NSEG = 8
LOG = r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r829bmc_int8_dl.log'

def log(msg):
    line = '%s %s' % (time.strftime('%H:%M:%S'), msg)
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def seg(idx):
    part = os.path.join(PARTS_DIR, 'part%d' % idx)
    lo = TOTAL * idx // NSEG
    hi = TOTAL * (idx + 1) // NSEG - 1
    want = hi - lo + 1
    have = os.path.getsize(part) if os.path.exists(part) else 0
    if have >= want:
        log('seg%d already complete (%d)' % (idx, have))
        return
    t0 = time.time()
    while True:
        try:
            req = urllib.request.Request(URL, headers={'Range': 'bytes=%d-%d' % (lo + have, hi)})
            r = urllib.request.urlopen(req, timeout=60)
            with open(part, 'ab') as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
                    have += len(chunk)
            break
        except Exception as e:
            have = os.path.getsize(part) if os.path.exists(part) else 0
            log('seg%d retry at %d: %s' % (idx, have, str(e)[:100]))
            time.sleep(3)
    dt = time.time() - t0
    log('seg%d done %d bytes in %.0fs (%.1f MB/s)' % (idx, have, dt, have / dt / 1e6 if dt > 0 else 0))

def main():
    os.makedirs(PARTS_DIR, exist_ok=True)
    if os.path.exists(FINAL) and os.path.getsize(FINAL) == TOTAL:
        log('FINAL already present with correct size, nothing to do')
        return
    log('download start total=%d nseg=%d' % (TOTAL, NSEG))
    ths = [threading.Thread(target=seg, args=(i,), daemon=True) for i in range(NSEG)]
    for t in ths: t.start()
    for t in ths: t.join()
    sizes = [os.path.getsize(os.path.join(PARTS_DIR, 'part%d' % i)) for i in range(NSEG)]
    if sum(sizes) != TOTAL or any(s != (TOTAL * (i + 1) // NSEG - TOTAL * i // NSEG) for i, s in enumerate(sizes)):
        log('SIZE MISMATCH parts=%s' % sizes)
        sys.exit(2)
    with open(FINAL, 'wb') as out:
        for i in range(NSEG):
            with open(os.path.join(PARTS_DIR, 'part%d' % i), 'rb') as f:
                while True:
                    chunk = f.read(1 << 22)
                    if not chunk: break
                    out.write(chunk)
    fs = os.path.getsize(FINAL)
    with open(FINAL, 'rb') as f:
        hdr = f.read(8)
        hlen = struct.unpack('<Q', hdr)[0]
    ok = fs == TOTAL and 0 < hlen < 100_000_000
    log('FINAL assembled size=%d (expect %d) safetensors_header_len=%d -> %s' % (fs, TOTAL, hlen, 'OK' if ok else 'BAD'))
    if not ok:
        sys.exit(3)
    for i in range(NSEG):
        os.remove(os.path.join(PARTS_DIR, 'part%d' % i))
    log('ALL DONE')

if __name__ == '__main__':
    main()
