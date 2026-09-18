import { businessBackground } from '../explorer'
import type { TaskBrief } from '../types'

export function BusinessBrief({ task }: { task: TaskBrief | null }) {
  return (
    <section className="business-brief" aria-label="演示业务场景">
      <div className="business-summary"><span className="business-icon" aria-hidden="true">↳</span><p><small>贯穿六个实验的业务场景</small><strong>{task?.title ?? '运费规则升级'}</strong><span>{businessBackground.summary}</span></p></div>
      <details className="business-details"><summary>查看业务背景 <span aria-hidden="true">＋</span></summary><div><p>{businessBackground.description}</p><ul>{businessBackground.constraints.map((item) => <li key={item}>{item}</li>)}</ul></div></details>
    </section>
  )
}
