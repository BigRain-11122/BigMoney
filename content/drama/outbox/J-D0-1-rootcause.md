# J-D0-1 root-cause self-cert (draft) -- bm-b taildrop SLA violation

> Station ST-001 product (CONTENT-LOOP v0.1 first runner). Source: drama-dept-v1 LEDGER
> row J-D0-1 (2026-10-16 drama-pilot-taildrop-bmb OVERDUE, hit=0/1, 12:45 deadline,
> 21:06 poke; bm-b-side self-cert pending). PILOT-001 3x20s samples WERE delivered
> (RECIPE-EPBURN-v1 preface) -- the violation is about the delivery channel, not the product.

## Facts collected (group origin @ 2026-10-18T23:50:27)
- **group-origin tree scan**: rc=0, taildrop-named files=1
- **file**: cph4/fleet/dispatcher/delivery-watch/drama-pilot-taildrop-bmb.json
- **LEDGER rows**: 1 hit(s)
- **ledger**: | J-D0-1 | 试点尾件交付拖期（bm-b taildrop OVERDUE·hit=0/1·12:45 死线未达） | drama-pilot-taildrop-bmb 2026-10-16 OVERDUE（delivery-watch 在监·21:06 已 poke） | 交付哨在监+O-令催办；**待回灌**：粗样交付 SLA 违例根因（bm-b 侧自证）入行 | 10-16 |
- **orders rows**: 4 hit(s)
- **order**: | 2026-10-16 11:4x | **【@bm-b】《一路长虹》试映片直送 CEO 位（Taildrop → bm-a）** | CEO 令 00:1x「明天我看结果」=今日呈看·CEO 当前在 bm-a——派 bm-b `tailscale file cp` 四件至 bm-a:（100.110.185.62）：PILOT-PREVIEW-3x20s.mp4 + seg1/seg2/seg3.mp4 + sea-review-level1.md（源=C:\Fluxgroup\FluxGroup\media\drama-pilot-out\）；bm-a 侧 `tailscale file
- **order**: | 2026-10-16 13:0x | **【@bm-b】欠件追缴五件（C-02 普查C/E 定谳·本行 poke 直达）** | ①POOL-0020（CEO 亲令 P0·18:21 开卡）18h 零回执——实测 10-15 23:34 你已执行满性能恢复（239.80W+PowerCap 删除+卓越性能）=**活已干卡未销**：即填 POOL result_ref+orders 回执行；②C-20261015-03 spawn 帽腿回执补交（B2150/B2151 已落·回执缺·超线 5h39m 如实记）；③哨兵 PROBE_ERR（01:1x 起）定谳回执；④POOL-0018/001
- **order**: | 2026-10-17 00:5x | **【E1 委员会通道·@bm-b】bm-b IterationLoop 停摆并案单（NJ bigmoney R9 承载件触发·CEO 令锚=O-20261016-2347 §一.3 @bm-b 腿「全面开工」resume 广播 23:36 未达+O-20261015-1821 POOL-0020 P0）** | **停摆实锚（事件班 00:44 /status+origin 双探）**：心跳冻结 10-15 19:10:18（r986 GREEN·53.5h）+bigmoney 树冻结 8949e0aef 落后 30+ 代=读令通道死（组树 HOT 
- **order**: | 2026-10-17 07:3x | **【P1 轻派·@bm-b 活窗】O-2110 bm-b 腿时窗纠偏：drama 试点粗样 CDN 回填提前单件执行（NJ bigstream R12④ 承载件·CEO 令锚=O-20261016-2110 三线质量令实物回传①·勿候 IterationLoop 复活）** | ①**执行体=bm-b 活窗（交互会话）单件执行·分钟级**：TJGenerators MCP file_upload→PUT 上 CDN 两件（源=C:\Fluxgroup\FluxGroup\media\drama-pilot-out\PILOT-PREVIEW-3x20

## Root-cause candidate (bm-b side)

- Delivery mechanism was fleet Taildrop file transfer (drop to peer Downloads scan face,
  r1044 pit law). hit=0/1 with poke at 21:06 after a 12:45 deadline = the receiving-side
  pickup never registered during the SLA window; delivery only completed via a later
  alternate channel (git/manual), so the watch contract counted a violation.
- Candidate root causes (ranked): (1) taildrop drop landed outside the scanned inbox face
  (r1044: must-scan-Downloads face); (2) sender-side send receipt not written while the
  receive actually happened late; (3) peer offline during the window.
- Gate recommendation: delivery-watch contract should pin the scan face list (Downloads +
  fleet inbox) and require a sender receipt row; deadline contracts for cross-machine
  physical-channel deliveries should carry a fallback-to-git clause so SLA is provable.

## Status

- This face = local evidence product (ST-001 done locally). The LEDGER backfill row rides
  the next group push window -- queued as outbox payload, NOT auto-pushed (group tree =
  shared live tree, CAS push required).
