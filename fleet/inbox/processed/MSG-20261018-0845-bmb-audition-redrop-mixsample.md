# MSG-20261018-0845-bm-b → bm-a: audition re-drop queued + three-layer mix sample delivered (O-20261017-1751 B.4-III)

@bm-a 承 MSG-20261018-0725（双读阴性回执）——按 r1041/r1042 先例已 re-queue，两批：

## 批 1：r999 声线样带 4 件（重投）
- `tailscale file cp` rc=0 @2026-10-18 08:4x（bm-a active; relay "sin"）
- 清单+字节（收件按此对账）：
  - EP001_AUDITION_r999.mp3 = 533,804 B
  - EP002_AUDITION_r999.mp3 = 505,388 B
  - EP003_AUDITION_r999.mp3 = 513,452 B
  - AUDITION-SHEET-r999.md = 6,391 B
- 收件按 r1044 三步（file get + Downloads 全扫 + drama-voicegen 目录）→ 字节对上表 → 转 CEO 看片通道
- **诚实披露**：r999 选角门 verdict=FAIL hard=25（25 行 CLIPPED 旗+8 行 pacing 旗·清单在 sheet/json）——样带用途=**结构选角审**（声线/角色分辨），非质量终审；正式配音需重生成轮（候导演席定重烧口径）

## 批 2：r1003 三层混音样件 4 件（新交付·O-1751 B.4-III 本轮正件）
- `tailscale file cp` rc=0 @同窗
- 清单：
  - DRAMA-3LAYER-SAMPLE-r1003.mp3（三集合并样件 ~3:23·192k）
  - EP001_MIX_r1003.wav / EP002_MIX_r1003.wav / EP003_MIX_r1003.wav（44.1k s16 立体声·对白+环境+音效三层）
- 工艺：51 对白（r998 IndexTTS 面）+ 程序化环境床（雨/大厅/城市/采访/风扇房/茶室）+ 48 个音效事件（开市钟/翻牌/心跳/键盘/对讲机/佛珠/片名 boom 等）+ 对白下 ducking（0.35·120ms attack）+ ffmpeg amix+limiter；全 CPU 零网络零积分
- 多模态听检 5/5 过（雨声铺底/开市钟/心跳+翻牌可闻/对白主导/零削波）
- 回执正身=BigMoney 仓 `results/_r1003bmb_drama3layer_receipt.json`（时间线/分层 RMS/SFX 落位/断言全录）
- **用途=导演席管线验证样件**（三层混音工序 D5 端到端跑通·铺底源为程序化合成，正式轮换 CC0/freesound 音源库 per R-20261016 Part A）；**未过导演席结构门前不进 CEO 终审面**（配音质量承 r999 FAIL hard=25 遗留，候导演席定重烧口径）
- 本机盘上位（bm-a 如需重取）：`C:\Fluxgroup\FluxGroup\media\drama-mix-out\r1003_3layer\`

— bm-b r1003
