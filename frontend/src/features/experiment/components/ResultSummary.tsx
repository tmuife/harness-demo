import type { ExperimentResult, RunSnapshot } from '../types'

const outcomeLabel: Record<NonNullable<RunSnapshot['outcome']>, string> = {
  passed: '确定性验证通过',
  failed: '确定性验证未通过',
  analysis: '已完成分析',
  proposal: '仅生成代码建议',
  controlled_stop: '控制门禁已生效',
  handoff_error: '交接记录不可用',
  grounding_error: '当前依据未取得',
  infrastructure_error: '实验运行异常',
}

export function ResultSummary({ experiment }: { experiment: ExperimentResult | null }) {
  if (!experiment || (experiment.status !== 'completed' && experiment.status !== 'incomplete')) return null
  const comparison = experiment.comparison
  const cells: Array<['PLAIN' | 'HARNESS', RunSnapshot]> = [
    ['PLAIN', experiment.plain], ['HARNESS', experiment.harness],
  ]
  return (
    <section className="result-summary" aria-labelledby="observation-title" aria-live="polite">
      <div className="result-kicker"><span>FINAL EVIDENCE</span><small>本次运行观察</small></div>
      <h2 id="observation-title">{comparison?.observation ?? '本次实验已结束，请结合两侧证据查看结果。'}</h2>
      <p className="qualification">{comparison?.qualification ?? '仅表示本次真实 LLM 运行观察，不是统计性 benchmark。'}</p>
      <div className="outcome-grid">
        {cells.map(([label, run]) => (
          <article className={`outcome outcome-${run.outcome ?? 'pending'}`} key={label}>
            <span>{label}</span>
            <strong>{run.outcome ? outcomeLabel[run.outcome] : '暂无结论'}</strong>
            <small>{run.calls} 次模型调用 · {run.status}</small>
          </article>
        ))}
      </div>
      {comparison?.metrics.length ? (
        <div className="metric-table" role="table" aria-label="能力关键指标">
          <div role="row" className="metric-head"><span role="columnheader">观察项</span><span role="columnheader">PLAIN</span><span role="columnheader">HARNESS</span></div>
          {comparison.metrics.map((metric) => (
            <div role="row" className="metric-row" key={metric.label}>
              <strong role="rowheader">{metric.label}</strong><span role="cell">{metric.plain}</span><span role="cell">{metric.harness}</span>
            </div>
          ))}
        </div>
      ) : null}
    </section>
  )
}
