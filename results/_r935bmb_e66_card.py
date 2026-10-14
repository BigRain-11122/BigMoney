# r935 bm-b: append E66 methodology card
import io

p = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\knowledge\METHODOLOGY_ASSETS.md"
card = "\n- **E66 执行轴配对块隔离判负法+三波决定论交叉链（as-burned control 臂跨波字节恒等门）**：proven，研究面。执行侧轴（出场 X/仓位 S/时机 T）判负正法三件套：①同一入场 cell 池冻结复用（W16 173 cell verbatim）×被测轴全 face 全叉=完整配对块（任一臂过初筛→该 cell 全臂入判=配对读数面·块完整律·块帽 90 冻结确定性降序规则）；②control 臂=cell 原生 as-burned 值→**跨波决定论交叉门**（W17 control=W18 as-burned=W19 as-burned 同 cell 三列字节恒等 43/173 三证=确定性引擎零漂移的免费回归测试·失配=面错配 VOID fail-closed 非科学读数）；③退化对排除律（cell-as-burned(f) 子群构造性 delta≡0 零信息→Wilcoxon 只跑 informative pairs·census 全数披露非隐藏）+零方差臂排除披露（zvx 律）+两 as-burned 子群二级读数（方向不对称面独有交付件）。三波 live 实证：X 344 格/S 188 格/T 112 格三连 lawful-zero·§5 预测 6/6 全 HIT（四波校准最优）·语法效率结论兑现（未来 GENERATE 只需入场×过滤面·X=template_default+S=as-burned+T=daily_signal）。证据=results/trial_labor_w19/*（r935 bm-b）+W17/W18 §7/§8。\n"
with io.open(p, "a", encoding="utf-8", newline="\n") as f:
    f.write(card)
print("E66 appended")
