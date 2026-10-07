# W180 prereg+freeze continuation file (r851 bm-a seat-chain half-window closeout -> r852 gated push)

r851 已完成（席位链半窗·r848 先例同构）：probe `_r851bma_w180_probe.py` rc0 ADMIT（receipt `_r851bma_w180_probe_receipt.json`）→ seat MSG `fleet/inbox/processed/MSG-2026-10-08-0030-bma-w180-seat.md` origin d3b0737fe（self-ack e069782f7）→ band gate `_r851bma_w180_bandgate.py` 四腿 ADMIT（receipt `_r851bma_w180_bandgate.json`）。

## r852 范围（= r849 先例逐段镜像）
1. prereg buildgen：`results/_r852bma_w180_buildgen.py`（AST 抽取 `results/_r849bma_w179_prereg_build.py` 的 BACK179+EXPECT；S80 map 见下）→ 产出 `_r852bma_w180_prereg_build.py` → `research/PERPETUAL_N1_W180_PREREG.md`
2. freeze buildgen：S80f 从 `results/_r849bma_w179_freeze_buildgen.py` 血统（PF_PAIRS/EN_PAIRS/MAT_PAIRS/CL_PAIRS AST 抽取 `_r849bma_w179_freeze_edits.py`）→ 五面插入（pf N1_BANDS[180] + n1 WAVE_CONFIGS[180]+materializer+PASS-claim）
3. banned gate `python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W180_PREREG.md` exit 0
4. pf selftest 9/9 + n1 selftest（含 W180 mat 腿）双绿 → 冻结 commit（surgical push 若撞 bm-b/bm-c 竞态）
5. 冻结落地后引擎 tick 自烧（本机 bm-a tick 架构·12 分片·PreIgnitionChecks 前置）

## W180 带位（r851 probe 机读·勿转抄 r587）
- A = **410_804..412_803**（naive 410_604..412_603 被 W179 B 带 410_604..410_803 拒于起点→阶梯 A-hops-prior-B **第四十例** E36·hops=1·A base==410_803+1）
- B = **412_804..413_003**（naive 410_804..411_003 CLEAN 但落本波 A 窗内→W141 leg2 同窗互斥·hops=1·B base==412_803+1）
- W181+ 投影（probe leg4）：A first-clean 412_804..414_803 hops=0 / B 413_004..413_203 hops=0（B inside A=True；W180 B 带注册后将拒 naive W181 A=阶梯第四十一例预期）

## W180 prereg 事实（全部 r851 窗机读核验）
- registry：177 行 tail=W179·owner 169 行·bm-a 95 行·第 170 波·bm-a 第 96 枚自有
- 账本锚头 **799,705**（W179 finalize r850 one-pass 落账·prev 797,505）·K=**391,720** 合并池
- 投影：null 池 391,720+2,200=**393,920**·账本 799,705+2,200=**801,905**
- W179 实测键（results/perpetual_faces/n1_w179_results.json·键名本窗核验）：merged mu −0.092733（4dp **−0.0927**·与 W178 同 4dp 无需滚）·w179_only mu **−0.093224**（4dp −0.0932）·mu_delta_w179_vs_w178ext **−0.000971**·merged sigma **0.245086**·se_mu_at_k391720 **0.000392**·A p95 **0.3265**（p99 0.4552·A mu −0.087915）·kl: line_merged_391720 **1.1850**·line_pre_w179 **1.1851**·delta **−0.0001**·n_eff_held_equal **797,505**·canon_flip NOT performed
- §5 预测锚滚面：w-only **−0.0923→−0.0932**·sigma 键 **0.245104→0.245086**·p95 锚 **0.3275→0.3265**·线锚 **1.1849→1.1850**·line_pre **1.1848→1.1851**·head **797,505→799,705**·K **389,520→391,720**·n_eff **795,305→797,505**·池投影 **391,720→393,920**
- SHAs：W179 freeze=**ef540bf8f**·W179 prereg 冻结时 blob=**6f14c35d5**（S80 transform 的 src=该 blob 的 W179 冻结时版本·非 r850 回填后版本）·W180 seat=**d3b0737fe**·self-ack=**e069782f7**
- @CHAIN@ 追加：`；W179=bm-a r849 freeze（ef540bf8f）`；@KLT@ 追加 `/W179 **−0.0001**`；@SEMT@ 追加 `→W179 **0.000392**`

## S80 pair 骨架（W179-era → W180-era·r735 序律）
- 会话复合（长先）：`已回填（r846 窗→r850 窗`·`r848 bm-a 带闸窗（pre-seat probe r848 单窗→r851 …r851 单窗`·`（r848 承袭→（r851 承袭`·`r848 probe 单跑兑现注记→r851 …`·`（r848 probe leg2/leg3 实跑）→（r851 …`·`r848 probe 回执 A_semantics 机读序数=THIRTY-NINTH→r851 …=FORTIETH`·`r844 probe leg4→r848 probe leg4`·`（r845 冻结件）→（r849 冻结件）`·`_r848bma_w179_probe_receipt.json→_r851bma_w180_probe_receipt.json`·`MSG-2026-10-07-2320-bma-w179-seat→MSG-2026-10-08-0030-bma-w180-seat`·`4c645c95f→d3b0737fe`·`【r849】→【r851】`
- 带几何（投影先于 naive·B 带先于 prior-B）：`410_604..412_603→412_804..414_803`（proj-A）·`410_804..411_003→413_004..413_203`（proj-B）·`410_604..410_803→412_804..413_003`（own-B）·`408_604..410_603→410_804..412_803`（own-A）·`408_404..410_403→410_604..412_603`（naive-A）·`408_404..408_603→410_604..410_803`（prior-B）·`408_604..408_803→410_804..411_003`（naive-B）·`408_603+1→410_803+1`·`410_603+1→412_803+1`·`408_604+j→410_804+j`·`410_604+j→412_804+j`
- 序数（高先）：`第四十例→第四十一例`·`第三十九例→第四十例`·`第 177 枚→第 178 枚`·`行 168+本候选→行 169+本候选`·`第九十五枚→第九十六枚`·`第 169 波→第 170 波`·`行 94+本候选→行 95+本候选`·`bm-a 94 行注册→bm-a 95 行注册`·`一百七十六行注册→一百七十七行注册`·`机证 176 行→机证 177 行`·`一百七十七面实测→一百七十八面实测`
- 数字（投影先·head 先于 n_eff）：`**391,720 投影**→**393,920 投影**`·`**1.1849**→**1.1850**`·`·line_pre 1.1848·→·line_pre 1.1851·`·`**0.3275**→**0.3265**`·`**−0.0923**→**−0.0932**`·`0.245104→0.245086`·`797,505→799,705`·`795,305→797,505`·`389,520→391,720`
- n1_w 形（高先）：`n1_w179→n1_w180`·`n1_w178→n1_w179`
- 波词级联（高先）：`W180→W181`·`W179→W180`·`W178→W179`
- 裸数余留：`波号 179=→波号 180=`·`--wave 179→--wave 180`
- FRESH 令牌：@S55@（W181+ 投影·用上面 probe leg4 值+「第四十一例」预期语）·@SEATPUB@（r851 seat push 直达+不再重送语+self-ack r851 同窗·r848 先例）·@ORDINALS@（第 170 波/第九十六枚/行 95+本候选/W179 追加最近自有波链/注册表 W179 行后/MSG 名+sha）·@OWNCHAIN@（`/W178 最近自有波→/W178/W179 最近自有波`）·@N171@→"180"·@N170@→"179"·@N169@→"178"（EXPECT 0 安全网）
- 血统 quirk 保留（r795/r845/r849 先例·如实披露）：@S5ANCH@「bm-a r839 承袭收口窗」stale 窗戳 verbatim 保留·@SEATSENT@「r841 席位/（r841 seat push」stale 戳 verbatim 保留·anchor 波词 off-by-one（prose 读「W180 finalize」但数字机滚正确 799,705/391,720）
- stale 扫描清单（W180 版）：`r848 probe 回执`/`（r848 probe leg2`/`r844 probe`/`r845 冻结件`/`已回填（r846 窗`/`4c645c95f`/`【r849】`/`THIRTY-NINTH`/`第三十九例`/`0.3275`/`0.245104`/`−0.0923`/`1.1849`/`389,520`/`797,505`（注意 n_eff 797,505 是合法新值——stale 检查须排除 @KLKEY@ 的 n_eff 面·用「净账本锚头 797,505」整串作 stale 探针）
- 双读法恒等：投影与回执序数面一致（r849 律「投影和回执序数 MATCH」——W180 检查：seat MSG leg4 预告第 40 例==probe 回执 FORTIETH ✓ 已核）

## r851 产证物清单（commit 收口用）
- results/_r851bma_w180_probe.py + _r851bma_w180_probe_receipt.json（已推 origin）
- fleet/inbox/processed/MSG-2026-10-08-0030-bma-w180-seat.md（已推 origin）
- results/_r851bma_w180_bandgate.py + _r851bma_w180_bandgate.json（本轮收口 commit）
- results/_r851bma_s80_grnd.py/.txt + _r851bma_w179_keys.py/.json（S80 grounding 证据·收口 commit）
- 本件 results/_r851bma_w180_seat_chain_continuation.md（收口 commit）
