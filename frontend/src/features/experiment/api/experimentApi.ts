import type {
  Capability,
  ExperimentCreated,
  ExperimentEvent,
  ExperimentResult,
  TaskBrief,
} from '../types'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: '服务请求失败。' }))
    throw new Error(typeof body.detail === 'string' ? body.detail : '服务请求失败。')
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export function loadCatalog(): Promise<[Capability[], TaskBrief]> {
  return Promise.all([request<Capability[]>('/capabilities'), request<TaskBrief>('/task')])
}

export function createExperiment(capabilityId: string): Promise<ExperimentCreated> {
  return request<ExperimentCreated>('/experiments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ taskId: 'shipping-policy-upgrade', capabilities: [capabilityId] }),
  })
}

export function getExperiment(experimentId: string): Promise<ExperimentResult> {
  return request<ExperimentResult>(`/experiments/${encodeURIComponent(experimentId)}/result`)
}

export function subscribeToExperiment(
  experimentId: string,
  onEvent: (event: ExperimentEvent) => void,
  onError: () => void,
): EventSource {
  const source = new EventSource(`${API_BASE}/experiments/${encodeURIComponent(experimentId)}/events`)
  source.addEventListener('experiment', (message) => {
    onEvent(JSON.parse((message as MessageEvent<string>).data) as ExperimentEvent)
  })
  source.onerror = onError
  return source
}

export async function submitApproval(approvalId: string, approved: boolean): Promise<void> {
  await request(`/approvals/${encodeURIComponent(approvalId)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approved }),
  })
}
