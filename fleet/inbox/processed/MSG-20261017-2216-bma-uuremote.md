# MSG-20261017-2216-bma · UU 远控开启回执（O-20261017-2207-bm-c 受理）

- 软件真名: UU远程（网易 GameViewer）v4.43.1.3614（Uninstall 注册表 DisplayName=UU远程）
- 安装路径: C:\Program Files\Netease\GameViewer\（GUI=bin\GameViewer.exe；服务=GameViewerService.exe --service）
- 状态: **已在跑**——无需启动动作；服务 + 被控服务端 + 健康守护三件齐活，CEO 可直接连入
- 进程证据（2026-10-17 22:15 实测，Win32_Process census）:
  - GameViewerService.exe PID=68620 SessionId=0 服务面（Win32_Service: State=Running / StartMode=Auto / started 22:03:25）
  - GameViewerServer.exe PID=77612 **SessionId=1（控制台交互会话≠0）** started 22:13:28
  - GameViewerHealthd.exe PID=102364 SessionId=1 started 22:13:28
  - quser: console 会话 ID=1 (sjs20, 活动中, 自 10-15) + UU 虚拟显示会话 ID=3 (21:51 建立过一次远控会话)
- 启动方式: 已在跑（服务 Auto 自启+自愈维持）。零手工启动。注记: 22:12 首扫时 Server/GUI 曾在 UU 虚拟会话 SID=3（对应 21:51 那次远控连接），22:13:28 软件自身已在控制台 SID=1 重建 Server/Healthd——本机全程零动作，无需一次性交互任务法（该法已备未用）。
- 服务组件确认: GameViewerService = Running / Auto ✓（§4 达标）
- 结论: 被控端就绪（Server+Service 落交互会话），无需任何账号动作；若 CEO 连入仍黑屏→如实回告，续查虚拟会话链路（本回执只报状态零催办）。

—— user (Jason) via bm-a · r1041 S0.5 即办回执 · 2026-10-17 22:16
