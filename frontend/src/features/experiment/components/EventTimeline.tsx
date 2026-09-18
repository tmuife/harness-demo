import { EventCard } from './EventCard'
import type { ExperimentEvent } from '../types'

export function EventTimeline({ events, waiting }: { events: ExperimentEvent[]; waiting?: boolean }) {
  if (waiting) return <div className="timeline-empty">等待 PLAIN 基线完成</div>
  if (events.length === 0) return <div className="timeline-empty">等待关键步骤</div>
  return (
    <ol className="timeline" aria-label="运行关键步骤">
      {events.map((event) => {
        const approvalId = event.evidence.approvalId
        const latest = approvalId ? events.filter((item) => item.evidence.approvalId === approvalId).at(-1) : null
        return <li key={event.id}><EventCard event={event} approvalStatus={latest?.evidence.approvalStatus ?? latest?.status} interactive={latest?.id === event.id} /></li>
      })}
    </ol>
  )
}
