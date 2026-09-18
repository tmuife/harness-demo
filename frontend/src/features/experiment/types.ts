export type CapabilityStatus = 'available' | 'planned'
export type Side = 'plain' | 'harness'
export type RunStatus = 'waiting' | 'running' | 'completed' | 'failed'
export type Outcome =
  | 'passed' | 'failed' | 'analysis' | 'proposal' | 'controlled_stop'
  | 'handoff_error' | 'grounding_error' | 'infrastructure_error'
export type FinalTestStatus = 'passed' | 'failed' | 'not_run' | 'unknown'
export type EventStage =
  | 'input' | 'llm' | 'tool' | 'write' | 'test' | 'feedback'
  | 'approval' | 'handoff' | 'grounding' | 'result' | 'error'

export interface Capability {
  id: string
  title: string
  description: string
  evidence: string
  status: CapabilityStatus
  demoTask?: DemoTask | null
  primaryComponents?: HarnessComponent[]
  supportingComponents?: HarnessComponent[]
  coverageNote?: string | null
}

export interface HarnessComponent {
  id: string
  title: string
}

export interface DemoTask {
  number: number
  question: string
  plainCondition: string
  harnessCondition: string
  completionDefinition: string[]
  expectedEvidence: string[]
  talkTrack: string
}

export interface TaskBrief {
  id: string
  title: string
  summary: string
}

interface EvidenceFields {
  sources?: string[]
  contextCount?: number | null
  turn?: number | null
  targetTurn?: number | null
  call?: boolean
  output?: string | null
  toolName?: string | null
  path?: string | null
  characters?: number | null
  ok?: boolean | null
  command?: string | null
  returnCode?: number | null
  passed?: boolean | null
  passedCount?: number | null
  failedCount?: number | null
  failedTests?: string[]
  diff?: string | null
  modifiedFiles?: string[]
  calls?: number | null
  testRuns?: number | null
  feedbackRounds?: number | null
  finalTest?: FinalTestStatus | null
  checks?: Record<string, boolean>
  workspaceUnchanged?: boolean | null
  scopeOk?: boolean | null
  proposalOnly?: boolean | null
  error?: string | null
  approvalId?: string | null
  action?: string | null
  scope?: string | null
  inputPriority?: string[]
  schemaValid?: boolean | null
  permissionGranted?: boolean | null
  executed?: boolean | null
  maxTurns?: number | null
  stopReason?: string | null
  approvalStatus?: string | null
  protectedActionExecuted?: boolean | null
  session?: string | null
  handoffAvailable?: boolean | null
  handoffValid?: boolean | null
  handoffFields?: string[]
  sourceLabel?: string | null
  policyVersion?: string | null
  effectiveDate?: string | null
  groundingUsed?: boolean | null
  taskOutcome?: string | null
  capabilityOutcome?: string | null
  rejectedRequests?: number | null
}

export type EventEvidence = {
  [Kind in EventStage]: EvidenceFields & { kind: Kind }
}[EventStage]

export interface ExperimentEvent {
  id: string
  experimentId: string
  side: Side
  stage: EventStage
  status: string
  sequence: number
  occurredAt: string
  title: string
  summary: string
  evidence: EventEvidence
}

export interface RunSnapshot {
  status: RunStatus
  outcome: Outcome | null
  calls: number
  inputSources: string[]
  modifiedFiles: string[]
  testRuns: number
  feedbackRounds: number
  finalTest: FinalTestStatus
  checks: Record<string, boolean>
  workspaceUnchanged: boolean | null
  scopeOk: boolean | null
  proposalOnly: boolean
  maxTurns?: number | null
  stopReason?: string | null
  approvalStatus?: string | null
  protectedActionExecuted?: boolean | null
  handoffAvailable?: boolean | null
  handoffValid?: boolean | null
  policyVersion?: string | null
  effectiveDate?: string | null
  groundingUsed?: boolean | null
  taskOutcome?: string | null
  capabilityOutcome?: string | null
  rejectedRequests?: number
}

export interface ComparisonMetric {
  label: string
  plain: string
  harness: string
}

export interface ComparisonSummary {
  observation: string
  qualification: string
  metrics: ComparisonMetric[]
}

export interface ExperimentResult {
  experimentId: string
  capabilityId: string
  status: 'starting' | 'running' | 'completed' | 'incomplete'
  plain: RunSnapshot
  harness: RunSnapshot
  events: ExperimentEvent[]
  comparison: ComparisonSummary | null
}

export interface ExperimentCreated {
  experimentId: string
  capabilityId: string
  plainRunId: string
  harnessRunId: string
}
