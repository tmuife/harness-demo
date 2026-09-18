import { describe, expect, it } from 'vitest'
import { experimentReducer, initialState } from './experimentReducer'
import type { ExperimentEvent } from './types'

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
    const ready = { ...initialState, status: 'ready' as const }
    const selected = experimentReducer(ready, { type: 'select', capabilityId: 'understand' })
    expect(experimentReducer(selected, { type: 'select', capabilityId: 'act' }).selectedCapabilityId).toBe('act')
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
