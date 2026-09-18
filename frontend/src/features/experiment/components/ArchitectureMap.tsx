import { componentGroups, componentRelation, relatedCapabilities, teachingComponents } from '../explorer'
import type { Capability } from '../types'

interface ArchitectureMapProps {
  capabilities: Capability[]
  selectedComponentId: string | null
  selectedCapability: Capability | undefined
  disabled: boolean
  onSelect: (id: string) => void
}

export function ArchitectureMap({ capabilities, selectedComponentId, selectedCapability, disabled, onSelect }: ArchitectureMapProps) {
  const selectedGroup = teachingComponents.find((item) => item.id === selectedComponentId)?.groupId
  return (
    <section className="architecture-map" aria-labelledby="architecture-title">
      <header className="map-heading">
        <div><span className="eyebrow">01 / EXPLORE THE SYSTEM</span><h2 id="architecture-title">Harness 架构</h2></div>
        <span className="teaching-label">教学架构 · 11 个组件</span>
      </header>
      <div className="external-objects external-top" aria-label="架构外部输入">
        <span><i aria-hidden="true">↳</i> 用户任务 <small>TASK</small></span>
        <span><i aria-hidden="true">✳</i> 大语言模型 <small>LLM</small></span>
      </div>
      <div className="harness-frame">
        <div className="boundary-label"><span>HARNESS</span><small>让模型在工程约束中行动</small></div>
        <div className="architecture-grid">
          <svg className="architecture-wires" viewBox="0 0 1000 440" preserveAspectRatio="none" aria-hidden="true">
            <path className={selectedGroup === 'information' || selectedGroup === 'orchestration' ? 'is-active' : ''} d="M 235 92 H 500" />
            <path className={selectedGroup === 'execution' || selectedGroup === 'orchestration' ? 'is-active' : ''} d="M 500 92 H 765" />
            <path className={selectedGroup === 'continuity' || selectedGroup === 'orchestration' ? 'is-active' : ''} d="M 235 280 H 500 V 130" />
            <path className={selectedGroup === 'verification' || selectedGroup === 'orchestration' ? 'is-active' : ''} d="M 765 280 H 500" />
            <path className={selectedGroup === 'control' ? 'is-active' : ''} d="M 500 280 V 400 M 235 92 V 280 M 765 92 V 280" />
          </svg>
          {componentGroups.map((group) => (
            <section key={group.id} className={`architecture-group group-${group.id}`} aria-label={group.title}>
              <h3><span>{group.title}</span><small>{group.label}</small></h3>
              <div className="group-nodes">
                {teachingComponents.filter((item) => item.groupId === group.id).map((component) => {
                  const selected = selectedComponentId === component.id
                  const relation = selectedCapability ? componentRelation(selectedCapability, component.id) : null
                  const related = relatedCapabilities(capabilities, component.id)
                  const title = related.flatMap((item) => [...item.primaryComponents ?? [], ...item.supportingComponents ?? []]).find((item) => item.id === component.id)?.title ?? component.title
                  return (
                    <button
                      type="button"
                      key={component.id}
                      className={`architecture-node ${selected ? 'is-selected' : ''} ${relation ? `relation-${relation}` : ''} ${related.length === 0 ? 'is-uncovered' : ''}`}
                      aria-pressed={selected}
                      aria-label={title}
                      disabled={disabled}
                      onClick={() => onSelect(component.id)}
                    >
                      <span className="node-topline"><span className="node-symbol" aria-hidden="true">{component.id === 'orchestration' ? '↻' : component.id === 'safety' ? '◇' : '＋'}</span><small>{component.english}</small><span className="node-arrow" aria-hidden="true">↗</span></span>
                      <strong>{title}</strong>
                      <span className="node-caption">{selected ? '当前选择' : relation === 'primary' ? '主要组件' : relation === 'supporting' ? '支撑组件' : related.length ? `${related.length} 个关联实验` : '暂无独立演示'}</span>
                    </button>
                  )
                })}
              </div>
            </section>
          ))}
        </div>
      </div>
      <div className="external-objects external-bottom" aria-label="架构外部环境">
        <span><i aria-hidden="true">⌘</i> 工作区 / 测试环境</span>
        <span><i aria-hidden="true">≡</i> 外部依据 <small>本地模拟</small></span>
      </div>
      <footer className="map-legend"><span><i className="legend-primary" />主要组件</span><span><i className="legend-supporting" />支撑组件</span><p>选择组件，查看它如何参与实验。</p></footer>
      {selectedComponentId ? <a className="mobile-task-jump" href="#explorer-panel-title" onClick={() => document.getElementById('explorer-panel-title')?.focus()}>查看所选组件与任务 ↓</a> : null}
    </section>
  )
}
