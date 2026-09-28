# POOL_RETIREMENT_S1_CENSUS —— T-2026-09-29-116 s1 消费面普查（results/runnable_pool.json 读者全清单）

- 法源：T-2026-09-29-116-P1（spec=O-1855(2) 评估窗开票·D-20260928-03(1) 结构终态）＋前史正典 research/LANE_MIGRATION_S1.md（bm-a r370-r390 车道迁移全链——本件零重建，只做池面专用消费普查）。
- 产出轮：bm-c r195（2026-09-29）。方法=全仓 grep `runnable_pool`（.py/.ps1/.html/.js/.md 全类型·生产目录扫描含 scripts/monitor/Tools/config/live/engine/根 py）→ 逐读点实读分类；历史一次性件与纯文本引用单列不计入消费面。
- 零回测零引擎零判据面——工程普查件，非预注册批。s1 交付面=本表；s2/s3/s4 按 T-116 spec 序推进。

## 一、常设生产读点（standing consumers）

| # | 读者 | 读点（实线号） | 读面 | 读语义 | 迁移注记 |
|---|---|---|---|---|---|
| 1 | Tools/autofill.py（tick 引擎·10min schtask） | POOL 常量 L85；claim fresh-read L843；keepalive L992；runner-shard 扫描 L1122；harvest L1347；origin 守卫 `_pool_origin_stale` L164（claim L896/keepalive L1029 调用） | **共享面 fresh 全量读**（每决策点重读）＋origin 三点差分守卫 | full load ＋ keyed（entry id×shard key 双键·r141）＋ status 扫描 | 池最高权威执行体；写侧已 lane-first-strict＋settle union 写回（r388 `_POOL_LANE_PRIMARY=True`）；迁移窗执行权威=共享面（r410 坑律七十七批实证） |
| 2 | Tools/pool_worker.py（跨公司工人·T-113 s2·schtask） | POOL L57；`_load_pool` L407-419 | **origin blob 优先**（`git show origin/main:results/runnable_pool.json`·r404-cont 防重烧）＋本地文件回退 | full load → ready/shard status 扫描＋worker_class 资格＋claims 新鲜度 | 池零写（claim-by-file 律）；**option (b) 废共享面=破坏单 blob origin 读协议**（须改三 blob union·s4 设计输入） |
| 3 | Tools/resident_dispatcher.py（30s 预检·T-108 D2·1min schtask） | POOL=af.POOL L63；本地 mtime+full load L155；cached-origin sha+full load L174；takeable 扫描 L183-203 | 本地面＋cached-origin 面（零网络） | status 扫描（lane 兼容 ready shard）→转派 autofill tick | churn gate 锚「池 mtime/origin sha 变化」——option (b) 下须重锚车道面 |
| 4 | Tools/fill_ladder.py（供给地板·T-107 slice-2·dispatcher 采用） | shared L54（lane L55 仅写侧）；full load L184-185 | **共享面 only**（读侧无 lane/合并视图） | status 扫描（ready 计数 vs floor）＋ keyed（existing_ids 幂等）＋judge 族 status 扫描（standing_no_judge_inflight 门） | 写侧=double-file（共享+lane 同字节·r399 律）；读侧切 merge-on-read=s3 wave 候选 |
| 5 | scripts/compute_audit.py（S6 审计腿·每轮） | `pool_ready_count` L193-200；`pool_ready_entries` L291-313（sample L446-466 消费）；sync 写手 L501-524 | 共享面 | status 扫描（ready 计数/未认领明细/armed_at/claimed） | **兼=终态生成器**：L513 `sync_face("runnable_pool")`＝合并配方双向 settle（r385 slice-5）——option (a) 派生视图的再生成腿本体 |
| 6 | monitor/build_status.py（总控面板宿主=bm-a） | `_lane_view("runnable_pool")` L431/481/1886 | **合并视图**（merge_lane_views.face_view·r374 已切） | full load（面板渲染） | 已切零动作；HTML 面（bigmoney/dashboard/town.html）**零直读**（消费 dashboard_status.json 间接面） |
| 7 | scripts/daily_report.py（每日战报·S6 腿） | `_lane_view("runnable_pool")` L120 | **合并视图**（r374 已切） | full load（聚合行） | 已切零动作 |

## 二、基础设施件（非消费面但读写面在册）

- **scripts/merge_lane_views.py**：合并器本体（`merge_runnable_pool` L351＝marker 律/done 吸收/治理字段非空优先/分片 key-union 全配方）＋`face_view`/`sync_face`/`resolve` 三口。共享件=legacy source #0 恒在源序首位。**s2 spec 面（merge-on-read helper）已被此前工作实质交付**（r374 消费切换+r382 face_view 基座+r385 sync_face）——T-116 s2=零重建，仅剩按 s3 双跑对账契约消费。
- **config/lane_io.py** L36：`_KNOWN_FACES` 注册（镜像族）；池镜像已移出 mirror 族改 sync_face（r385）。

## 三、一次性/解析期件（非 standing·零迁移义务）

- scripts/governance_audit_s1.py L146（治理审计枚举器·--as-of 定日重跑·id+status 投影）；Tools/skills/bigmoney-conflict-resolve/scripts/classify_conflicts.py L116（UU 路由·读冲突 blob 非活件）；Tools/_r200/_r201/_r404/_r408/_r409 与 results/_r*.py（历史 flip/resolve 证据件）。doc 面（iteration_prompt.txt/CODELY.md/orders/tasks/research 正典引用）=文本引用非读点。engine/live/tests/根 py/*.ps1/*.html＝**零命中**（实测 2026-09-29）。

## 四、s3/s4 设计输入（普查结论）

1. **共享面现状已半终态**：r388 后 tick 写=lane 权威记录＋共享 union 写回；共享面仅剩三类手写残点=fill_ladder double-file 写、会话一次性 defer/flip 脚本、（潜在）未来批 runner 注册件——s4「grep zero 手写」验收的真实剩余面。
2. **wave 划分**：wave-1=决策读点切 merge-on-read（#1 autofill fresh-read 族、#4 fill_ladder 读侧、#5 compute_audit ready 扫描；#2/#3 读 origin/缓存 origin 面=git 传输面，跟随 s4 拍板再动）；wave-2=已切面板面（#6/#7）零动作确认。双跑对账=`face_view==shared` 断言连续 3 tick 零漂移（r374 先例仪器现成）。
3. **s4 拍板关键事实**：option (a)（派生视图保留）保 pool_worker 单 blob origin 读协议与 dispatcher churn gate 锚——工程代价最小；option (b)（废共享面）破坏上述两面＋三机 git 传输契约，代价集中在跨公司工人端。普查证据倾向 (a)（终局裁决归 s4 切片，非本件越权）。
4. 下轮指针：s3 wave-1 起草（autofill 读点切 face_view 的中途窗安全分析——tick 写侧 settle 与读侧 merge 的重入序）＋双跑对账 harness 接线。
