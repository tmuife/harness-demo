# Harness Lab 前端

这是 Harness 可视化对照演示的前端服务，使用 React、TypeScript 和 Vite。

Harness Lab 提供六类可运行 Harness 能力：Understand、Act、Prove、Control、Continue 和 Ground。页面在运行中展示 PLAIN → HARNESS 的语义步骤，完成后先给出带“本次运行”限定的结论和能力指标，再按信息、行动、审批、交接、依据、验证、反馈和结论对齐两侧过程。

模型完整输出、Diff 和测试日志默认收在类型化证据中。页面底部的“完整记录”区域用于排错，可按全部、PLAIN 或 HARNESS 筛选，不影响默认讲解流程。

首页以 11 个组件的教学架构图为入口。选择组件后，右侧直接展示职责、关联 Demo、任务目标、PLAIN/HARNESS 条件和观察重点；多个关联实验可以单选切换。点击组件不会启动模型调用，只有“开始对照”会创建真实实验。

顶部“查看业务背景”解释共享运费场景，“查看完整任务”补充当前 Demo 的完成条件和讲解提示。Understand 是只读分析；Control 的受控停止与任务完成分开表达；Ground 的外部依据为本地模拟。组件与 Demo 是主要/支撑关系，子 Agent 编排目前仅提供职责说明。

开始后页面进入实验工作台，保留任务入口和观察阶段定位。运行中锁定配置，Control 审批保持内联可操作；刷新会恢复最近实验和待审批状态。完成后可返回架构继续探索，最近结果始终标记原 Demo，不随新选择改变归属。完整记录中的审批只作为历史展示。

窄屏使用分组组件列表，并提供“查看所选组件与任务”定位；节点、实验选择和详情支持键盘与减少动画。

本阶段直接连接现有后端，不请求新的组件目录接口。`src/features/experiment/explorer.ts` 集中维护教学布局、组件职责和任务摘要回退，能力状态、关联关系与运行证据仍来自 API。后续后端收敛范围是组件说明/分组、业务背景和逐项任务目标/完成条件，需在前端评审后单独决定实施。

详细页面与接口设计见：

- [架构探索首页提案](../openspec/changes/add-harness-architecture-explorer/proposal.md)
- [架构探索首页设计](../openspec/changes/add-harness-architecture-explorer/design.md)
- [现有对照与接口设计](../openspec/changes/improve-comparison-readability/design.md)

## 本地开发

以下命令均从 `frontend/` 执行：

```bash
npm install
npm run dev
```

先在另一个终端启动后端 API：

```bash
cd ../backend
uv run uvicorn harness_demo.web.app:app --host 127.0.0.1 --port 8000
```

Vite 会在终端输出本地访问地址，并将 `/api` 请求代理到 `http://127.0.0.1:8000`。如部署在不同地址，可使用公开的 `VITE_API_BASE_URL` 配置 API 根路径；不要在任何 `VITE_` 变量中放入 API Key 或其他秘密。

## 检查与构建

```bash
npm run lint
npm run test
npm run build
npm run preview
```

- `lint`：运行 Oxlint。
- `test`：运行 Vitest 与 Testing Library 单元测试。
- `build`：执行 TypeScript project build 并生成 Vite 生产构建。
- `preview`：本地预览已生成的生产构建。

不要在 `VITE_` 环境变量或浏览器代码中放置 OpenAI API Key 等秘密。LLM 调用、工作区访问和测试执行应始终由后端负责。
