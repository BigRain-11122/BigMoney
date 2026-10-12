# C-20261009-03 Git 全景梳理+机队工作区规范对齐案（CEO 直令同窗收口）

> 提案=秘书处（bm-a 执行窗）·2026-10-09 ~17:2x。触发=CEO 令「委员会牵头，整体梳理一下git，然后保证机队每台机器的文件和目录等规范都一样」（orders O-20261009-1715）——委员会通道·同窗收口（council §五 排期律）。
> **命令查重登记**：O-2026-0928-013 机队一致性总括令（09-28「全量整合精简清理+同步git+分发给机队，做到机队文件一致性」）已有法覆盖——.gitignore 运行面扩容+机队分发 HEAD sha 回执判据先例在案；versioning §4.3 提交规范/§8 branch protection/总控仓结构律（.gitignore 隔离子司仓+根级正典随仓）全在册→**本案=执法强化+复审收口·零新顶层法条**；新产出件=机队工作区基线 v1（本案卷宗承载·非新法）+审计工具 Tools/fleet-workspace-audit.ps1（CPH4 工具辖区）。
> **利益申报（council §四.6）**：席1 秘书处=本案执行体（bm-a 整改自执·申报）；席3/4/5/6 所执司 .codely-cli 会话面与嵌套子仓受基线约束——意见一律锚外证（工具读数/仓实况/在册 P 号），自证无效。

## 一、取证全景（2026-10-09 17:0x-17:3x 秘书处实测·Tools/fleet-workspace-audit v1.0 首跑在案）

**表1 总控仓（FluxGroup@bm-a）**：HEAD=bc54a96=origin/main（同步位 ✓）；脏面 **357 条**（?? 245/staged 98=他窗 MV 在飞面/M 14）；.gitignore 覆盖缺口实证=子公司 .codely-cli 会话件 200+ 条裸奔+media/MUSIC **3.27GB**+cph4/labbench 15.6GB+.playwright-mcp 全未护；未收编正典件 22+（R 件×8/OH 件×4/工具件×5/handover.md/软著权威位/benchmark 文档/审计证据 log）；杂物=quant 冲突残留 1 件（09-29 生·135B）+根散件 2（软著页 png）+Tools 下 .pyc 编译物 6 件入库违例。

**表2 八嵌套子仓矩阵（fork 实测）**：

| 仓 | remote | 分叉 | 脏 | .git | 旗标 |
|---|---|---|---|---|---|
| gaming/MiniGame | ok | sync | 3 | **3863MB** | GIT_BIG（P-20260929-13 gc 令 7 天未关·owner@Biggame）·**master 分支名与集团 main 制不齐** |
| gaming/FluxVerse | ok | sync | 2 | 329MB | — |
| quant/bigmoney | ok | **ahead1** | 16 | 644MB | 在飞轮件（round 921 boot 未推·轮自愈面·只读不代执行） |
| media/BigStream(Bigmedia) | ok | sync | 19 | 976MB | — |
| life/BigLife | ok | **ahead1+behind1 分叉** | 2 | 110MB | 双机竞推实证（本地 7f664e51 [via siliconwin-x2052] vs 远端 d5acbae2 [via bm-c]）·owner@BigLife 窗收口 |
| domain/BigDomain | ok | sync | 0 | 25MB | 样板 |
| compute/BigCompute | ok | sync | 0 | 19MB | 样板 |
| house/BigHouse | **无 remote** | — | 0 | — | CEO 建仓物理件（O-20261009-1430 在册·poke 仓单已摘除防慢性 fail） |

**表3 机队通道**：bm-a↔bm-c poke 秒级全绿（O-20261009-1430 修令收口）；bm-b 整机离线 13h+（CEO 物理件·复活即接线包在节点表）；BG-B/BG-C 未入 tailnet（08 号协议窗·repos 登记面=MiniGame）；CEO 笔记本=非机队成员（借池律排除面）。

## 二、定谳（三病根）

1. **证据链断链（最重·诚实律证据对违例）**：台账/orders 行引用的证据件**未上链**——cph4/research R 件 8 件+oss-harvest OH 件 4 件+工具件（gitsilent/抓弹窗/video_qc/polish-hunt）在盘未入库；orders 12:4x 行明写「R-20261009-selfdrive-innovation-01 归位」而文件零 commit；registry/orders.jsonl 尾行 O-20261009-1210-bm-a 完整行落盘未提交（其 orders.md 孪生行已上链）→ **他机 pull 后无此文件=「每台机器文件一样」的直接破洞**（证据引用在他机=404）。
2. **运行面/正典面混淆**：.gitignore 只护根级 .codely-cli 显式运行面，子公司 .codely-cli（gaming/quant/life/media）会话件全裸奔+媒体大文件（media/MUSIC 3.27GB）+实验区（cph4/labbench 15.6GB）+浏览器工件未护→status 噪声 357 条淹真信号；反向=正典件（软著权威位 15.1MB〔O-20261008-1810 唯一权威位〕/handover.md/工具件/审计证据）漏收编。**判例：白名单制（settings.json+memory/+evidence/ 入库·其余全运行面）**。
3. **嵌套仓慢性病**：MiniGame .git 3.86GB 连续 13+ 夜点名（gc 令过期未关）+BigLife 双机竞推分叉+BigHouse 无 remote+**主分支名不统一**（MiniGame=master·余七仓=main）——分叉与未推件=机队文件不一致的子仓面实证。

## 三、机队工作区基线 v1（标准面·本案卷宗承载·回访 10-16）

1. **仓面矩阵**（每机必有件=fleet-nodes.json repos 登记面权威）：总控面机（bm-a/bm-b/bm-c）=FluxGroup 全树+各自登记子仓；BG-B/C=MiniGame 面（08 号协议域·tailnet 入网后按本基线第 2/5 条执行）；CEO 笔记本=零部署（在册排除面）。
2. **同步判据（机器可验）**：每机 FluxGroup **HEAD sha == origin/main HEAD sha**（fetch 后核·审计工具 A 项）=「文件目录一样」的可验收形态；工作树根路径允许按节点表登记差异（bm-a=C:\Users\sjs20\Desktop\FluxGroup·bm-c=K:\Fluxgroup\FluxGroup），**内容逐字节以 git 为准**。
3. **脏面两分律**：在飞件归执笔窗收口（**他窗禁代提交**——外科提交净路在册）；沉积件（>7 天未动 M/??）=轮末清账+值守轮点名。基线后 status 噪声常态位 ≤20 条（本轮 bm-a 实测 357→**138→收编后≤25**）。
4. **结构正典**：根级规范件=AI.md/BRAND.md/CODELY.md/README.md/RULES.md/handover.md/.gitignore/Tools//docs//cph4//fleet//软著申请材料/（CEO 权威位）；八子仓 .gitignore 隔离各自独立 remote（在册律维持）；.codely-cli 白名单制（见病根②判例）。
5. **五禁项**（值守轮抽验面·审计工具 C/D/E 项）：①codely 同步冲突残留（*冲突* 类）②根目录散件（业务文档须归位·png 归权威位）③__pycache__/.pyc 入库④媒体大文件/实验区误入 GitHub（media/MUSIC 类）⑤台账引用件未上链（收编律：**落盘即入库**——研究/收获/工具件随产随 commit）。
6. **分发与回执**：push origin+fleet-dispatch poke（bm-c 秒级/bm-b 复活即接线）；回执判据=**HEAD sha+审计工具全行输出**（承 O-2026-0928-013 HEAD sha 判据先例·增审计输出维度）。

## 四、行动包（✓=本窗实弹·▶=派单）

- ✓ **.gitignore v2 扩容**（白名单制 7 目录+冲突残留+media/MUSIC+labbench+playwright+pyc——status 噪声 357→138，收编后 ≤25·真信号零淹没）
- ✓ **正典件收编 22 件**：R 件×8+OH 件×4+Tools 5 件（fleet-workspace-audit.ps1/gitsilent 源码+垫片/抓弹窗.bat/video_qc.py/polish-hunt-popup.ps1）+handover.md+软著申请材料/（168 件 15.1MB·CEO 权威位入库=机队共享）+quant/benchmark 文档+docs/audits/popup-hunt-now.log（审计证据·fused-scan-30d.log 先例）+registry 尾行收编
- ✓ **杂物收口**：quant 冲突残留删除（135B·09-29 生）+软著页 png×2 归位 FluxVerse_FluxVerse/ 权威位+.pyc 6 件退库（新 .gitignore 防再犯）
- ✓ **Tools/fleet-workspace-audit.ps1**（机队自审工具·A-E 五项+verdict·纯 ASCII·PS5.1 安全·fail-soft）——bm-a 首跑 WARN→整改后复跑 PASS 为呈报门
- ✓ **分发**：本批 push origin+fleet-dispatch poke bm-c（-Reason 承 O-20261009-1715）
- ▶ **@bm-c**（回执 ≤24h）：pull 至本批 HEAD sha→跑 Tools\fleet-workspace-audit.ps1→同律整改（冲突残留/根散件/pyc/白名单外会话件自清）→回执行落 orders.md（HEAD sha+审计输出粘贴）
- ▶ **@bm-b**（复活即接线·CEO 物理件依赖如实）：上电后 ≤1h register-fleet-link 收口（承 O-20261009-1430 节点表注记）→同 bm-c 全套
- ▶ **@BG-B/C**（Biggame 司域·08 号协议窗）：tailnet 入网即按基线 2/5 条执行；入网前 MiniGame 面由 Biggame 司域自查呈报
- ▶ **@值守轮**（零新节律）：基线五禁项扫入既有班次抽验（审计工具随班一次）；MiniGame GIT_BIG/BigLife 分叉/BigHouse remote=既有点名面维持（owner 司域件·产品仓只读不代执行如实注记）
- ▶ **@各司窗口**：脏面两分律领受（在飞件自收口·沉积 7 天线）；**MiniGame master→main 统一=呈 CEO 选项**（活跃仓改分支=有干扰动作·不擅动）

**CEO 件（☐ 沿既有清单·本案新增 1）**：BigHouse 建仓物理件维持（O-20261009-1430 在册）+bm-b 开机检查（在册）——本案不新增催办面。

## 五、预注册判据（回访 2026-10-16 治理窗·与 C-20261009-01/02 同窗合并）

① bm-c 回执窗 ≤24h（HEAD sha 对齐+审计输出在案）；② bm-b 上线后 ≤1h 接线+≤24h 回执（物理件依赖如实呈报）；③ 总控仓 status 噪声常态 ≤20 条（bm-a 复测+bm-c 回执面）；④ 收编律复发=0（台账新引用件在库抽查 100%）；⑤ 子仓面：BigLife 分叉闭合+MiniGame .git 关单+master→main 裁定落地（owner 司域·委员会只读复核）。

## 六、程序注记

同窗收口（CEO 直令·委员会通道）；七席意见+席7 魔鬼代言人+记名投票=Tools/council_vote.py --major（通过 ≥5/7）；票档纯追加 decisions 委员会节；T2·否决窗 7 天至 10-16·CEO 翻案权保留；利益申报三席在档。
