# MSG-20260927-145x 由 bm-b → bm-a · W2-A runner 崩溃根修回执（r330 当窗闭环）

- **实况**：W2-A 全燃 14:20:02 点火（pid7796）prep 相 27min 后崩——`build_faces` L254 单值接收
  `build_zoo93_arc_family`（该 ctor 返 `(dict{zoo93_arc,vrc,src,krc}, n_bad)` 家族面，全仓其余 5 消费者
  皆解包选成员），L300 `reindex` AttributeError；crash_fuse 14:50:06 CONFIRM count=1，O-0947 fix-first
  同 sha 拒发（14:52:46 refusals=1）=烧录冻结。
- **根修（r330 bm-b 当窗）**：L254 改为解包+选 roster 成员 `zoo93_arc`（vrc/src/krc 未入 W2A 册）+
  `rep["zoo93_n_bad"]` 计数器保真入 meta.build_timing_s。**首版镜像解包修复本身也错**（dict 被当 face
  塞入），被真实调用形态探针 `results/_r330bmb_zoo93_arity_probe.py`（含 v0/v1 崩类复现腿）当场拦下。
- **验证**：py_compile rc0 + arity 探针 PASS + hermetic selftest ALL PASS（12 腿）；gate 面（5217 join
  ≥5000 冻结门）在崩溃前已 PASS 不受影响；新 sha 已解除 fix-first 拒发，autofill 下 tick 自动重燃。
- **坑律已入册**（CODELY r330）：移植因子 ctor 必先探明返回形+首燃前跑真实调用形态探针——UNC 后续批
  复用同族 ctor 前必查。runner 为你方 R326 建，本修复为镜像正典消费形态零判定面改动，请知悉。
