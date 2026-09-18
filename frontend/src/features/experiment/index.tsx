import { useEffect, useReducer, useRef } from 'react'
import { createExperiment, getExperiment, loadCatalog, subscribeToExperiment } from './api/experimentApi'
import { CapabilityPanel } from './components/CapabilityPanel'
import { CompleteRecord } from './components/CompleteRecord'
import { ComparisonLanes } from './components/ComparisonLanes'
import { ComponentMap } from './components/ComponentMap'
import { ResultSummary } from './components/ResultSummary'
import { TaskBrief } from './components/TaskBrief'
import { experimentReducer, initialState } from './experimentReducer'
import './styles.css'

const STORAGE_KEY = 'harness-lab:last-experiment'

export function HarnessLab() {
  const [state, dispatch] = useReducer(experimentReducer, initialState)
  const sourceRef = useRef<EventSource | null>(null)

  const attachStream = (experimentId: string) => {
    sourceRef.current?.close()
    sourceRef.current = subscribeToExperiment(
      experimentId,
      (event) => {
        dispatch({ type: 'event', event })
        if (event.stage === 'result' || event.stage === 'error') {
          void getExperiment(experimentId).then((experiment) => dispatch({ type: 'experiment-loaded', experiment }))
        }
      },
      () => dispatch({ type: 'reconnecting' }),
    )
  }

  useEffect(() => {
    void loadCatalog()
      .then(([capabilities, task]) => {
        dispatch({ type: 'catalog-loaded', capabilities, task })
        const savedId = sessionStorage.getItem(STORAGE_KEY)
        if (!savedId) return
        return getExperiment(savedId)
          .then((experiment) => {
            dispatch({ type: 'experiment-loaded', experiment })
            if (experiment.status === 'starting' || experiment.status === 'running') attachStream(savedId)
          })
          .catch(() => {
            sessionStorage.removeItem(STORAGE_KEY)
            dispatch({ type: 'recovery-failed' })
          })
      })
      .catch((error: unknown) => dispatch({ type: 'catalog-failed', error: messageFrom(error) }))
    return () => sourceRef.current?.close()
  }, [])

  const start = async () => {
    if (!state.selectedCapabilityId) return
    dispatch({ type: 'starting' })
    try {
      const created = await createExperiment(state.selectedCapabilityId)
      sessionStorage.setItem(STORAGE_KEY, created.experimentId)
      const experiment = await getExperiment(created.experimentId)
      dispatch({ type: 'experiment-loaded', experiment })
      attachStream(created.experimentId)
    } catch (error) {
      dispatch({ type: 'error', error: messageFrom(error) })
    }
  }

  const loading = state.status === 'loading'
  const running = state.status === 'starting' || state.status === 'running'
  return (
    <main className="lab-shell">
      <header className="masthead"><span className="signal" aria-hidden="true" /><span>HARNESS LAB</span><small>LIVE COMPARISON CONSOLE</small></header>
      <div className="lab-grid">
        <CapabilityPanel capabilities={state.capabilities} selectedId={state.selectedCapabilityId} disabled={running || loading} task={state.task} onSelect={(capabilityId) => dispatch({ type: 'select', capabilityId })} />
        <div className="workbench">
          {loading && <section className="loading-state">正在加载实验配置…</section>}
          {state.task && <TaskBrief task={state.task} />}
          {state.status === 'recovery-failed' && <p className="notice">最近实验已过期；请开始新的对照。</p>}
          {state.error && <div className="error-state" role="alert">{state.error}</div>}
          <div className="runbar">
            <div><span className="eyebrow">EXPERIMENT STATUS</span><strong>{running ? '正在顺序运行：PLAIN → HARNESS' : state.selectedCapabilityId ? `已选择 ${state.selectedCapabilityId}` : '选择一个可运行能力'}</strong></div>
            <button type="button" className="run-button" onClick={() => void start()} disabled={!state.selectedCapabilityId || loading || running}>{running ? '运行中' : '开始对照'}</button>
          </div>
          <ResultSummary experiment={state.experiment} />
          <ComparisonLanes experiment={state.experiment} />
          {state.reconnecting && <p className="notice">事件连接中断，正在尝试恢复…</p>}
          <CompleteRecord events={state.experiment?.events ?? []} />
          <ComponentMap capabilities={state.capabilities} />
        </div>
      </div>
    </main>
  )
}

function messageFrom(error: unknown): string {
  return error instanceof Error ? error.message : '发生未知错误。'
}
