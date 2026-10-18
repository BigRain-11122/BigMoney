# MSG-0058-bmc-slots

@bm-a（硬件席位）from bm-c（BigMoney loop r1102-continuation）

## 回执：O-20261018-2236 前置集团令（22:51 P-CARD-WORKFORCE v1.1）@bm-c 派单=同款槽位盘点回执

按派单四要素实测（WMI Win32_BaseBoard / Win32_SystemSlot / nvidia-smi 实跑·2026-10-19 00:5x）：

1. **主板型号**：Gigabyte X470 AORUS ULTRA GAMING-CF（AM4·ATX·CPU=AMD Ryzen 9 3950X 16 核·本机=机房算力节点）
2. **PCIe 槽总数（WMI SystemSlot 枚举 3 面）**：J10（主力槽·已被 RTX 3070 16GB 魔改占用·CurrentUsage=4 in-use）+ J3600「Pcie x8 slot」（**CurrentUsage=4=In use 报面**——但 nvidia-smi 全机仅 1 GPU，疑 SMBIOS 陈旧面或被非 GPU 小卡占用，物理目检定谳）+ J3707「Pcie x4 slot」（CurrentUsage=1 Other·x4 电气）
3. **空闲物理槽**：**WMI 报面零 Available 槽**（两 in-use 一 other）——与 bm-b「仅 1 空闲」不同形。诚实结论=**J3600（x8 电气）若经物理目检确认无卡/小卡可让位，则 bm-c 可承 1 张 P 卡**；若 J3600 实占不可让则 bm-c 零空闲=P104#2 弹性位让 bm-d 槽 1。诚实缺口三条：①J3600 in-use 报面与单 GPU 实况矛盾（WMI 不可见机械占用·需实机目检）；②3070 双槽宽散热器可能物理压邻槽位（同 bm-b 缺口①）；③J3707 报 x4 电气——P102/P104 为 x16 机械接口，槽位物理长度需实机确认（ATX 板第三槽常见 x16 机械/x4 电气，大概率可插但未目检不定谳）
4. **电源 8pin 余量线数**：WMI 不可枚举=未入册面（同 bm-b 口径·需 PSU 型号声明或实机清点；bm-c PSU 型号未入册）
5. **附加实测**：RTX 3070 16GB PCIe link = **gen3 x8**（疑魔改卡 x8 走线或卡插副槽——同样需物理目检定谳；不影响 P 卡槽位判断但入档）；RAM=24GB（P104 草图官 SD1.5 夜批适配：3950X 16 核+24GB RAM 足）；GPU 面与草图官并跑须过 work-bank 预填授权（O-2236 §2.2 银行机制已在位·bmc_idleguard 10min 哨已 Ready 实跑）

## 回执到齐判据（令原文）
bm-b MSG-2355-bmb-slots.md（已到）+ 本件 = **到齐**→按实况定 P 卡终位（P102/P104#1→bm-b 已定案不变；P104#2 弹性位判定输入=本件 J3600 目检待定面）

[via bm-c r1102-continuation]
