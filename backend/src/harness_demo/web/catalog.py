"""Server-owned task, teaching, and capability metadata."""

from __future__ import annotations

from harness_demo.web.models import Capability, DemoTask, HarnessComponent, TaskBrief

TASK = TaskBrief(
    id="shipping-policy-upgrade",
    title="运费规则升级",
    summary="保持 calculate_shipping_fee 公共签名不变，更新配送政策并通过固定验证。",
)

_COMPONENTS = {
    "orchestration": "编排循环",
    "tools": "工具系统",
    "memory": "记忆系统",
    "context": "上下文管理",
    "prompt": "提示词构建",
    "parsing": "输出解析",
    "state": "状态管理",
    "errors": "异常处理",
    "safety": "安全防护",
    "quality": "质量验证",
    "subagents": "子 Agent 编排",
}


def _components(*ids: str) -> list[HarnessComponent]:
    return [HarnessComponent(id=item, title=_COMPONENTS[item]) for item in ids]


def _task(
    number: int, question: str, plain: str, harness: str, evidence: list[str], talk: str
) -> DemoTask:
    return DemoTask(
        number=number,
        question=question,
        plainCondition=plain,
        harnessCondition=harness,
        completionDefinition=[
            "保持 calculate_shipping_fee 的公共签名和整数分金额单位。",
            "不得修改测试；任何代码完成声明均以固定 pytest 验证为准。",
        ],
        expectedEvidence=evidence,
        talkTrack=talk,
    )


CAPABILITIES = (
    Capability(
        id="understand",
        title="Understand · 项目上下文",
        description="让模型获得源码、测试、项目规则和集成说明。",
        evidence="输入文件、装配优先级与规则识别项",
        status="available",
        demoTask=_task(
            1,
            "正确的项目上下文会怎样改变工程分析？",
            "只向模型提供运费升级工单。",
            "在同一工单外提供源码、测试、项目规则和集成说明。",
            ["输入来源", "上下文优先级", "规则识别", "未修改工作区"],
            "本次主要变化是项目上下文；两侧都只分析，不写文件。",
        ),
        primaryComponents=_components("context"),
        supportingComponents=_components("prompt", "quality"),
    ),
    Capability(
        id="act",
        title="Act · 受限工具行动",
        description="让模型在受控范围内读取、写入并运行测试。",
        evidence="结构化工具调用、校验、Diff 与测试",
        status="available",
        demoTask=_task(
            2,
            "模型建议如何成为可审计、可验证的真实行动？",
            "模型只能返回补丁或完整实现建议。",
            "模型可以调用受限的读文件、写文件和固定测试工具。",
            ["tool call", "schema 与权限决定", "实现 Diff", "固定测试"],
            "本次主要变化是工具行动；系统只执行通过校验的请求。",
        ),
        primaryComponents=_components("tools"),
        supportingComponents=_components("orchestration", "parsing", "safety", "quality"),
    ),
    Capability(
        id="prove",
        title="Prove · 测试反馈循环",
        description="将失败测试摘要反馈给模型并允许修复。",
        evidence="测试轮次、失败分类、反馈与停止原因",
        status="available",
        demoTask=_task(
            3,
            "外部测试失败如何驱动有限而不是无限的修复循环？",
            "只生成一次实现，测试结果不返回模型。",
            "每次失败后返回精简摘要，并在最大轮数内允许修复。",
            ["生成/测试轮次", "失败反馈", "停止原因", "最终验证"],
            "本次主要变化是测试反馈；测试源码始终不直接交给模型。",
        ),
        primaryComponents=_components("quality"),
        supportingComponents=_components("orchestration", "errors", "tools", "state"),
    ),
    Capability(
        id="control",
        title="Control · 边界与审批",
        description="在关键写入前要求审批并拒绝越界操作。",
        evidence="允许范围、审批、拒绝与最终范围检查",
        status="available",
        demoTask=_task(
            4,
            "模型想要写入时，谁决定行动是否允许？",
            "使用较宽但仍限于合成工作区的写入范围，无人工审批。",
            "仅允许写入 src/shipping.py，第一次有效写入必须人工批准。",
            ["策略范围", "审批决定", "拒绝记录", "受保护动作", "测试"],
            "本次主要变化是控制门禁；拒绝审批代表门禁成功，不是基础设施错误。",
        ),
        primaryComponents=_components("safety"),
        supportingComponents=_components("tools", "state", "orchestration"),
    ),
    Capability(
        id="continue",
        title="Continue · 跨会话状态",
        description="通过结构化交接记录继续未完成工作。",
        evidence="Session A/B、交接记录、恢复输入与验证",
        status="available",
        demoTask=_task(
            5,
            "会话中断后，下一次调用如何基于已完成工作继续？",
            "Session B 只有工单和当前允许文件。",
            "Session B 额外读取 Session A 的经校验 JSON handoff。",
            ["会话边界", "handoff 字段", "恢复输入", "修改与测试"],
            "本次主要变化是跨会话状态；A/B 不共享模型消息历史。",
        ),
        primaryComponents=_components("memory", "state"),
        supportingComponents=_components("context", "prompt"),
    ),
    Capability(
        id="ground",
        title="Ground · 外部依据",
        description="使用带版本和生效日期的本地权威依据。",
        evidence="来源、版本、生效日期、工具调用与契约测试",
        status="available",
        demoTask=_task(
            6,
            "任务依赖会变化的外部政策时，如何取得可追溯依据？",
            "只看到工单和明确标记为过期的缓存政策。",
            "可以读取本地模拟 provider 的当前版本化政策工具。",
            ["依据来源", "版本/生效日期", "grounding 工具", "契约测试"],
            "本次主要变化是当前权威依据；provider 是本地模拟数据，不是联网服务。",
        ),
        primaryComponents=_components("context"),
        supportingComponents=_components("tools", "prompt", "quality", "safety"),
        coverageNote="子 Agent 编排未在本轮六个现场实验中直接演示。",
    ),
)

CAPABILITY_TO_DEMO = {
    "understand": 1,
    "act": 2,
    "prove": 3,
    "control": 4,
    "continue": 5,
    "ground": 6,
}


def find_capability(capability_id: str) -> Capability | None:
    return next((item for item in CAPABILITIES if item.id == capability_id), None)
