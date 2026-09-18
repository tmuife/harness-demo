import type { Capability, ExperimentEvent, ExperimentResult, TaskBrief } from './types'

export type ScreenStatus =
  | 'loading'
  | 'ready'
  | 'starting'
  | 'running'
  | 'completed'
  | 'incomplete'
  | 'error'
  | 'recovery-failed'

export interface ExperimentState {
  status: ScreenStatus
  capabilities: Capability[]
  task: TaskBrief | null
  selectedCapabilityId: string | null
  experiment: ExperimentResult | null
  error: string | null
  reconnecting: boolean
}

export const initialState: ExperimentState = {
  status: 'loading',
  capabilities: [],
  task: null,
  selectedCapabilityId: null,
  experiment: null,
  error: null,
  reconnecting: false,
}

type Action =
  | { type: 'catalog-loaded'; capabilities: Capability[]; task: TaskBrief }
  | { type: 'catalog-failed'; error: string }
  | { type: 'select'; capabilityId: string }
  | { type: 'starting' }
  | { type: 'experiment-loaded'; experiment: ExperimentResult }
  | { type: 'event'; event: ExperimentEvent }
  | { type: 'reconnecting' }
  | { type: 'error'; error: string }
  | { type: 'recovery-failed' }

export function experimentReducer(state: ExperimentState, action: Action): ExperimentState {
  switch (action.type) {
    case 'catalog-loaded':
      return { ...state, capabilities: action.capabilities, task: action.task, status: 'ready', error: null }
    case 'catalog-failed':
      return { ...state, status: 'error', error: action.error }
    case 'select':
      return state.status === 'ready' || state.status === 'completed' || state.status === 'incomplete'
        ? { ...state, selectedCapabilityId: action.capabilityId, error: null }
        : state
    case 'starting':
      return { ...state, status: 'starting', error: null, reconnecting: false }
    case 'experiment-loaded':
      return {
        ...state,
        experiment: action.experiment,
        selectedCapabilityId: action.experiment.capabilityId,
        status: action.experiment.status === 'completed' ? 'completed' : action.experiment.status === 'incomplete' ? 'incomplete' : 'running',
        reconnecting: false,
      }
    case 'event': {
      if (!state.experiment) return state
      const events = [...state.experiment.events, action.event]
        .filter((event, index, all) => all.findIndex((candidate) => candidate.id === event.id) === index)
        .sort((left, right) => left.sequence - right.sequence)
      return { ...state, experiment: { ...state.experiment, events }, status: 'running', reconnecting: false }
    }
    case 'reconnecting':
      return { ...state, reconnecting: true }
    case 'error':
      return { ...state, status: 'error', error: action.error }
    case 'recovery-failed':
      return { ...state, experiment: null, status: 'recovery-failed', reconnecting: false }
  }
}
