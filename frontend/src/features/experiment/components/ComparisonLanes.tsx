import { EventTimeline } from './EventTimeline'
import { PhaseComparison } from './PhaseComparison'
import type { ExperimentResult, Side } from '../types'

export function ComparisonLanes({ experiment }: { experiment: ExperimentResult | null }) {
  if (experiment && (experiment.status === 'completed' || experiment.status === 'incomplete')) {
    return <PhaseComparison experiment={experiment} />
  }
  const events = experiment?.events ?? []
  const lane = (side: Side, title: string) => (
    <section className={`lane lane-${side}`} aria-label={`${title} 运行轨道`}>
      <header>
        <span>{side === 'plain' ? '01' : '02'}</span><h2>{title}</h2>
        <em>{experiment?.[side].status ?? (side === 'harness' ? 'waiting' : 'idle')}</em>
      </header>
      <EventTimeline
        events={events.filter((event) => event.side === side)}
        waiting={side === 'harness' && (!experiment || experiment.harness.status === 'waiting')}
      />
    </section>
  )
  return <section className="comparison live-comparison"><div className="lanes">{lane('plain', 'PLAIN')}{lane('harness', 'HARNESS')}</div></section>
}
