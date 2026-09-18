import { describe, expect, it } from 'vitest'
import { experimentReducer, initialState } from './experimentReducer'
import type { ExperimentEvent } from './types'
import { capabilities, experiment, task } from '../../test/experimentFixtures'

const event = (id: string, sequence: number): ExperimentEvent => ({
  id,
  experimentId: 'exp_1',
  side: 'plain',
  stage: 'llm',
  status: 'info',
  sequence,
  occurredAt: '2026-09-07T10:00:00Z',
  title: '模型调用',
  summary: '分析',
  evidence: { kind: 'llm' },
})

describe('experimentReducer', () => {
  it('replaces the selected capability', () => {
    const ready = { ...initialState, status: 'ready' as const, capabilities, task }
    const selected = experimentReducer(ready, { type: 'select', capabilityId: 'understand' })
    expect(experimentReducer(selected, { type: 'select', capabilityId: 'act' }).selectedCapabilityId).toBe('act')
  })

  it('rejects late running snapshots and foreign events after completion', () => {
    const completed = experimentReducer({ ...initialState, capabilities }, { type: 'experiment-loaded', experiment: experiment() })
    expect(experimentReducer(completed, { type: 'experiment-loaded', experiment: experiment('act', 'running') })).toBe(completed)
    expect(experimentReducer(completed, { type: 'event', event: event('late', 99) })).toBe(completed)
  })

  it('merges a delayed snapshot without dropping newer streamed evidence', () => {
    const current = { ...initialState, status: 'running' as const, experiment: { ...experiment('act', 'running'), events: [{ ...event('newer', 10), experimentId: 'exp_test' }] } }
    const next = experimentReducer(current, { type: 'experiment-loaded', experiment: experiment('act', 'running') })
    expect(next.experiment?.events[0].id).toBe('newer')
  })

  it('deduplicates and sorts streamed events', () => {
    const state = {
      ...initialState,
      status: 'running' as const,
      experiment: {
        experimentId: 'exp_1',
        capabilityId: 'understand',
        status: 'running' as const,
        plain: run('running'),
        harness: run('waiting'),
        events: [event('evt_2', 2)],
        comparison: null,
      },
    }
    const next = experimentReducer(experimentReducer(state, { type: 'event', event: event('evt_1', 1) }), { type: 'event', event: event('evt_2', 2) })
    expect(next.experiment?.events.map((item) => item.id)).toEqual(['evt_1', 'evt_2'])
  })
})

function run(status: 'waiting' | 'running') {
  return {
    status,
    outcome: null,
    calls: 0,
    inputSources: [],
    modifiedFiles: [],
    testRuns: 0,
    feedbackRounds: 0,
    finalTest: 'unknown' as const,
    checks: {},
    workspaceUnchanged: null,
    scopeOk: null,
    proposalOnly: false,
  }
}
