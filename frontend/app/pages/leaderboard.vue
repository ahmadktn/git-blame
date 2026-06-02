<template>
  <div class="max-w-7xl mx-auto px-6 py-10">
    <div class="flex items-start justify-between mb-8">
      <div>
        <h1 class="font-mono text-2xl font-bold text-[var(--color-text-primary)]">Hall of Technical Debt</h1>
        <p class="text-[var(--color-text-muted)] text-sm mt-1 max-w-lg">A rigorous ranking of contributors based on commit hygiene, test coverage, and documentation diligence. Ranked by our proprietary 'Debt/Value' index.</p>
      </div>
      <div class="flex gap-1 border border-[var(--color-border)] rounded overflow-hidden">
        <button v-for="t in timeFilters" :key="t" class="font-mono text-xs px-3 py-1.5 transition-colors" :class="timeFilter === t ? 'bg-[var(--color-brand-green)] text-[var(--color-surface-0)] font-bold' : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]'" @click="timeFilter = t">{{ t }}</button>
      </div>
    </div>

    <!-- Podium -->
    <div class="flex items-end justify-center gap-4 mb-10 pt-4">
      <!-- Rank 2 -->
      <PodiumCard :contributor="contributors[1]" rank="2" class="mt-10" />
      <!-- Rank 1 (gold - taller) -->
      <PodiumCard :contributor="contributors[0]" rank="1" :gold="true" />
      <!-- Rank 3 -->
      <PodiumCard :contributor="contributors[2]" rank="3" class="mt-14" />
    </div>

    <!-- Table -->
    <div class="bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded-lg overflow-hidden">
      <div class="grid grid-cols-[60px_1fr_1fr_100px_120px_80px] gap-4 px-5 py-3 border-b border-[var(--color-border)] bg-[var(--color-surface-2)]">
        <span v-for="h in tableHeaders" :key="h" class="font-mono text-[10px] text-[var(--color-text-dim)] tracking-wider">{{ h }}</span>
      </div>

      <div v-for="(c, i) in tableContributors" :key="c.name" class="grid grid-cols-[60px_1fr_1fr_100px_120px_80px] gap-4 px-5 py-3.5 border-b border-[var(--color-border)] hover:bg-[var(--color-surface-2)] transition-colors items-center">
        <span class="font-mono text-sm text-[var(--color-text-dim)]">{{ String(i + 4).padStart(2, '0') }}</span>
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 rounded bg-[var(--color-surface-4)] border border-[var(--color-border)] flex items-center justify-center shrink-0">
            <User :size="12" class="text-[var(--color-text-muted)]" />
          </div>
          <span class="font-mono text-sm text-[var(--color-text-primary)]">{{ c.name }}</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="flex-1 h-1.5 bg-[var(--color-surface-4)] rounded-full overflow-hidden">
            <div class="h-full rounded-full" :style="{ width: c.avgScore + '%', background: scoreBarColor(c.avgScore) }"></div>
          </div>
          <span class="font-mono text-xs font-bold" :style="{ color: scoreBarColor(c.avgScore) }">{{ c.avgScore }}</span>
        </div>
        <span class="font-mono text-sm text-[var(--color-text-muted)]">{{ c.commits.toLocaleString() }}</span>
        <GradeTag :grade="c.bestGrade" />
        <component :is="trendIcon(c.trend)" :size="14" :class="trendColor(c.trend)" />
      </div>

      <div class="px-5 py-3 flex items-center justify-between">
        <span class="font-mono text-[11px] text-[var(--color-text-dim)]">VIEWING TOP 7 OF 124 CONTRIBUTORS</span>
        <button class="font-mono text-xs text-[var(--color-brand-green)] hover:underline">Show full audit list</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { User, TrendingUp, TrendingDown, Minus } from '@lucide/vue'

const timeFilter = ref('All Time')
const timeFilters = ['All Time', 'Recent Crunch']

const contributors = [
  { name: '@sarah_dev', avgScore: 96.2, bestCommit: 'A+', badge: 'GOLD STANDARD', bio: null },
  { name: '@felix_codes', avgScore: 89.4, bio: '"The documentation king. Refactors without breaking things."' },
  { name: '@alex_stack', avgScore: 82.1, bio: '"High throughput, occasional debt. Critical for speed."' },
]

const tableContributors = [
  { name: '@dave_refactor', avgScore: 78.5, commits: 412, bestGrade: 'A', trend: 'up' },
  { name: '@emma_logic', avgScore: 62.8, commits: 891, bestGrade: 'B+', trend: 'down' },
  { name: '@j_smyth', avgScore: 55.2, commits: 233, bestGrade: 'B-', trend: 'flat' },
  { name: '@force_pusher', avgScore: 32.4, commits: 1204, bestGrade: 'D', trend: 'warn' },
]

const tableHeaders = ['RANK', 'AUTHOR', 'AVG SCORE', 'COMMITS', 'BEST GRADE', 'TREND']

function scoreBarColor(s) {
  if (s >= 80) return '#4ade80'
  if (s >= 60) return '#eab308'
  if (s >= 40) return '#f97316'
  return '#ef4444'
}

function trendIcon(t) {
  if (t === 'up') return TrendingUp
  if (t === 'down') return TrendingDown
  return Minus
}
function trendColor(t) {
  if (t === 'up') return 'text-[#4ade80]'
  if (t === 'down') return 'text-red-400'
  if (t === 'warn') return 'text-yellow-400'
  return 'text-[var(--color-text-dim)]'
}
</script>
