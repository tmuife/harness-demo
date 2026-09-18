import { capabilityForComponent, componentForCapability } from './explorer'
import type { Capability, ExperimentEvent, ExperimentResult, TaskBrief } from './types'

export type ScreenStatus = 'loading' | 'ready' | 'starting' | 'running' | 'completed' | 'incomplete' | 'error' | 'recovery-failed'

export interface ExperimentState {
  status: ScreenStatus
  view: 'explore' | 'experiment'
  capabilities: Capability[]
  task: TaskBrief | null
  selectedComponentId: string | null
  selectedCapabilityId: string | null
  experiment: ExperimentResult | null
  error: string | null
  reconnecting: boolean
}

export const initialState: ExperimentState = {
  status: 'loading', view: 'explore', capabilities: [], task: null,
  selectedComponentId: null, selectedCapabilityId: null, experiment: null,
  error: null, reconnecting: false,
}

type Action =
  | { type: 'loading' }
  | { type: 'catalog-loaded'; capabilities: Capability[]; task: TaskBrief }
  | { type: 'catalog-failed'; error: string }
  | { type: 'select'; capabilityId: string }
  | { type: 'select-component'; componentId: string }
  | { type: 'view'; view: 'explore' | 'experiment' }
  | { type: 'starting' }
  | { type: 'experiment-loaded'; experiment: ExperimentResult }
  | { type: 'event'; event: ExperimentEvent }
  | { type: 'reconnecting' }
  | { type: 'sync-error'; error: string }
  | { type: 'error'; error: string }
  | { type: 'recovery-failed' }

export function isRunning(status: ScreenStatus) {
  return status === 'starting' || status === 'running'
}

function mergeEvents(events: ExperimentEvent[]): ExperimentEvent[] {
  return [...new Map(events.map((event) => [event.id, event])).values()].sort((left, right) => left.sequence - right.sequence)
}

export function experimentReducer(state: ExperimentState, action: Action): ExperimentState {
  switch (action.type) {
    case 'loading':
      return { ...state, status: 'loading', error: null }
    case 'catalog-loaded':
      return { ...state, capabilities: action.capabilities, task: action.task, status: 'ready', error: null }
    case 'catalog-failed':
      return { ...state, status: 'error', error: action.error }
    case 'select':
      if (isRunning(state.status) || state.status === 'loading') return state
      if (!state.capabilities.some((item) => item.id === action.capabilityId && item.status === 'available')) return state
      return { ...state, selectedCapabilityId: action.capabilityId, error: null }
    case 'select-component':
      if (isRunning(state.status) || state.status === 'loading') return state
      return {
        ...state, selectedComponentId: action.componentId, error: null,
        selectedCapabilityId: capabilityForComponent(state.capabilities, action.componentId, state.selectedCapabilityId),
      }
    case 'view':
      if (isRunning(state.status) || (action.view === 'experiment' && !state.experiment)) return state
      return { ...state, view: action.view }
    case 'starting':
      return { ...state, status: 'starting', view: 'experiment', experiment: null, error: null, reconnecting: false }
    case 'experiment-loaded': {
      const sameExperiment = state.experiment?.experimentId === action.experiment.experimentId
      // A late running snapshot must not overwrite a completed result.
      if (sameExperiment && !isRunning(state.experiment!.status) && isRunning(action.experiment.status)) return state
      const capability = state.capabilities.find((item) => item.id === action.experiment.capabilityId)
      return {
        ...state,
        experiment: { ...action.experiment, events: mergeEvents([...(sameExperiment ? state.experiment!.events : []), ...action.experiment.events]) },
        selectedCapabilityId: sameExperiment ? state.selectedCapabilityId : action.experiment.capabilityId,
        selectedComponentId: sameExperiment ? state.selectedComponentId : componentForCapability(capability),
        view: sameExperiment ? state.view : 'experiment',
        status: action.experiment.status === 'completed' ? 'completed' : action.experiment.status === 'incomplete' ? 'incomplete' : 'running',
        error: null, reconnecting: false,
      }
    }
    case 'event':
      if (!state.experiment || state.experiment.experimentId !== action.event.experimentId || !isRunning(state.status)) return state
      return { ...state, experiment: { ...state.experiment, events: mergeEvents([...state.experiment.events, action.event]) }, reconnecting: false }
    case 'reconnecting':
      return isRunning(state.status) ? { ...state, reconnecting: true } : state
    case 'sync-error':
      return { ...state, error: action.error, reconnecting: true }
    case 'error':
      return { ...state, status: 'error', view: 'explore', error: action.error, reconnecting: false }
    case 'recovery-failed':
      return { ...state, experiment: null, status: 'recovery-failed', view: 'explore', reconnecting: false, error: null }
  }
}
