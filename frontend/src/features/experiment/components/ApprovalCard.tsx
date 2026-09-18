import { useState } from 'react'
import { submitApproval } from '../api/experimentApi'

export function ApprovalCard({ approvalId, action, scope }: { approvalId: string; action: string; scope: string }) {
  const [decision, setDecision] = useState<'approved' | 'rejected' | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const decide = async (approved: boolean) => {
    setBusy(true)
    setError(null)
    try {
      await submitApproval(approvalId, approved)
      setDecision(approved ? 'approved' : 'rejected')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : '提交审批失败。')
    } finally {
      setBusy(false)
    }
  }
  if (decision) return <p className="approval-decision">审批{decision === 'approved' ? '已批准' : '已拒绝'}。</p>
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
