# Harness Lab 前端

这是 Harness 可视化对照演示的前端服务，使用 React、TypeScript 和 Vite。

Harness Lab 提供六类可运行 Harness 能力：Understand、Act、Prove、Control、Continue 和 Ground。页面在运行中展示 PLAIN → HARNESS 的语义步骤，完成后先给出带“本次运行”限定的结论和能力指标，再按信息、行动、审批、交接、依据、验证、反馈和结论对齐两侧过程。

模型完整输出、Diff 和测试日志默认收在类型化证据中。页面底部的“完整记录”区域用于排错，可按全部、PLAIN 或 HARNESS 筛选，不影响默认讲解流程。

每项能力都有“查看任务”弹窗，说明共享业务目标、两侧条件、完成定义、证据和讲解提示。组件映射说明六个结果导向 Demo 与培训的 11 个 Harness 组件之间的主要/支撑关系；它不是一对一覆盖率，子 Agent 编排在本轮没有独立演示。Control 的审批仍以内联时间线卡片处理，任务弹窗不负责审批。

详细页面与接口设计见：

- [OpenSpec proposal](../openspec/changes/improve-comparison-readability/proposal.md)
- [OpenSpec design](../openspec/changes/improve-comparison-readability/design.md)

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
