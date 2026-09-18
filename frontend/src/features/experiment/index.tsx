import { useCallback, useState } from 'react'
import { ArchitectureMap } from './components/ArchitectureMap'
import { BusinessBrief } from './components/BusinessBrief'
import { CompleteRecord } from './components/CompleteRecord'
import { ComparisonLanes } from './components/ComparisonLanes'
import { DemoTaskDialog } from './components/DemoTaskDialog'
import { ExplorerPanel } from './components/ExplorerPanel'
import { ResultSummary } from './components/ResultSummary'
import { isRunning } from './experimentReducer'
import { taskPreview, teachingComponents } from './explorer'
import { phaseForEvent, phaseLabels } from './phases'
import { useExperiment } from './useExperiment'
import type { Capability } from './types'
import './styles.css'
import './explorer.css'

export function HarnessLab() {
  const { state, dispatch, start, reload, sync } = useExperiment()
  const [taskCapability, setTaskCapability] = useState<Capability | null>(null)
  const closeTask = useCallback(() => setTaskCapability(null), [])
  const running = isRunning(state.status)
  const loading = state.status === 'loading'
  const selected = state.capabilities.find((item) => item.id === state.selectedCapabilityId)
  const experimentCapability = state.capabilities.find((item) => item.id === state.experiment?.capabilityId)
  const activeCapability = experimentCapability ?? selected
  const preview = activeCapability ? taskPreview(activeCapability) : null
  const experimentView = state.view === 'experiment'

  const changeView = (view: 'explore' | 'experiment') => {
    dispatch({ type: 'view', view })
    requestAnimationFrame(() => document.getElementById(view === 'explore' ? 'explorer-title' : 'workbench-title')?.focus())
  }

  return (
    <>
      <main className="lab-shell explorer-shell">
        <header className="masthead"><span className="brand-mark" aria-hidden="true">H<span>_</span></span><span>HARNESS <b>LAB</b></span><small>从架构到行动 / AN INTERACTIVE FIELD GUIDE</small><span className="masthead-edition">VOL. 01</span></header>
        <div className="explorer-container">
          {!experimentView ? <header className="explorer-hero">
            <div><span className="eyebrow">THE ENGINEERING AROUND THE MODEL</span><h1 id="explorer-title" tabIndex={-1}>从一个组件，<br /><span>看懂 Harness。</span></h1></div>
            <div className="hero-note"><span className="hero-number">11<span> / </span>06</span><p>11 个工程组件，6 个对照实验。<br />选择一个入口，观察模型如何获得信息、<br className="desktop-break" />采取行动，并让结果接受验证。</p><span className="hero-caption">EXPLORE → COMPARE → UNDERSTAND</span></div>
          </header> : <header className="workbench-heading">
            <button type="button" className="text-button" disabled={running} onClick={() => changeView('explore')}>← 返回架构总览</button>
            <h1 id="workbench-title" tabIndex={-1}>{activeCapability?.title ?? '正在恢复实验'}</h1>
            <span className="run-status" role="status">{running ? '顺序运行：PLAIN → HARNESS' : '本次实验记录'}</span>
          </header>}
          <BusinessBrief task={state.task} />
          {loading ? <div className="loading-state" role="status">正在加载实验配置…</div> : null}
          {state.status === 'recovery-failed' ? <p className="notice">最近实验已过期；请重新选择并开始对照。</p> : null}
          {state.error ? <div className="error-state" role="alert">{state.error}{!state.task ? <button type="button" className="text-button" onClick={() => void reload()}>重新加载</button> : state.reconnecting ? <button type="button" className="text-button" onClick={() => void sync()}>重试同步</button> : null}</div> : null}
          {!experimentView ? <>
            {state.experiment ? <button type="button" className="recent-experiment" onClick={() => changeView('experiment')}><span>最近实验 · {experimentCapability?.title ?? state.experiment.capabilityId}</span><span>查看本次记录 ↗</span></button> : null}
            <div className="explorer-grid">
              <ArchitectureMap capabilities={state.capabilities} selectedComponentId={state.selectedComponentId} selectedCapability={selected} disabled={loading || running || !state.task} onSelect={(componentId) => dispatch({ type: 'select-component', componentId })} />
              <ExplorerPanel capabilities={state.capabilities} componentId={state.selectedComponentId} capability={selected} disabled={loading || running || !state.task} onSelect={(capabilityId) => dispatch({ type: 'select', capabilityId })} onDetails={setTaskCapability} onStart={() => void start()} />
            </div>
          </> : <section className="explorer-workbench" aria-label="实验工作台">
            <div className="compact-architecture" aria-label="本次实验组件">
              <span className="eyebrow">HARNESS /</span>
              {teachingComponents.filter((component) => activeCapability?.primaryComponents?.some((item) => item.id === component.id)).map((component) => <span className="active-component" key={component.id}>{component.title} · 主要</span>)}
              <span className="compact-support">支撑：{activeCapability?.supportingComponents?.map((item) => item.title).join('、') || '暂无说明'}</span>
              {activeCapability ? <button type="button" className="text-button" onClick={() => setTaskCapability(activeCapability)}>查看完整任务 ↗</button> : null}
            </div>
            {preview ? <div className="experiment-task"><strong>{preview.objective}</strong><nav aria-label="观察重点定位"><span>观察重点</span>{preview.phases.map((phase) => {
              const event = state.experiment?.events.find((item) => phaseForEvent(item, activeCapability!.id) === phase)
              const target = !running ? `phase-${phase}` : event ? `event-${event.id}` : 'experiment-evidence'
              return <a key={phase} href={`#${target}`} onClick={() => document.getElementById(target)?.focus()}>{phaseLabels[phase].title} ↗</a>
            })}</nav></div> : null}
            <ResultSummary experiment={state.experiment} />
            <div id="experiment-evidence" tabIndex={-1}><ComparisonLanes experiment={state.experiment} /></div>
            {state.reconnecting ? <p className="notice" role="status">正在恢复事件连接，已收到的证据将保留。<button type="button" className="text-button" onClick={() => void sync()}>重试同步</button></p> : null}
            <CompleteRecord events={state.experiment?.events ?? []} />
          </section>}
          <footer className="explorer-footer"><span>HARNESS LAB <i>/</i> 模型之外的工程</span><span>组件关系用于教学 · 对照结论来自本次运行</span></footer>
        </div>
      </main>
      {taskCapability ? <DemoTaskDialog capability={taskCapability} task={state.task} onClose={closeTask} /> : null}
    </>
  )
}
