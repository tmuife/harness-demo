## ADDED Requirements

### Requirement: 展示任务与 Harness 能力目录
系统 SHALL 在实验页面展示当前任务以及六项 Harness 能力的名称、说明、证据类型和可用状态。系统 MUST 将 `understand`、`act`、`prove` 标记为可运行，将 `control`、`continue`、`ground` 标记为设计中，直到后端明确将其开放。

#### Scenario: 加载实验页面
- **WHEN** 用户进入实验页面且能力与任务接口成功返回
- **THEN** 页面展示运费规则升级任务和全部六项能力
- **AND** 每项能力显示其当前可用状态

#### Scenario: 能力目录加载失败
- **WHEN** 能力或任务接口返回错误
- **THEN** 页面显示可重试的错误状态
- **AND** 开始对照操作保持禁用

### Requirement: 选择单一可运行能力
第一阶段系统 SHALL 使用可勾选控件选择 Harness 能力，但 MUST 将可运行配置限制为最多一项。选择另一项可运行能力时 SHALL 替换当前选择；设计中能力 MUST NOT 被加入运行配置。

#### Scenario: 选择可运行能力
- **WHEN** 用户选择 `understand`、`act` 或 `prove` 中的一项
- **THEN** 页面将该能力显示为当前 Harness 配置
- **AND** 在任务与能力数据可用时启用开始对照操作

#### Scenario: 替换当前能力
- **WHEN** 用户已选择一项可运行能力并选择另一项
- **THEN** 新能力替换原选择
- **AND** 请求配置仍只包含一个 capability ID

#### Scenario: 查看设计中能力
- **WHEN** 用户展开 `control`、`continue` 或 `ground`
- **THEN** 页面展示该能力的目的和预期证据
- **AND** 系统不允许以该能力创建实验，也不生成模拟结果

### Requirement: 创建固定基线对照实验
系统 SHALL 使用同一任务、模型条件和独立干净工作区创建固定 PLAIN 基线与当前 HARNESS 配置的对照实验。系统 MUST NOT 提供任意“配置 A vs 配置 B”模式；后续多能力组合也 SHALL 只应用于 HARNESS 侧。

#### Scenario: 创建有效实验
- **WHEN** 用户选择一个可运行能力并开始对照
- **THEN** 前端向后端提交受控 task ID 和单元素 `capabilities` 数组
- **AND** 后端返回实验 ID、PLAIN/HARNESS 两侧标识及确认后的配置

#### Scenario: 运行期间更改配置
- **WHEN** 实验处于启动或运行状态
- **THEN** 页面锁定能力选择和开始操作
- **AND** 当前显示配置与服务端确认的实验配置保持一致

#### Scenario: 服务端拒绝配置
- **WHEN** 请求包含未知、设计中或超过第一阶段数量限制的能力
- **THEN** 后端拒绝创建实验并返回有界错误
- **AND** 不创建工作区或调用 LLM

### Requirement: 顺序执行两侧实验
系统 SHALL 先完整执行 PLAIN 侧，再执行 HARNESS 侧。HARNESS 侧在 PLAIN 结束前 MUST 保持等待状态，第一阶段 MUST NOT 提供并行运行开关。

#### Scenario: 基线正在运行
- **WHEN** PLAIN 侧已经开始且尚未结束
- **THEN** 页面实时展示 PLAIN 事件
- **AND** HARNESS 轨道显示等待基线完成

#### Scenario: 基线完成
- **WHEN** PLAIN 侧到达 completed 或 failed 终态
- **THEN** 后端开始 HARNESS 侧运行
- **AND** 页面继续在同一实验中展示 HARNESS 事件

#### Scenario: 单侧基础设施失败
- **WHEN** 一侧因 LLM API、连接或执行基础设施错误终止
- **THEN** 页面将实验标记为不完整并保留已产生的证据
- **AND** 不把基础设施错误展示为模型工程结果的 FAIL

### Requirement: 通过结构化事件实时展示进度
后端 SHALL 通过 SSE 提供有序、可恢复的实验事件。每个事件 MUST 包含稳定事件 ID、实验 ID、运行侧、受控 stage、status、单调 sequence、时间、标题和摘要；证据字段 SHALL 根据事件类型提供经过限制的数据。

#### Scenario: 接收实时事件
- **WHEN** 后端产生 input、llm、tool、write、test、feedback、approval、handoff、grounding、result 或 error 事件
- **THEN** 前端将事件追加到对应运行轨道
- **AND** 按 sequence 排序并按事件 ID 去重

#### Scenario: SSE 临时断开
- **WHEN** 事件连接在实验未结束时断开
- **THEN** 页面保留已有事件并显示重连状态
- **AND** 前端使用最近事件 ID 恢复连接，避免重复展示

#### Scenario: 接收终态事件
- **WHEN** 实验到达完成或失败终态
- **THEN** 前端停止重连并查询最终结果快照
- **AND** 使用快照校准可能遗漏的末尾事件和汇总数据

### Requirement: 并排展示过程与工程证据
桌面端 SHALL 并排展示 PLAIN 与 HARNESS 运行轨道，移动端 SHALL 使用可明确识别两侧状态的标签视图。页面 SHALL 将模型回答与输入来源、工具活动、文件 Diff、测试反馈、调用次数、范围检查和最终结果分层展示。

#### Scenario: 桌面端查看对照
- **WHEN** 视口具备并排展示空间
- **THEN** PLAIN 与 HARNESS 使用等宽轨道同时可见
- **AND** 用户无需切换页面即可比较两侧状态和关键指标

#### Scenario: 移动端查看对照
- **WHEN** 视口不足以可靠并排展示日志和 Diff
- **THEN** 页面使用 PLAIN/HARNESS 标签切换运行轨道
- **AND** 结果摘要仍同时列出两侧关键指标

#### Scenario: 查看事件详情
- **WHEN** 用户展开具有证据的事件
- **THEN** 详情区域以纯文本或安全转义内容显示经过后端脱敏和截断的数据
- **AND** 长内容在限定区域内滚动且不破坏页面布局

### Requirement: 展示可验证的最终结果
系统 SHALL 为两侧展示调用次数、修改文件、测试状态、约束检查和 PASS/FAIL 等可用结果，并 SHALL 清楚区分模型结果失败、基础设施错误和仅产生分析或提案的正常结果。

#### Scenario: 实验正常完成
- **WHEN** 后端返回最终结果快照
- **THEN** 页面展示两侧关键指标和差异摘要
- **AND** PASS/FAIL 来源于后端的确定性评价，而不是模型自述

#### Scenario: Demo 1 完成分析
- **WHEN** Understand 实验结束且工作区按设计未修改
- **THEN** 页面展示分析检查项和输入来源差异
- **AND** 不把未产生代码修改错误标记为未完成

#### Scenario: Demo 2 基线只产生提案
- **WHEN** Act 的 PLAIN 侧返回建议但未修改工作区
- **THEN** 页面明确显示“仅提案”
- **AND** 不声称已经执行写入或测试

### Requirement: 使用时间线内联人工审批
系统 SHALL 将 Demo 4 的待审批动作显示为 HARNESS 时间线中的内联审批卡片，而非阻塞式弹窗。审批卡片 MUST 展示计划动作和目标范围，并提供明确的批准与拒绝操作。

#### Scenario: 收到待审批事件
- **WHEN** 后端为可运行的 Control 实验发送待审批事件
- **THEN** 对应时间线位置显示内联审批卡片
- **AND** 后续受保护动作保持暂停

#### Scenario: 提交审批决定
- **WHEN** 用户批准或拒绝待审批动作
- **THEN** 前端通过受控审批接口提交一次决定
- **AND** 卡片固化为只读审批记录，后续事件继续显示在其后

#### Scenario: 重复提交审批
- **WHEN** 已处理的审批再次收到用户操作或重复请求
- **THEN** 后端拒绝重复决定
- **AND** 前端保留服务端确认的最终审批状态

### Requirement: 短期恢复最近实验
前端 SHALL 在 `sessionStorage` 中保存最近一次实验 ID，后端 SHALL 在内存中保留运行事件和最终结果，并为已结束实验使用 30 分钟 TTL。第一阶段 MUST NOT 为实验历史引入数据库。

#### Scenario: 页面刷新后恢复实验
- **WHEN** `sessionStorage` 中存在实验 ID 且后端仍保留该实验
- **THEN** 前端查询实验状态、事件和结果并恢复页面
- **AND** 运行中的实验继续订阅事件流

#### Scenario: 最近实验已过期
- **WHEN** 保存的实验 ID 不存在、服务已重启或 TTL 已到期
- **THEN** 页面清除无效 ID 并返回初始状态
- **AND** 显示简短说明而不将其作为运行失败

#### Scenario: 结束实验达到保留期限
- **WHEN** 实验结束超过 30 分钟
- **THEN** 后端可以删除其内存事件和结果
- **AND** 删除操作不影响正在运行的实验

### Requirement: 保持前后端安全边界
前端 MUST NOT 接收或保存 API Key、宿主机工作区路径、任意命令或未截断的敏感异常。后端 SHALL 只接受注册的 task ID 和 capability ID，并继续强制工作区、写入路径、固定测试命令、超时、脱敏和输出长度限制。

#### Scenario: 前端创建实验
- **WHEN** 浏览器提交实验请求
- **THEN** 请求只包含公开 task ID 和 capability ID
- **AND** 模型配置、凭据、文件路径和工具权限由后端决定

#### Scenario: 展示后端错误
- **WHEN** 后端操作失败并向前端返回错误
- **THEN** 错误内容不包含 API Key、认证头、原始 SDK 请求或宿主机绝对路径
- **AND** 页面安全地以文本方式显示有界摘要

#### Scenario: 配置前端环境
- **WHEN** 部署或启动前端
- **THEN** 公开的 API base URL 可以使用 `VITE_` 环境变量配置
- **AND** 任何秘密 MUST NOT 存入 `VITE_` 环境变量

### Requirement: 提供完整且可访问的界面状态
页面 SHALL 提供加载、无选择、设计中、启动失败、运行中、等待、重连、完成和恢复失败状态。交互控件 MUST 可通过键盘操作并具有可识别标签，状态与结果 MUST NOT 只依靠颜色传达。

#### Scenario: 初始进入页面
- **WHEN** 页面正在加载任务与能力目录
- **THEN** 页面显示加载占位并禁用开始操作
- **AND** 加载结束后进入无选择或可重试错误状态

#### Scenario: 使用键盘操作
- **WHEN** 用户使用键盘浏览能力、开始操作、轨道标签或证据详情
- **THEN** 所有交互均可获得可见焦点并被触发
- **AND** 控件名称和状态可由辅助技术识别

#### Scenario: 用户偏好减少动画
- **WHEN** 浏览器启用 `prefers-reduced-motion`
- **THEN** 页面移除非必要的进入和状态过渡动画
- **AND** 信息层级和运行反馈保持完整
