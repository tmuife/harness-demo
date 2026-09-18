import { useEffect, useRef } from 'react'
import type { Capability, TaskBrief } from '../types'
import { businessBackground, taskPreview } from '../explorer'

interface DemoTaskDialogProps {
  capability: Capability
  task: TaskBrief | null
  onClose: () => void
}

export function DemoTaskDialog({ capability, task, onClose }: DemoTaskDialogProps) {
  const closeRef = useRef<HTMLButtonElement>(null)
  const dialogRef = useRef<HTMLDivElement>(null)
  const preview = taskPreview(capability)
  const detail = preview.detail

  useEffect(() => {
    const previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null
    const main = document.querySelector('main')
    const wasInert = main?.inert ?? false
    if (main) main.inert = true
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    closeRef.current?.focus()
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
      if (event.key !== 'Tab' || !dialogRef.current) return
      const controls = Array.from(dialogRef.current.querySelectorAll<HTMLElement>('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'))
      if (controls.length === 0) return
      const first = controls[0]
      const last = controls[controls.length - 1]
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      if (main) main.inert = wasInert
      document.body.style.overflow = previousOverflow
      previousFocus?.focus()
    }
  }, [onClose])

  return (
    <div className="task-dialog-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        ref={dialogRef}
        className="task-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="demo-task-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header>
          <div><span className="eyebrow">DEMO TASK · {detail?.number ?? '—'}</span><h2 id="demo-task-title">{capability.title}</h2></div>
          <button ref={closeRef} type="button" className="dialog-close" onClick={onClose} aria-label="关闭任务详情">×</button>
        </header>
        {detail ? (
          <div className="task-dialog-body">
            <p className="task-question">{detail.question}</p>
            <p><b>任务目标：</b>{preview.objective}</p>
            {task ? <p><b>共享业务任务：</b>{task.title} · {businessBackground.summary}</p> : null}
            <div className="task-conditions"><section><span>PLAIN</span><p>{detail.plainCondition}</p></section><section><span>HARNESS</span><p>{detail.harnessCondition}</p></section></div>
            <section><h3>完成定义</h3><ul>{detail.completionDefinition.map((item) => <li key={item}>{item}</li>)}</ul></section>
            <section><h3>本次观察证据</h3><ul>{detail.expectedEvidence.map((item) => <li key={item}>{item}</li>)}</ul></section>
            <p className="talk-track">讲解提示：{detail.talkTrack}</p>
          </div>
        ) : <p className="task-dialog-empty">任务详情暂不可用。</p>}
      </section>
    </div>
  )
}
