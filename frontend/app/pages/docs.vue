<template>
  <div class="max-w-5xl mx-auto px-6 py-12">
    <h1 class="font-mono text-2xl font-bold text-[var(--color-text-primary)] mb-2">Documentation</h1>
    <p class="text-[var(--color-text-muted)] mb-10">Everything you need to understand how Audit.git scores your commits.</p>

    <div class="grid grid-cols-[220px_1fr] gap-8">
      <!-- Sidebar nav -->
      <nav class="space-y-1 sticky top-20 self-start">
        <a v-for="s in sections" :key="s.id" :href="`#${s.id}`"
          class="block font-mono text-xs px-3 py-1.5 rounded text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface-2)] transition-colors">
          {{ s.label }}
        </a>
      </nav>

      <!-- Content -->
      <div class="space-y-12">
        <section id="overview">
          <h2 class="font-mono text-base font-bold text-[var(--color-text-primary)] mb-4 pb-2 border-b border-[var(--color-border)]">Overview</h2>
          <p class="text-[var(--color-text-muted)] text-sm leading-relaxed mb-4">
            Audit.git uses a three-stage pipeline to evaluate every commit message: a deterministic rule engine, NLP feature extraction, and GPT-4o semantic analysis. The results are combined into a weighted composite score from 0 to 100.
          </p>
          <div class="bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded p-4 font-mono text-xs text-[var(--color-text-muted)]">
            <p class="text-[var(--color-brand-green)] mb-1">// Composite score formula</p>
            <p>final_score = (rule_score * 0.4) + (llm_score * 0.6)</p>
          </div>
        </section>

        <section id="api">
          <h2 class="font-mono text-base font-bold text-[var(--color-text-primary)] mb-4 pb-2 border-b border-[var(--color-border)]">API Reference</h2>
          <div class="space-y-4">
            <ApiEndpoint v-for="ep in endpoints" :key="ep.path" v-bind="ep" />
          </div>
        </section>

        <section id="grades">
          <h2 class="font-mono text-base font-bold text-[var(--color-text-primary)] mb-4 pb-2 border-b border-[var(--color-border)]">Grade Scale</h2>
          <div class="grid grid-cols-5 gap-3">
            <div v-for="g in grades" :key="g.grade" class="p-4 border border-[var(--color-border)] rounded text-center bg-[var(--color-surface-1)]">
              <GradeTag :grade="g.grade" class="mb-2" />
              <p class="font-mono text-xs text-[var(--color-text-dim)] mt-2">{{ g.range }}</p>
              <p class="text-[11px] text-[var(--color-text-muted)] mt-1">{{ g.label }}</p>
            </div>
          </div>
        </section>

        <section id="rules">
          <h2 class="font-mono text-base font-bold text-[var(--color-text-primary)] mb-4 pb-2 border-b border-[var(--color-border)]">Rule Engine</h2>
          <div class="space-y-3">
            <div v-for="rule in rules" :key="rule.name" class="flex items-start gap-4 p-4 bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded">
              <span class="font-mono text-xs px-2 py-0.5 bg-[var(--color-surface-3)] border border-[var(--color-border)] rounded text-[var(--color-brand-green)] shrink-0">{{ rule.weight }}</span>
              <div>
                <p class="font-mono text-xs font-bold text-[var(--color-text-primary)]">{{ rule.name }}</p>
                <p class="text-[var(--color-text-muted)] text-xs mt-0.5">{{ rule.desc }}</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
const sections = [
  { id: 'overview', label: 'Overview' },
  { id: 'api', label: 'API Reference' },
  { id: 'grades', label: 'Grade Scale' },
  { id: 'rules', label: 'Rule Engine' },
]

const endpoints = [
  { method: 'POST', path: '/analyze', desc: 'Start analysis job for a public repo URL. Returns a job object immediately.', body: '{ "repo_url": "https://github.com/user/repo", "max_commits": 100 }' },
  { method: 'GET', path: '/analyze/{job_id}', desc: 'Poll job status. Status: pending | running | complete | failed.' },
  { method: 'GET', path: '/analyze/{job_id}/commits', desc: 'Fetch scored commits with pagination. Query: skip, limit.' },
  { method: 'GET', path: '/analyze/{job_id}/export', desc: 'Export results as CSV.' },
]

const grades = [
  { grade: 'A', range: '80-100', label: 'Elite' },
  { grade: 'B', range: '60-79', label: 'Solid' },
  { grade: 'C', range: '40-59', label: 'Average' },
  { grade: 'D', range: '20-39', label: 'Weak' },
  { grade: 'F', range: '0-19', label: 'Chaos' },
]

const rules = [
  { name: 'Length', weight: '25pts', desc: 'Subject line between 10 and 72 characters.' },
  { name: 'Casing', weight: '15pts', desc: 'Sentence case or Conventional Commits type prefix.' },
  { name: 'No Trailing Period', weight: '10pts', desc: 'Subject line must not end with a period.' },
  { name: 'Imperative Verb', weight: '25pts', desc: 'Message starts with an imperative verb (Add, Fix, Refactor, etc.).' },
  { name: 'No Generic Words', weight: '15pts', desc: 'No "fix", "update", "wip", "stuff" without context.' },
  { name: 'Body Present', weight: '5pts', desc: 'Multi-line commit with explanatory body.' },
  { name: 'Line Length', weight: '5pts', desc: 'Body lines wrapped at 72 characters.' },
]
</script>
