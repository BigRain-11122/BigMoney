# ST-13 配音台本预处理回执（EP001-003 · ST-013 · r1024 bm-b）

> 站点=CONTENT-LOOP ST-013；时点=2026-10-19T14:11:37；车道=cpu（13:2x 排满令 v2 @bm-b 日间填充腿）；零网络（本地 git 对象）零云端；纯确定性预处理。

## 一、结论一览

- 台本行 52 行全量落表（MD 人读面 + JSON 机读孪生），逐行带声库映射/情绪提示/预估时长/镜窗配速。
- 配速风险面：OVERFLOW 21 行 / TIGHT 12 行——生产站烧制前必须逐行决断（压语速或加镜窗），本表已按行点名。
- 声库缺口如实：旁白+配角=18 行 GAP（无银行条目·禁顶替）；多说话人 2 行自动拆（heuristic 待选角站复核）+ 3 行待人工拆。

## 二、溯源

- EP001 = origin/main:cph4/fleet/drama-001-stockera/episodes/EP001.json（blob 9579d9927b62 · sha256 a7569cdc3a5dd241…）
- EP002 = origin/main:cph4/fleet/drama-001-stockera/episodes/EP002.json（blob b63c26864db9 · sha256 7db84c133b28569b…）
- EP003 = origin/main:cph4/fleet/drama-001-stockera/episodes/EP003.json（blob 2bb15e5bd43e · sha256 9d77dc008f48f92a…）

## 三、诚实边界

- 情绪=规则 v0.1（首中即停词表+说话人基线），非表演规格；预估时长=常数速率，非合成实测。
- 旁白无银行条目与满仓共 voice_05 底嗓（ST-009 债）——本表只点名不解债，根解=ST-012 夜窗。
- 台本源=集团仓剧集 JSON 当前 origin 面；后续集数台本=同法续站。

## 四、后续站位

- 选角/合成站消费本表：GAP 行处置（旁白条目入银行 or 一次性方案）+OVERFLOW 行决断+多说话人复核。
- ST-012 角色声 LoRA 夜窗车道照单（22:0x·GitHub 轮子扫描先行）。

