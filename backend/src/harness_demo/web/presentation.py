"""Sanitize public evidence and build deterministic comparison explanations."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from harness_demo.common import PROJECT_ROOT, truncate
from harness_demo.web.models import (
    ComparisonMetric,
    ComparisonSummary,
    EventEvidence,
    EventStage,
    RunSnapshot,
)

QUALIFICATION = "仅表示本次真实 LLM 运行观察，不是统计性 benchmark。"


def sanitize_text(value: str) -> str:
    normalized = value.replace(str(PROJECT_ROOT), "<backend>")
    normalized = re.sub(r"(OPENAI_API_KEY\s*=\s*)\S+", r"\1[REDACTED]", normalized)
    normalized = re.sub(r"(Authorization:\s*Bearer\s+)\S+", r"\1[REDACTED]", normalized)
    return truncate(normalized, 4_000)


def build_evidence(stage: EventStage, raw: Mapping[str, object] | None = None) -> EventEvidence:
    values: dict[str, object] = {"kind": stage}
    for key, value in (raw or {}).items():
        if isinstance(value, str):
            values[key] = sanitize_text(value)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            values[key] = [sanitize_text(item) if isinstance(item, str) else item for item in value]
        elif isinstance(value, Mapping):
            values[key] = {
                sanitize_text(str(item_key)): item_value
                for item_key, item_value in value.items()
                if isinstance(item_value, bool)
            }
        elif isinstance(value, (bool, int)) or value is None:
            values[key] = value
    return EventEvidence.model_validate(values)


def build_comparison(
    capability_id: str,
    plain: RunSnapshot,
    harness: RunSnapshot,
) -> ComparisonSummary | None:
    if plain.status not in {"completed", "failed"} or harness.status not in {"completed", "failed"}:
        return None
    if "infrastructure_error" in {plain.outcome, harness.outcome}:
        return ComparisonSummary(
            observation="本次实验未完整完成；运行异常使两侧结果不能直接比较。",
            qualification=QUALIFICATION,
            metrics=[
                ComparisonMetric(
                    label="运行状态",
                    plain=_outcome_label(plain),
                    harness=_outcome_label(harness),
                )
            ],
        )
    if capability_id == "understand":
        return ComparisonSummary(
            observation=("本次运行中，PLAIN 仅依据工单完成分析；HARNESS 结合项目上下文完成分析。"),
            qualification=QUALIFICATION,
            metrics=[
                ComparisonMetric(
                    label="输入来源",
                    plain=f"{len(plain.input_sources)} 项",
                    harness=f"{len(harness.input_sources)} 项",
                ),
                ComparisonMetric(
                    label="识别规则",
                    plain=_check_count(plain),
                    harness=_check_count(harness),
                ),
                ComparisonMetric(
                    label="工作区",
                    plain=_workspace_label(plain),
                    harness=_workspace_label(harness),
                ),
            ],
        )
    if capability_id == "act":
        return ComparisonSummary(
            observation=(
                "本次运行中，PLAIN 仅生成代码建议；HARNESS 在受限工作区实际修改并验证实现。"
            ),
            qualification=QUALIFICATION,
            metrics=[
                ComparisonMetric(
                    label="完成方式",
                    plain="仅生成建议" if plain.proposal_only else _outcome_label(plain),
                    harness="实际修改" if harness.modified_files else "本次未修改",
                ),
                ComparisonMetric(
                    label="固定测试",
                    plain=_test_label(plain),
                    harness=_test_label(harness),
                ),
                ComparisonMetric(
                    label="修改范围",
                    plain="未写入",
                    harness=_scope_label(harness),
                ),
            ],
        )
    if capability_id == "prove":
        return ComparisonSummary(
            observation=_prove_observation(plain, harness),
            qualification=QUALIFICATION,
            metrics=[
                ComparisonMetric(
                    label="模型生成", plain=f"{plain.calls} 次", harness=f"{harness.calls} 次"
                ),
                ComparisonMetric(
                    label="测试执行",
                    plain=f"{plain.test_runs} 次",
                    harness=f"{harness.test_runs} 次",
                ),
                ComparisonMetric(
                    label="失败反馈",
                    plain=f"{plain.feedback_rounds} 次",
                    harness=f"{harness.feedback_rounds} 次",
                ),
                ComparisonMetric(
                    label="最终验证", plain=_test_label(plain), harness=_test_label(harness)
                ),
            ],
        )
    if capability_id == "control":
        return ComparisonSummary(
            observation=(
                "本次运行中，PLAIN 不要求人工批准；HARNESS 将首次受保护写入交给控制门禁。"
            ),
            qualification=QUALIFICATION,
            metrics=[
                ComparisonMetric(
                    label="人工审批", plain="不需要", harness=_approval_label(harness)
                ),
                ComparisonMetric(
                    label="受保护写入", plain="不适用", harness=_protected_action_label(harness)
                ),
                ComparisonMetric(
                    label="控制结果",
                    plain="基线无门禁",
                    harness=harness.capability_outcome or "暂无证据",
                ),
                ComparisonMetric(
                    label="最终验证", plain=_test_label(plain), harness=_test_label(harness)
                ),
            ],
        )
    if capability_id == "continue":
        return ComparisonSummary(
            observation=(
                "本次运行中，HARNESS 将经校验的 Session A 交接记录带入新的 Session B；PLAIN 不传递该状态。"
            ),
            qualification=QUALIFICATION,
            metrics=[
                ComparisonMetric(
                    label="Session B 输入",
                    plain=f"{len(plain.input_sources)} 项",
                    harness=f"{len(harness.input_sources)} 项",
                ),
                ComparisonMetric(
                    label="结构化交接", plain=_handoff_label(plain), harness=_handoff_label(harness)
                ),
                ComparisonMetric(
                    label="最终验证", plain=_test_label(plain), harness=_test_label(harness)
                ),
            ],
        )
    if capability_id == "ground":
        return ComparisonSummary(
            observation=(
                "本次运行中，HARNESS 通过本地模拟 provider 获取可追溯的当前政策；PLAIN 只依据过期缓存。"
            ),
            qualification=QUALIFICATION,
            metrics=[
                ComparisonMetric(
                    label="当前依据",
                    plain="未取得",
                    harness="已取得" if harness.grounding_used else "未取得",
                ),
                ComparisonMetric(
                    label="政策版本",
                    plain=plain.policy_version or "过期缓存",
                    harness=harness.policy_version or "暂无证据",
                ),
                ComparisonMetric(
                    label="生效日期",
                    plain=plain.effective_date or "暂无证据",
                    harness=harness.effective_date or "暂无证据",
                ),
                ComparisonMetric(
                    label="最终验证", plain=_test_label(plain), harness=_test_label(harness)
                ),
            ],
        )
    return None


def _outcome_label(run: RunSnapshot) -> str:
    return {
        "analysis": "已完成分析",
        "proposal": "仅生成代码建议",
        "passed": "确定性验证通过",
        "failed": "确定性验证未通过",
        "infrastructure_error": "实验运行异常",
        "controlled_stop": "控制门禁已生效",
        "handoff_error": "交接记录不可用",
        "grounding_error": "当前依据未取得",
        None: "暂无结论",
    }[run.outcome]


def _check_count(run: RunSnapshot) -> str:
    return f"{sum(run.checks.values())}/{len(run.checks)} 项" if run.checks else "暂无证据"


def _workspace_label(run: RunSnapshot) -> str:
    if run.workspace_unchanged is True:
        return "未修改（符合预期）"
    if run.workspace_unchanged is False:
        return "发生修改"
    return "暂无证据"


def _test_label(run: RunSnapshot) -> str:
    return {
        "passed": "验证通过",
        "failed": "验证未通过",
        "not_run": "未执行",
        "unknown": "暂无证据",
    }[run.final_test]


def _scope_label(run: RunSnapshot) -> str:
    if run.scope_ok is True:
        return "符合允许范围"
    if run.scope_ok is False:
        return "超出允许范围"
    return "暂无证据"


def _approval_label(run: RunSnapshot) -> str:
    return {
        "approved": "已批准",
        "rejected": "已拒绝",
        "timed_out": "等待超时",
        "pending": "等待中",
        None: "暂无证据",
    }.get(run.approval_status, run.approval_status or "暂无证据")


def _protected_action_label(run: RunSnapshot) -> str:
    if run.protected_action_executed is True:
        return "已执行"
    if run.protected_action_executed is False:
        return "未执行"
    return "暂无证据"


def _handoff_label(run: RunSnapshot) -> str:
    if run.handoff_valid is True:
        return "已校验并恢复"
    if run.handoff_valid is False:
        return "记录不可用"
    if run.handoff_available is False:
        return "未提供"
    return "暂无证据"


def _prove_observation(plain: RunSnapshot, harness: RunSnapshot) -> str:
    if harness.feedback_rounds and harness.final_test == "passed":
        return "本次运行中，HARNESS 获得失败摘要后继续修复并通过验证。"
    if harness.feedback_rounds:
        return "本次运行中，HARNESS 根据失败摘要继续修复，但最终验证仍未通过。"
    if harness.final_test == "passed":
        return "本次运行中，HARNESS 首轮验证通过，因此无需进入失败反馈循环。"
    return f"本次运行中，PLAIN 最终{_test_label(plain)}；HARNESS 最终{_test_label(harness)}。"
