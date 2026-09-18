import type { TaskBrief as TaskBriefModel } from '../types'

export function TaskBrief({ task }: { task: TaskBriefModel }) {
  return (
    <section className="task-brief" aria-labelledby="task-title">
      <div>
        <div className="eyebrow">CURRENT TASK · {task.id}</div>
        <h1 id="task-title">{task.title}</h1>
        <p>{task.summary}</p>
      </div>
      <div className="task-constraint">
        <span>约束</span>
        <strong>同任务 · 同模型 · 干净工作区</strong>
      </div>
    </section>
  )
}
