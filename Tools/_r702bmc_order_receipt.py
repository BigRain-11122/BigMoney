"""r702 bm-c order receipt: O-20261007-2145-bm-c resume broadcast.
bm-c = issuing machine (interactive session did machine-state v4 resume at
21:2x); per order sec.1.2 the never-paused/sender machine replies one line
"no-op running". Bookkeeping: heartbeat orders_ack append (168->169) +
round report receipt line. Pattern: _r701bmc_close.py EOL-preserving."""
import datetime as _dt
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
ORDER = "O-20261007-2145-bm-c.md"

now = time.time()
now_iso = _dt.datetime.fromtimestamp(now).astimezone().isoformat(timespec="seconds")


def load_json_raw(p):
    raw = open(p, 'rb').read()
    return json.loads(raw.decode('utf-8-sig')), raw


def eol_of(raw):
    return b'\r\n' if b'\r\n' in raw[:4000] else b'\n'


def dump_json(obj, raw, p):
    eol = eol_of(raw)
    data = (json.dumps(obj, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    if eol == b'\r\n':
        data = data.replace(b'\n', b'\r\n')
    open(p, 'wb').write(data)


hb, hb_raw = load_json_raw(HB)
ack = hb.get("orders_ack", [])
if ORDER not in ack:
    ack.append(ORDER)
hb["orders_ack"] = ack
hb["ts"] = now_iso
dump_json(hb, hb_raw, HB)
chk = json.loads(open(HB, 'rb').read().decode('utf-8-sig'))
assert ORDER in chk["orders_ack"] and len(chk["orders_ack"]) == 169
print("heartbeat orders_ack ok: 168->169 (appended %s)" % ORDER)

row = (now_iso + " | r702 bm-c order receipt | O-20261007-2145-bm-c 全面开工全员复原广播令：本机=说令机→回执 no-op running "
       "（issuing session 已 machine-state v4 resume·六任务 Enabled·cron 5/5·qwen3.6-coder:35b 常驻 pin·ComfyUI 复启；"
       "OS loop 全程未停=r702 本轮即活证；Ollama 0.40.0 resume 首载 GPU 误判窗坑录已知悉·issuing session 已处置 13.1GB 上卡 ~63 tok/s） "
       "| orders_ack 168→169 | 收令时点=S7 close 双扫捕获（round-start 扫后 ~21:45 落令·pre-push 爪首次拦截即此令面·rebase 收编后爪净）")

rr_raw = open(RR, 'rb').read()
eol = b'\r\n' if b'\r\n' in rr_raw[-2000:] else b'\n'
row_b = row.encode('utf-8')
if eol == b'\r\n':
    row_b = row_b.replace(b'\n', b'\r\n')
if not rr_raw.endswith(eol):
    rr_raw += eol
open(RR, 'ab').write(row_b + eol)
new_raw = open(RR, 'rb').read()
assert new_raw == rr_raw + row_b + eol, 'round report append mismatch'
print("round report ok: order receipt line appended (%dB)" % len(row_b))
