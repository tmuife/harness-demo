import { useEffect, useRef, useState } from 'react'
import { EventCard } from './EventCard'
import type { ExperimentEvent, Side } from '../types'

type Filter = 'all' | Side

export function CompleteRecord({ events }: { events: ExperimentEvent[] }) {
  const [open, setOpen] = useState(false)
  const [filter, setFilter] = useState<Filter>('all')
  const triggerRef = useRef<HTMLButtonElement>(null)
  const headingRef = useRef<HTMLHeadingElement>(null)
  const openedRef = useRef(false)

  useEffect(() => {
    if (open) {
      openedRef.current = true
      headingRef.current?.focus()
    } else if (openedRef.current) {
      triggerRef.current?.focus()
    }
  }, [open])

  if (events.length === 0) return null
  const filtered = events
    .filter((event) => filter === 'all' || event.side === filter)
    .sort((left, right) => left.sequence - right.sequence)

  return (
    <section className="record-shell">
      <button
        ref={triggerRef}
        type="button"
        className="record-trigger"
        aria-expanded={open}
        aria-controls="complete-record"
        onClick={() => setOpen((current) => !current)}
      >
        <span><small>ENGINEERING TRACE</small><strong>{open ? '收起完整记录' : '查看完整记录'}</strong></span>
        <i aria-hidden="true">{open ? '−' : '+'}</i>
      </button>
      {open ? (
        <div className="complete-record" id="complete-record">
          <div className="record-heading">
            <div><span className="eyebrow">COMPLETE RECORD</span><h2 ref={headingRef} tabIndex={-1}>完整结构化记录</h2></div>
            <p>用于排错；模型输出、Diff 和测试日志仍经过脱敏与截断。</p>
          </div>
          <div className="record-filters" aria-label="记录运行侧筛选">
            {(['all', 'plain', 'harness'] as Filter[]).map((value) => (
              <button type="button" aria-pressed={filter === value} key={value} onClick={() => setFilter(value)}>
                {value === 'all' ? '全部' : value.toUpperCase()}
              </button>
            ))}
          </div>
          <ol className="record-list" aria-label="完整运行事件">
            {filtered.map((event) => <li key={event.id}><EventCard event={event} showMeta /></li>)}
          </ol>
        </div>
      ) : null}
    </section>
  )
}
