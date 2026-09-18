import { describe, expect, it } from 'vitest'
import { capabilities } from '../../test/experimentFixtures'
import { capabilityForComponent, relatedCapabilities, taskPreview, teachingComponents } from './explorer'

describe('explorer teaching adapter', () => {
  it('recommends primary demos before supporting demos and retains a related selection', () => {
    expect(relatedCapabilities(capabilities, 'context').map((item) => item.id)).toEqual(['understand', 'ground', 'continue'])
    expect(capabilityForComponent(capabilities, 'context', null)).toBe('understand')
    expect(capabilityForComponent(capabilities, 'context', 'ground')).toBe('ground')
    expect(capabilityForComponent(capabilities, 'parsing', 'ground')).toBe('act')
  })

  it('does not invent relationships or run unavailable capabilities', () => {
    const planned = capabilities.map((item) => ({ ...item, status: 'planned' as const }))
    expect(capabilityForComponent(planned, 'context', 'understand')).toBeNull()
    expect(capabilityForComponent(capabilities, 'subagents', 'act')).toBeNull()
    expect(relatedCapabilities([{ ...capabilities[0], primaryComponents: undefined, supportingComponents: undefined }], 'context')).toEqual([])
    expect(teachingComponents).toHaveLength(11)
  })

  it('uses stable ordering without demo numbers', () => {
    const missingNumbers = capabilities.map((item) => ({ ...item, demoTask: undefined }))
    expect(relatedCapabilities(missingNumbers, 'context').map((item) => item.id)).toEqual(['ground', 'understand', 'continue'])
  })

  it('keeps read-only analysis distinct from code completion', () => {
    const preview = taskPreview(capabilities[0])
    expect(preview.objective).toContain('分析')
    expect(preview.detail.completionDefinition.join(' ')).toContain('两侧只读分析')
    expect(preview.detail.completionDefinition).not.toContain('不得修改测试；任何代码完成声明均以固定 pytest 验证为准。')
    expect(preview.detail.plainCondition).toBe(capabilities[0].demoTask?.plainCondition)
  })

  it('provides honest task fallbacks without run evidence', () => {
    const preview = taskPreview({ ...capabilities[5], demoTask: undefined })
    expect(preview.detail.harnessCondition).toBe('暂无详细条件说明。')
    expect(preview.detail.completionDefinition.join(' ')).toContain('本地模拟数据')
    expect(preview.detail.expectedEvidence).toEqual([capabilities[5].evidence])
  })
})
