import { useCallback, useEffect, useReducer, useRef } from 'react'
import { ApiError, createExperiment, getExperiment, loadCatalog, subscribeToExperiment } from './api/experimentApi'
import { experimentReducer, initialState, isRunning } from './experimentReducer'

const STORAGE_KEY = 'harness-lab:last-experiment'

export function useExperiment() {
  const [state, dispatch] = useReducer(experimentReducer, initialState)
  const sourceRef = useRef<EventSource | null>(null)
  const generation = useRef(0)
  const startingRef = useRef(false)
  const syncRef = useRef<(() => Promise<void>) | null>(null)

  const connect = useCallback(async (experimentId: string, token: number) => {
    const current = () => generation.current === token
    // Serialize snapshots so result events from two sides cannot overwrite newer state.
    let queue = Promise.resolve()
    let terminal = false
    const sync = (): Promise<void> => {
      queue = queue.then(async () => {
        if (!current() || terminal) return
        try {
          const experiment = await getExperiment(experimentId)
          if (!current()) return
          dispatch({ type: 'experiment-loaded', experiment })
          terminal = !isRunning(experiment.status)
          if (terminal) {
            sourceRef.current?.close()
            sourceRef.current = null
          }
        } catch (error) {
          if (!current()) return
          if (error instanceof ApiError && error.status === 404) {
            terminal = true
            sourceRef.current?.close()
            sessionStorage.removeItem(STORAGE_KEY)
            dispatch({ type: 'recovery-failed' })
          } else {
            dispatch({ type: 'sync-error', error: `暂时无法同步实验，请重试。${messageFrom(error)}` })
          }
        }
      })
      return queue
    }
    syncRef.current = sync
    await sync()
    if (!current() || terminal) return
    sourceRef.current?.close()
    sourceRef.current = subscribeToExperiment(experimentId, (event) => {
      if (!current() || terminal || event.experimentId !== experimentId) return
      dispatch({ type: 'event', event })
      if (event.stage === 'result' || event.stage === 'error' || event.stage === 'approval') void sync()
    }, () => {
      if (!current() || terminal) return
      dispatch({ type: 'reconnecting' })
      // EOF may be a missed final event; consult the result before reconnecting forever.
      void sync()
    })
  }, [])

  const initialize = useCallback(async () => {
    const token = ++generation.current
    sourceRef.current?.close()
    dispatch({ type: 'loading' })
    try {
      const [capabilities, task] = await loadCatalog()
      if (generation.current !== token) return
      dispatch({ type: 'catalog-loaded', capabilities, task })
      const savedId = sessionStorage.getItem(STORAGE_KEY)
      if (savedId) {
        // Keep configuration locked if recovery temporarily fails; retry the same run.
        dispatch({ type: 'starting' })
        await connect(savedId, token)
      }
    } catch (error) {
      if (generation.current === token) dispatch({ type: 'catalog-failed', error: messageFrom(error) })
    }
  }, [connect])

  useEffect(() => {
    void initialize()
    return () => { generation.current += 1; sourceRef.current?.close() }
  }, [initialize])

  const start = async () => {
    const capability = state.capabilities.find((item) => item.id === state.selectedCapabilityId)
    if (!state.task || capability?.status !== 'available' || isRunning(state.status) || startingRef.current) return
    startingRef.current = true
    const token = ++generation.current
    sourceRef.current?.close()
    dispatch({ type: 'starting' })
    try {
      const created = await createExperiment(capability.id)
      if (generation.current !== token) return
      sessionStorage.setItem(STORAGE_KEY, created.experimentId)
      await connect(created.experimentId, token)
    } catch (error) {
      if (generation.current === token) dispatch({ type: 'error', error: messageFrom(error) })
    } finally {
      startingRef.current = false
    }
  }

  return { state, dispatch, start, reload: initialize, sync: () => syncRef.current?.() }
}

function messageFrom(error: unknown): string {
  return error instanceof Error ? error.message : '发生未知错误。'
}
