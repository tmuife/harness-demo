import { useRef, useState, type MouseEvent } from 'react'
import { DemoTaskDialog } from './DemoTaskDialog'
import type { Capability, TaskBrief } from '../types'

interface CapabilityPanelProps {
  capabilities: Capability[]
  selectedId: string | null
  disabled: boolean
  onSelect: (capabilityId: string) => void
  task: TaskBrief | null
}

export function CapabilityPanel({ capabilities, selectedId, disabled, onSelect, task }: CapabilityPanelProps) {
  const [taskCapability, setTaskCapability] = useState<Capability | null>(null)
  const triggerRef = useRef<HTMLButtonElement | null>(null)
  const closeTask = () => {
    setTaskCapability(null)
    requestAnimationFrame(() => triggerRef.current?.focus())
  }
  const showTask = (capability: Capability, event: MouseEvent<HTMLButtonElement>) => {
    triggerRef.current = event.currentTarget
    setTaskCapability(capability)
  }
  return (
    <>
      <aside className="capability-panel" aria-label="Harness 能力选择">
      <div className="eyebrow">HARNESS COMPONENTS</div>
      <h2>选择一个变量</h2>
      <p className="panel-copy">PLAIN 始终保持固定基线。每次运行只启用一项主要能力。</p>
      <div className="capability-list">
        {capabilities.map((capability) => {
          const selected = selectedId === capability.id
          const planned = capability.status === 'planned'
          return (
            <article className={`capability ${selected ? 'is-selected' : ''} ${planned ? 'is-planned' : ''}`} key={capability.id}>
              <label>
                <input
                  type="checkbox"
                  checked={selected}
                  disabled={disabled || planned}
                  onChange={() => onSelect(capability.id)}
                />
                <span className="capability-title">{capability.title}</span>
                <span className={`availability ${planned ? 'planned' : 'available'}`}>
                  {planned ? '设计中' : '可运行'}
                </span>
              </label>
              <p>{capability.description}</p>
              <small>证据：{capability.evidence}</small>
              <p className="component-summary">主要：{(capability.primaryComponents ?? []).map((item) => item.title).join('、') || '暂无说明'}</p>
              <button type="button" className="task-detail-button" onClick={(event) => showTask(capability, event)}>查看任务</button>
            </article>
          )
        })}
      </div>
      </aside>
      {taskCapability ? <DemoTaskDialog capability={taskCapability} task={task} onClose={closeTask} /> : null}
    </>
  )
}
