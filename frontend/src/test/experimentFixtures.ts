import type { Capability, ExperimentResult, RunSnapshot } from '../features/experiment/types'

// Public catalogue snapshot; tests never contact a server or an LLM.
export const capabilities: Capability[] = [
  {
    "id": "understand",
    "title": "Understand · 项目上下文",
    "description": "让模型获得源码、测试、项目规则和集成说明。",
    "evidence": "输入文件、装配优先级与规则识别项",
    "status": "available",
    "demoTask": {
      "number": 1,
      "question": "正确的项目上下文会怎样改变工程分析？",
      "plainCondition": "只向模型提供运费升级工单。",
      "harnessCondition": "在同一工单外提供源码、测试、项目规则和集成说明。",
      "completionDefinition": [
        "保持 calculate_shipping_fee 的公共签名和整数分金额单位。",
        "不得修改测试；任何代码完成声明均以固定 pytest 验证为准。"
      ],
      "expectedEvidence": [
        "输入来源",
        "上下文优先级",
        "规则识别",
        "未修改工作区"
      ],
      "talkTrack": "本次主要变化是项目上下文；两侧都只分析，不写文件。"
    },
    "primaryComponents": [
      {
        "id": "context",
        "title": "上下文管理"
      }
    ],
    "supportingComponents": [
      {
        "id": "prompt",
        "title": "提示词构建"
      },
      {
        "id": "quality",
        "title": "质量验证"
      }
    ],
    "coverageNote": null
  },
  {
    "id": "act",
    "title": "Act · 受限工具行动",
    "description": "让模型在受控范围内读取、写入并运行测试。",
    "evidence": "结构化工具调用、校验、Diff 与测试",
    "status": "available",
    "demoTask": {
      "number": 2,
      "question": "模型建议如何成为可审计、可验证的真实行动？",
      "plainCondition": "模型只能返回补丁或完整实现建议。",
      "harnessCondition": "模型可以调用受限的读文件、写文件和固定测试工具。",
      "completionDefinition": [
        "保持 calculate_shipping_fee 的公共签名和整数分金额单位。",
        "不得修改测试；任何代码完成声明均以固定 pytest 验证为准。"
      ],
      "expectedEvidence": [
        "tool call",
        "schema 与权限决定",
        "实现 Diff",
        "固定测试"
      ],
      "talkTrack": "本次主要变化是工具行动；系统只执行通过校验的请求。"
    },
    "primaryComponents": [
      {
        "id": "tools",
        "title": "工具系统"
      }
    ],
    "supportingComponents": [
      {
        "id": "orchestration",
        "title": "编排循环"
      },
      {
        "id": "parsing",
        "title": "输出解析"
      },
      {
        "id": "safety",
        "title": "安全防护"
      },
      {
        "id": "quality",
        "title": "质量验证"
      }
    ],
    "coverageNote": null
  },
  {
    "id": "prove",
    "title": "Prove · 测试反馈循环",
    "description": "将失败测试摘要反馈给模型并允许修复。",
    "evidence": "测试轮次、失败分类、反馈与停止原因",
    "status": "available",
    "demoTask": {
      "number": 3,
      "question": "外部测试失败如何驱动有限而不是无限的修复循环？",
      "plainCondition": "只生成一次实现，测试结果不返回模型。",
      "harnessCondition": "每次失败后返回精简摘要，并在最大轮数内允许修复。",
      "completionDefinition": [
        "保持 calculate_shipping_fee 的公共签名和整数分金额单位。",
        "不得修改测试；任何代码完成声明均以固定 pytest 验证为准。"
      ],
      "expectedEvidence": [
        "生成/测试轮次",
        "失败反馈",
        "停止原因",
        "最终验证"
      ],
      "talkTrack": "本次主要变化是测试反馈；测试源码始终不直接交给模型。"
    },
    "primaryComponents": [
      {
        "id": "quality",
        "title": "质量验证"
      }
    ],
    "supportingComponents": [
      {
        "id": "orchestration",
        "title": "编排循环"
      },
      {
        "id": "errors",
        "title": "异常处理"
      },
      {
        "id": "tools",
        "title": "工具系统"
      },
      {
        "id": "state",
        "title": "状态管理"
      }
    ],
    "coverageNote": null
  },
  {
    "id": "control",
    "title": "Control · 边界与审批",
    "description": "在关键写入前要求审批并拒绝越界操作。",
    "evidence": "允许范围、审批、拒绝与最终范围检查",
    "status": "available",
    "demoTask": {
      "number": 4,
      "question": "模型想要写入时，谁决定行动是否允许？",
      "plainCondition": "使用较宽但仍限于合成工作区的写入范围，无人工审批。",
      "harnessCondition": "仅允许写入 src/shipping.py，第一次有效写入必须人工批准。",
      "completionDefinition": [
        "保持 calculate_shipping_fee 的公共签名和整数分金额单位。",
        "不得修改测试；任何代码完成声明均以固定 pytest 验证为准。"
      ],
      "expectedEvidence": [
        "策略范围",
        "审批决定",
        "拒绝记录",
        "受保护动作",
        "测试"
      ],
      "talkTrack": "本次主要变化是控制门禁；拒绝审批代表门禁成功，不是基础设施错误。"
    },
    "primaryComponents": [
      {
        "id": "safety",
        "title": "安全防护"
      }
    ],
    "supportingComponents": [
      {
        "id": "tools",
        "title": "工具系统"
      },
      {
        "id": "state",
        "title": "状态管理"
      },
      {
        "id": "orchestration",
        "title": "编排循环"
      }
    ],
    "coverageNote": null
  },
  {
    "id": "continue",
    "title": "Continue · 跨会话状态",
    "description": "通过结构化交接记录继续未完成工作。",
    "evidence": "Session A/B、交接记录、恢复输入与验证",
    "status": "available",
    "demoTask": {
      "number": 5,
      "question": "会话中断后，下一次调用如何基于已完成工作继续？",
      "plainCondition": "Session B 只有工单和当前允许文件。",
      "harnessCondition": "Session B 额外读取 Session A 的经校验 JSON handoff。",
      "completionDefinition": [
        "保持 calculate_shipping_fee 的公共签名和整数分金额单位。",
        "不得修改测试；任何代码完成声明均以固定 pytest 验证为准。"
      ],
      "expectedEvidence": [
        "会话边界",
        "handoff 字段",
        "恢复输入",
        "修改与测试"
      ],
      "talkTrack": "本次主要变化是跨会话状态；A/B 不共享模型消息历史。"
    },
    "primaryComponents": [
      {
        "id": "memory",
        "title": "记忆系统"
      },
      {
        "id": "state",
        "title": "状态管理"
      }
    ],
    "supportingComponents": [
      {
        "id": "context",
        "title": "上下文管理"
      },
      {
        "id": "prompt",
        "title": "提示词构建"
      }
    ],
    "coverageNote": null
  },
  {
    "id": "ground",
    "title": "Ground · 外部依据",
    "description": "使用带版本和生效日期的本地权威依据。",
    "evidence": "来源、版本、生效日期、工具调用与契约测试",
    "status": "available",
    "demoTask": {
      "number": 6,
      "question": "任务依赖会变化的外部政策时，如何取得可追溯依据？",
      "plainCondition": "只看到工单和明确标记为过期的缓存政策。",
      "harnessCondition": "可以读取本地模拟 provider 的当前版本化政策工具。",
      "completionDefinition": [
        "保持 calculate_shipping_fee 的公共签名和整数分金额单位。",
        "不得修改测试；任何代码完成声明均以固定 pytest 验证为准。"
      ],
      "expectedEvidence": [
        "依据来源",
        "版本/生效日期",
        "grounding 工具",
        "契约测试"
      ],
      "talkTrack": "本次主要变化是当前权威依据；provider 是本地模拟数据，不是联网服务。"
    },
    "primaryComponents": [
      {
        "id": "context",
        "title": "上下文管理"
      }
    ],
    "supportingComponents": [
      {
        "id": "tools",
        "title": "工具系统"
      },
      {
        "id": "prompt",
        "title": "提示词构建"
      },
      {
        "id": "quality",
        "title": "质量验证"
      },
      {
        "id": "safety",
        "title": "安全防护"
      }
    ],
    "coverageNote": "子 Agent 编排未在本轮六个现场实验中直接演示。"
  }
]

export const task = { id: 'shipping-policy-upgrade', title: '运费规则升级', summary: '更新配送政策并通过固定验证。' }

export function runSnapshot(status: RunSnapshot['status'] = 'completed'): RunSnapshot {
  return { status, outcome: status === 'completed' ? 'analysis' : null, calls: 0, inputSources: [], modifiedFiles: [], testRuns: 0, feedbackRounds: 0, finalTest: 'not_run', checks: {}, workspaceUnchanged: true, scopeOk: true, proposalOnly: false }
}

export function experiment(capabilityId = 'act', status: ExperimentResult['status'] = 'completed'): ExperimentResult {
  return { experimentId: 'exp_test', capabilityId, status, plain: runSnapshot(), harness: runSnapshot(status === 'running' ? 'running' : 'completed'), events: [], comparison: null }
}
