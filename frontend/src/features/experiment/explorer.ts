import type { Capability, DemoTask } from './types'
import type { Phase } from './phases'

export const componentGroups = [
  { id: 'information', title: '信息准备', label: 'CONTEXT IN' },
  { id: 'orchestration', title: '编排中枢', label: 'AGENT LOOP' },
  { id: 'execution', title: '行动执行', label: 'ACTION OUT' },
  { id: 'continuity', title: '跨会话连续性', label: 'CONTINUITY' },
  { id: 'verification', title: '验证与恢复', label: 'FEEDBACK' },
  { id: 'control', title: '贯穿行动的控制边界', label: 'GUARDRAILS' },
] as const

export interface TeachingComponent {
  id: string
  title: string
  english: string
  groupId: (typeof componentGroups)[number]['id']
  description: string
}

// Teaching copy and layout only. Availability, relationships and evidence come from the API.
export const teachingComponents: TeachingComponent[] = [
  { id: 'context', title: '上下文管理', english: 'Context', groupId: 'information', description: '把相关的源码、规则与当前依据交给模型，让判断建立在任务所需的信息上。' },
  { id: 'prompt', title: '提示词构建', english: 'Prompt', groupId: 'information', description: '将任务、项目约束与参考资料组织成有来源和优先级的模型输入。' },
  { id: 'orchestration', title: '编排循环', english: 'Orchestration', groupId: 'orchestration', description: '协调模型调用、工具执行与反馈，决定何时继续、何时停止。' },
  { id: 'subagents', title: '子 Agent 编排', english: 'Sub-agents', groupId: 'orchestration', description: '将工作分配给隔离的子 Agent，并协调并行执行与结果汇总。当前六个 Demo 没有直接演示这一能力。' },
  { id: 'parsing', title: '输出解析', english: 'Parsing', groupId: 'execution', description: '识别结构化工具请求并校验参数，把模型输出转成可以被系统检查的行动。' },
  { id: 'tools', title: '工具系统', english: 'Tools', groupId: 'execution', description: '让模型通过受控工具读取文件、修改实现和运行测试，留下可查看的行动证据。' },
  { id: 'memory', title: '记忆系统', english: 'Memory', groupId: 'continuity', description: '保存可复用的发现与未完成事项。本项目通过一次实验内的交接记录演示跨会话续做。' },
  { id: 'state', title: '状态管理', english: 'State', groupId: 'continuity', description: '记录任务进展、会话边界和执行结果，让后续步骤知道工作到了哪里。' },
  { id: 'quality', title: '质量验证', english: 'Verification', groupId: 'verification', description: '用外部测试和约束检查评价实际结果，并将失败证据用于后续修复。' },
  { id: 'errors', title: '异常处理', english: 'Recovery', groupId: 'verification', description: '区分可修复的测试失败与运行异常，在有限轮次内反馈、重试或停止。' },
  { id: 'safety', title: '安全防护', english: 'Safety & approval', groupId: 'control', description: '模型提出行动，系统决定是否允许。通过范围校验与人工审批保护关键写入。' },
]

export const businessBackground = {
  summary: '围绕配送政策变更，分析或修改运费计算逻辑。',
  description: '一家商店需要升级运费规则。模型将面对同一个合成运费计算器，分析项目约束，或在各 Demo 允许的条件下更新实现。六个实验分别观察信息、行动、反馈、控制、连续性和依据的差异。',
  constraints: ['任务和政策均为合成业务资料。', '实验仅在隔离工作区中进行，测试文件不可修改。', '分析、建议、实际执行与验证结果分别呈现，以本次运行证据为准。'],
}

interface TaskTeaching {
  objective: string
  completion: string[]
  phases: Phase[]
}

const taskTeaching: Record<string, TaskTeaching> = {
  understand: {
    objective: '分析运费升级需求，识别项目规则与实现约束。',
    completion: ['识别运费规则和项目约束，并说明分析所依据的输入。', '两侧只读分析，不修改工作区；不以实现测试通过评价分析结果。'],
    phases: ['information', 'conclusion'],
  },
  act: {
    objective: '将运费逻辑修改建议，变成受控的文件操作与验证。',
    completion: ['PLAIN 仅生成代码建议，不将建议描述为已执行。', 'HARNESS 的完成声明以允许文件的实际修改和固定测试为准，不修改测试或公共签名。'],
    phases: ['action', 'verification'],
  },
  prove: {
    objective: '实现运费规则，并在有限轮次内根据测试反馈修复。',
    completion: ['比较一次生成与有限反馈循环的实现、测试轮次和停止原因。', '首轮通过时无需反馈；最终实现是否完成以固定测试为准。'],
    phases: ['verification', 'feedback'],
  },
  control: {
    objective: '修改运费计算逻辑，观察范围限制与审批如何控制写入。',
    completion: ['分别查看控制门禁是否生效、受保护动作是否执行与任务是否完成。', '拒绝或超时可使任务停止，不将其描述为实现成功；获准写入仍需范围检查和测试。'],
    phases: ['approval', 'action', 'verification'],
  },
  continue: {
    objective: '由 Session A 调查任务，让隔离的 Session B 接手续做。',
    completion: ['查看会话边界、交接有效性和 Session B 实际获得的输入。', '交接记录仅用于本次工作区，Session B 的实现以修改与固定验证评价。'],
    phases: ['handoff', 'information', 'verification'],
  },
  ground: {
    objective: '依据当前版本配送政策更新运费逻辑，并验证规则。',
    completion: ['查看是否实际取得当前政策的来源、版本与生效日期。', '以当前政策契约验证实现；provider 为本地模拟数据，不代表真实联网。'],
    phases: ['grounding', 'verification'],
  },
}

export interface TaskPreview {
  objective: string
  detail: DemoTask
  phases: Phase[]
}

export function taskPreview(capability: Capability): TaskPreview {
  const teaching = taskTeaching[capability.id]
  const detail = capability.demoTask
  return {
    objective: teaching?.objective ?? capability.description,
    phases: teaching?.phases ?? ['conclusion'],
    detail: {
      number: detail?.number ?? 0,
      question: detail?.question ?? '这项能力会怎样影响本次任务？',
      plainCondition: detail?.plainCondition ?? '暂无详细条件说明。',
      harnessCondition: detail?.harnessCondition ?? '暂无详细条件说明。',
      completionDefinition: teaching?.completion ?? detail?.completionDefinition ?? ['暂无详细完成条件。'],
      expectedEvidence: detail?.expectedEvidence?.length ? detail.expectedEvidence : [capability.evidence || '暂无证据说明'],
      talkTrack: detail?.talkTrack ?? '以本次运行的实际证据为准。',
    },
  }
}

export function componentRelation(capability: Capability, componentId: string) {
  if (capability.primaryComponents?.some((item) => item.id === componentId)) return 'primary'
  if (capability.supportingComponents?.some((item) => item.id === componentId)) return 'supporting'
  return null
}

export function relatedCapabilities(capabilities: Capability[], componentId: string): Capability[] {
  return capabilities.filter((capability) => componentRelation(capability, componentId)).sort((left, right) => {
    const rank = (item: Capability) => componentRelation(item, componentId) === 'primary' ? 0 : 1
    return rank(left) - rank(right)
      || (left.demoTask?.number ?? Infinity) - (right.demoTask?.number ?? Infinity)
      || left.id.localeCompare(right.id)
  })
}

export function capabilityForComponent(capabilities: Capability[], componentId: string, currentId: string | null) {
  const available = relatedCapabilities(capabilities, componentId).filter((item) => item.status === 'available')
  return available.find((item) => item.id === currentId)?.id ?? available[0]?.id ?? null
}

export function componentForCapability(capability: Capability | undefined): string | null {
  return capability?.primaryComponents?.[0]?.id ?? capability?.supportingComponents?.[0]?.id ?? null
}
