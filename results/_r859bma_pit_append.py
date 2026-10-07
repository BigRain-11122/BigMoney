import io

# --- pit 1: pool enrollment surgical method (pit-pool-edit.md) ---
P1 = r'research/pit-pool-edit.md'
entry1 = (
"\r\n- [2026-10-08 03:3x r859 bm-a] **池新条目登记双法坑（submit=门禁验证器非写入器 + 插入串写前 parse 门）**：正法登记流程="
"① python Tools/autofill.py submit 过全部门禁（重复 id/多核门 O-2355/consumer_plan 必填/inbox_guard D-20260929-02 rival 冻结门）拿到合格 entry 内容→"
"② git checkout 回滚 submit 的 ensure_ascii 转义写面（本窗 46 行 CJK 面被 \\uXXXX 重写=r509 外科超限实弹）→"
"③ raw-text 定点插入（宿主格式=条目 2 空格开闭+3 空格字段+CRLF+raw CJK；尾锚 \\r\\n  }\\r\\n ]\\r\\n} 唯一性断言；字段行间逗号+末字段去尾逗号）。"
"本窗两连炸实弹=块构造 join 漏字段逗号+尾锚自带 } 双闭合，写后才 parse 发现=16 秒坏窗喂了 daemon 一次 pool_unreadable fault（r629 60s 自愈窗再现）——"
"铁律=插入串构造后先 json.loads(new) 验证再落盘，禁写后验证。另 claim_lost_yield=登记未到 origin 的合法让路（daemon 认领门读 origin refs、origin_sha=null 诚实 yield），"
"登记 commit+push 后下 tick 自认——非故障勿重试器械。How to apply：一切池登记=submit 门禁验证+外科写入双腿；插入前 parse 门必先行；写后 diff --numstat 外科断言（本窗 16+/1- 达标）。"
)
with io.open(P1, 'a', encoding='utf-8', newline='') as fh:
    fh.write(entry1)
print('pit-pool-edit appended:', len(entry1.encode('utf-8')), 'B')

# --- pit 2: MSG sender attribution contract (pit-protocol.md) ---
P2 = r'research/pit-protocol.md'
entry2 = (
"\r\n- [2026-10-08 03:3x r859 bm-a] **inbox_guard 发件人归属双形式契约（r859 实弹）**：本机池登记前的 MSG 公示若命名/body 不契约→submit 门 D-20260929-02 把自家 MSG 判成 unknown 发件人的 rival 宣告=自己冻结自己（REFUSED rival declaration freeze）。"
"契约双形式任一即可归属：① 文件名 MSG-YYYYMMDD-HHMM-<sender>-(ALL|all)-<topic>.md（inbox_guard.MSG_NAME_PAT 正则）；② 正文含行首「发件[:：]<machine_id>」（SENDER_PAT=发件[:：]\\s*([A-Za-z0-9-]+)）——"
"本窗实弹 -bma-w16screen-seat.md 无 ALL 段+无 发件 行=双漏→改名 -bma-ALL-+补 发件 行即通。How to apply：一切要过 inbox_guard 认领冻结门的公示 MSG（池席位/开烧/切片宣告）发布前自检双形式。"
)
with io.open(P2, 'a', encoding='utf-8', newline='') as fh:
    fh.write(entry2)
print('pit-protocol appended:', len(entry2.encode('utf-8')), 'B')
