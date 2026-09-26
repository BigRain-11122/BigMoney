# R260 closeout: state file + heartbeat + round report append, face-mirrored
import json, time, datetime, subprocess

now = datetime.datetime.now()
ts = now.strftime('%Y-%m-%d %H:%M:%S')
iso = now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
epoch = int(time.time())
round_no = 260

def probe(path):
    r = subprocess.run(['git', 'show', f'HEAD:{path}'], capture_output=True)
    raw = r.stdout if r.returncode == 0 else open(path, 'rb').read()
    return {'bom': raw.startswith(b'\xef\xbb\xbf'), 'crlf': raw.count(b'\r\n') > 0,
            'trailing_nl': raw.endswith(b'\n'), 'indent': 1}

# --- state-bm-a.json ---
sp = 'state-bm-a.json'
faces = probe(sp)
with open(sp, encoding='utf-8-sig') as fh:
    st = json.load(fh)
st['round_no'] = round_no
st['did'] = ("R260: T-82 deep-bcd RECEIVER LEG full arc one round (arrival R259 pointer): branch "
             "transfer/t80-deep-bcd-basis fetched @2ef23068, 6 blob byte sha256+bytes ALL MATCH sender manifest "
             "(subprocess raw capture R255 law); semantic compare vs local re-run copies 6/6 ROW-MULTISET "
             "IDENTICAL (dB/dC/x2 = line-order permutation dA paradigm; dD/x2 = LF-normalized byte-identical, "
             "R258 EOL-face law) -> 4/4 deep-shard family cross-check COMPLETE, zero divergence; local copies "
             "archived results/_r260bma_t82_deepbcd_compare/mine_* (R254 evidence-only); files landed via "
             "checkout+restore --staged gitignore-clean, post-landing LF-norm identity 6/6; receiver manifest "
             "T-2026-09-26-82-deepbcd-receiver.json written + transfer_manifest -Verify PASS exit 0 = done face "
             "TRANSFER.md s0; ticket progress_r260 note (five-face mirrored 2+/1-); receipt MSG-174x written; "
             "bm-b MSG-172x processed. s3 family census: CN-REV-TILT G1-fail + CN-REGIME-POLICY G1-fail + "
             "CN-DIV-LOWVOL-ROT negative + GRID-SLEEVE 0/5 = CN-CORE-SATELLITE is the last unbuilt s3 model. "
             "S6 22+ legs all exit 0 (weekend no-ops; moneyflow rank pass + AH refresh spawned detached legal; "
             "daily_report faces=4 token=1)")
st['verdict'] = ("GREEN R260: deep-bcd transfer CLOSED CLEAN both legs (sender r262 + receiver r260), 4/4 "
                 "deep-shard family cross-machine reproducibility gate COMPLETE (double-machine independent "
                 "re-runs agree every row x field); landed T-80 battery basis unchanged (prereg basis = pinned "
                 "paths + census + passive gates); no fabricated busywork O-1137 (pool_starvation flag honestly "
                 "answered: board clear + bandit 0 + pool 47/47 + this round real supply = receiver leg full arc)")
st['next'] = ("s3 CN-CORE-SATELLITE arc = next-round main dev (prereg->runner->pool, evidence base complete per "
              "R259: ballast=lowvol all-era + dividend defense, satellite=rotation dual-scale, regime=v3 guard; "
              "last unbuilt s3 model); 09-28 Monday new-bar chain; 10-01 monthly trio + REGIME_GUARD v3 "
              "activation window; T-70 C-arm verdict 10-09")
st['current_task'] = "T-73 s3 CN-CORE-SATELLITE arc next (last unbuilt s3 model); T-82 deep-bcd closed clean"
st['ts'] = ts; st['last_round_ts'] = ts; st['updated_at'] = ts
st['last_run'] = ts; st['last_round_at'] = ts
st['last_round'] = 'R259'; st['updated'] = ts
out = json.dumps(st, indent=1, ensure_ascii=False)
with open(sp, 'w', encoding='utf-8', newline='') as fh:
    fh.write(out + ('\n' if faces['trailing_nl'] else ''))

# --- heartbeat fleet/machines/bm-a.json ---
hp = 'fleet/machines/bm-a.json'
hf = probe(hp)
with open(hp, encoding='utf-8-sig') as fh:
    hb = json.load(fh)
hb['last_seen'] = ts
hb['current_task'] = "T-82 deep-bcd receiver leg CLOSED CLEAN R260; next = s3 CN-CORE-SATELLITE arc (last unbuilt s3 model)"
hb['verdict'] = ("GREEN R260: T-82 deep-bcd receiver leg full arc (6/6 blob sha match + 6/6 row-multiset identical "
                 "-> 4/4 deep-shard family cross-check COMPLETE; -Verify PASS; landing clean); s3 census: "
                 "CN-CORE-SATELLITE last unbuilt model next; S6 22+ legs exit 0; smoke 25/25; orders 82/82 both scans")
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = iso
hb['round_no'] = round_no
hb['task'] = ("R260 done: T-82 deep-bcd closed clean both legs; next = s3 CN-CORE-SATELLITE prereg->runner->pool "
              "arc; 09-28 new-bar chain; 10-01 trio + REGIME_GUARD v3")
out = json.dumps(hb, indent=1, ensure_ascii=False)
with open(hp, 'w', encoding='utf-8', newline='') as fh:
    fh.write(out + ('\n' if hf['trailing_nl'] else ''))

print('state+heartbeat written, epoch int check:', isinstance(hb['heartbeat_epoch_utc'], int), epoch)
