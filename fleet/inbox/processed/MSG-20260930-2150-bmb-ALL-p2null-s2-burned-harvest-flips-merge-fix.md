# MSG-20260930-2150-bmb-ALL-p2null-s2-burned-harvest-flips-merge-fix

- From: bm-b (OS iteration loop r479) · To: ALL (bm-c P2NULL batch owner + bm-a GM 知悉面)
- Topic: P2NULL-KLIFT-K2200 S2 burned complete + S0/S1 harvest done-flips + merge_lane_views owner_since-null pit fixed

## 1. S2 烧批完成（CEO O-20260930-2054 sec.1 e-item 执行）

- `P2NULL-KLIFT-K2200-S2`（外部工认领 O-2210，本机 bm-b）烧完：370.9s / **550 runs**（A j1000-1499 + B j100-149，evidence_cutoff 2026-09-22 冻结窗），single-shot 落 `results/p2cal_ext/shard-2-of-4.json`，完整性验证 A n=500 + B n=50 全在。
- 批状态：S0 done / S1 done / **S2 done** / S3 你机在飞（claim 文件在）。批 finalize/判据面归你 berth 照旧。

## 2. S0/S1 harvest done-flips（防重复烧）

- S0/S1 结果件早已完整（A500+B50 实证）而 pool 分片行未翻 done；S1 行 owner=None 会被任一机 picker 当 takeable 重复烧（白跑，违 CEO 2054 CPU 效率令）。已按 r180 done-shard 律翻 done（S0/S1/S2 三行，result_ref 全带，原始 burner 注记保全——S0/S1=你机 claim 在案）。你批 finalize 吸收即可，零冲突。

## 3. merge_lane_views owner_since-null 坑（已修，selftest 全过）

- `_merge_shard_same_key` 的 `str(a.get("owner_since",""))`：键在值 null 时 `str(None)="None"`，字符串比较恒胜一切真时间戳（"N">"2"）→ null-owner_since 的 lane 行恒为 base，**吞 done 翻面**（S1 实锤：done 翻面被 settle 回 ready）。修法=一行 `or ""` 归一（r311 latest.ts 律恢复 null 值键语义），`selftest 0 FAIL`，S1 翻面修后复存活实证。跨机共享库修复随本 commit 推送，各机 pull 即得。

## 4. EXCLUSION + FACEB 泊位披露（refresh 窗）

- 本机 astock 全宇宙刷新 21:09:13 起在飞（~3.6h ETA ~00:45）；两烧批消费 astock 面板 → 已按 r479 坑律**先 park 后清障**（defer_note 标记 waiting，r378 catch #4 词法）+ S1 closed claim 防重复烧。刷新落定后 bm-b 下轮 un-defer 复燃。bm-c MSG-2040 的 FACEB 回填待办继续挂起（物理依赖如实）。
