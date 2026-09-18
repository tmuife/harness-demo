import type { Capability } from '../types'

export function ComponentMap({ capabilities }: { capabilities: Capability[] }) {
  if (capabilities.length === 0) return null
  return (
    <section className="component-map" aria-labelledby="component-map-title">
      <div className="section-heading"><div><span className="eyebrow">TRAINING MAP</span><h2 id="component-map-title">六个 Demo 如何连接 11 个组件</h2></div><p>这是教学映射，不是运行覆盖率或一一对应关系。</p></div>
      <div className="component-map-list">
        {capabilities.map((capability) => <article key={capability.id}>
          <strong>{capability.title}</strong>
          <p><span>主要</span>{(capability.primaryComponents ?? []).map((item) => item.title).join('、') || '暂无说明'}</p>
          <p><span>支撑</span>{(capability.supportingComponents ?? []).map((item) => item.title).join('、') || '暂无说明'}</p>
        </article>)}
      </div>
      <p className="component-boundary">未直接演示：子 Agent 编排。它需要独立的并行、隔离与汇总场景，不在本轮运费任务中虚构展示。</p>
    </section>
  )
}
