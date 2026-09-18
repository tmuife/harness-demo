> 当前实现已迁入 `backend/`；本清单中的 Python 项目路径均相对于 `backend/`。

## 1. 项目与真实 LLM 基础

- [x] 1.1 更新 `pyproject.toml`，加入 `openai`、`python-dotenv`、测试依赖和 `harness-demo` 控制台入口，并用 `uv` 刷新锁文件。
- [x] 1.2 添加 `.env.example` 和 `.gitignore`，包含 Responses API 所需配置、超时/轮数占位值，并忽略 `.env` 与 `.demo-workspace/`。
- [x] 1.3 实现 `src/harness_demo/llm.py`，验证必需环境变量、创建带超时的 `OpenAI` 客户端，并提供最小 Responses API 文本调用能力。
- [x] 1.4 为 LLM 异常实现有界且脱敏的错误输出，确保 API Key、认证头和完整敏感请求详情不会进入终端或工作区。

## 2. CLI 与共享运费夹具

- [x] 2.1 创建 `src/harness_demo/__main__.py`，用 `argparse` 支持 Demo 1 至 Demo 3、`--harness` 和不调用 LLM 的 `list` 命令，并拒绝其他编号。
- [x] 2.2 创建共享 `fixtures/shipping` 工单、`AGENTS.md`、集成/政策说明和带边界及国际订单缺陷的 `src/shipping.py`。
- [x] 2.3 创建运费夹具测试，覆盖普通用户 4999/5000、会员 2999/3000、国际订单、公共函数签名和测试文件未修改约束。
- [x] 2.4 实现按 Demo 编号和模式重建 `.demo-workspace/demo-<n>-<mode>` 的工作区准备逻辑，并验证重复运行及 PLAIN/HARNESS 互不污染。
- [x] 2.5 实现共享的有界终端输出与最终评价辅助逻辑，展示模型轮数、文件变化、测试退出状态和 PASS/FAIL，同时截断过长内容。

## 3. Demo 1：项目上下文

- [x] 3.1 实现 Demo 1 PLAIN 分支，只向真实 LLM 发送固定工单和分析输出要求，不读取或注入项目文件。
- [x] 3.2 实现 Demo 1 HARNESS 分支，将源码、测试、`AGENTS.md` 和集成说明组装成带来源路径边界的上下文包后发送给同一模型。
- [x] 3.3 实现 Demo 1 演示检查项，展示回答是否覆盖目标文件、金额单位、普通/会员阈值、国际订单、公共 API 和验证命令，并标明该检查不是 benchmark。
- [x] 3.4 验证 Demo 1 两种模式都不修改工作区，并在终端清楚区分 PLAIN/HARNESS 输入差异和分析结果。

## 4. Demo 2：受限工具行动

- [x] 4.1 实现 Demo 2 PLAIN 分支，向真实 LLM 提供任务和必要上下文，只展示建议或代码文本，且保持工作区实现不变。
- [x] 4.2 在 Demo 2 中定义 Responses API 的 `read_file`、`write_file` 和 `run_tests` 函数工具 schema，并实现未知工具与无效参数的错误结果。
- [x] 4.3 实现文件工具的工作区路径校验，将写入限定到允许的实现文件；实现固定参数数组、`shell=False`、固定 `cwd`、超时和输出截断的测试工具。
- [x] 4.4 实现 Demo 2 HARNESS 工具循环，执行模型请求、回传函数结果，并在模型完成或达到 `DEMO_MAX_TURNS` 时停止。
- [x] 4.5 实现 Demo 2 结果卡，展示工具活动、实际修改文件、实现 diff、测试状态、公共 API/作用域检查和最终 PASS/FAIL。

## 5. Demo 3：测试反馈循环

- [x] 5.1 定义 Demo 3 两种模式共用的提示输入和完整目标文件输出格式，只提供工单与初始实现，不向 LLM 暴露测试源码。
- [x] 5.2 实现对 LLM 完整目标文件输出的提取与校验，格式无效时安全失败，且只写入当前工作区的 `src/shipping.py`。
- [x] 5.3 实现 Demo 3 PLAIN 分支：调用真实 LLM 一轮、写入生成结果、在调用结束后运行最终测试，并且不把结果反馈给模型。
- [x] 5.4 实现 Demo 3 HARNESS 分支：每次写入后运行测试，通过时立即停止，失败时把截断后的失败测试名、断言差异和必要错误反馈给模型。
- [x] 5.5 为 Demo 3 Harness 循环实施最大轮数，达到上限时保留最后实现和各轮摘要并报告 FAIL，首次通过时不发起额外调用。
- [x] 5.6 实现 Demo 3 成对结果卡，展示 LLM 调用次数、每轮写入/测试/反馈、最终测试结果和 PASS/FAIL。

## 6. 自动化验证与演示交付

- [x] 6.1 为配置校验、CLI 分派、`list` 无副作用、工作区重建、路径逃逸、命令限制、输出截断和结果评价添加确定性单元测试。
- [x] 6.2 使用可注入的轻量假 Responses 客户端测试 Demo 1 至 Demo 3 控制流、工具调用和反馈轮数，并确认生产 CLI 不暴露 fake/scripted/mock 模式。
- [x] 6.3 运行完整测试套件和静态/diff 检查，确认夹具初始实现按预期失败、正确实现通过，且测试不会访问真实网络。
- [x] 6.4 更新 `README.md`，说明 `.env` 配置、Demo 1 至 Demo 3 的成对命令、每个实验变量、安全边界和真实 LLM 输出波动。
- [x] 6.5 使用现场 `OPENAI_BASE_URL` 与 `OPENAI_MODEL` 分别演练六条真实命令，确认 Responses API 文本及函数工具调用可用，并记录仍需调节的提示词或任务难度。
