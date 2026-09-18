import { componentRelation, relatedCapabilities, taskPreview, teachingComponents } from '../explorer'
import type { Capability } from '../types'

interface ExplorerPanelProps {
  capabilities: Capability[]
  componentId: string | null
  capability: Capability | undefined
  disabled: boolean
  onSelect: (id: string) => void
  onDetails: (capability: Capability) => void
  onStart: () => void
}

export function ExplorerPanel({ capabilities, componentId, capability, disabled, onSelect, onDetails, onStart }: ExplorerPanelProps) {
  const component = teachingComponents.find((item) => item.id === componentId)
  const related = componentId ? relatedCapabilities(capabilities, componentId) : []
  const preview = capability ? taskPreview(capability) : null

  return (
    <aside className="explorer-panel" aria-labelledby="explorer-panel-title">
      <div className="panel-heading"><span className="eyebrow">02 / TRY A CAPABILITY</span><span className="panel-index">{component ? String(teachingComponents.indexOf(component) + 1).padStart(2, '0') : '—'}</span></div>
      {component ? <>
        <span className="component-english">{component.english}</span>
        <h2 id="explorer-panel-title" tabIndex={-1}>{component.title}</h2>
        <p className="component-description">{component.description}</p>
      </> : <div className="explorer-welcome">
        <div className="welcome-symbol" aria-hidden="true"><span>＋</span><i /></div>
        <h2 id="explorer-panel-title">从一个组件开始。</h2>
        <p>点选架构中的组件，看看它解决什么问题，再通过真实对照观察它的作用。</p>
        <ol><li><span>01</span>理解组件的职责</li><li><span>02</span>预览模型要完成的任务</li><li><span>03</span>比较 PLAIN 与 HARNESS</li></ol>
      </div>}

      {component && related.length === 0 ? <div className="no-demo"><strong>暂无独立演示</strong><p>当前六个实验未直接覆盖此组件，可以继续探索其他组件。</p></div> : null}
      {related.length > 0 ? <fieldset className="demo-options" disabled={disabled}>
        <legend>关联实验 <span>{related.length.toString().padStart(2, '0')}</span></legend>
        {related.map((item) => (
          <div className="demo-option" key={item.id}>
            <label className={capability?.id === item.id ? 'is-selected' : ''}>
              <input type="radio" name="explorer-demo" value={item.id} checked={capability?.id === item.id} disabled={item.status === 'planned'} onChange={() => onSelect(item.id)} />
              <span>{item.title}<small>{componentRelation(item, componentId!) === 'primary' ? '主要关联' : '支撑关联'} · {item.status === 'available' ? '可运行' : '设计中'}</small></span>
            </label>
            {item.status === 'planned' ? <button type="button" className="text-button planned-details" onClick={() => onDetails(item)}>查看任务</button> : null}
          </div>
        ))}
      </fieldset> : null}

      {capability && preview ? <section className="task-preview" aria-labelledby="preview-title">
        <div className="preview-heading"><span className="eyebrow">THE TASK</span><span>DEMO {String(preview.detail.number || '—').padStart(2, '0')}</span></div>
        <h3 id="preview-title">{preview.objective}</h3>
        <dl className="preview-conditions"><div><dt>PLAIN</dt><dd>{preview.detail.plainCondition}</dd></div><div><dt>HARNESS</dt><dd>{preview.detail.harnessCondition}</dd></div></dl>
        <div className="preview-evidence"><h4>观察重点</h4><ul>{preview.detail.expectedEvidence.map((item) => <li key={item}>{item}</li>)}</ul></div>
        <button type="button" className="text-button" onClick={() => onDetails(capability)}>查看完整任务 <span aria-hidden="true">↗</span></button>
      </section> : null}
      <div className="explorer-launch"><button type="button" className="run-button" disabled={!capability || capability.status !== 'available' || disabled} onClick={onStart}>开始对照 <span aria-hidden="true">→</span></button><p>同一任务 · PLAIN → HARNESS · 一次一个主要变量</p></div>
    </aside>
  )
}
