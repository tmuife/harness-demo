import { StrictMode } from 'react'
import { act, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { capabilities, experiment, task } from '../../test/experimentFixtures'
import { HarnessLab } from '.'
import * as api from './api/experimentApi'
import type { ExperimentEvent } from './types'

vi.mock('./api/experimentApi', async (importOriginal) => ({
  ...await importOriginal<typeof api>(),
  loadCatalog: vi.fn(), createExperiment: vi.fn(), getExperiment: vi.fn(),
  subscribeToExperiment: vi.fn(), submitApproval: vi.fn(),
}))

const close = vi.fn()
let receive: (event: ExperimentEvent) => void
let disconnect: () => void

beforeEach(() => {
  vi.resetAllMocks()
  sessionStorage.clear()
  vi.mocked(api.loadCatalog).mockResolvedValue([capabilities, task])
  vi.mocked(api.createExperiment).mockResolvedValue({ experimentId: 'exp_test', capabilityId: 'act', plainRunId: 'plain', harnessRunId: 'harness' })
  vi.mocked(api.getExperiment).mockResolvedValue(experiment())
  vi.mocked(api.submitApproval).mockResolvedValue(undefined)
  vi.mocked(api.subscribeToExperiment).mockImplementation((_, onEvent, onError) => {
    receive = onEvent
    disconnect = onError
    return { close } as unknown as EventSource
  })
})

async function choose(component: string) {
  const button = await screen.findByRole('button', { name: component })
  await waitFor(() => expect(button).toBeEnabled())
  await userEvent.click(button)
}

function approval(status = 'pending'): ExperimentEvent {
  return { id: `approval_${status}`, experimentId: 'exp_test', side: 'harness', stage: 'approval', status, sequence: status === 'pending' ? 1 : 2, occurredAt: '2026-09-16T10:00:00Z', title: '受保护写入', summary: '写入前需要人工决定', evidence: { kind: 'approval', approvalId: 'apr_test', approvalStatus: status, action: '写入运费实现', scope: 'src/shipping.py' } }
}

describe('architecture explorer', () => {
  it('browses tasks without starting a run, and keeps modal copy consistent', async () => {
    render(<HarnessLab />)
    expect(screen.getByRole('button', { name: /开始对照/ })).toBeDisabled()
    await choose('上下文管理')
    expect(screen.getByRole('radio', { name: /Understand/ })).toBeChecked()
    await userEvent.click(screen.getByRole('radio', { name: /Ground/ }))
    const objective = screen.getByRole('heading', { name: '依据当前版本配送政策更新运费逻辑，并验证规则。' })
    expect(objective).toBeInTheDocument()
    const trigger = screen.getByRole('button', { name: /查看完整任务/ })
    await userEvent.click(trigger)
    const dialog = screen.getByRole('dialog', { name: /Ground/ })
    expect(within(dialog).getByText(objective.textContent!)).toBeInTheDocument()
    expect(document.querySelector('main')?.inert).toBe(true)
    await userEvent.keyboard('{Tab}')
    expect(within(dialog).getByRole('button', { name: '关闭任务详情' })).toHaveFocus()
    await userEvent.keyboard('{Escape}')
    expect(trigger).toHaveFocus()
    expect(document.querySelector('main')?.inert).toBe(false)
    expect(api.createExperiment).not.toHaveBeenCalled()
    expect(api.subscribeToExperiment).not.toHaveBeenCalled()
  })

  it('reaches all six demos and leaves subagents informational', async () => {
    render(<HarnessLab />)
    for (const [component, demo] of [['上下文管理', 'Understand'], ['工具系统', 'Act'], ['质量验证', 'Prove'], ['安全防护', 'Control'], ['记忆系统', 'Continue']]) {
      await choose(component)
      const radio = screen.getByRole('radio', { name: new RegExp(demo) })
      await userEvent.click(radio)
      expect(radio).toBeChecked()
      expect(screen.getByRole('button', { name: /开始对照/ })).toBeEnabled()
    }
    await choose('上下文管理')
    await userEvent.click(screen.getByRole('radio', { name: /Ground/ }))
    expect(screen.getByRole('radio', { name: /Ground/ })).toBeChecked()
    await choose('子 Agent 编排')
    expect(screen.getByRole('button', { name: /开始对照/ })).toBeDisabled()
    expect(screen.queryByRole('radio')).not.toBeInTheDocument()
  })

  it('shows planned tasks without allowing them to run', async () => {
    vi.mocked(api.loadCatalog).mockResolvedValue([capabilities.map((item) => ({ ...item, status: 'planned' })), task])
    render(<HarnessLab />)
    await choose('输出解析')
    expect(screen.getByRole('radio', { name: /Act/ })).toBeDisabled()
    await userEvent.click(screen.getByRole('button', { name: '查看任务' }))
    expect(screen.getByRole('dialog', { name: /Act/ })).toBeInTheDocument()
    expect(api.createExperiment).not.toHaveBeenCalled()
  })

  it('retries a core catalogue failure', async () => {
    vi.mocked(api.loadCatalog).mockRejectedValueOnce(new Error('目录暂不可用'))
    render(<HarnessLab />)
    expect(await screen.findByRole('alert')).toHaveTextContent('目录暂不可用')
    expect(screen.getByRole('button', { name: /开始对照/ })).toBeDisabled()
    await userEvent.click(screen.getByRole('button', { name: '重新加载' }))
    await choose('工具系统')
    expect(screen.getByRole('button', { name: /开始对照/ })).toBeEnabled()
  })

  it('keeps completed Act results separate when exploring Control', async () => {
    render(<HarnessLab />)
    await choose('工具系统')
    await userEvent.click(screen.getByRole('button', { name: /开始对照/ }))
    await screen.findByRole('heading', { name: 'Act · 受限工具行动', level: 1 })
    expect(api.createExperiment).toHaveBeenCalledExactlyOnceWith('act')
    await userEvent.click(screen.getByRole('button', { name: /返回架构总览/ }))
    await choose('安全防护')
    await userEvent.click(screen.getByRole('radio', { name: /Control/ }))
    expect(screen.queryByRole('region', { name: '实验工作台' })).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /最近实验 · Act/ }))
    expect(screen.getByRole('heading', { name: 'Act · 受限工具行动', level: 1 })).toBeInTheDocument()
    expect(screen.getByText('将运费逻辑修改建议，变成受控的文件操作与验证。')).toBeInTheDocument()
  })

  it('allows correcting a selection after start failure', async () => {
    vi.mocked(api.createExperiment).mockRejectedValueOnce(new Error('启动失败'))
    render(<HarnessLab />)
    await choose('工具系统')
    await userEvent.click(screen.getByRole('button', { name: /开始对照/ }))
    expect(await screen.findByRole('alert')).toHaveTextContent('启动失败')
    await choose('上下文管理')
    expect(screen.getByRole('radio', { name: /Understand/ })).toBeChecked()
    expect(screen.getByRole('button', { name: /开始对照/ })).toBeEnabled()
  })

  it.each([
    ['批准', true, '审批已批准。'],
    ['拒绝', false, '审批已拒绝。'],
  ] as const)('recovers pending approval and submits %s while keeping configuration locked', async (button, approved, confirmation) => {
    sessionStorage.setItem('harness-lab:last-experiment', 'exp_test')
    const current = experiment('control', 'running')
    current.events = [approval()]
    vi.mocked(api.getExperiment).mockResolvedValue(current)
    render(<HarnessLab />)
    const decision = await screen.findByRole('button', { name: button })
    expect(screen.getByRole('button', { name: /返回架构总览/ })).toBeDisabled()
    expect(screen.getByRole('button', { name: /查看完整任务/ })).toBeEnabled()
    await userEvent.click(decision)
    expect(api.submitApproval).toHaveBeenCalledExactlyOnceWith('apr_test', approved)
    expect(await screen.findByText(confirmation)).toBeInTheDocument()
    expect(api.createExperiment).not.toHaveBeenCalled()
  })

  it('does not turn a past approval into a new approval after recovery', async () => {
    sessionStorage.setItem('harness-lab:last-experiment', 'exp_test')
    const current = experiment('control', 'running')
    current.events = [approval(), approval('timed_out')]
    vi.mocked(api.getExperiment).mockResolvedValue(current)
    render(<HarnessLab />)
    await screen.findByRole('heading', { name: 'Control · 边界与审批', level: 1 })
    expect(screen.queryByRole('button', { name: '批准' })).not.toBeInTheDocument()
    expect(screen.getAllByText(/审批等待超时/).length).toBeGreaterThan(0)
  })

  it('does not duplicate approval actions in the complete record and handles conflicts', async () => {
    sessionStorage.setItem('harness-lab:last-experiment', 'exp_test')
    const current = experiment('control', 'running')
    current.events = [approval()]
    vi.mocked(api.getExperiment).mockResolvedValue(current)
    vi.mocked(api.submitApproval).mockRejectedValue(new api.ApiError('审批已处理', 409))
    render(<HarnessLab />)
    await screen.findByRole('button', { name: '批准' })
    await userEvent.click(screen.getByRole('button', { name: /查看完整记录/ }))
    expect(screen.getAllByRole('button', { name: '批准' })).toHaveLength(1)
    await userEvent.click(screen.getByRole('button', { name: '拒绝' }))
    expect(await screen.findByText('审批已处理，等待服务端记录同步。')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: '批准' })).not.toBeInTheDocument()
  })

  it('keeps streaming after the baseline result and reconciles the final snapshot', async () => {
    sessionStorage.setItem('harness-lab:last-experiment', 'exp_test')
    vi.mocked(api.getExperiment).mockResolvedValue(experiment('act', 'running'))
    render(<HarnessLab />)
    await waitFor(() => expect(api.subscribeToExperiment).toHaveBeenCalledTimes(1))
    act(() => receive({ ...approval(), id: 'plain_result', side: 'plain', stage: 'result', title: '基线完成', evidence: { kind: 'result' } }))
    await waitFor(() => expect(api.getExperiment).toHaveBeenCalledTimes(2))
    expect(close).not.toHaveBeenCalled()
    vi.mocked(api.getExperiment).mockResolvedValue(experiment('act', 'completed'))
    act(() => disconnect())
    await waitFor(() => expect(screen.getByRole('button', { name: /返回架构总览/ })).toBeEnabled())
    expect(close).toHaveBeenCalled()
  })

  it('keeps a temporarily unavailable saved run locked and retries without creating another run', async () => {
    sessionStorage.setItem('harness-lab:last-experiment', 'exp_test')
    vi.mocked(api.getExperiment).mockRejectedValueOnce(new Error('连接中断'))
    render(<HarnessLab />)
    expect(await screen.findByRole('alert')).toHaveTextContent('重试')
    expect(screen.getByRole('button', { name: /返回架构总览/ })).toBeDisabled()
    await userEvent.click(screen.getAllByRole('button', { name: '重试同步' })[0])
    await waitFor(() => expect(screen.getByRole('button', { name: /返回架构总览/ })).toBeEnabled())
    expect(api.createExperiment).not.toHaveBeenCalled()
  })

  it('clears only expired saved runs and returns to a usable explorer', async () => {
    sessionStorage.setItem('harness-lab:last-experiment', 'expired')
    vi.mocked(api.getExperiment).mockRejectedValue(new api.ApiError('已过期', 404))
    render(<HarnessLab />)
    await screen.findByText(/最近实验已过期/)
    expect(sessionStorage.getItem('harness-lab:last-experiment')).toBeNull()
    await choose('质量验证')
    expect(screen.getByRole('button', { name: /开始对照/ })).toBeEnabled()
  })

  it('does not attach duplicate streams under StrictMode', async () => {
    sessionStorage.setItem('harness-lab:last-experiment', 'exp_test')
    vi.mocked(api.getExperiment).mockResolvedValue(experiment('act', 'running'))
    const view = render(<StrictMode><HarnessLab /></StrictMode>)
    await waitFor(() => expect(api.subscribeToExperiment).toHaveBeenCalledTimes(1))
    view.unmount()
    expect(close).toHaveBeenCalled()
  })
})
