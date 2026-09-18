import { ApprovalCard } from './ApprovalCard'
import { EvidenceDrawer } from './EvidenceDrawer'
import type { ExperimentEvent } from '../types'

const stageLabels: Record<ExperimentEvent['stage'], string> = {
  input: '输入', llm: '模型', tool: '工具', write: '写入', test: '测试', feedback: '反馈',
  approval: '审批', handoff: '交接', grounding: '依据', result: '结论', error: '异常',
}

export function EventCard({ event, showMeta = false, approvalStatus, interactive = false }: { event: ExperimentEvent; showMeta?: boolean; approvalStatus?: string; interactive?: boolean }) {
  return (
    <article className={`event-card event-${event.stage}`} id={showMeta ? undefined : `event-${event.id}`} tabIndex={-1}>
      <div className="event-card-head">
        <span className="event-stage">{stageLabels[event.stage]}</span>
        {showMeta ? <span className={`side-chip side-${event.side}`}>{event.side.toUpperCase()}</span> : null}
        {showMeta ? <span className="event-sequence">#{event.sequence}</span> : null}
      </div>
      <strong>{event.title}</strong>
      <p>{event.summary}</p>
      {showMeta ? <time dateTime={event.occurredAt}>{new Date(event.occurredAt).toLocaleTimeString()}</time> : null}
      {event.stage === 'approval' && event.evidence.approvalId ? (
        <ApprovalCard
          approvalId={event.evidence.approvalId}
          action={event.evidence.action ?? event.summary}
          scope={event.evidence.scope ?? '受控工作区'}
          status={approvalStatus ?? event.evidence.approvalStatus ?? event.status}
          interactive={interactive && !showMeta}
        />
      ) : null}
      <EvidenceDrawer evidence={event.evidence} />
    </article>
  )
}
