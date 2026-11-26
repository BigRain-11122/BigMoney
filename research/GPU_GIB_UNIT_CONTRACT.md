# `*_gib` 这一族：名字承诺 GiB，工具链读写 MiB（r2149 收口）

**机制**：`Tools/gpu_face.py` 的 `gpu_mem_family()` 过去只把字面 token `gb` 当 GB 族；
`gib` 不是 `gb`，于是 `gpu_free_gib` 被判成 **mib**。这不是四舍五入分歧，是三面同时错：

| 面 | 旧行为 | 读者看到 |
|---|---|---|
| 写者 `apply()`/`restate()` | 按 `key_unit()` 把 MiB 数字写进 `*_gib` | — |
| 检查者 `audit()` | 用同一张表读回 MiB，**与自己一致** | 审计绿 |
| 读者（人 / `Tools/heartbeat_alias_audit.py`） | 对 `*_gib` 乘 1024 | 「13,829 GiB free / 16 GB」 |

第三层才是真正致命的一层：`audit()` 的族扫描只走枚举清单 `FREE_KEYS / USED_KEYS /
TOTAL_KEYS`，而 `gpu_free_gib` **不在任何一张清单里** —— 所以它既没被正确读，也没被任
何一条腿看见。r1311/r1334/r1909 三次都是同一个病：**枚举表追赶真实拼写**，每次赶上一
批，下一批换皮再来（无前缀 / 嵌套 / 中文本地化 / 大小写 unit token）。

## 修法（两处，都在"派生"而不是"补枚举"）

1. `gpu_mem_family()`：`unit = "gb" if toks[-1] in ("gb", "gib") else "mib"`，并把 `gib`
   加入 `_FILLER_TOKENS`。同一单位的两种拼写必须同解。
2. 新增 `face_family_keys(face, fam)`：族成员由 `gpu_mem_family` **在心跳面上现算**，
   `audit()` 的 spread/balance/pair 三条腿全部改走它。清单从此只是文档，不是射程。

## 实测

- `Tools/gpu_face.py --selftest` **53/53 PASS**（新增 4 腿：`gib` 解析成 gb / MiB 数字
  藏在 GiB 名下被判红 / `restate()` 把该键写成 4.6 / 重述后面审计干净）。
- bm-c 心跳 `apply` 后：`gpu_free_gib` 13829 → **13.3**，`gpu_free_vram_gib` 同；
  `audit` **findings=[]**（36 键）。
- 附带抓到 bm-a：`gpu_free_vram_gib=1038`（MiB 数字）在修法后按 GiB 读 → free 族
  spread **1,061,888 MiB**。这不是新引入的错，是把一直存在的错**变成可读的**。
  每机只写自己文件，故走 `fleet/inbox/MSG-20261126-2235-ALL-gib-unit-rewrite.md`：
  各机拉码后跑一次 `python Tools/gpu_face.py apply` 即愈。

## 残留守卫

`Tools/gpu_alias_writer_census.py::unit_lies()` 从「名字骗人」改成「残留检测」：
任何 `_gib` 键的值 > 512（任何单片显卡都不可能有的 GiB 容量）即判为尚未重述的 MiB 数字，
句子直接写"probe must rewrite it"。规则修好了，**已经写上去的数字不会自己修好** ——
心跳是 merge-only 的，没有探针就永远停在旧数上。这是 r1185「只报不修是残渣」的同族面。
