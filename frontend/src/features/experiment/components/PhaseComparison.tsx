import { EventCard } from './EventCard'
import {
  eventsForPhase,
  missingPhaseLabel,
  phaseLabels,
  visiblePhases,
} from '../phases'
import type { ExperimentResult, Side } from '../types'

export function PhaseComparison({ experiment }: { experiment: ExperimentResult }) {
  const phases = visiblePhases(experiment.capabilityId, experiment.events)
  const sideCell = (phase: (typeof phases)[number], side: Side) => {
    const events = eventsForPhase(experiment.events, experiment.capabilityId, phase, side)
    if (events.length === 0) {
      const run = experiment[side]
      return (
        <p className="phase-empty">
          {missingPhaseLabel(
            phase, side, experiment.capabilityId, run.finalTest, run.feedbackRounds,
          )}
        </p>
      )
    }
    return <div className="phase-events">{events.map((event) => <EventCard event={event} key={event.id} />)}</div>
  }

  return (
    <section className="phase-comparison" aria-labelledby="phase-title">
      <div className="section-heading">
        <div><span className="eyebrow">HOW IT HAPPENED</span><h2 id="phase-title">关键过程对照</h2></div>
        <p>沿相同阶段看清 Harness 在哪里加入了上下文、行动或反馈。</p>
      </div>
      <div className="phase-head" aria-hidden="true"><span>阶段</span><span>PLAIN</span><span>HARNESS</span></div>
      {phases.map((phase) => (
        <article className="phase-row" key={phase}>
          <header>
            <span>{phaseLabels[phase].index}</span>
            <div><strong>{phaseLabels[phase].title}</strong><small>{phaseLabels[phase].question}</small></div>
          </header>
          <section aria-label={`${phaseLabels[phase].title} PLAIN`}><b>PLAIN</b>{sideCell(phase, 'plain')}</section>
          <section aria-label={`${phaseLabels[phase].title} HARNESS`}><b>HARNESS</b>{sideCell(phase, 'harness')}</section>
        </article>
      ))}
    </section>
  )
}
