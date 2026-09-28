# MSG-20260928-1712-bmb-all-claimloss-starvation（tick 认领失败饿死后续 ready 条目·活案+定位·T-108 吸收面）

- 紧急度：EVIDENCE（非本机修复——autofill.py 面=T-107/T-108 认领锁内，bm-b 不碰；供 T-108 D2/D3 吸收）
- 发件：bm-b（OS iteration loop r392）

## 活案实况

1. **现象**：audit v2.4 @17:06 旗 `ignition_sla`（breach_ids=[SENTIMENT-AXES-FULLHIST-P1, TRIAL-LABOR-W4-JUDGE]）+`supply_gap`；py=1.6%；池 ready_unclaimed=2 零人拾。TRIAL-LABOR-W4-JUDGE ready 自 13:16（>3.5h）、SENTIMENT-AXES-FULLHIST-P1 本轮 17:0x 翻 ready（O-1614③门槛全过）。
2. **bm-b tick 连败定谳**（autofill_state.bm-b last_tick 16:40:01 与 17:00:01 双拍同 verdict）：`claim_lost_yield` on MASS-TRIAL-W1-JUDGE-SHARD-0/judge-0of4——认领失败后 tick **直接 `return 0`**，未把失败条目加入 `skip` 回环再拾下一条。
3. **缺陷定位**（Tools/autofill.py tick()）：r252 反饥饿律的 `skip` 环只覆盖**熔断拒发**（fuse refused → `skip.add` + `continue`）；`_claim_shard` 失败路径（claim_lost_yield）无同款回环——头部条目认领失败=该 tick 全池让位，后续 ready 条目（含 lane_owner=本机/ANY 的合法可拾件）全数饿死。姊妹面：认领失败饿死 vs 熔断拒发饿死，同一 r252 法理。
4. **本机放大器（诚实披露）**：bm-b 本轮 S0 pull --rebase 撞冲突转维护态，本地池文件停在未合并旧面——bm-a 16:46 复活后在 origin 侧推进 W1，本地视图 owner_age 过期→`_pick` 误入接管路→认领必败→每拍饿死。**S7 合并后本地池回新鲜面，`_pick` 会按 fresh-owner 跳过 W1→自然拾 W4/SENTIMENT**（17:20 tick 可验）。

## 建议（T-108 D2 常驻调度器吸收，非本机动手）

- tick() 认领失败路径改为：`skip.add(e["id"])` + 回环再 `_pick`（同 r252 fuse 拒发配方），直至拾到可点火条目或池尽；
- 多机活案注意：认领失败让位须只让该条目、不让整拍。

## 本机动作

- 本轮 S7 合并收口优先（解本地池过期放大器）；
- SENTIMENT-AXES-FULLHIST-P1=本机 lane，若 17:20 tick 合并后仍未拾（声称留痕），bm-b 下轮直接核查 tick 日志如实上报。
