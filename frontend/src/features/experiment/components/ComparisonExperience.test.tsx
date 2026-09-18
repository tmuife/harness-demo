import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { CompleteRecord } from './CompleteRecord'
import { EvidenceDrawer } from './EvidenceDrawer'
import { PhaseComparison } from './PhaseComparison'
import { ResultSummary } from './ResultSummary'
import type {
  EventStage,
  ExperimentEvent,
  ExperimentResult,
  FinalTestStatus,
  Outcome,
  RunSnapshot,
  Side,
} from '../types'

describe('explanatory comparison', () => {
  it('shows only Understand core phases when no other phase has events', () => {
    const experiment = result('understand', [
      event('input', 'plain', 1, 'PLAIN 输入'),
      event('result', 'plain', 2, 'PLAIN 结论'),
      event('input', 'harness', 3, 'HARNESS 输入'),
      event('result', 'harness', 4, 'HARNESS 结论'),
    ])

    render(<PhaseComparison experiment={experiment} />)

    expect(screen.getByText('获得信息')).toBeInTheDocument()
    expect(screen.getByText('形成结论')).toBeInTheDocument()
    expect(screen.queryByText('采取行动')).not.toBeInTheDocument()
    expect(screen.queryByText('执行验证')).not.toBeInTheDocument()
  })

  it('shows Prove focus phases and factual missing feedback labels', () => {
    const experiment = result('prove', [
      event('input', 'plain', 1, 'PLAIN 输入'),
      event('result', 'plain', 2, 'PLAIN 结论'),
      event('input', 'harness', 3, 'HARNESS 输入'),
      event('result', 'harness', 4, 'HARNESS 结论'),
    ], run('failed', 'failed', 1, 1, 0), run('passed', 'passed', 1, 1, 0))

    render(<PhaseComparison experiment={experiment} />)

    expect(screen.getByText('采取行动')).toBeInTheDocument()
    expect(screen.getByText('执行验证')).toBeInTheDocument()
    expect(screen.getByText('接收反馈')).toBeInTheDocument()
    expect(screen.getByText('未提供该能力')).toBeInTheDocument()
    expect(screen.getByText('无需反馈（首轮验证通过）')).toBeInTheDocument()
  })

  it('shows Control approval and Ground grounding phase focus', () => {
    render(<PhaseComparison experiment={result('control', [])} />)
    expect(screen.getByText('等待审批')).toBeInTheDocument()
    expect(screen.getByText('不需要审批')).toBeInTheDocument()

    render(<PhaseComparison experiment={result('ground', [])} />)
    expect(screen.getAllByText('取得依据').length).toBeGreaterThan(0)
    expect(screen.getAllByText('未取得当前政策依据').length).toBeGreaterThan(0)
  })

  it('puts the qualified one-run conclusion and capability metrics first', () => {
    const experiment = result('act', [], run('proposal', 'not_run'), run('passed', 'passed'))
    experiment.comparison = {
      observation: '本次运行中，PLAIN 仅建议；HARNESS 完成修改并验证。',
      qualification: '仅表示本次真实 LLM 运行观察，不是统计性 benchmark。',
      metrics: [{ label: '固定测试', plain: '未执行', harness: '验证通过' }],
    }

    render(<ResultSummary experiment={experiment} />)

    expect(screen.getByRole('heading', { name: /PLAIN 仅建议/ })).toBeInTheDocument()
    expect(screen.getByText('不是统计性 benchmark。', { exact: false })).toBeInTheDocument()
    expect(screen.getByText('仅生成代码建议')).toBeInTheDocument()
    expect(screen.getAllByText('验证通过').length).toBeGreaterThan(0)
  })

  it('expands and filters the same-page complete record', async () => {
    const user = userEvent.setup()
    const events = [event('input', 'plain', 1, '基线输入'), event('result', 'harness', 2, 'Harness 结论')]
    render(<CompleteRecord events={events} />)

    const trigger = screen.getByRole('button', { name: /查看完整记录/ })
    expect(screen.queryByRole('heading', { name: '完整结构化记录' })).not.toBeInTheDocument()
    await user.click(trigger)
    expect(screen.getByRole('heading', { name: '完整结构化记录' })).toHaveFocus()
    expect(screen.getByText('基线输入')).toBeInTheDocument()
    expect(screen.getByText('Harness 结论')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'PLAIN' }))
    expect(screen.getByText('基线输入')).toBeInTheDocument()
    expect(screen.queryByText('Harness 结论')).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /收起完整记录/ }))
    expect(trigger).toHaveFocus()
  })

  it('renders typed test evidence instead of generic JSON', async () => {
    const user = userEvent.setup()
    render(<EvidenceDrawer evidence={{
      kind: 'test', command: 'python -m pytest -q', returnCode: 1,
      passedCount: 5, failedCount: 1, failedTests: ['test_member'], output: '5 passed, 1 failed',
    }} />)

    await user.click(screen.getByText('查看证据'))
    expect(screen.getByText('固定命令')).toBeInTheDocument()
    expect(screen.getByText('test_member')).toBeInTheDocument()
    expect(screen.queryByText(/"returnCode"/)).not.toBeInTheDocument()
  })

  it('renders approval, handoff, and grounding evidence with labels', async () => {
    const user = userEvent.setup()
    render(<EvidenceDrawer evidence={{
      kind: 'grounding', sourceLabel: 'local-demo-provider', policyVersion: '2026-09', effectiveDate: '2026-09-01',
      groundingUsed: true, handoffValid: true, approvalStatus: 'approved', stopReason: 'model_completed',
    }} />)

    await user.click(screen.getByText('查看证据'))
    expect(screen.getByText('依据来源')).toBeInTheDocument()
    expect(screen.getByText('2026-09')).toBeInTheDocument()
    expect(screen.getByText('已取得')).toBeInTheDocument()
  })

  it('keeps infrastructure errors distinct from model verification failure', () => {
    render(<ResultSummary experiment={result(
      'act', [], run('infrastructure_error', 'unknown'), run('passed', 'passed'),
    )} />)

    expect(screen.getByText('实验运行异常')).toBeInTheDocument()
    expect(screen.queryByText('确定性验证未通过')).not.toBeInTheDocument()
  })

  it('keeps long output in one bounded evidence block', async () => {
    const user = userEvent.setup()
    const output = `line one\n${'x'.repeat(1_000)}\nline three`
    render(<EvidenceDrawer evidence={{ kind: 'llm', turn: 1, output }} />)

    await user.click(screen.getByText('查看证据'))
    expect(screen.getByText((_, element) => element?.tagName === 'PRE' && element.textContent === output)).toBeInTheDocument()
    expect(screen.getAllByText('完整输出')).toHaveLength(1)
  })
})

function event(stage: EventStage, side: Side, sequence: number, title: string): ExperimentEvent {
  return {
    id: `evt_${sequence}`,
    experimentId: 'exp_1',
    side,
    stage,
    status: 'completed',
    sequence,
    occurredAt: '2026-09-10T10:00:00Z',
    title,
    summary: `${title}摘要`,
    evidence: { kind: stage },
  }
}

function run(
  outcome: Outcome,
  finalTest: FinalTestStatus,
  calls = 1,
  testRuns = 0,
  feedbackRounds = 0,
): RunSnapshot {
  return {
    status: 'completed', outcome, calls, inputSources: [], modifiedFiles: [], testRuns,
    feedbackRounds, finalTest, checks: {}, workspaceUnchanged: null, scopeOk: null,
    proposalOnly: outcome === 'proposal',
  }
}

function result(
  capabilityId: string,
  events: ExperimentEvent[],
  plain = run('analysis', 'not_run'),
  harness = run('analysis', 'not_run'),
): ExperimentResult {
  return {
    experimentId: 'exp_1', capabilityId, status: 'completed', plain, harness,
    events, comparison: null,
  }
}
