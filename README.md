# Harness 可视化对照演示

本仓库用于展示同一个工程任务在 PLAIN 模式和启用 Harness 能力后的结果差异。项目现在按前后端两个独立服务组织：Python 后端提供可运行的命令行对照实验，React 前端将用于构建 Harness Lab 可视化对照界面。

## 目录结构

```text
demonstration/
├── backend/    # Python 3.12 + uv，真实 LLM Harness 演示
├── frontend/   # React + TypeScript + Vite，可视化界面
├── docs/       # 项目级设计文档
└── openspec/   # OpenSpec change、spec 和任务记录
```

## 当前状态

- 后端 Demo 1–6 已实现，分别对比项目上下文、受限工具行动、测试反馈、边界审批、跨会话状态和版本化外部依据。
- Harness Lab 页面已实现能力选择、真实运行、结论优先的对照摘要、阶段对齐和结构化证据展示。
- 当前可读性改进记录在 [improve-comparison-readability](openspec/changes/improve-comparison-readability/) change 中。

## 后端

所有 Python 命令都在 `backend/` 中执行：

```bash
cd backend
uv sync
cp .env.example .env
```

配置 `.env` 后查看或运行演示：

```bash
uv run harness-demo list
uv run harness-demo 1
uv run harness-demo 1 --harness
```

### 工作区与重复运行

Demo 会在 `backend/.demo-workspace/` 中运行，不会直接修改原始夹具
`backend/fixtures/shipping/`。每次运行开始前，系统都会删除对应的内部工作区，并从夹具重新创建一份干净副本；因此可以安全地重复运行同一个 Demo 或依次运行不同 Demo。

| Demo | PLAIN | HARNESS | 可写入范围 |
| --- | --- | --- | --- |
| 1：项目上下文 | 只读分析 | 只读分析 | 无 |
| 2：受限工具行动 | 仅生成代码建议 | 可实际读取、写入并测试 | 仅 `src/shipping.py` |
| 3：测试反馈循环 | 写入一次生成结果后评价 | 可在每轮反馈后继续修复 | 仅 `src/shipping.py` |
| 4：边界与审批 | 较宽但仍受限的合成工作区写入，无审批 | 首次写入需批准，仅 `src/shipping.py` | 依策略而定 |
| 5：跨会话状态 | Session B 不接收 Session A 状态 | Session B 读取经校验的 `handoff.json` | `src/shipping.py` 与一次性交接记录 |
| 6：外部依据 | 使用明确过期的缓存政策 | 读取本地模拟 provider 的当前版本化政策 | 仅 `src/shipping.py` |

每个 Demo 与模式使用不同目录，例如 `demo-2-plain/` 和 `demo-2-harness/`，两者互不影响。再次运行相同的 `Demo + 模式` 会覆盖该目录中的上次结果；如需保留某次运行后的 Diff，请先复制或查看其工作区。Demo 4 的 HARNESS 侧会在首次有效写入前等待批准；拒绝或超时显示“控制门禁已生效，任务未执行”。Demo 5 的交接记录只存在于本次工作区；Demo 6 的 provider 是本地模拟数据，不访问网络。

完整配置、Demo 命令和安全说明见 [backend/README.md](backend/README.md)。

## 前端

所有 Node.js 命令都在 `frontend/` 中执行：

```bash
cd frontend
npm install
npm run dev
```

前端需要后端 API 时，另开一个终端：

```bash
cd backend
uv run uvicorn harness_demo.web.app:app --host 127.0.0.1 --port 8000
```

当前可用检查：

```bash
npm run lint
npm run test
npm run build
```

前端现状和脚本说明见 [frontend/README.md](frontend/README.md)。

能力卡片上的“查看任务”会显示该 Demo 的 PLAIN/HARNESS 条件、完成定义、预期证据和讲解提示。组件映射说明六个 Demo 如何解释培训中的 11 项 Harness 组件；它不是一对一覆盖率，子 Agent 编排在本轮没有单独 Demo。

## 文档

- [Harness 演示设计](docs/DESIGN.zh-CN.md)
- [前端可读性改进提案](openspec/changes/improve-comparison-readability/proposal.md)
- [前端可读性技术设计](openspec/changes/improve-comparison-readability/design.md)

真实 LLM 输出存在波动。本项目展示具体运行中的上下文、行动和反馈差异，不是统计意义上的模型 benchmark。
