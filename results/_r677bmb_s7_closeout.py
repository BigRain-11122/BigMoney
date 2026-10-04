# -*- coding: utf-8 -*-
"""r677 bm-b S7 closeout: state.json + heartbeat + round report + CODELY pit line.
Programmatic json writes with reparse self-check (r645 law); epoch int (R170/R178);
clock T-separator (R262); round report bytes-safe append (r641 newline='' law)."""
import json, time, datetime, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now().astimezone()
clock = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# --- 1. state.json (bm-b face) ---
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["machine_id"] = "bm-b"
st["round_no"] = 677
st["note"] = ("r677: W116 freeze round -- S0 netpath absorb+merge origin (bm-c r479 4-commit "
              "batch, zero UU) push DELIVERED; D-19 dual MATCH (decisions 4E5BE321 + group orders "
              "68947C17, ssh sparse-clone variant: https schannel SSL flap -> ssh first-proven-alive "
              "same-round, mkdtemp unique dirs); orders 154/154 zero-unacked (dual scan); smoke 48/48; "
              "board zero-open; satengine alive; W116 = 106th engine wave / bm-b 39th owned: seat MSG "
              "pre-push DELIVERED 4b0409196 (r565 law) + freeze five faces (canon row + pf N1_BANDS + "
              "n1 WAVE_CONFIGS + selftest W116 leg + summary + per-wave prereg) push DELIVERED "
              "bc1e82773; bands A 275_004..277_003 / B 62_701..62_900 machine-derived ADMIT (pre-seat "
              "probe + freeze-window gate dual derive identical hops 0/0, banned gate 0); anchor=W115 "
              "finalize (K=250,920, net chain head 617,548, bm-c r445 one-pass); pf 9/9 + n1 selftest "
              "PASS incl W116 materializer leg; W117+ projection A 277_004..279_003 CLEAN / B "
              "first-clean 65_050..65_249 (arith 62_901..63:100 refused at options actual + registered "
              "A-band overlap, hops=1); engine queue_depth=12 (W116 materialized), ignition held by "
              "engine RAM floor gate (3.4-3.7GB < 4.0GB floor, machine discipline, heartbeat alive, "
              "self-ignites when RAM clears); S6 38/38 rc0 (ZERO-DRIFT streak 51; bm-a heartbeat stale "
              "36min -> 4 lane faces stale-takeover by bm-b per O-2100 s2.4); trio NULLS healthy "
              "V801/Q623/D468 ETA 10-06..08; py 61.6% >= 50% accept, watermark red=false; S7 self-heal "
              "4/4 (loop pin=2 no-op, watchdog + both claws in place)")
st["last_round_at"] = clock
st["ts"] = clock
st["updated"] = clock
st["last_seen"] = clock
st["round_no_label"] = "round 677 (bm-b)"
st["clock_read"] = clock
st["last_decisions_read_at"] = clock
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
json.load(open(sp, encoding="utf-8"))  # reparse self-check
assert st["round_no"] == 677 and "T" in st["clock_read"]
print("state.json r677 written + reparsed OK")

# --- 2. heartbeat fleet/machines/bm-b.json ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["round_no"] = 677
hb["round_no_label"] = "round 677 (bm-b)"
hb["current_task"] = ("r677 close: W116 frozen (106th engine wave, bm-b 39th owned, five faces + "
                      "prereg DELIVERED bc1e82773) engine queue=12, ignition held by RAM floor gate "
                      "(3.4GB<4.0GB, self-ignites when clear); trio NULLS V801/Q623/D468 ETA 10-06..08; "
                      "next grain = W117 seat (never-dry, projection re-derive required)")
hb["verdict"] = "healthy burning"
hb["ts"] = clock
hb["updated"] = clock
hb["updated_at"] = clock
try:
    import psutil
    vm = psutil.virtual_memory()
    hb["cpu_util_pct"] = round(psutil.cpu_percent(interval=1), 1)
    hb["free_ram_gb"] = round(vm.available / 1024**3, 2)
    hb["idle_ram_gb"] = hb["free_ram_gb"]
    hb["ram_free_gb"] = hb["free_ram_gb"]
    hb["ram_avail_gb"] = hb["free_ram_gb"]
except Exception:
    pass
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
back = json.load(open(hp, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in back["clock_read"] and back["round_no"] == 677
assert back["orders_ack_count"] == 154 or len(back["orders_ack"]) == 154
print("heartbeat r677 written + reparsed OK (epoch int, orders_ack 154 intact)")

# --- 3. round report line (bytes-safe append, newline='' per r641) ---
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (f"{clock} | r677 | W116 freeze (106th engine wave / bm-b 39th owned): seat MSG-20261004-1515 "
        f"pre-push DELIVERED 4b0409196 (r565 law) + five faces + per-wave prereg DELIVERED bc1e82773; "
        f"bands A 275_004..277_003 / B 62_701..62_900 machine-derived ADMIT (pre-seat probe + freeze "
        f"gate dual-window derive identical hops 0/0, banned gate 0); anchor=W115 finalize (K=250,920, "
        f"net head 617,548); D-19 dual MATCH (ssh sparse-clone variant: https schannel SSL flap, "
        f"ssh proven alive same-round); orders 154/154 zero unacked dual scan; smoke 48/48; board "
        f"zero-open; watermark red=false py 61.6%>=50% accept; S6 38/38 rc0 ZERO-DRIFT streak 51 "
        f"(bm-a stale 36min -> 4 lane faces stale-takeover O-2100 s2.4); trio NULLS healthy ETA "
        f"10-06..08; W116 queue=12 ignition held by engine RAM floor gate (3.4-3.7GB<4.0GB machine "
        f"discipline, heartbeat alive, self-ignites when RAM clears); S7 self-heal 4/4 | "
        f"证据: seat+freeze push_verify DELIVERED x2, pf 9/9 + n1 selftest PASS (W116 leg live), gate "
        f"receipt results/_r677bmb_w116_band_gate.json, S6 log results/_r677bmb_s6_log.txt 38/38 rc0 | "
        f"下轮: W116 ignition watch (RAM floor) + W117 seat per never-dry (A 277_004..279_003 / B "
        f"65_050..65_249 projection re-derive mandatory r587) + trio continue\n")
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line)
tail = open(rp, "rb").read()[-200:]
assert b"r677" in tail, "round report append verify failed"
print("round report r677 line appended")

# --- 4. CODELY.md pit line (S4 memory, hot layer, one entry) ---
cp = os.path.join(ROOT, "CODELY.md")
pit = (f"\n- [2026-10-04 15:3x r677 bm-b] D-19 sparse-clone 通道 SSL 瞬态律：https github clone 实弹撞 "
       f"schannel SSL 握手失败（schannel: failed to receive handshake）而同窗 SSH 通道实证活（同轮 git "
       f"push 经 ssh.github.com:443 成功）——正解=clone 双 URL 跑 ssh 先（git@github.com:BigRain-11122/"
       f"FluxGroup.git 先试·https 兜底）；连带=部分 clone 失败残留目录被锁时 shutil.rmtree("
       f"ignore_errors=True) 静默不删→重试撞「destination path already exists」——tempfile.mkdtemp 每次 "
       f"唯一目录即愈（_r677bmb_d19_check.py 范式）。How to apply：D-19/水位类 sparse-clone 探针一律 ssh "
       f"先双 URL+mkdtemp 唯一目录；https SSL 失败先证伪通道勿立机制故障叙事（r641 复现律族）。\n")
with open(cp, "a", encoding="utf-8", newline="") as f:
    f.write(pit)
tailc = open(cp, "rb").read()[-120:]
assert b"r677 bm-b" in tailc, "CODELY append verify failed"
print("CODELY.md r677 pit line appended")
print("CLOSEOUT_WRITES_OK")
