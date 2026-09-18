import { useState } from 'react'
import { ApiError, submitApproval } from '../api/experimentApi'

export function ApprovalCard({ approvalId, action, scope, status = 'pending', interactive = true }: { approvalId: string; action: string; scope: string; status?: string; interactive?: boolean }) {
  const [decision, setDecision] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const decide = async (approved: boolean) => {
    setBusy(true)
    setError(null)
    try {
      await submitApproval(approvalId, approved)
      setDecision(approved ? 'approved' : 'rejected')
    } catch (reason) {
      if (reason instanceof ApiError && (reason.status === 409 || reason.status === 404)) {
        setDecision(reason.status === 409 ? 'handled' : 'expired')
      } else setError(reason instanceof Error ? reason.message : '提交审批失败。')
    } finally {
      setBusy(false)
    }
  }
  const resolved = status !== 'pending' ? status : decision
  const labels: Record<string, string> = { approved: '审批已批准。', rejected: '审批已拒绝。', timed_out: '审批等待超时，受保护动作已停止。', handled: '审批已处理，等待服务端记录同步。', expired: '审批已过期或不可用。' }
  if (resolved) return <p className="approval-decision" role="status">{labels[resolved] ?? '审批已结束。'}</p>
  if (!interactive) return <p className="approval-decision">审批请求（历史记录）</p>
  return (
    <div className="approval-card">
      <strong>等待人工审批</strong>
      <span>{action}</span>
      <small>目标范围：{scope}</small>
      <div>
        <button type="button" onClick={() => void decide(true)} disabled={busy}>批准</button>
        <button type="button" className="quiet" onClick={() => void decide(false)} disabled={busy}>拒绝</button>
      </div>
      {error ? <p role="alert" className="approval-error">{error}</p> : null}
    </div>
  )
}
