import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { CapabilityPanel } from './CapabilityPanel'
import { ComponentMap } from './ComponentMap'

const capabilities = [
  { id: 'understand', title: 'Understand · 项目上下文', description: '上下文', evidence: '输入', status: 'available' as const },
  { id: 'control', title: 'Control · 边界与审批', description: '审批', evidence: '审批', status: 'planned' as const },
]

describe('CapabilityPanel', () => {
  it('selects available capability but disables planned capability', async () => {
    const onSelect = vi.fn()
    render(<CapabilityPanel capabilities={capabilities} selectedId={null} disabled={false} task={null} onSelect={onSelect} />)
    await userEvent.click(screen.getByRole('checkbox', { name: /understand/i }))
    expect(onSelect).toHaveBeenCalledWith('understand')
    expect(screen.getByRole('checkbox', { name: /control/i })).toBeDisabled()
  })

  it('opens the selected demo task without changing the capability selection', async () => {
    const user = userEvent.setup()
    const onSelect = vi.fn()
    const detailed = [{
      id: 'control', title: 'Control · 边界与审批', description: '审批', evidence: '审批', status: 'available' as const,
      demoTask: {
        number: 4, question: '谁决定行动是否允许？', plainCondition: '无需审批', harnessCondition: '首次写入审批',
        completionDefinition: ['不改测试'], expectedEvidence: ['审批决定'], talkTrack: '先看门禁',
      },
      primaryComponents: [{ id: 'safety', title: '安全防护' }],
      supportingComponents: [{ id: 'tools', title: '工具系统' }],
      coverageNote: null,
    }]
    render(<CapabilityPanel capabilities={detailed} selectedId={null} disabled={false} task={{ id: 'shipping-policy-upgrade', title: '运费规则升级', summary: '更新运费规则' }} onSelect={onSelect} />)

    const trigger = screen.getByRole('button', { name: '查看任务' })
    await user.click(trigger)
    expect(screen.getByRole('dialog', { name: 'Control · 边界与审批' })).toBeInTheDocument()
    expect(screen.getByText('谁决定行动是否允许？')).toBeInTheDocument()
    expect(onSelect).not.toHaveBeenCalled()
    await user.keyboard('{Escape}')
    await waitFor(() => expect(trigger).toHaveFocus())
  })

  it('shows the component coverage boundary in the teaching map', () => {
    render(<ComponentMap capabilities={[{
      id: 'understand', title: 'Understand', description: '上下文', evidence: '输入', status: 'available',
      primaryComponents: [{ id: 'context', title: '上下文管理' }], supportingComponents: [], coverageNote: null,
    }]} />)

    expect(screen.getByText('六个 Demo 如何连接 11 个组件')).toBeInTheDocument()
    expect(screen.getByText(/未直接演示：子 Agent 编排/)).toBeInTheDocument()
  })
})
