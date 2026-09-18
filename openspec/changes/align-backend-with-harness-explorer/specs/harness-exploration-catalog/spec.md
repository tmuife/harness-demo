## ADDED Requirements

### Requirement: 提供完整的公开教学组件目录
系统 SHALL 通过只读 GET /api/harness-components 返回全部 11 个已知 Harness 组件，每项包含稳定 id、title、description、groupId 和 coverage。系统 SHALL 保留现有 capability 中的组件 ID 和标题，MUST NOT 返回布局坐标、实时执行状态、凭据、内部提示词或绝对工作区路径。

#### Scenario: 读取完整目录
- **WHEN** 客户端请求组件目录
- **THEN** 响应包含 11 个唯一组件，包括 subagents，且职责非空、组 ID 属于已定义教学分组
- **AND** 请求不读取 LLM 凭据、不创建实验或工作区、不调用模型

#### Scenario: 查看未直接演示的组件
- **WHEN** 客户端读取 subagents
- **THEN** coverage 为 not_demonstrated 且职责说明其教学用途
- **AND** 目录不提供虚构 Demo 或成功运行状态

### Requirement: 从单点能力映射推导教学覆盖
系统 SHALL 复用 capability 的 primaryComponents 和 supportingComponents 作为唯一 Demo—组件关系源。存在主要关联时 coverage SHALL 为 primary，否则存在支撑关联时 SHALL 为 supporting，否则 SHALL 为 not_demonstrated。coverage MUST NOT 作为创建实验的可用性或成功判定。

#### Scenario: 校验映射一致性
- **WHEN** 目录通过确定性校验
- **THEN** 每个被引用组件均存在，名称一致，同一 Demo 的主要/支撑列表不重叠
- **AND** 组件覆盖与实际映射一致，目录不维护重复的关联 Demo 关系表

#### Scenario: 相关 Demo 暂未开放
- **WHEN** 主要关联 Demo 被标记为 planned
- **THEN** 组件的教学关系仍可展示
- **AND** 该 Demo 是否允许创建实验仍由 capability.status 决定

### Requirement: 扩展业务背景和逐项准确的任务说明
系统 SHALL 在 TaskBrief 中添加可空 businessBackground 和默认空数组 sharedConstraints，在 DemoTask 中添加可空 objective，并为当前六项生产目录填充有效任务目标。系统 SHALL 保留既有字段与标识，并提供对应 Demo 行为的 completionDefinition；公开说明 MUST NOT 预先承诺实验成功或将所有 Demo 统一为写文件通过测试。

#### Scenario: 获取业务背景和任务目标
- **WHEN** 客户端读取 /api/task 和 /api/capabilities
- **THEN** 可获得公共场景、共同约束和六项不同的明确任务目标
- **AND** 既有 id/title/summary、两侧条件、完成定义、预期证据、讲解提示及关系字段仍可用

#### Scenario: 读取 Understand 完成条件
- **WHEN** 客户端查看 Understand
- **THEN** 任务说明要求规则分析和工作区不变
- **AND** 不将写入实现或实现测试通过列为该分析 Demo 的完成要求

#### Scenario: 读取其他五项任务说明
- **WHEN** 客户端查看 Act、Prove、Control、Continue 和 Ground
- **THEN** 文案分别准确表达建议与执行、有限反馈、门禁与任务结果分离、隔离会话交接以及本地版本化依据
- **AND** 不把仅建议描述为已执行，不要求必然先失败，不把拒绝描述为任务成功，不宣称长期记忆或真实联网

#### Scenario: 旧构造方省略新增字段
- **WHEN** 现有代码构造 TaskBrief 或 DemoTask 时不传新增字段
- **THEN** 模型使用 null 或空数组的兼容默认值
- **AND** 不改变现有必需字段的含义或六项实验的分派

### Requirement: 接入服务端元数据并保持前端独立回退
已验收前端 SHALL 在展示适配层优先使用有效的新组件目录和任务字段，并 SHALL 支持旧服务缺少接口或字段。新组件目录请求 MUST 独立于核心目录加载，可选请求失败 MUST NOT 阻塞已获得有效核心目录的实验入口。

#### Scenario: 新后端接入已验收页面
- **WHEN** 新目录和新增任务字段有效
- **THEN** 架构职责、分组、覆盖及任务预览/详情使用服务端元数据
- **AND** 第一阶段布局和交互保持一致，关联关系仍从 capability 推导

#### Scenario: 旧服务或目录请求失败
- **WHEN** 新目录返回 404、网络错误或非法内容，或者旧任务响应缺少新增字段
- **THEN** 页面采用第一阶段集中回退数据；目录失败显示简短非阻塞提示
- **AND** 有效核心目录下的任务浏览、单 Demo 创建及当前实验不受阻塞

#### Scenario: 可选目录内容不兼容
- **WHEN** 新目录存在重复/缺失/未知组件 ID、非法组 ID/coverage 或空职责
- **THEN** 页面对整个可选目录回退，不混合不一致的部分关系
- **AND** 文本安全渲染，核心能力状态不会被可选目录覆盖

#### Scenario: 核心目录失败
- **WHEN** capabilities 或 task 加载失败但新组件目录成功
- **THEN** 页面仍显示核心加载错误并禁止创建实验
- **AND** 组件元数据不能被用于假定实验可运行

### Requirement: 元数据扩展兼容现有实验和安全边界
系统 SHALL 保持现有 /api/capabilities、/api/task、实验创建、结果、SSE、审批和 CLI 的既有字段及执行行为。新增目录和字段 MUST NOT 改变六 Demo 条件、请求能力数限制、工作区边界、固定测试、超时、脱敏或确定性评价。

#### Scenario: 旧客户端继续运行
- **WHEN** 旧客户端忽略新增字段并使用现有接口发起有效单 Demo 实验
- **THEN** 系统按原有 PLAIN → HARNESS 顺序执行并返回原有结构化结果
- **AND** 内联审批所用接口及 SSE 恢复行为保持兼容

#### Scenario: 请求含非法配置
- **WHEN** 客户端提交未知 capability、多能力组合或额外受控配置
- **THEN** 后端继续拒绝请求
- **AND** 新组件目录不会扩展运行授权或绕过路径、命令校验
