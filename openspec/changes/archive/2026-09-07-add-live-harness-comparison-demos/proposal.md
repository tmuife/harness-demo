## Why

当前项目只有演示方向，没有可运行的真实 LLM 对照实验，无法直观看出 harness 为工程任务带来的上下文、行动和反馈能力。需要用一个简单、常见的运费规则升级任务，在相同模型与初始条件下成对运行基线模式和 Harness 模式，让差异能够通过模型回答、文件变化和测试结果被观察。

## What Changes

- 增加 `harness-demo <编号> [--harness]` 命令；不带标志运行基线模式，带标志只启用当前 Demo 的目标 harness 能力。
- 使用官方 OpenAI Python SDK 和 `.env` 中的 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL` 实际调用 LLM，不为演示命令提供脚本结果降级。现场使用的 Base URL 和模型完整支持 Responses API 及其函数工具调用，因此首版统一使用 Responses API，不实现 Chat Completions 兼容分支。
- 建立一个合成的 Python 运费计算器任务，覆盖普通用户、会员、国际订单和免邮边界规则，并要求保持公共函数签名且不得修改测试。
- 首次交付围绕同一个任务实现三个相互独立的对照 Demo：Demo 1 展示项目上下文，Demo 2 展示文件与测试工具，Demo 3 展示测试反馈循环。Demo 4 至 Demo 6 延后到后续变更。
- 每次运行从相同夹具创建隔离工作区，并按 Demo 展示分析要点、文件变更、工具活动和测试结果。
- 保持实现面向演示：每个 Demo 使用清晰的独立脚本，允许少量重复，不引入通用智能体框架、插件系统、数据库或复杂适配器层。
- 增加最小安全措施，包括忽略真实 `.env`、限制工作区写入、限制子进程命令/时间/输出，以及避免打印凭据。

## Capabilities

### New Capabilities

- `live-harness-comparison-demos`: 使用真实 LLM 在统一运费规则升级任务上运行 Demo 1 至 Demo 3 的基线/Harness 对照实验，分别展示项目上下文、工具行动和测试反馈产生的客观工程结果。

### Modified Capabilities

无。

## Impact

- 新增 `backend/src/harness_demo` CLI、共享 LLM 调用代码和各 Demo 的独立脚本。
- 新增运费计算器合成夹具、项目约束与政策说明、验证测试和一次性 `backend/.demo-workspace`。
- 更新 `backend/pyproject.toml`，加入控制台入口以及 `openai`、`python-dotenv` 依赖。
- 新增 `backend/.env.example` 并更新仓库忽略规则；真实 API 配置只保存在本地 `backend/.env`。
- 不接入真实业务仓库、公司系统、MCP 或生产数据；除 LLM API 外不需要其他外部服务。

## Deferred Decisions

- Demo 4 延后实现。后续实现时，Harness 模式的现场运行应始终在首次写入前等待人工确认，不提供面向演示者的跳过审批 CLI 参数；自动化测试通过注入确认函数或输入流覆盖批准与拒绝分支。这样既保留现场可见的控制点，也不会让测试依赖人工输入。
- Demo 5 延后实现。后续采用“会话 A 只分析并生成结构化交接记录，会话 B 使用全新上下文完成实现”的固定切分。会话 A 不修改代码，使交接记录成为两种模式之间唯一新增的信息通道，避免会话 B 通过已有 diff 间接恢复进度。
- Demo 6 延后实现，当前变更不创建提供方政策工具或相关数据。

## Open Questions

- Demo 3 是否允许 LLM 直接读取测试源码？当前倾向是不直接提供测试源码，只将测试失败摘要反馈给 Harness 模式，以突出反馈循环；该选择需要在编写 capability spec 前确认。
