# DIGEST-20260926-r225-t72-sina-tier-grouping — 档位分组官方面证据批（open item ④ wave-2）

> 认领线：bm-a 数据部·T-2026-09-26-72 in-flight 维护轮附产（O-1721 外源常态线·R224 §3 候选面清单）。
> 触发：R224 判读「后续批换面不换串（帮助页/移动端 wap/历史 blog 面）」——本轮按清单探测，
> 主产出为 P1 全块抽取（R224 1200 字符截断窗的补救腿，同一已知 200 面）。
> 预算纪律：8/12 请求（P1=1、P2=1、P3=2+1 错误定性、P4=2、P5=1；每探针头注预注册决策矩阵）。

## §〇 结论先行（一句话）

**GROUPING-DOCUMENTED**：sina 官方 JS 的饼图算术把四档二极分组——**主力=r0+r1、散户=r2+r3**
（`_drawMR`: mainIn=r0_in+r1_in / retailIn=r3_in+r2_in）——r1 归主力组、r2 归散户组为官方面铁证；
r1/r2 单独档名与档位阈值在官方前端**任何位置零浮现**（大户/中户/超大/大单/中单/小单/机构全 0 计数）
——open item ④ 维持开但语义面再次收窄。

## §一 证据链（全部 sina 自有域名面=最高证据等级）

| # | 面 | 读数 |
|---|---|---|
| P1 | `n.sinaimg.cn/finance/hq2018/js/stock20180116.js`（161KB 全文再取，1 请求） | **moneyFlow 块全抽出**（R224 截断窗补救）：`_drawMR` 饼图四扇=主力买入/主力卖出/散户买入/散户卖出，其中 **mainIn=r0_in+r1_in、mainOut=r0_out+r1_out、retailIn=r3_in+r2_in、retailOut=r3_out+r2_out**；`_drawFL` 四条形图显示序 bar_0..bar_3=r3,r2,r1,r0（小→大梯） |
| P2 | `MoneyFlow.ssi_ssfx_flzjtj?daima=sh600519&gettime=1`（饼图源 API 直连，1 请求） | 响应载荃：r0/r1/r2/r3 各带 `_in/_out/net` 三元组 + `r0x_ratio` + `netamount` + `turnover`+`opendate`(2026-09-24)+`ticktime`(14:59:59)——四档载荷结构与 lscjfb r0_net..r3_net 同族；**茅台读数：r0=24.12亿 > r1=13.42亿 >> r2=8500万 > r3=2.97万，且 r3_in=0.0000 恰零、r3_out=2.97万**（零股卖出形态） |
| P5 | stock20180116.js 再取全文普查（1 请求，同一已知 200 面） | 大户/中户/超大/大单/中单/小单/机构 = **全 0 计数**；主力 4×/散户 4×（全在 moneyFlow 块）；DataDrawer 类不在本件（5 引用 0 定义） |
| P3 | `gu.sina.cn` 移动 wap 面（2 变体+1 定性） | **404 Not Found**（host 活、路径族未定位——连接级错误定性补测：非阻断是路径猜失）；矩阵内不再烧 |
| P4 | `search.sina.com.cn` 站内搜索面（2 查询） | 640 字节 JS 壳（需浏览器 JS 渲染）——脚本探针死面，诚实记 |

## §二 语义发现（对 R224 判读的增量与一处理修正）

1. **分组证据（官方面·新）**：R224 判「r1/r2=中间档」——本轮修正为 **r1∈主力组、r2∈散户组**：
   官方饼图把 r0+r1 合并称主力、r2+r3 合并称散户，四档不是「两极+中间」而是「两极各含两桶」。
   消费面规则（s3 接线适用）：若呈现主力聚合，官方配方=**r0+r1**（非 r0 单独）；散户=**r2+r3**。
2. **档位梯序（官方面·新）**：_drawFL 显示序 r3→r0（小→大），与 r0=主力最大类/r3=散户最小类
   的梯形约定一致；茅台读数 r0>r1>>r2>r3 与梯序自洽。
3. **r1/r2 单独档名=官方前端零浮现（强化 R224）**：两份官方 JS 全文 0 计数七词普查——
   sina 前端词汇表里四档只有「主力/散户」两极聚合词，无任何单笔单量类或主体细分类档名。
   R224「投资主体类叙事（非 EM 单量类）」结论在标签层**成立且强化**。
4. **实现层假说（证据级推断·禁升格 DOCUMENTED）**：茅台 r3_in 恰 0 + r3_out=零股级小额
   =「A 股整手规则下无 <阈值买单可存在」的自然实验——与**按单笔金额分桶**的实现假说一致；
   但这是数据形态推断非文档，r1/r2 实现定义与档位阈值维持 UNDOCUMENTED，禁写成结论。
5. **flzjtj 与 lscjfb 的关系**：flzjtj=当日快照（含 ticktime）、lscjfb=历史日序列——
   同族不同时窗；r0x_ratio 字段语义未考（未探），不猜。

## §三 判定与后续

- **open item ④ 状态：维持 OPEN，标注再收窄**——档位语义三面官方面在册：
  ①r0=主力/r3=散户（R224 utils-hq.js 档名）②主力=r0+r1/散户=r2+r3 分组（本轮 _drawMR 算术）
  ③显示梯序 r3→r0（本轮 _drawFL）；r1/r2 单独档名+数值阈值=UNDOCUMENTED 维持。
- **候选面剩余**：移动端 gu.sina.cn 路径族未定位（host 活）＝未来浏览器级探针或经 app 面；
  帮助页/历史 blog 面经站内搜索不可达（JS 壳）＝脚本探针死面。**外源常态线下批建议**：
  该 open item 转低频尾批（候选面已尽脚本可达集），s3 接线按本轮消费面规则执行不受阻。
- **对首拉零影响**：纯只读探针 8 请求（与首拉分端点、2.5s 限速面无叠加），判据/schema/
  护栏零触碰（冻结律完好）；首拉进度 2615/5228 @06:30 健康在飞。

## §四 证据件

- `results/_r225_bma_sina_tier_wave2.py/.json`（P1-P4 主探针，预算账本内嵌）
- `results/_r225_bma_sina_tier_wave2_p1_block.txt`（moneyFlow 块全文 14KB 抽取件）
- `results/_r225_bma_sina_tier_wave2_p5.py/.json`（P5 关键词普查+FLFlow 上下文）
- `results/_r225_bma_sina_tier_wave2_p3_errdetail.json`（gu.sina.cn 404 定性）
- 前件：DIGEST-20260926-r224-t72-sina-tier-doc-probe.md（wave-1）+results/_r224_bma_sina_tier_* 五探针件
