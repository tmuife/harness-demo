# Harness 演示后端

这个 Python 项目使用真实 LLM，对比同一个运费规则升级任务在 PLAIN 模式和增加一项 Harness 能力后的结果。

当前包含六个独立实验：

| Demo | PLAIN | `--harness` |
| --- | --- | --- |
| 1：项目上下文 | 只向 LLM 提供工单 | 增加源码、测试、项目规则和集成说明 |
| 2：受限工具行动 | LLM 只能给出代码提案 | LLM 可以读取文件、写入目标文件并运行固定测试 |
| 3：测试反馈循环 | 生成一次后才做最终评价 | 将测试失败摘要反馈给 LLM，并允许继续修复 |
| 4：边界与审批 | 较宽但有界的合成工作区写入，无人工审批 | 仅允许写入实现文件，首次写入须人工审批 |
| 5：跨会话状态 | Session B 不获得 Session A 的消息或交接信息 | Session B 读取经校验的 `handoff.json` 继续任务 |
| 6：外部依据 | 只依据标记为过期的缓存政策 | 使用本地模拟 provider 的当前版本化政策工具 |

演示使用统一的合成运费计算器。正确规则包含普通/会员免邮阈值、阈值边界和国际订单固定运费。

## 环境准备

后端使用 Python 3.12 和 `uv`。以下命令均从 `backend/` 执行：

```bash
uv sync
cp .env.example .env
```

编辑 `.env`：

```dotenv
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=your-model-name

OPENAI_TIMEOUT_SECONDS=120
DEMO_MAX_TURNS=4
DEMO_APPROVAL_TIMEOUT_SECONDS=300
```

目标 Base URL 和模型需要支持 OpenAI Responses API 及函数工具调用。后端直接使用官方 OpenAI Python SDK，不使用 Agents SDK，也不为演示命令提供预设回答模式。

`.env` 已被仓库忽略，不要提交真实凭据。

## 运行演示

查看可用 Demo；此命令不会读取配置、创建工作区或调用 LLM：

```bash
uv run harness-demo list
```

每个实验可以分别运行基线和 Harness 模式：

```bash
uv run harness-demo 1
uv run harness-demo 1 --harness

uv run harness-demo 2
uv run harness-demo 2 --harness

uv run harness-demo 3
uv run harness-demo 3 --harness

uv run harness-demo 4
uv run harness-demo 4 --harness

uv run harness-demo 5
uv run harness-demo 5 --harness

uv run harness-demo 6
uv run harness-demo 6 --harness
```

每次运行都会从 `fixtures/shipping/` 创建独立的干净工作区：

```text
.demo-workspace/demo-1-plain/
.demo-workspace/demo-1-harness/
```

重复运行会重建对应目录。终端使用 `[LLM]`、`[TOOL]`、`[WRITE]`、`[TEST]`、`[FEEDBACK]` 和 `[RESULT]` 展示关键过程。

Demo 3 不直接向 LLM 提供测试源码。PLAIN 模式只生成一次；Harness 模式获得精简的失败测试名称、断言差异和错误摘要。基线测试失败是有价值的演示结果，因此需要结合终端中的最终 `PASS/FAIL` 理解命令退出状态。

Demo 4 的 CLI 在 HARNESS 第一次有效写入前等待 `y/yes/是` 批准；`n`、无输入或超过 `DEMO_APPROVAL_TIMEOUT_SECONDS`（默认 300 秒）会停止受保护写入并留下控制证据。Demo 5 的 `handoff.json` 只存在于本次工作区，PLAIN Session B 不接收它。Demo 6 的 `get_current_shipping_policy` 只读取本地合成 JSON，显示版本和生效日期，不调用真实外部服务。

## Harness Lab API

启动供前端使用的本地 API：

```bash
uv run uvicorn harness_demo.web.app:app --host 127.0.0.1 --port 8000
```

服务默认监听 `http://127.0.0.1:8000`，提供能力目录、任务、实验创建、结果和 SSE 事件流。现有 `harness-demo` CLI 保持独立可用。前端开发服务器将 `/api` 代理到此地址；API Key、工作区路径和工具权限不会发送到浏览器。

Web 事件以一次有意义的输入、模型调用、工具、写入、测试、反馈或结果作为一条记录。模型正文、Diff 和测试日志作为经过脱敏、截断的事件证据返回，不再按控制台输出逐行拆分。最终结果快照还包含输入来源、调用/测试/反馈次数、修改文件和能力定制的 PLAIN/HARNESS 对照摘要；这些结论只描述本次运行，不是统计 benchmark。

开发 API 源码时如需热重载，请仅监听 `src/`，避免 Demo 写入 `.demo-workspace/` 时重启进程并清空内存中的实验状态：

```bash
uv run uvicorn harness_demo.web.app:app --host 127.0.0.1 --port 8000 --reload --reload-dir src
```

运行实际对照实验时不要使用当前的 `uv run harness-api`，因为该脚本会监听整个后端目录；工作区中的 Python 文件变化会触发重载，导致实验记录丢失并返回 404。

## 安全边界

- 任务、代码和政策均为合成内容。
- 模型触发的文件操作只能访问当前 Demo 工作区。
- 写入工具只允许修改 `src/shipping.py`。
- 测试工具只能执行固定的 `python -m pytest -q`。
- 子进程使用 `shell=False`、固定目录、超时和输出长度限制。
- API Key、认证头和原始请求错误不会打印到终端。
- Demo 6 的 provider 内容按白名单 schema 读取并作为数据处理，不作为高优先级指令。

## 开发验证

确定性测试使用注入的轻量假 Responses 客户端，不访问网络：

```bash
uv run python -m pytest -q
uv run python -m ruff check src tests fixtures
```

Python 虚拟环境不可跨目录直接搬移。如果迁移前保留的 `.venv` 导致某个命令仍引用旧路径，应删除该本地虚拟环境后重新执行 `uv sync`；`.venv` 不属于项目源文件。

项目级设计见 [../docs/DESIGN.zh-CN.md](../docs/DESIGN.zh-CN.md)。
