## Why

当前项目只有 Understand、Act、Prove 三个可运行对照，Control、Continue、Ground 仍处于设计状态；同时六个面向结果的 Demo 与培训 PPT 中 11 个 Harness 工程组件之间的关系没有在产品中明确呈现。需要完成六个真实 LLM 对照并补足任务说明、组件映射和客观证据，使现场讲解既保持简洁，又能与 PPT 的架构内容形成可追踪的闭环。

## What Changes

- 保留六个结果导向 Demo，不按 11 个组件拆成 11 个独立实验；为每个 Demo 标注一个主要能力、支撑组件、唯一实验变量和未覆盖范围。
- 完成 Control、Continue、Ground 的 PLAIN/HARNESS 后端流程、CLI 入口、Web 编排、结构化事件、确定性评价和安全测试，使六个 Demo 均可真实运行。
- 补强 Understand、Act、Prove 的演示证据，显式展示上下文/提示词装配、结构化工具调用/校验/执行，以及失败分类/有限反馈/停止原因。
- 为六个 Demo 提供各自的任务详情；用户可以从能力卡片点击按钮，在可访问的弹窗中查看共享业务任务、该 Demo 的 PLAIN/HARNESS 条件、完成定义、预期证据和演示提示。
- 在界面中展示“六个 Demo ↔ 11 个 Harness 组件”的主要/支撑/未直接演示映射，并明确子 Agent 编排当前不是独立现场实验，避免宣称六个 Demo 等于完整覆盖 11 个组件。
- 继续使用同一合成运费任务、真实 Responses API、干净工作区、顺序运行、单次运行限定语和确定性外部证据；不把单次结果表述为统计 benchmark。
- 保持 PPT 文件只读；本 change 通过 Demo 元数据和讲解界面与其内容对齐，不修改演示文稿本身。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `live-harness-comparison-demos`: 从三个可运行 Demo 扩展为六个，定义 Control、Continue、Ground 的真实 LLM 流程，并补充所有 Demo 的任务说明、组件证据和确定性评价要求。
- `harness-comparison-web-ui`: 开放六项能力，增加按 Demo 查看任务详情、组件映射、Demo 4 审批、Demo 5 交接状态和 Demo 6 权威依据的完整展示与交互要求。

## Impact

- 后端：`backend/src/harness_demo/` 新增 Demo 4–6 流程并扩展 CLI、夹具、报告事件、Web catalogue/runner/models/store/presentation 和审批协调。
- 前端：`frontend/src/features/experiment/` 扩展能力元数据、任务详情弹窗、组件映射、三项新 Demo 的阶段/证据渲染和审批交互。
- API：任务与能力目录增加结构化任务详情和组件映射；实验创建开放 `control`、`continue`、`ground`；事件和结果快照增加 approval、handoff、grounding 及对应评价字段。
- 测试：增加 Demo 4–6 的假 Responses 客户端控制流、安全边界、审批并发/恢复、交接隔离、权威来源验证，以及六项桌面/移动端和无障碍 UI 场景。
- 文档与流程：更新现有 README 和演示说明；不引入数据库、通用 Agent 框架、任意 shell、真实外部供应商服务或新的生产凭据。
- 依赖：应先完成并验证 `improve-comparison-readability` 的剩余前端检查，避免在未确认的展示基线上并行修改相同前端区域。
