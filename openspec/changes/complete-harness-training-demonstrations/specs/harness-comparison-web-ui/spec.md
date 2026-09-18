## MODIFIED Requirements

### Requirement: 展示任务与 Harness 能力目录
系统 SHALL 在实验页面展示共享业务任务以及六项 Harness 能力的名称、说明、证据类型、可用状态、各自任务详情和 PPT 组件映射。系统 SHALL 将 `understand`、`act`、`prove`、`control`、`continue`、`ground` 全部标记为可运行；服务端 catalogue SHALL 是这些公开元数据和可用状态的事实源。

#### Scenario: 加载实验页面
- **WHEN** 用户进入实验页面且能力与任务接口成功返回
- **THEN** 页面展示运费规则升级共享任务和全部六项可运行能力
- **AND** 每项能力显示其名称、简要说明、主要证据和查看任务操作

#### Scenario: 展示能力组件摘要
- **WHEN** 页面渲染任一能力卡片
- **THEN** 卡片或其紧邻详情显示该 Demo 的主要组件和支撑组件摘要
- **AND** 页面不把该映射描述为六个 Demo 与 11 个组件一一对应

#### Scenario: 能力目录加载失败
- **WHEN** 能力或任务接口返回错误
- **THEN** 页面显示可重试的错误状态
- **AND** 开始对照操作保持禁用

### Requirement: 选择单一可运行能力
系统 SHALL 使用可勾选控件选择 Harness 能力，但 MUST 将运行配置限制为最多一项。选择另一项能力时 SHALL 替换当前选择；六项已注册能力均 SHALL 可以加入运行配置，未知或服务端标记为不可用的未来能力 MUST NOT 被加入。

#### Scenario: 选择任一已注册能力
- **WHEN** 用户选择 `understand`、`act`、`prove`、`control`、`continue` 或 `ground` 中的一项
- **THEN** 页面将该能力显示为当前 Harness 配置
- **AND** 在任务与能力数据可用时启用开始对照操作

#### Scenario: 替换当前能力
- **WHEN** 用户已选择一项可运行能力并选择另一项
- **THEN** 新能力替换原选择
- **AND** 请求配置仍只包含一个 capability ID

#### Scenario: 服务端返回未来不可用能力
- **WHEN** catalogue 包含状态为不可用或设计中的未来能力
- **THEN** 页面可以展示其目的和状态但禁止将其加入运行配置
- **AND** 页面不生成模拟结果

### Requirement: 创建固定基线对照实验
系统 SHALL 使用同一任务、模型条件和独立干净工作区创建固定 PLAIN 基线与当前 HARNESS 配置的对照实验，并 SHALL 接受六项已注册且可用能力中的单一 capability ID。系统 MUST NOT 提供任意“配置 A vs 配置 B”模式；后续多能力组合也 SHALL 只应用于 HARNESS 侧。

#### Scenario: 创建有效实验
- **WHEN** 用户选择一个可运行能力并开始对照
- **THEN** 前端向后端提交受控 task ID 和单元素 `capabilities` 数组
- **AND** 后端返回实验 ID、PLAIN/HARNESS 两侧标识及确认后的配置

#### Scenario: 创建 Control、Continue 或 Ground 实验
- **WHEN** 请求包含 `control`、`continue` 或 `ground` 中的一个已注册 capability ID
- **THEN** 后端创建对应编号的真实 PLAIN/HARNESS 对照并按顺序运行
- **AND** 后端不返回模拟或 planned 占位结果

#### Scenario: 运行期间更改配置
- **WHEN** 实验处于启动或运行状态
- **THEN** 页面锁定能力选择和开始操作
- **AND** 当前显示配置与服务端确认的实验配置保持一致

#### Scenario: 服务端拒绝配置
- **WHEN** 请求包含未知、服务端不可用或超过允许数量的能力
- **THEN** 后端拒绝创建实验并返回有界错误
- **AND** 不创建工作区或调用 LLM

## ADDED Requirements

### Requirement: 通过弹窗查看每个 Demo 的任务详情
页面 SHALL 在六项能力卡片上提供独立的“查看任务”操作，并在可访问的模态弹窗中展示该 Demo 的实验问题、共享业务任务、PLAIN 条件、HARNESS 条件、完成定义、预期证据和演示提示。任务详情 SHALL 来自服务端 catalogue，前端 MUST NOT 自行重建或解释内部 prompt。

#### Scenario: 打开任务详情
- **WHEN** 用户激活某项能力的“查看任务”按钮
- **THEN** 页面打开标题包含 Demo 编号和名称的模态弹窗
- **AND** 弹窗展示该能力对应的完整公开任务详情而不开始实验或改变当前选择

#### Scenario: 从任务详情理解实验变量
- **WHEN** 用户阅读任务弹窗
- **THEN** 页面明确区分共享任务、PLAIN 条件、HARNESS 条件和本次主要变化
- **AND** 页面列出客观完成定义与运行时应观察的证据

#### Scenario: 通过键盘关闭任务详情
- **WHEN** 键盘用户使用关闭按钮或 Escape 关闭弹窗
- **THEN** 弹窗关闭且焦点返回触发该弹窗的“查看任务”按钮
- **AND** 当前能力选择和已有实验状态保持不变

#### Scenario: 使用辅助技术识别任务弹窗
- **WHEN** 任务详情处于打开状态
- **THEN** 弹窗暴露 dialog 名称、模态语义和可识别的章节标题
- **AND** 焦点保持在弹窗的可操作范围内，背景交互不可被误触发

#### Scenario: 任务元数据缺失
- **WHEN** 某项能力缺少有效任务详情字段
- **THEN** 页面显示中性的“任务详情暂不可用”状态并保留能力摘要
- **AND** 页面不显示空弹窗、内部错误对象或推测内容

### Requirement: 展示六个 Demo 与 11 个组件的教学映射
页面 SHALL 使用服务端提供的稳定组件元数据展示六个 Demo 与培训 PPT 11 个 Harness 组件之间的主要、支撑和未直接演示关系。映射 MUST 明确这是教学解释而不是运行覆盖率、实现依赖图或统计验证结果。

#### Scenario: 查看组件映射
- **WHEN** 用户展开或进入组件映射区域
- **THEN** 页面可以按 Demo 查看主要组件和支撑组件，也可以识别未直接演示的组件
- **AND** 同一组件可以关联多个 Demo

#### Scenario: 展示子 Agent 覆盖边界
- **WHEN** 映射包含子 Agent 编排
- **THEN** 页面将其标记为本轮未直接演示
- **AND** 页面不为其显示虚构的运行结果或完成状态

#### Scenario: 在窄屏查看组件映射
- **WHEN** 视口无法容纳完整桌面矩阵
- **THEN** 页面按 Demo 使用可读的纵向分组或等价响应式布局
- **AND** 主要、支撑和未演示关系不只依赖颜色区分

### Requirement: 展示 Control、Continue 与 Ground 的能力定制过程和结果
系统 SHALL 为三个新增 Demo 显示与其目标匹配的结构化阶段、客观指标和确定性本次运行观察。Control SHALL 展示允许范围、批准状态、拒绝和任务执行结果；Continue SHALL 展示 Session A/B 边界、handoff 状态和最终验证；Ground SHALL 展示依据来源、版本、生效日期、工具调用和契约验证。系统 MUST NOT 用模型自述替代这些事实。

#### Scenario: 展示 Control 等待审批
- **WHEN** Control HARNESS 运行产生 pending approval
- **THEN** 页面在时间线对应位置显示现有内联审批卡片并保持后续受保护动作等待
- **AND** 任务详情弹窗不替代或遮蔽审批决定的语义

#### Scenario: 展示 Control 拒绝结果
- **WHEN** 用户拒绝受保护动作
- **THEN** 完成视图分别显示“控制门禁已生效”和“任务未执行”
- **AND** 页面不将该结果显示为模型验证失败或基础设施异常

#### Scenario: 展示 Continue 交接过程
- **WHEN** Continue 实验产生 Session A、handoff 和 Session B 事件
- **THEN** 阶段对照按因果顺序展示会话边界、交接字段、恢复输入、修改和测试
- **AND** PLAIN 缺少 handoff 时显示“未提供跨会话交接”而不是推断模型遗忘

#### Scenario: 展示 Ground 权威依据
- **WHEN** Ground 实验产生 grounding 事件和最终快照
- **THEN** 页面展示来源类型、政策版本、生效日期、是否调用当前政策工具和契约测试结果
- **AND** 页面明确标注 provider 是本地模拟权威来源而非真实联网服务

#### Scenario: 新 Demo 发生基础设施异常
- **WHEN** Control、Continue 或 Ground 任一侧因配置、连接、审批协调或 provider 基础设施问题终止
- **THEN** 页面保留已产生证据并将实验标记为不完整
- **AND** 页面不把基础设施异常解释为 Harness 能力优劣

### Requirement: 为新增 Demo 提供稳定阶段焦点
完成态阶段对照 SHALL 为 Control 强制显示行动、审批、验证和结论焦点，为 Continue 强制显示信息、交接、行动、验证和结论焦点，为 Ground 强制显示信息、依据、行动、验证和结论焦点。某一侧没有对应事件时 SHALL 显示基于结构化结果的中性说明。

#### Scenario: Control 一侧没有越界请求
- **WHEN** Control 的某侧没有产生拒绝事件
- **THEN** 页面显示“本次未发生越界请求”或等价事实说明
- **AND** 页面不把缺失拒绝事件解释为边界不存在或模型必然合规

#### Scenario: Continue 缺少有效 handoff
- **WHEN** Continue HARNESS 侧没有可用 handoff
- **THEN** 交接焦点显示“交接记录不可用”及已有错误证据
- **AND** 页面不隐藏该焦点或显示虚构恢复步骤

#### Scenario: Ground 未调用当前政策工具
- **WHEN** Ground HARNESS 侧未产生成功 grounding 工具事件
- **THEN** 依据焦点显示“未取得当前政策依据”
- **AND** 即使最终代码偶然通过部分检查也不得显示为已基于当前依据完成
