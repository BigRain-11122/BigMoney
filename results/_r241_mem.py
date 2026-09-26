"""r241 memory append (python direct UTF-8 per r230 law)."""
import io

entry = ("\n- [2026-09-26 10:5x] 坑律（bm-b r241·T-78 s3·ExitPatch 补丁命中面·E1 自检期自捕）："
         "**ExitPatch 工厂补丁改写的是 engine.backtester.ExitConfig（引擎 run_backtest 消费的绑定名）"
         "——自检夹具若直引 engine.exit_rules.ExitConfig 构造验证=绕过补丁读原类，断言假 FAIL（cfg.loss_time_days 得 8 非 16）**；"
         "正律=ExitPatch 类断言一律经 `_eb.ExitConfig`（`import engine.backtester as _eb`，combined_exit_screen/live.paper 同款消费面），"
         "跑批腿经 run_backtest 天然走对（病只在夹具直引面）。连带：合成价格夹具要逼组合 NAV 破触发线必须先封住单员损失面"
         "（initial_stop=-0.95+time_decay=9999+大仓位 0.30×3 员连续信号——默认 -8% 硬止损+10% 仓位下 NAV dd 结构性到不了 -5%，"
         "弱夹具=假不触发）。指针=scripts/exit_overlay_p1.py selftest [2/5][3/5] + results/_r241_ddc_verify.py。\n")

with io.open("CODELY.md", "a", encoding="utf-8", newline="") as fh:
    fh.write(entry)
print("CODELY.md appended")
