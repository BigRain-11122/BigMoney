# DIGEST 2026-11-07 r1265 (bm-a) -- 板子排在它判的车道之前

## 症状
python -m smoke_test 370/373 PASS，1 条新红：
product: data lane freshness board agrees with the lanes and the calendar | heat=2026-11-05==2026-11-06 ...

## 三个时点
- 14:19 链里的 data_lane_freshness 腿写板子（那时 heat 尾 = 2026-11-05）
- 14:32 update_heat --takeover 写下一份快照（2026-11-06，署名 bm-a）
- 14:52 smoke 拿板子对现算 → 红

## 根因（结构，不是数据）
Tools/s6_chain_bmc.py 的腿表里，汇总板在第 42 行，它汇总的十条车道更新在 68–614 行。链内板子永远晚一个周期；链外更新（代班、手工回填）落后更多。

## 修法
新增 data_lane_freshness_close 腿：最后一个车道生产者（fund_statements）之后、两个引用它的真人面（daily_report / ceo_live_usage）之前再 derive 一次。幂等 0.2s 零网络。早腿保留（ownership / silence 读它的面）。腿数 133→134。

## 验证
- python Tools/s6_chain_bma.py 1265 --only=data_lane_freshness_close → rc0，verdict=host_down counts={'retired':1,'unverifiable':4,'in_sync':5}
- 独立复算 data_lane_freshness.audit(calendar, now) vs 已发布面：	ail_mismatch=[]，expected=2026-11-06 两侧一致
- 同轮顺带修复三条「下游真人面没跟着重生」的红（r1262 同族）：gpu_face apply / lane_ownership_declaration run / daily_report run / monitor.build_status

## 可复用的一句话
一个汇总面排在它的生产者前面，会在一份正确数据上变红；修的是位置，不是判据。
