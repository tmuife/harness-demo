## MODIFIED Requirements

### Requirement: 展示任务与 Harness 能力目录
系统 SHALL 在教学架构首页展示共享业务场景，并通过组件关联入口提供六项 Harness 能力的名称、说明、证据类型、可用状态、任务详情和主要/支撑组件关系。服务端 catalogue SHALL 是能力可用状态和 Demo—组件关系的事实源；系统 MUST 支持当前六项能力均可运行，以及服务端将任一能力标记为 planned 的情况。

#### Scenario: 加载实验页面
- **WHEN** 用户进入实验页面且能力与任务接口成功返回
- **THEN** 页面展示运费规则升级业务背景入口和教学架构
- **AND** 六项能力均可通过关联组件找到，并显示服务端当前可用状态

#### Scenario: 展示能力组件摘要
- **WHEN** 用户查看任一关联 Demo
- **THEN** 组件侧栏展示其主要/支撑关系、简要任务、预期证据和完整任务入口
- **AND** 页面不将映射描述为六个 Demo 与 11 个组件一一对应

#### Scenario: 能力目录加载失败
- **WHEN** 能力或任务接口返回错误
- **THEN** 页面显示可重试的错误状态
- **AND** 开始对照操作保持禁用，不用本地教学数据冒充已加载的可运行目录

### Requirement: 选择单一可运行能力
系统 SHALL 通过架构组件及其关联 Demo 的单选交互选择 Harness 能力，并 MUST 将可运行配置限制为最多一项。选择另一项可运行 Demo 时 SHALL 替换当前选择；planned 能力 MUST NOT 被加入运行配置。点击组件或打开任务详情 MUST NOT 自动启动实验。

#### Scenario: 选择可运行能力
- **WHEN** 用户通过关联组件选中 understand、act、prove、control、continue 或 ground 中被服务端标记为 available 的一项
- **THEN** 页面显示该能力的任务预览和当前 Harness 配置
- **AND** 在任务与能力数据可用时启用开始对照操作

#### Scenario: 替换当前能力
- **WHEN** 用户已选择一项可运行能力并选择另一项
- **THEN** 新能力替换原选择且任务预览随之更新
- **AND** 请求配置仍只包含一个 capability ID

#### Scenario: 查看设计中能力
- **WHEN** 用户查看任一被服务端标记为 planned 的关联 Demo
- **THEN** 页面展示目的和预期证据并标记设计中
- **AND** 系统不允许以该能力创建实验，也不生成模拟结果

### Requirement: 创建固定基线对照实验
系统 SHALL 使用同一任务、模型条件和独立干净工作区创建固定 PLAIN 基线与当前 HARNESS 配置的对照实验。系统 MUST NOT 提供任意“配置 A vs 配置 B”模式；后续多能力组合也 SHALL 只应用于 HARNESS 侧。系统 SHALL 仅在用户触发开始对照后创建实验，并以服务端确认的 capability 绑定结果展示。

#### Scenario: 创建有效实验
- **WHEN** 用户选择一个可运行能力并开始对照
- **THEN** 前端向后端提交受控 task ID 和单元素 capabilities 数组，不提交组件 ID 代替能力 ID
- **AND** 后端返回实验 ID、PLAIN/HARNESS 两侧标识及确认后的配置，前端进入对照工作台

#### Scenario: 运行期间更改配置
- **WHEN** 实验处于启动或运行状态
- **THEN** 页面锁定组件/Demo 配置选择和开始操作，保留任务只读入口
- **AND** 当前显示配置与服务端确认的实验配置保持一致，内联审批保持可达

#### Scenario: 服务端拒绝配置
- **WHEN** 请求包含未知、设计中或超过第一阶段数量限制的能力
- **THEN** 后端拒绝创建实验并返回有界错误
- **AND** 不创建工作区或调用 LLM，前端允许修正选择或重试
