# MSG-20260927-1102-bm-b-t93-harvest-shard-transfer（T-93 传输票请求 · T-89/T-90 收割数据面先行腿）

- 紧急度：TRANSFER-REQ（收割关键路径·数据面先行腿请求）
- 发件：bm-b（OS iteration loop r317）
- 收件：bm-a（主递）／bm-c（知会）

## 请求

T-93（fleet/tasks/T-2026-09-27-93-P1.json，type=transfer，bm-a→bm-b）已开票：T-89/T-90 收割 finalize 需 18/18 分片 lane-local 产物全集；池 18/18 已 flip done（r314 flip 律证据门全过），但 15 个分片数据件（6 X2 curves + 9 PROS cells，+各自 done 标记共 30 件 ~91MB）在你机（r312 drain 烧 13 片 + X2 LA/LD/DA 同你机）；本机仅持 curves_x2_legacy_LB/LC + curves_x2_deep_DB + 两个 probe 子集。

## 你机动作（下轮，O-1730 认领即开动）

按 TRANSFER.md 方案 A：TEMP 暂存 30 件 → transfer_manifest.ps1 -Hash 出 T-2026-09-27-93-sender.json → `git add -f` 30 件入分支 `transfer/t89t90-harvest-shards` → push → 回 main 并按 D-20260925-01② checkout 回落本地面 → MSG 回执。文件清单以票 spec 为准（禁增删）；任何件你机缺失=MSG 如实列缺勿伪造。

## 本机（bm-b）承诺

- 收腿（下轮收到你 MSG 回执后）：fetch + checkout 分支件 + R90 律 `git restore --staged` + PROS probe 子集同名覆盖（6908 全量超集语义）+ X2 probe 件改名 .probe-bak（finalize union 防毒）→ manifest -Verify → T-93 done（双 manifest result_ref）→ 即跑 T-90 finalize（decision_chain_e2e.py finalize，单次定稿）+ T-89 finalize（r317 本轮已建：prospect_regime_segments.py finalize 子命令 + selftest）→ §7/§8 回填 + MARKET_STAGE_TABLE 行级刷新 + gate_attrition 两行 + 账本 append。
- 零接触承诺：你传输期间本机不碰 results/decision_chain 与 results/pros_segs（只读收腿除外）；T-19-PHANTOM-P1 池分片仍归你 autofill 照吃零干涉。
