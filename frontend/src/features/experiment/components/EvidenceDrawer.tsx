import { useState } from 'react'
import type { EventEvidence } from '../types'

export function EvidenceDrawer({ evidence }: { evidence: EventEvidence }) {
  const [copied, setCopied] = useState(false)
  const rows = evidenceRows(evidence)
  const blocks = [
    evidence.diff ? { label: '代码差异', value: evidence.diff } : null,
    evidence.output ? { label: '完整输出', value: evidence.output } : null,
    evidence.error ? { label: '错误摘要', value: evidence.error } : null,
  ].filter((block): block is { label: string; value: string } => block !== null)
  if (rows.length === 0 && blocks.length === 0) return null

  const copy = async () => {
    const content = [
      ...rows.map(([label, value]) => `${label}: ${value}`),
      ...blocks.map((block) => `${block.label}:\n${block.value}`),
    ].join('\n\n')
    await navigator.clipboard?.writeText(content)
    setCopied(true)
  }

  return (
    <details className="evidence">
      <summary>查看证据</summary>
      <div className="evidence-body">
        {rows.length > 0 ? (
          <dl>{rows.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
        ) : null}
        {blocks.map((block) => (
          <div className="evidence-block" key={block.label}>
            <span>{block.label}</span>
            <pre>{block.value}</pre>
          </div>
        ))}
        <button type="button" className="copy-button" onClick={() => void copy()}>
          {copied ? '已复制' : '复制证据'}
        </button>
      </div>
    </details>
  )
}

function evidenceRows(evidence: EventEvidence): Array<[string, string]> {
  const rows: Array<[string, string]> = []
  if (evidence.sources?.length) rows.push(['输入来源', evidence.sources.join('、')])
  if (evidence.turn) rows.push(['轮次', String(evidence.turn)])
  if (evidence.session) rows.push(['会话', evidence.session])
  if (evidence.inputPriority?.length) rows.push(['输入优先级', evidence.inputPriority.join(' → ')])
  if (evidence.targetTurn) rows.push(['反馈目标轮次', String(evidence.targetTurn)])
  if (evidence.toolName) rows.push(['工具', evidence.toolName])
  if (evidence.schemaValid != null) rows.push(['参数校验', evidence.schemaValid ? '通过' : '未通过'])
  if (evidence.permissionGranted != null) rows.push(['权限决定', evidence.permissionGranted ? '允许' : '拒绝'])
  if (evidence.executed != null) rows.push(['真实执行', evidence.executed ? '已执行' : '未执行'])
  if (evidence.path) rows.push(['目标文件', evidence.path])
  if (evidence.characters != null) rows.push(['写入字符', String(evidence.characters)])
  if (evidence.command) rows.push(['固定命令', evidence.command])
  if (evidence.returnCode != null) rows.push(['退出码', String(evidence.returnCode)])
  if (evidence.passedCount != null || evidence.failedCount != null) {
    rows.push(['测试摘要', `${evidence.passedCount ?? 0} 通过 · ${evidence.failedCount ?? 0} 失败`])
  }
  if (evidence.failedTests?.length) rows.push(['失败项', evidence.failedTests.join('、')])
  if (evidence.calls != null) rows.push(['模型调用', `${evidence.calls} 次`])
  if (evidence.testRuns != null) rows.push(['测试执行', `${evidence.testRuns} 次`])
  if (evidence.feedbackRounds != null) rows.push(['失败反馈', `${evidence.feedbackRounds} 次`])
  if (evidence.maxTurns != null) rows.push(['最大轮数', String(evidence.maxTurns)])
  if (evidence.stopReason) rows.push(['停止原因', evidence.stopReason])
  if (evidence.approvalStatus) rows.push(['审批状态', evidence.approvalStatus])
  if (evidence.protectedActionExecuted != null) rows.push(['受保护动作', evidence.protectedActionExecuted ? '已执行' : '未执行'])
  if (evidence.handoffAvailable != null) rows.push(['交接记录', evidence.handoffAvailable ? '已提供' : '未提供'])
  if (evidence.handoffValid != null) rows.push(['交接校验', evidence.handoffValid ? '有效' : '无效'])
  if (evidence.handoffFields?.length) rows.push(['交接字段', evidence.handoffFields.join('、')])
  if (evidence.sourceLabel) rows.push(['依据来源', evidence.sourceLabel])
  if (evidence.policyVersion) rows.push(['政策版本', evidence.policyVersion])
  if (evidence.effectiveDate) rows.push(['生效日期', evidence.effectiveDate])
  if (evidence.groundingUsed != null) rows.push(['当前依据', evidence.groundingUsed ? '已取得' : '未取得'])
  if (evidence.taskOutcome) rows.push(['任务结果', evidence.taskOutcome])
  if (evidence.capabilityOutcome) rows.push(['能力结果', evidence.capabilityOutcome])
  if (evidence.rejectedRequests != null) rows.push(['拒绝请求', `${evidence.rejectedRequests} 次`])
  if (evidence.modifiedFiles?.length) rows.push(['修改文件', evidence.modifiedFiles.join('、')])
  if (evidence.scopeOk != null) rows.push(['修改范围', evidence.scopeOk ? '符合允许范围' : '超出允许范围'])
  if (evidence.workspaceUnchanged != null) rows.push(['工作区', evidence.workspaceUnchanged ? '未修改' : '已修改'])
  Object.entries(evidence.checks ?? {}).forEach(([label, passed]) => rows.push([label, passed ? '识别' : '未识别']))
  return rows
}
