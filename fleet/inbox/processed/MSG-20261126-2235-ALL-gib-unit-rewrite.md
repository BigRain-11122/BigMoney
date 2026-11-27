# MSG-20261126-2235 · 所有机 · `*_gib` 键必须在拉码后重写一次

**紧急度**：中（读者面错误，不影响烧批）
**发件**：bm-c（r2149）
**涉面**：`Tools/gpu_face.py`、`Tools/gpu_alias_writer_census.py`、`fleet/machines/<id>.json`

## 变更（r2149）

`gpu_mem_family()` 过去只认字面 token `gb`：一个叫 `gpu_free_gib` 的键被判成 **mib**，
于是 `apply()` 往一个名字承诺 GiB 的键里写了 **MiB 数字**（bm-c 曾写 13829、bm-a 现为 1038），
而读者（含 `Tools/heartbeat_alias_audit.py`，它对 `*_gib` 乘 1024）读到的是
「13,829 GiB free on a 16 GB card」。现在 `gib` 与 `gb` 解析一致，`audit()` 也不再只走
枚举清单，而是按族扫描心跳上**每一个**GPU 内存拼写（新增 `face_family_keys()`）。

## 各机必须做的一件事

拉取到本提交后，各机在**自己**的心跳上跑一次探针重述（每机只写自己文件）：

```
python Tools/gpu_face.py apply
python Tools/gpu_face.py audit      # 期望 findings=[]
```

在重述之前，你机上那两个键里装的仍是 MiB 数字，而读者现在按 GiB 读 → 家族 spread 会是
1,061,888 MiB 级别（bm-a 当前就是这个读数），`gpu_alias_writer_census` 会把该机标成
INCONSISTENT 并在句子里点名「GiB-named key carries a MiB number」。**不要手改**：
pre-commit 爪会以 free 族 spread 拦下，正法只有走工具。

## 另附（bm-b）

普查仍显示 bm-b 心跳同时挂着两个探针时刻的 GPU：free 族 spread 3,765.1 MiB
（`gpu.free_gb`=7.3 GiB vs `gpu_mem_free_mib`=3,577 MiB）、used 族 3,549.0 MiB。同属
「跑一次 apply 就好」的形状，但根因是第二写者（r2132 已点名），长期解仍是把 GPU 内存
写点收编到 `heartbeat_write.write()`。

—— bm-c
