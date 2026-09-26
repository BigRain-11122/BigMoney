---
name: bigmoney-conflict-resolve
description: BigMoney 机队跨机 git push/rebase 冲突正典解法（多机共享仓 UU/AA 批量冲突分类+配方路由）。Use when git pull --rebase 或 git push 在 BigMoney 仓撞冲突（non-fast-forward 拒绝、rebase UU 状态面、同窗双机 push 撞车批量 UU），需按文件形态选择 union/take-new/锚前插增等正典配方零丢失解决；或处理 rebase 重放撞未跟踪同路径件、orders_ack 差集、HANDOVER/digest 撞头。覆盖 r161/r176/r185/r188/r203/R208/R209/R210/r220 实弹坑律族。
---

# BigMoney 跨机冲突正典解法（bigmoney-conflict-resolve）

多机（bm-a/bm-b/bm-c）同仓并发 push 的冲突解正典。配方全部来自实弹坑律族（律锚见各条），分类先于解——**先跑分类器再动手**：

```
python tools/skills/bigmoney-conflict-resolve/scripts/classify_conflicts.py
```

输出逐件分类+推荐配方（exit 2=有 UNKNOWN 件=禁盲解、逐件手工定性）。分类器零网络零 LLM 确定性；selftest 子命令=离线自检 16 例。

## 一、触发与红线（先读）

1. **触发面**：S7 push 被拒（non-fast-forward）→ `git pull --rebase` 后 UU/AA 批量；或 rebase 中途重放撞车。轮首 S0 的 pull --rebase 冲突=按 OS 轮令转只读维护退避，**禁解**（例外=push-rejection 时的撞车批，多轮正典实践允许按下述配方解）。
2. **红线**：禁 force-push；解冲突失败=推 `origin machine/<id>-r<N>` 分支；禁 abort 重来（已解冲突白费，r220 律）。
3. **读面纪律**：诊断/读原始串一律 `repr` 先行；**禁 PowerShell `>` 重定向读编码敏感件**（产 UTF-16 BOM 伪影误导定因，r209 律）——读 git 对象用 subprocess bytes。

## 二、文件形态判别（分类器输出即此表）

| 形态 | 典型件 | 正典配方 | 律锚 |
|---|---|---|---|
| rolling-ledger | compute_audit.json·regime_state.json 的 history/launches/transitions 键 | **双 blob union 零丢失**（union 后行数=\|A∪B\|），态字段另取新 | r188/R208 |
| append-log | *.jsonl·watermark.jsonl | 行级 union 零丢失 | r188 |
| mixed-dict+ledger | autofill_state.json | launches=**union→按 ts desc 排序 cap 50（cap 语义=保最新 50）→写回前必 re-sort ts 升序**（生产者=append 序，写回序属格式面：desc 直写=launches 整列翻面伪 diff 且被生产者 tick 继承固化·bm-b r245 律）；last_tick=**按内部 ts 比较后整 dict 赋值，禁 str() 化比较**（同秒 tie→HEAD·r140 律）；写回后 `isinstance(last_tick, dict)` 断言；**行尾+缩进镜像 base blob 探测并以 newline 翻译模式写回**（CRLF 生产者格式·r223/r234 律，探测≠写回） | r203/R208/r215/r220/r245 |
| js-wrapper-snapshot | dashboard_status.js（`window.DASH_DATA = {...};`） | **禁 json.dumps 直写剥包装**——按生产者写出配方（monitor/build_status.py）逐字镜像，或 take-side 整字节 | R209 |
| snapshot | *_status.json·state-*.json·watermark_red.json·fundamental_b_layer_filter.json·token_usage.json | 取新整面（最新态覆盖语义·按命名 ts 键取新）；单写者件（state-<id>/machines/<id>）取本机侧、禁改他机文件 | R208/R216 |
| append-ledger-md | round_reports*.md | 两机新行按 ts 序 union（各机只追加自己的行） | R208 |
| anchor-insert | HANDOVER.md『最近核对』行 | origin 先落者保位；后到者把自家增量**插至『上一次核对』锚前**，禁整行覆盖禁抢号 | R210 |
| memory-union | CODELY.md | 行级 union 各机新条目（去重相同行） | R208/r212 |
| renumber-append | digests/DIGEST-*.md | 同窗撞头=后到者让号重编自家新节 | r176 |
| single-writer-heartbeat | fleet/machines/*.json | orders_ack token=**全文件名含 .md 后缀**（repr 印原始 ack 串再比对） | r220 |

## 三、解后纪律（写回前必过）

1. **解析验证过才写回+add**（r185 律）：每件 json.loads/py 语法过再落盘。
2. **同秒 tie 取 HEAD**（r140 律·R208 再证）。
3. **零丢失校验**：ledger 型 union 后行数=两 blob 并集数；byte 级锚（关键数字与存档精确相等）。
4. **留痕**：resolver 脚本落 `results/_r<N>_resolve.py` + 轮报告注明撞头与解法 + commit 时间序（后到让路按 fleet/README.md §4）。

## 四、rebase 重放特情（r220）

rebase 中途工作树出现未跟踪同路径件与待重放提交撞车（"untracked working tree files would be overwritten"）：**暂移件出树（TEMP）→ continue 走完 → 回移后作独立后续 commit**；禁 abort 重来。
