## MODIFIED Requirements

### Requirement: 编号化成对命令
系统 SHALL 提供 `harness-demo <编号> [--harness]` 命令并支持 Demo 1 至 Demo 6。相同编号不带 `--harness` 时 SHALL 运行该 Demo 的 PLAIN 基线模式，带 `--harness` 时 SHALL 只增加该 Demo 声明的主要 harness 能力；演示程序维持工作区隔离、凭据保护和固定评价所需的共同基础设施不得被描述为实验变量。

#### Scenario: 运行基线模式
- **WHEN** 操作员在 `backend/` 执行 `uv run harness-demo 1`
- **THEN** 系统运行 Demo 1 的 PLAIN 模式
- **AND** 启动信息显示 Demo 名称、模型、PLAIN 模式和当前实验变量

#### Scenario: 运行 Harness 模式
- **WHEN** 操作员在 `backend/` 执行 `uv run harness-demo 1 --harness`
- **THEN** 系统运行 Demo 1 的 HARNESS 模式
- **AND** 启动信息明确说明本次启用的主要 harness 能力

#### Scenario: 运行新增 Demo
- **WHEN** 操作员使用有效配置运行 Demo 4、Demo 5 或 Demo 6
- **THEN** 系统通过与 Demo 1 至 Demo 3 相同的真实 LLM、隔离工作区和有界报告路径执行对应模式
- **AND** 系统不使用预设模型回答代替真实调用

#### Scenario: 列出可用 Demo
- **WHEN** 操作员在 `backend/` 执行 `uv run harness-demo list`
- **THEN** 系统列出 Demo 1 至 Demo 6 的编号、名称和成对模式差异
- **AND** 系统不创建工作区且不调用 LLM

#### Scenario: 拒绝无效 Demo
- **WHEN** 操作员输入 Demo 1 至 Demo 6 之外的编号或值
- **THEN** 系统以非零状态退出并列出当前支持的 Demo 1 至 Demo 6
- **AND** 系统不创建工作区且不调用 LLM

### Requirement: 统一运费规则任务
系统 SHALL 使用同一个合成运费计算器业务目标贯穿 Demo 1 至 Demo 6。任务 MUST 要求保持 `calculate_shipping_fee(subtotal_cents, destination, is_member=False)` 的公共函数签名、使用整数分作为金额单位，并且不得修改测试来使测试通过。各 Demo MAY 通过不同的信息来源、工具范围、反馈、审批、会话状态或权威依据形成实验条件，但 MUST NOT 改变成对运行内部的目标实现和最终评价规则。

当前政策 SHALL 定义国内基础运费为 800 分、普通用户免邮阈值为 5000 分、会员免邮阈值为 3000 分，并对达到阈值的订单免邮；国际订单 SHALL 始终收取 2000 分且不参与免邮。Demo 6 的缓存政策 SHALL 明确标记为过期，并以版本化模拟 provider 中的当前政策作为确定性评价事实源。

#### Scenario: 验证普通用户阈值
- **WHEN** 最终实现计算国内普通用户 4999 分和 5000 分的订单
- **THEN** 结果分别为 800 分和 0 分

#### Scenario: 验证会员阈值
- **WHEN** 最终实现计算国内会员 2999 分和 3000 分的订单
- **THEN** 结果分别为 800 分和 0 分

#### Scenario: 验证国际订单
- **WHEN** 最终实现计算任意高金额的国际订单
- **THEN** 结果仍为 2000 分

#### Scenario: 验证公共 API 和修改范围
- **WHEN** 系统评价任一产生代码修改的 Demo
- **THEN** `calculate_shipping_fee` 的公共签名保持不变
- **AND** 夹具测试文件保持未修改

#### Scenario: 保持成对目标一致
- **WHEN** 系统运行同一 Demo 的 PLAIN 和 HARNESS 两侧
- **THEN** 两侧从相同业务目标、初始代码和当前政策评价开始
- **AND** 只有该 Demo 声明的信息或执行能力有意不同

## ADDED Requirements

### Requirement: 提供六个 Demo 的教学元数据
系统 SHALL 为 Demo 1 至 Demo 6 维护服务端拥有的结构化教学元数据，包括共享任务、该 Demo 的实验问题、PLAIN 条件、HARNESS 条件、完成定义、预期证据、一个或多个主要组件、支撑组件和覆盖边界。组件名称 SHALL 使用培训 PPT 中 11 个 Harness 组件的稳定标识，但系统 MUST NOT 声称六个 Demo 与 11 个组件一一对应或已直接验证全部组件。

#### Scenario: 获取某个 Demo 的任务定义
- **WHEN** CLI 或 Web catalogue 请求一个已注册 Demo 的公开元数据
- **THEN** 系统返回该 Demo 的任务条件、完成定义和预期证据
- **AND** 返回内容不包含完整内部 prompt、绝对工作区路径、模型凭据或任意工具权限

#### Scenario: 获取组件映射
- **WHEN** catalogue 返回六个 Demo 的组件映射
- **THEN** 每个 Demo 至少声明一个主要组件和零个或多个支撑组件
- **AND** 子 Agent 编排被明确标记为本 change 未直接演示

#### Scenario: 组件支持多个 Demo
- **WHEN** 上下文管理、工具系统或质量验证等组件出现在多个 Demo 中
- **THEN** 系统保留所有主要或支撑关系
- **AND** 不强制组件与 Demo 建立唯一对应关系

### Requirement: 显式展示 Demo 1 至 Demo 3 的 Harness 机制
系统 SHALL 在不改变 Understand、Act 和 Prove 核心实验条件的前提下，报告可说明 PPT 组件的有界结构化事实。Understand SHALL 报告公开上下文来源类别和装配优先级摘要；Act SHALL 报告结构化工具调用、schema 校验、权限判断、执行和结果回填；Prove SHALL 报告失败分类、最大轮数、实际轮数和停止原因。

#### Scenario: Understand 展示上下文装配
- **WHEN** Demo 1 准备任一侧的模型输入
- **THEN** input evidence 列出公开来源类别和相对来源标签
- **AND** evidence 不公开服务端系统提示词或凭据

#### Scenario: Act 展示工具执行边界
- **WHEN** Demo 2 HARNESS 模式收到一个函数工具调用
- **THEN** tool evidence 区分模型请求、参数校验、权限决定、执行状态和有界结果
- **AND** 未实际执行的步骤不得显示为已完成

#### Scenario: Prove 展示有限恢复循环
- **WHEN** Demo 3 HARNESS 模式因测试失败继续或停止
- **THEN** result evidence 记录可修复失败分类、实际轮数、最大轮数和停止原因
- **AND** 系统不公开测试源码给模型

### Requirement: Demo 4 展示边界与审批
Demo 4 SHALL 向两种模式提供相同任务和必要上下文，并把 Control 作为主要实验变量。两侧所有操作 MUST 保持在合成工作区和固定命令内；PLAIN SHALL 使用较宽但仍有界的写入范围且不要求人工批准，HARNESS SHALL 限定允许实现文件并在第一次有效写入前等待一次明确批准。

#### Scenario: Demo 4 基线在较宽边界内执行
- **WHEN** PLAIN 模式请求其允许范围内的文件工具或固定测试
- **THEN** 系统不创建人工审批门禁并按基线边界执行有效请求
- **AND** 系统仍拒绝工作区逃逸、测试文件写入和任意命令

#### Scenario: Demo 4 Harness 等待首次写入审批
- **WHEN** HARNESS 模式首次请求写入允许的 `src/shipping.py`
- **THEN** 系统在执行写入前产生包含动作与目标范围的 pending approval
- **AND** 受保护写入在收到决定前不得执行

#### Scenario: 批准受保护写入
- **WHEN** 操作员批准 pending approval
- **THEN** 系统仅执行该批准范围内的写入并继续有限工具循环
- **AND** 最终证据记录批准决定、实际修改范围、测试和范围检查

#### Scenario: 拒绝受保护写入
- **WHEN** 操作员拒绝 pending approval
- **THEN** 系统不执行受保护写入并记录中性的控制停止结果
- **AND** 系统分别表达任务未执行与控制门禁已生效，不将其标记为基础设施异常

#### Scenario: 拒绝越界工具请求
- **WHEN** HARNESS 模式请求允许实现文件之外的写入、未知工具或非固定命令
- **THEN** 系统在执行前拒绝请求并向模型返回有界错误结果
- **AND** 结构化证据记录请求范围、策略决定和未执行状态

#### Scenario: 审批等待超时
- **WHEN** pending approval 在配置的有界等待期内没有收到决定
- **THEN** 系统停止 HARNESS 运行并保留已有事件和工作区
- **AND** 结果显示审批等待超时而不是模型工程 FAIL

### Requirement: Demo 5 展示跨会话状态
Demo 5 SHALL 在每侧使用互不共享消息历史或 Responses 会话的 Session A 和 Session B。Session A SHALL 只调查并停止，Session B SHALL 负责继续实现和验证；PLAIN 的 Session B 只获得原始任务与当前允许文件，HARNESS 的 Session B SHALL 额外获得 Session A 产生并通过 schema 校验的有界 handoff/checkpoint。

#### Scenario: 隔离两个会话
- **WHEN** Demo 5 从 Session A 转入 Session B
- **THEN** Session B 使用新的 LLM 调用上下文且不继承 Session A 的消息历史
- **AND** Session A 不修改实现文件

#### Scenario: PLAIN 不接收交接记录
- **WHEN** PLAIN 的 Session B 开始
- **THEN** 模型只收到共享任务和当前允许文件
- **AND** Session A 的回答不被直接或间接装配进 Session B 输入

#### Scenario: HARNESS 持久化并恢复交接记录
- **WHEN** HARNESS 的 Session A 产生符合 schema 的 handoff
- **THEN** 系统将已完成事项、关键发现、剩余步骤、目标文件和验证命令保存到当前 Demo 工作区
- **AND** Session B 将该记录作为带来源标签的附加上下文读取

#### Scenario: 交接记录无效
- **WHEN** Session A 未产生 handoff 或内容未通过 schema、大小或安全校验
- **THEN** 系统不从自由文本猜测缺失字段
- **AND** 系统以有界证据报告交接失败并使用明确终态停止或进入文档规定的有限恢复路径

#### Scenario: 展示连续性结果
- **WHEN** 任一 Demo 5 模式结束
- **THEN** 系统展示 Session A/B 边界、Session B 输入来源、交接字段、修改、测试和最终任务状态
- **AND** 系统将这些事实表述为本次跨会话观察而不是长期记忆 benchmark

### Requirement: Demo 6 展示版本化外部依据
Demo 6 SHALL 使用一份明确标记为过期的缓存政策和一份本地模拟当前提供方政策。PLAIN SHALL 只依据任务、过期缓存或模型已有知识；HARNESS SHALL 可以调用只读 `get_current_shipping_policy` 工具获取经过 schema 校验的当前版本、生效日期和政策规则。两侧 SHALL 使用同一当前政策契约进行最终评价。

#### Scenario: PLAIN 只获得过期依据
- **WHEN** Demo 6 PLAIN 模式准备模型输入
- **THEN** 系统提供工单和明确标记为过期的缓存政策但不提供当前 provider 内容
- **AND** 最终结果不得因为模型声称了解最新规则而标记为已获取当前依据

#### Scenario: HARNESS 获取当前政策
- **WHEN** HARNESS 模式请求 `get_current_shipping_policy`
- **THEN** 系统从当前合成工作区的只读 provider JSON 返回白名单政策字段、版本和生效日期
- **AND** 系统记录 grounding 工具调用、来源标签和有界结果

#### Scenario: 隔离外部内容与指令
- **WHEN** provider 数据包含未知字段、超长文本或类似指令的内容
- **THEN** 系统只装配通过 schema 的政策数据并保持其 data 来源边界
- **AND** 未知或超限内容不得提升为系统、开发者或用户指令

#### Scenario: 确定性评价当前依据
- **WHEN** 任一 Demo 6 模式结束
- **THEN** 系统展示实际依据来源、政策版本、生效日期、契约测试和最终修改范围
- **AND** 只有实际获取正确当前依据且契约验证通过的 HARNESS 运行可以标记为“基于当前依据完成”

#### Scenario: 当前政策工具不可用
- **WHEN** provider 文件缺失、格式无效或工具执行失败
- **THEN** 系统保留有界错误证据并将本次实验标记为不完整或依据获取失败
- **AND** 系统不得静默回退到模型已有知识并声称已获取当前政策
