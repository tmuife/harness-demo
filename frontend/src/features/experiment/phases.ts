import type { EventStage, ExperimentEvent, Side } from './types'

export type Phase = 'information' | 'action' | 'approval' | 'handoff' | 'grounding' | 'verification' | 'feedback' | 'conclusion'

export const phaseOrder: Phase[] = ['information', 'action', 'approval', 'handoff', 'grounding', 'verification', 'feedback', 'conclusion']

export const phaseLabels: Record<Phase, { index: string; title: string; question: string }> = {
  information: { index: '01', title: '获得信息', question: '模型知道什么？' },
  action: { index: '02', title: '采取行动', question: '模型实际做了什么？' },
  approval: { index: '03', title: '等待审批', question: '受保护动作获准了吗？' },
  handoff: { index: '04', title: '交接状态', question: 'Session B 获得了什么状态？' },
  grounding: { index: '05', title: '取得依据', question: '当前事实来自哪里？' },
  verification: { index: '06', title: '执行验证', question: '结果经过验证了吗？' },
  feedback: { index: '07', title: '接收反馈', question: '失败是否成为下一轮输入？' },
  conclusion: { index: '08', title: '形成结论', question: '本次运行证明了什么？' },
}

const stagePhase: Record<EventStage, Phase> = {
  input: 'information', llm: 'action', tool: 'action', write: 'action', test: 'verification',
  feedback: 'feedback', approval: 'approval', handoff: 'handoff', grounding: 'grounding',
  result: 'conclusion', error: 'conclusion',
}

export function phaseForEvent(event: ExperimentEvent, capabilityId: string): Phase {
  if (event.stage === 'llm' && capabilityId === 'understand') return 'information'
  return stagePhase[event.stage]
}

export function visiblePhases(capabilityId: string, events: ExperimentEvent[]): Phase[] {
  const visible = new Set<Phase>(['information', 'conclusion'])
  if (capabilityId === 'act') {
    visible.add('action')
    visible.add('verification')
  }
  if (capabilityId === 'prove') {
    visible.add('action')
    visible.add('verification')
    visible.add('feedback')
  }
  if (capabilityId === 'control') {
    visible.add('action')
    visible.add('approval')
    visible.add('verification')
  }
  if (capabilityId === 'continue') {
    visible.add('action')
    visible.add('handoff')
    visible.add('verification')
  }
  if (capabilityId === 'ground') {
    visible.add('action')
    visible.add('grounding')
    visible.add('verification')
  }
  events.forEach((event) => visible.add(phaseForEvent(event, capabilityId)))
  return phaseOrder.filter((phase) => visible.has(phase))
}

export function eventsForPhase(
  events: ExperimentEvent[], capabilityId: string, phase: Phase, side: Side,
): ExperimentEvent[] {
  return events.filter(
    (event) => event.side === side && phaseForEvent(event, capabilityId) === phase,
  )
}

export function missingPhaseLabel(
  phase: Phase, side: Side, capabilityId: string, finalTest: string, feedbackRounds: number,
): string {
  if (
    phase === 'feedback' && side === 'harness' && capabilityId === 'prove'
    && finalTest === 'passed' && feedbackRounds === 0
  ) return '无需反馈（首轮验证通过）'
  if (side === 'plain' && phase === 'feedback' && capabilityId === 'prove') {
    return '未提供该能力'
  }
  if (phase === 'approval' && capabilityId === 'control') return side === 'plain' ? '不需要审批' : '本次未请求受保护写入'
  if (phase === 'handoff' && capabilityId === 'continue') return side === 'plain' ? '未提供跨会话交接' : '交接记录不可用'
  if (phase === 'grounding' && capabilityId === 'ground') return '未取得当前政策依据'
  if (phase === 'action' || phase === 'verification' || phase === 'feedback') {
    return '本次未执行'
  }
  return '暂无证据'
}
