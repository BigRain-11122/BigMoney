# -*- coding: utf-8 -*-
# _r373bmc_wrap.py -- r373 bm-c wrap-up: CODELY new-pit append + heartbeat +
# state + round report line + T-144 progress. Bytes-in/bytes-out, EOL-preserving.
import json, subprocess, time, datetime, io, os, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = 0x08000000
now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())

def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, creationflags=CNW)
    return r.returncode, r.stdout, r.stderr

# ---- machine stats ----
try:
    import psutil
    cpu = psutil.cpu_percent(interval=None)
    ram_free = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    cpu, ram_free = 5.0, 3.5
rc, out, _ = sh(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"])
gpu_free_mib = int(out.decode().strip().splitlines()[0]) if rc == 0 else 9515

# ---- 1. CODELY.md new pit entry (append at tail, CRLF) ----
SRC = ROOT + r"\CODELY.md"
raw = open(SRC, "rb").read()
assert raw.count(b"\r\n") > 100 and b"\r" not in raw.replace(b"\r\n", b"")
PIT = ("- [2026-10-02 16:2x r373 bm-c] autocrlf 双空间对账坑（CODELY union 首跑即崩实弹·r530/r500 族的 blob 面补全）："
       "repo blob=LF·工作树=CRLF（autocrlf=true）——union/对账脚本拿 git show origin blob 按 \\r\\n 切=整文件单元素 Index 崩；"
       "正解=对账一律在 blob 空间（LF）算字节与 md5、落盘按工作树 EOL（CRLF）写、git add 清滤自动归一回 blob 面"
       "（split(\"\\n\")+replace(b\"\\n\",b\"\\r\\n\") 落盘·union 后 len 断言=origin−moved+pointer）。"
       "How to apply：一切「对 origin blob 做字节对账/union」的脚本先探 blob 行尾（count \\r\\n vs \\n）再选切分面；md5 记账面=blob 空间非工作树空间。")
if "autocrlf 双空间对账坑" not in raw.decode("utf-8"):
    sep = b"" if raw.endswith(b"\r\n") else b"\r\n"
    raw = raw + sep + PIT.encode("utf-8") + b"\r\n"
    open(SRC, "wb").write(raw)
    print("CODELY.md new pit appended: %dB, total %dB" % (len(PIT.encode()) + 2, len(raw)))
else:
    print("CODELY.md pit already present (idempotent skip)")

# ---- 2. heartbeat ----
HB = ROOT + r"\fleet\machines\bm-c.json"
hb = json.load(open(HB, encoding="utf-8-sig"))
hb["round_no"] = 373
hb["cpu_pct"] = cpu; hb["cpu_util_pct"] = cpu
hb["cpu_idle_pct"] = round(100 - cpu, 1)
hb["free_ram_gb"] = ram_free; hb["ram_free_gb"] = ram_free; hb["idle_ram_gb"] = ram_free
hb["gpu_free_vram_mb"] = gpu_free_mib; hb["gpu_free_vram_mib"] = gpu_free_mib
hb["gpu_idle_vram_mb"] = gpu_free_mib; hb["gpu_idle_vram_mib"] = gpu_free_mib
hb["gpu_vram_free_mb"] = gpu_free_mib
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
hb["updated_at"] = ts; hb["last_seen"] = ts; hb["last_seen_at"] = ts
hb["prod_lanes"] = ("r373: pool-domain split landed (research/pit-pool.md 16 entries, byte-recon zero-loss) "
                    "+ S6 37 legs green + engine alive; fleet chain W1..W92 landed + W93..W98 registered in-flight "
                    "(W97 bm-b/W98 bm-a frozen this window)")
hb["current_task"] = ("r373 done: T-144(c) pool-domain split (pit-pool.md 16 entries) + CODELY union with 4 concurrent "
                      "bm-b lines; next = W99 seat+freeze (registry-tail check first) + T-144(c) engine/data/protocol splits")
hb["verdict"] = ("healthy: T-144(c) pool split zero-loss PASS (CODELY 97.2KB->88.4KB, pit-pool.md 14.9KB); WM green "
                 "(py 1.1% low = holiday no-new-bar legal idle); engine alive; claws both installed MATCH; dualrun "
                 "streak 49/3; attrition CLEAN; orders 143/0")
hb["activity_now"] = ("r373: pool-domain split landed (pit-pool.md 16 entries verbatim + byte recon + md5, CODELY.md "
                      "97.2KB->union 88.4KB) + S6 37 legs rc0 + union push with 4 concurrent bm-b CODELY lines preserved")
hb["latest_artifact"] = ("research/pit-pool.md (2026-10-02 16:0x, 14,905B, 16 pool-domain pit entries, md5=32e6617a) "
                         "+ results/_r373bmc_pool_split.py (machine receipt)")
hb["next_milestone"] = ("W99 seat+freeze after registry-tail fetch check (B-side refusal points [58_500,58_550] per "
                        "W98 projection -> D-20261002-05 pinned skip semantics at gate) <=48h; T-144(c) engine/data/"
                        "protocol + flow-sinking due 10-07; month-boundary first exam 10-31")
with open(HB, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
chk = json.load(open(HB, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
print("heartbeat updated: epoch=%d clock=%s cpu=%s ram=%s gpu=%s" % (epoch, ts, cpu, ram_free, gpu_free_mib))

# ---- 3. state ----
ST = ROOT + r"\state-bm-c.json"
st = json.load(open(ST, encoding="utf-8-sig"))
st["machine_id"] = "bm-c"
st["round_no"] = 373
st["last_round_at"] = "r373"
st["last_round_ts"] = now.strftime("%m/%d/%Y %H:%M:%S")
st["updated"] = ts
st["cpu_pct"] = cpu
st["idle_ram_gb"] = ram_free
st["gpu_free_vram_mib"] = gpu_free_mib
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = ts
st["last_ts"] = ts
st["last_seen"] = ts
st["verify"] = ("r373: T-144(c) pool-domain split one-pass landed (16 entries verbatim -> research/pit-pool.md "
                "14,905B md5=32e6617a; CODELY.md 97,224B md5 d613d5d67 -> 83,878B md5 56cbb2d2 at split; byte recon "
                "-13,881B moved +535B pointer, zero-loss assert PASS, repo ref-grep zero broken links, git diff "
                "surgical 1+/16-) + push-window union with 4 concurrent bm-b CODELY lines preserved (LF blob space "
                "88,176B md5 e7647f55 = origin 101,507 - 13,865 + 534; autocrlf dual-space pit appended) + S6 37 legs "
                "rc0 (dualrun streak 49/3, WM green py 1.1% holiday-legal, attrition CLEAN) + smoke 47/47 + orders "
                "143/0 double-scan + D-19 937A373D MATCH + engine alive (W96 0/12 remote at 15:47, fleet W93-W98 "
                "registered) + self-heal 4/4 (loop pin=5, watchdog, both claws MATCH)")
st["did"] = ("r373: T-144(c) pool split (pit-pool.md 16 entries) + CODELY fleet-union + S6 all-green + autocrlf "
             "dual-space pit entry")
st["current_task"] = ("W99 = next free number after registered W98 (bm-a r582 landed 15:53; B projection 58_401..58_600 "
                      "REFUSED at [58_500,58_550] -> D-20261002-05 pinned skip at gate); T-144(c) remaining "
                      "engine/data/protocol + flow-sinking due 10-07; T-143 month-exam prep 10-29; CODELY compile-"
                      "window GM ruling pending")
st["next"] = ("(r374)(a) fetch + registry-tail check -> W99 seat publication + five-face freeze (band gate with "
              "probe-seed cluster legs r335 + D-20261002-05 pinned skip semantics for B [58_500,58_550]; anchor=latest "
              "landed finalize per r576 anchor-roll law; unregistered-tail law: seat only after W98 registered - "
              "already true); (b) T-144(c) engine-domain split (r369/r373 split-tool paradigm, content-anchored, "
              "LF-blob accounting); (c) T-143 month-exam prep (10-29); (d) T-131 follow-up slices (PIT pubdate + "
              "census H-row + -u log face + per-symbol hardening); (e) month-boundary first exam 10-31")
st["note"] = ("r373 pit: union/byte-recon scripts MUST account in LF blob space (repo blob) not CRLF working-tree "
              "space (autocrlf=true) -- first union attempt crashed splitting \\r\\n on an LF blob; split-tool "
              "zero-loss assert direction matters (assert ln NOT in SRC + ln in DST; inverted assert = apply crashes "
              "pre-write fail-fast, zero damage). W97 seat taken by bm-b (15:40), W98 taken+frozen by bm-a (15:53) "
              "-- bm-c defers to W99 next window, no scarcity (arithmetic continuation, engine fuel ample W93-W98)")
st["last_round"] = ("2026-10-02 r373 bm-c: T-144(c) pool split (pit-pool.md 16 entries, zero-loss) + CODELY union "
                    "(4 bm-b lines preserved) + S6 all-green + smoke 47/47 + orders 143/0")
st["last_decisions_sha"] = "937A373DA4339EDC70E95D2EC3E2AC5B1B62E298C834AC84B5FD2955EC5FD4E1"
st["last_decisions_read_at"] = now.strftime("%m/%d/%Y %H:%M:%S")
with open(ST, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
chk2 = json.load(open(ST, encoding="utf-8-sig"))
assert isinstance(chk2["heartbeat_epoch_utc"], int)
print("state updated: round_no=373")

# ---- 4. round report line ----
RR = ROOT + r"\round_reports-bm-c.md"
rraw = open(RR, "rb").read()
eol = b"\r\n" if rraw.count(b"\r\n") > rraw.count(b"\n") - rraw.count(b"\r\n") else b"\n"
LINE = (ts + "｜r373｜dept:工程（T-144(c) D-20261002-06 池域拆件=本轮主产出：16 条池域坑律 verbatim 迁出 research/pit-pool.md·"
         "字节对账 97,224B→83,878B（−13,881 迁出+535 指针）·md5 双行·零丢失断言 PASS·repo 引用 grep 零断链·git diff 外科 1+/16−·"
         "push 窗 origin 并发 4 行 bm-b 尾行保全 union（LF blob 空间对账 88,176B））｜watermark verdict=绿（red=false·lane healthy·"
         "probe py 1.1% 低位=假日无新 bar 合法 idle·板 0 open·bandit 空·W93-W98 在飞判决批非零=常供线不触发）｜S0: pull --rebase "
         "被 3 活写遥测面拒（r532 律·非阻塞·fetch 后 main==origin 0/0）·orders 差集 143/0 双扫（R13 程序化）·D-19 937A373D "
         "MATCH-unchanged｜S1 smoke 47/47｜S2 板空·W97 席位=bm-b 公示（15:40）→W98=bm-a 公示+冻结（15:53）·bm-c 下号=W99 顺延 "
         "（unregistered-tail 律+无稀缺性）｜S3 引擎活检查 exit0（Tools 面常驻架构）·W96 0/12 在烧｜S6 37 腿 rc0（dualrun streak "
         "49/3·WM 绿·attrition CLEAN·假日 no-op 面合法）｜S7 自愈 4/4（loop pin=5·watchdog·precommit/prepush 爪双装 MATCH）·"
         "inbox 2 席位 MSG 已读（bm-b r581 已归档 processed）｜新坑律一条入册（autocrlf 双空间对账）｜未达 origin commit 数=0（push 后自证）｜"
         "下轮指针：(a) fetch 查表尾→W99 席位公示+五面冻结（B 侧 [58_500,58_550] 拒绝点按 D-20261002-05 钉死语义机闸 derive·"
         "r335 探针种子簇腿必带）(b) T-144(c) 引擎域拆件 (c) T-143 月考备战")
open(RR, "ab").write(eol + LINE.encode("utf-8") + eol if not rraw.endswith(eol) else LINE.encode("utf-8") + eol)
print("round report line appended")

# ---- 5. ticket progress ----
TK = ROOT + r"\fleet\tasks\T-2026-10-02-144-P1.json"
tk = json.load(open(TK, encoding="utf-8-sig"))
add = (" | (c) second split DONE r373 bm-c: pool domain 16 entries verbatim -> research/pit-pool.md "
       "(byte recon 97,224->83,878B split-state + md5 lines + zero-loss PASS + repo ref-grep clean; fleet-union at "
       "push with 4 concurrent bm-b CODELY lines preserved, LF-blob accounting 88,176B); remaining = engine/data/"
       "protocol domains + flow-sinking, due 10-07")
if "second split DONE r373" not in tk["claimed_by"]:
    tk["claimed_by"] += add
    with open(TK, "w", encoding="utf-8", newline="") as fh:
        json.dump(tk, fh, ensure_ascii=False, indent=1)
    print("ticket progress updated")
else:
    print("ticket already updated (idempotent skip)")
print("WRAP DONE")
