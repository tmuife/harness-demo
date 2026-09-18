## Purpose

定义使用真实 LLM 运行编号化 PLAIN/Harness 对照演示的行为，包括统一任务、隔离工作区、受限工具、测试反馈、结果展示和安全边界。

## Requirements

### Requirement: 真实 LLM 配置与调用
系统 SHALL 使用官方 OpenAI Python SDK 和 Responses API 调用真实 LLM，并从本地 `.env` 读取 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`、调用超时和最大轮数。正常的基线与 Harness 演示路径 MUST NOT 使用预设模型回答或自动降级到假客户端。

#### Scenario: 使用完整配置运行演示
- **WHEN** 操作员提供所有必需环境变量并运行一个有效 Demo
- **THEN** 系统使用配置的 Base URL、模型和 API Key 发起 Responses API 调用
- **AND** 终端输出模型名称但不输出 API Key

#### Scenario: 必需配置缺失
- **WHEN** 操作员运行 Demo 但缺少任一必需环境变量
- **THEN** 系统在创建工作区或调用 LLM 前以非零状态退出
- **AND** 错误信息指出缺失变量但不包含其他凭据值

#### Scenario: LLM API 调用失败
- **WHEN** Responses API 返回错误、连接失败或超时
- **THEN** 系统明确报告本次演示因 LLM 调用失败而终止
- **AND** 系统 MUST NOT 将预设文本作为模型结果继续运行

### Requirement: 编号化成对命令
系统 SHALL 提供 `harness-demo <编号> [--harness]` 命令，其中首次交付只支持 Demo 1、Demo 2 和 Demo 3。相同编号不带 `--harness` 时 SHALL 运行 PLAIN 基线模式，带 `--harness` 时 SHALL 只增加该 Demo 声明的目标 harness 能力。

#### Scenario: 运行基线模式
- **WHEN** 操作员在 `backend/` 执行 `uv run harness-demo 1`
- **THEN** 系统运行 Demo 1 的 PLAIN 模式
- **AND** 启动信息显示 Demo 名称、模型、PLAIN 模式和当前实验变量

#### Scenario: 运行 Harness 模式
- **WHEN** 操作员在 `backend/` 执行 `uv run harness-demo 1 --harness`
- **THEN** 系统运行 Demo 1 的 HARNESS 模式
- **AND** 启动信息明确说明本次启用的 harness 能力

#### Scenario: 列出可用 Demo
- **WHEN** 操作员在 `backend/` 执行 `uv run harness-demo list`
- **THEN** 系统列出 Demo 1 至 Demo 3 的编号、名称和成对模式差异
- **AND** 系统不创建工作区且不调用 LLM

#### Scenario: 拒绝未实现的 Demo
- **WHEN** 操作员输入 Demo 4 至 Demo 6 或其他无效编号
- **THEN** 系统以非零状态退出并列出当前支持的 Demo 1 至 Demo 3
- **AND** 系统不调用 LLM

### Requirement: 统一运费规则任务
系统 SHALL 使用同一个合成运费计算器任务贯穿 Demo 1 至 Demo 3。任务 MUST 要求保持 `calculate_shipping_fee(subtotal_cents, destination, is_member=False)` 的公共函数签名、使用整数分作为金额单位，并且不得修改测试来使测试通过。

当前政策 SHALL 定义国内基础运费为 800 分、普通用户免邮阈值为 5000 分、会员免邮阈值为 3000 分，并对达到阈值的订单免邮；国际订单 SHALL 始终收取 2000 分且不参与免邮。

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

### Requirement: 干净且隔离的工作区
系统 SHALL 在每次 Demo 运行开始时从不可变运费夹具创建干净工作区，并按 Demo 编号和 PLAIN/HARNESS 模式使用不同目录。系统 MUST 只重建由内部有效 Demo 编号计算出的目录，不得接受任意删除路径。

#### Scenario: 重复运行相同模式
- **WHEN** 操作员连续两次运行同一 Demo 的相同模式
- **THEN** 第二次运行从与第一次相同的初始夹具内容开始
- **AND** 第一次运行产生的代码修改不会进入第二次运行

#### Scenario: 成对模式互不影响
- **WHEN** PLAIN 模式已修改其工作区后再运行相同 Demo 的 HARNESS 模式
- **THEN** HARNESS 模式从原始夹具创建独立工作区

#### Scenario: 拒绝工作区路径逃逸
- **WHEN** 文件工具收到解析后位于当前 Demo 工作区之外的路径
- **THEN** 系统拒绝该操作且不读取或写入目标文件

### Requirement: Demo 1 展示项目上下文
Demo 1 SHALL 只要求 LLM 分析任务而不修改文件。PLAIN 模式 SHALL 只向 LLM 提供固定工单；HARNESS 模式 SHALL 在相同工单之外提供带明确文件边界的源码、测试、`AGENTS.md` 和集成说明上下文包。

#### Scenario: Demo 1 基线分析
- **WHEN** 操作员运行 Demo 1 的 PLAIN 模式
- **THEN** LLM 只收到工单文本和相同的输出要求
- **AND** 系统把回答标记为分析而不是已完成的代码修改

#### Scenario: Demo 1 Harness 分析
- **WHEN** 操作员运行 Demo 1 的 HARNESS 模式
- **THEN** LLM 收到工单以及源码、测试、项目约束和集成说明
- **AND** 每段上下文均标明来源文件路径

#### Scenario: 展示上下文分析结果
- **WHEN** Demo 1 的 LLM 调用完成
- **THEN** 系统展示回答是否包含目标源文件、金额单位、普通/会员阈值、国际订单规则、公共 API 约束和验证命令
- **AND** 这些文本检查被标记为演示提示而非统计 benchmark

### Requirement: Demo 2 展示受限工具行动
Demo 2 SHALL 向两种模式提供相同任务和必要上下文。PLAIN 模式 SHALL 只展示 LLM 返回的建议或代码文本且不得据此修改工作区；HARNESS 模式 SHALL 允许 LLM 通过 Responses API 函数工具读取工作区文件、写入允许的实现文件并运行固定测试命令。

#### Scenario: Demo 2 基线只产生提案
- **WHEN** 操作员运行 Demo 2 的 PLAIN 模式
- **THEN** 系统实际调用 LLM并展示其建议或代码
- **AND** 工作区中的实现文件保持初始内容
- **AND** 输出明确标记结果为提案而非已完成修改

#### Scenario: Demo 2 Harness 执行工具循环
- **WHEN** 操作员运行 Demo 2 的 HARNESS 模式且 LLM 请求有效工具
- **THEN** 系统执行工具、把结构化结果返回 LLM，并继续调用直到模型完成或达到最大轮数
- **AND** 系统记录每次读取、写入和测试活动的摘要

#### Scenario: Demo 2 产生客观结果
- **WHEN** Demo 2 Harness 工具循环结束
- **THEN** 系统展示实际修改文件列表、实现 diff、测试退出状态和最终 PASS/FAIL
- **AND** PASS 仅在实现满足运费测试、公共 API 和修改范围要求时产生

#### Scenario: 拒绝任意命令执行
- **WHEN** LLM 请求固定测试工具以外的子进程命令或未知工具
- **THEN** 系统不执行该命令
- **AND** 系统把简短错误结果返回 LLM

### Requirement: Demo 3 展示测试反馈循环
Demo 3 SHALL 为两种模式提供相同工单、初始实现和输出要求，且 MUST NOT 直接向 LLM 提供测试源码。两种模式 SHALL 将 LLM 第一次生成的完整实现写入各自工作区并使用同一测试集进行最终评价；只有 HARNESS 模式 SHALL 在模型结束前执行测试并把精简失败摘要反馈给 LLM。

#### Scenario: Demo 3 基线单轮生成
- **WHEN** 操作员运行 Demo 3 的 PLAIN 模式
- **THEN** 系统调用 LLM 一轮并写入其生成的完整目标实现
- **AND** 系统在模型调用结束后运行最终测试
- **AND** 测试结果不再反馈给 LLM

#### Scenario: Demo 3 Harness 首次测试通过
- **WHEN** 操作员运行 Demo 3 的 HARNESS 模式且第一次生成结果通过全部测试
- **THEN** 系统报告首次通过并停止反馈循环
- **AND** 系统不发起不必要的修复调用

#### Scenario: Demo 3 Harness 根据失败修复
- **WHEN** Harness 模式的当前实现未通过测试且尚未达到最大轮数
- **THEN** 系统把经过截断的失败测试名称、断言差异和必要错误信息反馈给 LLM
- **AND** 系统写入 LLM 返回的下一版完整实现并再次运行测试

#### Scenario: Demo 3 达到最大轮数
- **WHEN** Harness 模式在配置的最大轮数后仍未通过测试
- **THEN** 系统停止调用 LLM并报告最终 FAIL
- **AND** 系统保留最后一版工作区和各轮测试摘要供演示者检查

#### Scenario: Demo 3 成对结果展示
- **WHEN** 任一 Demo 3 模式结束
- **THEN** 系统展示 LLM 调用次数、每轮写入与测试摘要、最终测试结果和 PASS/FAIL

### Requirement: 安全且有界的执行
系统 MUST 将所有模型触发的文件操作限制在当前合成工作区，将测试执行限制为固定参数数组，并为 LLM 请求、子进程和终端输出设置界限。系统 MUST NOT 将 API Key、请求认证头或完整敏感异常写入提示词、工作区或终端。

#### Scenario: 测试命令超时
- **WHEN** 固定测试命令超过配置的超时时间
- **THEN** 系统终止测试进程并返回明确的超时结果

#### Scenario: 工具输出过长
- **WHEN** 文件、测试或模型输出超过演示上限
- **THEN** 系统截断输出并明确标记发生了截断

#### Scenario: 记录 API 错误
- **WHEN** SDK 抛出包含请求详情的异常
- **THEN** 系统只显示经过脱敏的错误类型和摘要
- **AND** 输出不包含 API Key 或认证请求头

### Requirement: 确定性辅助逻辑可测试
系统 SHALL 允许自动化测试以注入的轻量假客户端覆盖确定性控制流，但生产 CLI MUST NOT 暴露选择假客户端或预设模型回答的运行参数。

#### Scenario: 单元测试工具循环
- **WHEN** 测试注入返回固定 Responses API 文本和函数调用的假客户端
- **THEN** 测试能够验证 CLI 分派、工具参数处理、反馈轮数和结果评价而不访问网络

#### Scenario: 生产命令参数检查
- **WHEN** 操作员查看生产 CLI 帮助或运行参数
- **THEN** CLI 不包含 fake、scripted、mock 或等价的演示运行模式

