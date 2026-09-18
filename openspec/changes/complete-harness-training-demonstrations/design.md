## Context

培训 PPT 将 Harness 描述为 11 个相互独立又协同工作的工程组件，但现场 Demo 的目标不是逐个展示内部模块，而是让观众观察 Harness 在信息、行动、验证、控制、连续性和依据六个结果维度上的差异。现有代码已经实现 Understand、Act、Prove 及其结构化 Web 证据；Control、Continue、Ground 只有 catalogue、事件 stage 和部分审批 UI 契约，尚无可运行流程。

本 change 跨越 Python CLI、真实 Responses API 工具循环、FastAPI 内存实验编排和 React 展示。实现必须继续使用合成数据、一次性工作区、假客户端确定性测试和真实 LLM 生产路径，不修改只读培训 PPT，也不把六个单次运行包装成对 11 个组件的完整统计验证。

`improve-comparison-readability` 已完成绝大多数改动，但仍有前端验证任务未完成。本 change 以其类型化 reporter、阶段对齐、结论优先和完整记录为展示基线，实施前应先完成该 change 的验证并同步主规格。

## Goals / Non-Goals

**Goals:**

- 让 Demo 1–6 均可通过 CLI 和 Web 使用相同真实 LLM 路径成对运行。
- 保持每个 Demo 只有一个面向观众的主要实验变量，同时公开主要与支撑组件映射。
- 让所有结论来自输入来源、工具校验、文件变化、审批、测试、交接记录或权威版本等客观事实。
- 为每项能力提供短小但完整的任务详情弹窗，使观众在运行前理解基线、Harness 条件、完成定义和应观察证据。
- 复用现有 reporter、FastAPI store、SSE、React feature 结构和样式，不引入框架式抽象。
- 保持审批、工作区、命令、输出和凭据边界在 CLI 与 Web 中一致。

**Non-Goals:**

- 不把六个 Demo 重构为 11 个一对一实验，也不在本 change 中增加第七个子 Agent Demo。
- 不修改培训 PPT，不自动解析 PPT 作为运行时配置，也不在 UI 中逐页复刻 PPT。
- 不引入数据库、持久任务历史、通用 workflow engine、Agents SDK、任意 shell 或真实外部供应商 API。
- 不保证某次 PLAIN 必然失败或某次 HARNESS 必然通过，不计算胜率或跨运行统计。
- 不允许浏览器选择模型、工作区路径、工具权限、政策文件或内部提示词。
- 不用额外 LLM 生成任务说明、组件映射、结果结论或 PASS/FAIL。

## Decisions

### 1. 六个 Demo 是结果维度，11 个组件是静态教学映射

后端 catalogue 维护一组稳定的组件 ID 和中文名称，并为每个 Demo 声明 `primaryComponents`、`supportingComponents` 和可选的 `notDemonstrated` 说明。映射以代码审查的静态元数据表达，不从 PPT 文件或运行日志推断：

| Demo | 主要组件 | 支撑组件 |
| --- | --- | --- |
| Understand | 上下文管理 | 提示词构建、质量验证 |
| Act | 工具系统 | 编排循环、输出解析、安全防护、质量验证 |
| Prove | 质量验证 | 编排循环、异常处理、工具系统、状态记录 |
| Control | 安全防护 | 工具系统、状态管理、编排循环 |
| Continue | 记忆系统、状态管理 | 上下文管理、提示词构建 |
| Ground | 上下文管理 | 工具系统、提示词构建、质量验证、安全防护 |

子 Agent 编排标记为“本轮未直接演示”。同一组件可以支持多个 Demo，同一 Demo 也可以依赖多个组件；界面不得把矩阵解释为实现依赖图或覆盖率。

选择静态映射而不是运行时读取 PPT，是因为 PPT 是培训资产而非机器契约，文件路径、措辞和版本可能变化。稳定 ID 便于前后端类型、测试和未来人工同步。

### 2. 共享基础任务，能力 catalogue 携带每个 Demo 的任务详情

继续保留一个共享运费升级 `TaskBrief`。每个 capability 额外返回结构化 `demoTask`，至少包含：任务标题、实验问题、PLAIN 条件、HARNESS 条件、完成定义、预期证据和演示提示。只返回公开摘要与相对文件名，不返回完整内部 prompt、绝对路径或配置。

任务详情通过现有 capability catalogue 一次加载，不新增详情 API。六份静态内容很小，避免额外加载状态和错误分支。React 在每个能力卡片提供“查看任务”按钮，并用 feature-local 的可访问 dialog 展示详情；关闭后焦点回到原按钮，运行时也允许只读查看。

任务弹窗与 Demo 4 的审批不同：任务说明使用模态 dialog；审批继续使用时间线内联卡片，避免两个含义不同的操作争夺同一交互模式。

### 3. Demo 4 使用真实批准门禁，但不依赖模型主动越界

Control 的两侧都只能访问合成工作区和固定测试命令。PLAIN 获得较宽但仍有界的写入范围且无需批准；HARNESS 只允许写入 `src/shipping.py`，第一次有效写入必须经过批准。工具请求始终经过 schema、路径和命令校验；非法请求在执行前拒绝并作为结构化结果反馈给模型。

CLI 在首次有效写入前从终端读取一次明确的批准/拒绝决定。Web reporter 创建带稳定 `approvalId` 的 pending 事件，内存 store 以线程安全的一次性决定和有界等待协调审批接口与后台 runner；刷新或 SSE 重连从 store 恢复 pending 状态，重复决定返回冲突。等待超时以受控终态结束，不归因于模型失败。

演示成功不要求模型一定尝试越界。无论模型行为如何，允许范围、批准决定和“受保护动作是否执行”都构成确定性证据；如果发生越界请求，再额外展示拒绝记录。拒绝审批是预期的控制结果，而不是基础设施异常，结果必须分别表达“任务是否完成”和“控制门禁是否生效”。

### 4. Demo 5 用两个隔离调用和一个显式 handoff 展示连续性

Continue 在一次 Demo 运行中固定分为 Session A 与 Session B，两次调用不共享 Responses 会话或消息历史。Session A 只调查任务，不修改代码；Session B 负责继续实现和验证。

PLAIN 的 Session B 只获得原始任务与当前允许文件。HARNESS 在 Session A 结束时持久化一个有界 handoff/checkpoint，包含已完成事项、关键发现、剩余步骤、目标文件和验证命令；Session B 将它作为带明确来源的附加上下文装配。handoff 保存于当前一次性 Demo 工作区，只展示跨会话连续性，不充当长期用户记忆或跨 Demo 数据库。

结构化 handoff 先采用显式 schema 并严格校验；缺失字段或格式错误作为可解释的演示结果，不从自由文本猜测字段。Web 以 `handoff` 事件展示摘要和字段，完整内容仍受脱敏和截断限制。最终证据比较 Session B 的输入来源、重复调查情况、修改、测试和完成状态。

### 5. Demo 6 用本地版本化 provider 工具展示外部依据

夹具同时包含明确标为过期的缓存政策和一份模拟当前提供方政策 JSON。PLAIN 只获得工单和过期缓存/已有知识；HARNESS 额外获得只读 `get_current_shipping_policy` 工具。该工具无网络访问，只返回白名单字段，包括政策版本、生效日期、规则和值的来源标签。

两侧都由同一当前政策契约测试评价。Harness 的结果只有在实际调用工具、引用正确版本/生效日期且最终契约通过时，才能声明“基于当前依据完成”；模型自述或答案长度不构成依据。外部内容作为 data 与系统/开发者指令分隔，输出经过 schema 校验和长度限制，避免把模拟 provider 文本当作高优先级指令。

选择本地 provider 而不调用真实服务，是为了消除网络、认证和第三方版本波动，同时仍完整展示工具获取、来源元数据和契约验证链路。

### 6. Demo 1–3 只补证据，不改变核心实验语义

- Understand 的 input evidence 增加公开的上下文来源类别和装配优先级摘要，不公开服务端系统提示词。
- Act 的 tool evidence 明确区分模型产生结构化 tool call、schema 校验、权限判断、真实执行和结果回填；无工具调用时只陈述事实。
- Prove 的 test/feedback/result evidence 记录可修复失败分类、最大轮数、实际轮数和停止原因，并保持测试源码不直接提供给模型。

这些字段扩展现有 reporter 和 stage-specific evidence，不改变 PLAIN/HARNESS 输入差异、写入语义或确定性评价，也不增加额外的讲解用 LLM 调用。

### 7. 直接扩展现有 Demo 分派与报告边界

新增 `demo_4_control.py`、`demo_5_continue.py`、`demo_6_ground.py`，并把 CLI、`VALID_DEMOS`、Web capability-to-demo 映射和 runner 扩展到 1–6。每个文件直接表达其两侧流程，复用现有 workspace、固定测试、截断、路径验证和 reporter 小工具；不建立通用 Agent 基类或 workflow DSL。

公开事件继续使用现有 `input`、`llm`、`tool`、`write`、`test`、`feedback`、`approval`、`handoff`、`grounding`、`result`、`error` stage。只为确有需要的 stage 增加受控 evidence 字段。RunSnapshot 增加审批、交接、依据版本、停止原因和组件证据事实，后端用确定性模板生成六项能力各自的对照指标。

### 8. 保持顺序运行与结论优先的演示节奏

Web 仍先运行 PLAIN，再运行 HARNESS。任务详情在开始前解释“本次主要改变什么”；完成后按照“本次观察 → 能力指标 → 阶段对照 → 证据 → 完整记录”的顺序展示。Demo 4 强制出现审批阶段，Demo 5 强制出现交接阶段，Demo 6 强制出现依据阶段；缺失事件使用中性事实说明。

组件矩阵放在能力说明附近并默认保持紧凑，不置于最终证据之前重复占用注意力。现场可以只运行两到三个 Demo，但 catalogue 和任务说明必须覆盖全部六项。

### 9. 验证策略以确定性控制流为主，真实 LLM 只做人工排练

后端测试继续注入假 Responses client，覆盖有效/无效工具调用、批准/拒绝/超时、两会话隔离、handoff schema、provider 版本、最终评价和脱敏。Web 测试覆盖 approval 生命周期及 SSE 恢复。前端测试覆盖六项可选择、任务 dialog、组件映射、三类新 evidence、焦点恢复、键盘操作和移动端布局。

真实 LLM 验证记录固定模型、Provider、代码版本和配置，分别运行六对实验并保留失败也可讲解的证据。不把人工排练输出写成自动化断言。

## Risks / Trade-offs

- [Demo 4 模型可能从不越界] → 把强制范围和批准事件作为主要证据；越界拒绝是可选的额外观察，不人为伪造请求。
- [Demo 4 等待审批占用后台线程] → 使用有界等待、一致终态和一次性内存协调；首版保持单机演示规模，不引入队列。
- [Demo 5 handoff 格式受模型波动影响] → 使用明确 schema、有限重试或显式失败，不从自然语言猜测结构；保留原输出作为有界证据。
- [Demo 5 的简单任务让连续性显得人为] → 强制切断消息历史并在 UI 明示 Session A/B 边界，评价重点放在可恢复状态而非回答长度。
- [Demo 6 的本地 JSON 被误解为真实联网] → UI 明确标注“模拟当前提供方，只读本地工具”，讲清演示的是来源与版本治理，不是网络能力。
- [同一任务演示六次后观众已知道答案] → 每场只选两到三个代表 Demo；任务详情降低重复解释，成对实验内部仍保持一致条件。
- [组件映射随 PPT 版本漂移] → 使用稳定 ID、明确“基于 2026-09 培训模型”的文案和单点 catalogue；PPT 更新后人工审查映射。
- [新 change 与可读性 change 修改相同区域] → 先完成并归档或同步前一 change，再应用本 change；实现时以最终主规格为准解决 delta 冲突。
- [增加 RunSnapshot 字段使前后端契约变大] → 只加入六个 Demo 的客观事实，保持可选兼容字段和判别类型，不引入通用遥测载荷。
- [拒绝审批、任务失败和基础设施异常被混为一谈] → 分别记录运行状态、任务结果和能力门禁事实，使用不同的确定性标签。

## Migration Plan

1. 完成 `improve-comparison-readability` 的前端检查并将其 delta spec 同步到主规格。
2. 扩展夹具、公共模型、catalogue 和确定性评价，先保持 Demo 4–6 为 planned。
3. 实现并验证 Demo 4 后端、CLI、Web 审批和前端 evidence，再将 Control 标为 available。
4. 以相同方式依次实现 Continue 和 Ground；每项只有在 CLI、API、UI 和安全测试均通过后才开放。
5. 补强 Demo 1–3 evidence、任务详情 dialog 和组件映射，运行全量后端与前端检查。
6. 使用固定现场配置完成六组成对排练，记录推荐的两到三个现场组合、超时切换点和预录/静态证据备用方案。

回滚按能力进行：将尚不稳定的 Demo 恢复为 planned 并移除分派映射，不影响前三个已实现 Demo。新增夹具均为合成数据，实验状态仍在内存和一次性工作区中，不涉及数据迁移。若前后端契约需要整体回滚，允许服务重启清除短期实验状态。

## Confirmed Decisions

- Web 审批使用服务端 `DEMO_APPROVAL_TIMEOUT_SECONDS`，默认 300 秒；它独立于 LLM 请求超时。
- 审批拒绝以“控制门禁已生效，任务未执行”表示，并与模型验证失败和基础设施异常分开。
- Demo 5 使用固定 JSON schema handoff；目标 Provider 不支持结构化输出时，使用相同 schema 的 `save_handoff` 工具。
- 任务详情只展示公开任务、两侧条件、完成定义、证据和输入来源摘要，不展示完整内部 prompt。
- 组件矩阵明确子 Agent 编排未直接演示；异常处理和输出解析只作为支撑证据呈现。
- Demo 6 使用本地版本化 provider JSON，不调用真实外部服务。
- 产品开放六个 Demo；单次现场分享推荐 Act/Control/Continue 或 Understand/Prove/Ground 三选二到三项组合。
- 本 change 不增加子 Agent Demo；若未来需要演示隔离、并行与汇总，将单独建立 change。
