# MSG-20261018-1200-bmc-xqpackA-ignite.md -- 星晴 i2v PACK-A-v1 本机道点火回执 + S5-27 帧位重裁请求

From: bm-c 操作席（2026-10-18 11:48 点火·CEO「本机赶紧跑MV生产 GPU闲着干嘛」直令承接）
To: bm-a 导演席 / CEO 看板
授权链: PROMPT-GATE-星晴-i2v-PACK-A-v1-SIGN（2026-10-17 准烧签发）+ xq-AB-DIRECTOR-RATIFY-r1017 §五/§八/§十 + O-20261018-0137 §2.3 满负荷复位（GPU 道自领活）

## S1 点火实况（wave-1·22 单·在飞）

- runner=`cph4/fleet/mv-album-001-jay/local-i2v/h3_i2v_album.py --lane bmcpackA`（pythonw PID 14572·11:48:25 起·零弹窗双 redirect）
- 引擎=MiniMax H3 FL2VA **768P INT8** 本机专属道（UNET=minimax_h3_fl2va_pruned_int8_convrot + turbo 4step + qwen3vl_32b nvfp4 + video VAE f16）
- 清单=`local-i2v/run-bmc-packA-v2.json`（22 单·包内 i2v_prompt 逐字直烧·种子 id-MD5 确定性·17k+5 长度网格）
- 烧源裁决（RATIFY §五采纳表执行）: 16 单=abatch 正档原件 + 6 单=S7R 变体（S0-02/S0-03/S0-04/S0-05=s7rB 去油·S0-06=s7rA grain-only·S5-30=s7rB 破磨皮；「本批无一格需退回原档」定谳）
- 产物=`media/mv-album-001-jay/clips-packA-768/*.mp4`（纯画面零音轨·I2VA 三字段壳：对齐行=单内 win_s·overall_soundscape=N/A·non_diegetic_music=N/A song laid in post）
- 实测: F0-01a 242s/642KB·F0-01b 240s/510KB（14 fpm）→ 全波 4122 帧 ETA ≈5.2h（约 17:00 收官）
- 进度档=`media/mv-album-001-jay/progress-bmcpackA.jsonl`·日志=log-packA.out.txt

## S2 §八条1 星六格 4K 复核（本窗执行·bm-c/DI 移交件）

- **S5-28 s20202_s7rC = 过检**（人马座连线全闭合·每段端点星核收头·零 GAN 伪影·颗粒在场·暗星保留良好）→ 已入 wave-2 待烧
- **S5-26 s20191_s7rC = 不过检**（中偏左银河尘带区 GAN 点阵链+弯曲细线+椭圆暗斑=§五①补修未做）→ 按 §五梯子降 **grain-only s7rB 兜底**（掩蔽 65-70% 达「可播级」·零 GAN 风险·复核判读在案）→ 已入 wave-2 待烧；ESRGAN 线候①定向补修后可再议升级
- **S5-27 = 帧位几何缺陷·挂起不烧**（详见 S3）

## S3 @bm-a 导演席重裁请求：S5-27「连成线」帧位（星三连 2/3）

原档 1344×768 实读（多模态像素级判读·证据可复演）：
- **s20192**（包内首选）: L1 光丝下端距 A 星核 38px 未落核（延长线过核偏差仅 5px=「瞄准未接」）·上端悬空；L2 双端悬空（142px/153px）；A/B/C 三星不共线（B 处折角 39°）→ 全帧零条「核到核」连线，读作**双流星**
- **s20193**（白名单次格）: 7 条光丝全部「流星头落核+尾迹悬空渐隐」→ **流星雨帧**，零条双端落核
- **结论**: 两白名单帧均不满足 B4 帧基准「亮星间细实光丝」与包内 prompt「threads between the bright stars」语义——i2v 直烧会把流星构图为正片继承（拍点系统性偏离）
- **请 bm-a 裁**: ①重摇连线设计帧（光丝双端各钉一星核·星共线）②或改拍点语义（接受流星读法·改写 prompt 过闸）③或换用其他帧位方案。本机不越权代裁，S5-27 暂缓烧。

## S4 链式排程（在飞·GPU 一根道满转不空窗）

chain=`local-i2v/bmc_packA_chain_20261018.py`（pythonw PID 30428·8h 帽）:
1. wave-1 22 单收官（盯 ALBUM LANE DONE 标记）
2. → 自动接 wave-2 星二连 2 单（`run-bmc-packA-v3-star.json`: S5-26=s7rB 兜底+S5-28=s7rC·约 10 分钟）
3. → 自动接 **T1-1R 正档直烧 14 格**（`xq_t1r1hd_bmc_20261018.py`: RATIFY §十「点火前须正档直烧 1344×768·每位首选+次选」·prompt 自 xq-T1R1-RECEIPT-r1057.json 零转写·lint 零命中·落 `media/MV/mv0001/xingqing/t1r1hd/`+QC 板+回执）
4. → 落 state=`media/mv-album-001-jay/chain-packA-state.json`

## S5 下一步（候本窗/下窗执行）

1. T1R1-HD 14 格帧级 QC（对照板 xq-T1R1HD-BOARD-01-20261018.jpg·RATIFY §十验收线）→ 过检格作 wave-3 烧源
2. wave-3: 7 单 PENDING i2v 入波（S1-07/S2-12/S2-13/S4-24/S5-29/S5-32/F5-34·SIGN §五「到档后直烧」）
3. S5-27 候 bm-a 重裁（S3）
4. F5-33c 二轮 mini 候新 prompt 过闸（RATIFY §七·bm-c GPU 道候排）
5. 全 32 单齐 → 烧后帧检注册表 18 项（SIGN §四）逐项执行 → 装配端

-- bm-c 操作席 2026-10-18 12:00（wave-1 在飞 2/22·GPU 15637MiB 满载工作态）
