## Why

当前首页以六个能力选项和实验工作台为中心，11 个 Harness 组件的关系仅在底部文字映射中说明，观众不容易把架构、任务和实验结果联系起来。将架构图作为首页入口，并在组件旁直接预览任务，可以形成“理解组件 → 明确任务 → 运行对照 → 查看证据”的讲解路径。

## What Changes

- 将首页改为教学架构总览：展示 11 个组件、Harness 边界及模型、用户任务、工作区和外部依据等交互对象。
- 点击组件后展示职责、关联 Demo、主要/支撑关系和任务预览；一对多关系提供显式 Demo 选择，点击组件本身不启动实验。
- 顶部展示共享业务场景和“查看业务背景”入口；侧栏直接显示当前 Demo 的任务、PLAIN/HARNESS 条件和观察重点，保留完整任务详情入口。
- 开始实验后以现有对照工作台为主体，架构收为紧凑导航；保留结论优先、真实证据、内联审批和刷新恢复。
- 第一阶段只改前端，使用现有 `/api/capabilities`、`/api/task` 和实验接口。架构布局、组件教学解释及缺失的任务摘要使用明确隔离的前端展示元数据，不伪造运行证据。
- 覆盖桌面投屏、移动端、键盘、减少动画及错误/空白/运行状态；第一版不实现运行时组件追踪动画。
- 本 change 实现和视觉验收后交付用户查看效果；不自动实施 `align-backend-with-harness-explorer`。

## Capabilities

### New Capabilities

- `harness-architecture-explorer`: 教学架构导航、组件与 Demo 关联、两层任务预览、探索与实验工作台切换及可访问交互。

### Modified Capabilities

- `harness-comparison-web-ui`: 将能力卡片入口改为架构驱动的单 Demo 选择，调整任务入口和运行时配置归属，保持现有实验协议和对照能力。

## Impact

- 主要影响 `frontend/src/features/experiment/` 的页面组织、组件、局部状态、展示适配、样式和测试；沿用 React、TypeScript、CSS，可用 SVG 绘制连线。
- 不修改 `backend/`、Demo 条件、夹具、模型调用、审批协议或 SSE 契约，不增加图编辑器或全局状态依赖。
- 以当前六个 Demo 已开放的实现，以及 `improve-comparison-readability`、`complete-harness-training-demonstrations` 中已实现的交互为基线。主规格尚未同步的旧“后三项 planned”和勾选控件要求由本 change 的对应 delta 更新；不在创建或实施本 change 时顺带归档其他 change。
- 前端可独立运行与验收，后端配套 change 仅在用户评审后决定是否实施。
