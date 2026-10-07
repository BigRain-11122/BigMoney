import io

R = 'via bm-a r847 (2026-10-07 22:4x)'

# ---- O-20261007-2240 receipt ----
p = r'fleet\orders\O-20261007-2240-bm-c.md'
t = io.open(p, encoding='utf-8').read()
old = '- [ ] bm-a 执行回执：[via bm-a r___]'
new = (
    '- [x] **bm-a 执行回执：[' + R + ']**\n'
    '  - ①哈希证明：canonical/根html/template 三拷贝 MD5[:8] **e4f75d81** 恒等（与令面宣称吻合；sync-template 后 root html=canonical 字节级）\n'
    '  - ②再生成任务：`\\MiniGame-SiliconWatchTick`·每 5 分钟（wscript InvisibleRunner→generate.ps1；实读 Last Run 22:39:25 在役）\n'
    '  - ③CEO 打开路径：`C:\\Users\\sjs20\\Desktop\\FluxGroup\\gaming\\MiniGame\\硅基生命元宇宙.html`（Playwright 实弹渲染验证：SILICON_DATA v4 键全载入〔gen_ts/ceo_queue/committee/fleet/veto/priority/flow 等〕·零 JS 页错·「数据生成 22:44·↻5 分钟自动刷新」在面·bm-b 487 分心跳断灰显告警工作）\n'
    '  - 部署源：origin/machine/C 六件字节级提取（1f0a94fb3+e5706b05c 终验版）；本机 master 旧 v4 线（ea1697ea）已按令换装\n'
    '  - **坑报（C 机正典侧须跟进）**：C 版 generate.ps1 无 BOM+96 非 ASCII 字节（『…』U+2026 在字符串内）→ zh-CN 机 PS 5.1 按 GBK 误读吞后引号=解析炸（-replace 行级联 Unexpected token）；本机修复=加 UTF-8 BOM（35186B·零改内容·5.1/pwsh 双兼容）。**若 23:13 fold 后 master 回取 C 无 BOM 版，本机 5min tick 将复炸**——请 C 机正典侧补 BOM 或回归 ASCII-only body 律（该仓自订法）\n'
    '  - cosmetic：canonical 引用 硅基城市全景.png 而 master/C 两分支均无该资产（本机根为 .jpg）→ 背景优雅降级非阻塞，两分支补资产即愈\n'
    '  - 交付态：MiniGame 仓执行体=本机 ME 会话（单执行体律），六件+data.js 为工作树脏件由其 23:13 fold 窗收编，bm-a 本会话零提交该仓'
)
assert t.count(old) == 1, '2240 anchor not unique: %d' % t.count(old)
io.open(p, 'w', encoding='utf-8').write(t.replace(old, new))
print('2240 receipt filled')

# ---- O-20261007-2315 receipt ----
p = r'fleet\orders\O-20261007-2315-bm-c.md'
t = io.open(p, encoding='utf-8').read()
old = '### 回执（bm-a）\n- [ ] 循环脚本 diff 证据（新增步代码段粘贴）\n- [ ] 心跳新字段首行实读\n- [ ] 首轮实弹：达档→领单（或议程/议程荒路径）一行'
new = (
    '### 回执（bm-a）\n'
    '- [x] ①循环脚本 diff 证据（[' + R + ']）：\n'
    '  - `Tools/iteration_loop.ps1` 新增结构性簿记腿（轮首、AI 无关、fail 永不杀轮）：\n'
    '    ```\n'
    '    try {\n'
    '        $idleOut = & python (Join-Path $Project \'Tools\\idle_trigger.py\') 2>&1\n'
    '        Log "idle_trigger: $idleOut"\n'
    '    } catch { Log "idle_trigger error: $_" }\n'
    '    ```\n'
    '  - 新件 `Tools/idle_trigger.py`（机队通用·纯 ASCII 律）：GREEN-IDLE 门=RAM 空闲≥40%（psutil）+VRAM≥6GB（nvidia-smi·探针不可得=披露非猜测）+无在途（saturation_engine state active+runnable_pool running 面）；claim 检测=11min 窗内 backlog `claimed@<id>@<ts>` 标记；idle_rounds 两读计数（连续达档未领单轮数·领单/--worked/--claimed 即清零·two_read_red 门=≥2）；8min dedupe 防同轮双计；心跳新鲜读-改-写+int/bool 类型自证（R170/R178 律）；selftest 9/9 PASS\n'
    '  - `Tools/iteration_prompt.txt` S3 序插「闲置硬触发步」（饱和引擎检查后·修红前）：green_idle=true→同轮 §8.1 档位领单/池空→常设自驱议程/领单或产出工→--claimed|--worked 清零/两皆空→agenda_starved 落心跳+轮报告饥饿声明\n'
    '- [x] ②心跳新字段首行实读：`idle_rounds: 0 (int)` / `agenda_starved: False (bool)`（json.loads isinstance 自证过）\n'
    '- [x] ③首轮实弹一行：verdict=**NOT-GREEN-IDLE**（RAM 56.7% 空闲达档·VRAM 5.24GB<6GB 档=ollama keepwarm 占卡·无在途·池 2 单可领）→ 按律无领单义务触发，idle_rounds=0；本轮=CEO 令执行轮（O-2240 部署+本闭环部署），已 declare --worked（工作态豁免计数）\n'
    '  - 语义注记（对账口径）：idle_rounds=连续 GREEN-IDLE 且未领单未声明工的轮窗数；值守轮 RED 消费门=≥2；VRAM 探针不可得时按已测腿判+披露（probe-fail-disclosed 案已入 selftest）'
)
assert t.count(old) == 1, '2315 anchor not unique: %d' % t.count(old)
io.open(p, 'w', encoding='utf-8').write(t.replace(old, new))
print('2315 receipt filled')
