<template>
  <div class="flex min-h-[calc(100vh-56px)]">
    <!-- Sidebar -->
    <aside class="w-48 shrink-0 border-r border-[var(--color-border)] bg-[var(--color-surface-1)] flex flex-col pt-6">
      <div class="px-5 mb-6">
        <p class="font-mono text-sm font-bold text-[var(--color-brand-green)] leading-tight">{{ repoName || 'No repo' }}</p>
        <p class="font-mono text-[11px] text-[var(--color-text-dim)] mt-0.5">V0.4.2-alpha</p>
      </div>

      <nav class="flex-1 px-3 space-y-0.5">
        <button
          v-for="item in sideNav" :key="item.key"
          @click="activeSection = item.key"
          class="w-full flex items-center gap-2.5 px-3 py-2 rounded font-mono text-xs transition-colors"
          :class="activeSection === item.key ? 'bg-[var(--color-surface-3)] text-[var(--color-brand-green)] border border-[var(--color-brand-green)]/20' : 'text-[var(--color-text-muted)] hover:bg-[var(--color-surface-2)] hover:text-[var(--color-text-primary)]'"
        >
          <component :is="item.icon" :size="14" />
          {{ item.label }}
        </button>
      </nav>

      <div class="p-3 border-t border-[var(--color-border)]">
        <button @click="$router.push('/')" class="w-full flex items-center gap-2 px-3 py-2 font-mono text-xs text-[var(--color-brand-green)] border border-[var(--color-brand-green)]/30 rounded hover:bg-[var(--color-brand-green)]/10 transition-colors">
          <Plus :size="13" /> New Audit
        </button>
      </div>
    </aside>

    <!-- Main -->
    <main class="flex-1 overflow-hidden">
      <!-- Loading / Error / No job -->
      <div v-if="!jobId" class="flex flex-col items-center justify-center h-full gap-4">
        <GitCommit :size="40" class="text-[var(--color-text-dim)]" />
        <p class="font-mono text-sm text-[var(--color-text-muted)]">No analysis running. Enter a repo on the homepage.</p>
        <NuxtLink to="/" class="font-mono text-xs text-[var(--color-brand-green)] hover:underline">Go back</NuxtLink>
      </div>

      <div v-else-if="jobStatus === 'pending' || jobStatus === 'running'" class="flex flex-col items-center justify-center h-full gap-5">
        <div class="relative w-20 h-20">
          <div class="absolute inset-0 border-2 border-[var(--color-brand-green)]/20 rounded-full"></div>
          <div class="absolute inset-0 border-2 border-transparent border-t-[var(--color-brand-green)] rounded-full animate-spin"></div>
          <div class="absolute inset-3 border border-[var(--color-brand-green)]/30 rounded-full animate-spin-slow"></div>
        </div>
        <div class="text-center">
          <p class="font-mono text-sm text-[var(--color-text-primary)] mb-1">Analyzing repository...</p>
          <p class="font-mono text-xs text-[var(--color-text-dim)]">{{ jobProgress }}% complete</p>
        </div>
        <div class="w-48 h-1 bg-[var(--color-surface-3)] rounded-full overflow-hidden">
          <div class="h-full bg-[var(--color-brand-green)] rounded-full transition-all duration-500" :style="{ width: jobProgress + '%' }"></div>
        </div>
      </div>

      <div v-else-if="jobStatus === 'failed'" class="flex flex-col items-center justify-center h-full gap-4">
        <AlertTriangle :size="40" class="text-red-400" />
        <p class="font-mono text-sm text-red-400">Analysis failed.</p>
        <NuxtLink to="/" class="font-mono text-xs text-[var(--color-brand-green)] hover:underline">Try again</NuxtLink>
      </div>

      <!-- Complete -->
      <div v-else-if="jobStatus === 'complete'" class="h-full overflow-y-auto">
        <!-- Header bar -->
        <div class="sticky top-0 z-10 bg-[var(--color-surface-1)]/95 backdrop-blur-sm border-b border-[var(--color-border)] px-6 py-4">
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="font-mono text-[10px] px-2 py-0.5 bg-[var(--color-brand-green)]/15 text-[var(--color-brand-green)] border border-[var(--color-brand-green)]/30 rounded">ACTIVE AUDIT</span>
                <span class="font-mono text-[11px] text-[var(--color-text-dim)]">Last indexed: just now</span>
              </div>
              <h1 class="font-mono text-xl font-bold text-[var(--color-text-primary)]">The {{ repoShortName }} Integrity Report</h1>
              <div class="flex items-center gap-6 mt-2">
                <StatPill label="AUDITED COMMITS" :value="commits.length.toLocaleString()" />
                <StatPill label="CONTRIBUTORS" :value="contributorCount.toString()" />
                <StatPill label="PASS RATE" :value="passRate + '%'" />
              </div>
            </div>
            <div class="flex items-center gap-3">
              <button class="flex items-center gap-2 px-3 py-2 font-mono text-xs border border-[var(--color-border)] rounded text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] hover:border-[var(--color-text-muted)] transition-colors">
                <Download :size="12" /> EXPORT REPORT
              </button>
              <button @click="retrigger" class="flex items-center gap-2 px-3 py-2 font-mono text-xs border border-[var(--color-border)] rounded text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors">
                <RefreshCw :size="12" /> TRIGGER RE-SCAN
              </button>
              <!-- Global score -->
              <ScoreRing :score="globalScore" :size="88" :stroke-width="7" />
            </div>
          </div>
        </div>

        <div class="p-6 space-y-6">
          <div class="grid grid-cols-[1fr_300px] gap-6">
            <!-- Score analysis -->
            <div class="bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded-lg p-5">
              <h2 class="font-mono text-sm font-bold text-[var(--color-text-primary)] mb-4">Score Analysis</h2>
              <div class="space-y-4">
                <div class="bg-[var(--color-surface-2)] border border-[var(--color-border)] rounded p-4">
                  <div class="flex items-center justify-between mb-2">
                    <span class="font-mono text-[10px] tracking-wider text-yellow-400">DETERMINISTIC RULES</span>
                    <span class="font-mono text-sm font-bold text-[var(--color-text-primary)]">{{ avgRuleScore }}%</span>
                  </div>
                  <div class="h-2 bg-[var(--color-surface-4)] rounded-full overflow-hidden mb-3">
                    <div class="h-full bg-[var(--color-brand-green)] rounded-full" :style="{ width: avgRuleScore + '%' }"></div>
                  </div>
                  <div class="flex items-center gap-4">
                    <span class="flex items-center gap-1 font-mono text-[11px] text-[var(--color-brand-green)]"><CheckCircle :size="11" /> Length OK</span>
                    <span class="flex items-center gap-1 font-mono text-[11px] text-[var(--color-brand-green)]"><CheckCircle :size="11" /> Casing Correct</span>
                    <span class="flex items-center gap-1 font-mono text-[11px] text-yellow-400"><AlertCircle :size="11" /> No Trailing Dot</span>
                  </div>
                </div>
                <div class="bg-[var(--color-surface-2)] border border-[var(--color-border)] rounded p-4">
                  <div class="flex items-center justify-between mb-2">
                    <span class="font-mono text-[10px] tracking-wider text-[var(--color-brand-green)]">SEMANTIC ANALYSIS</span>
                    <span class="font-mono text-sm font-bold text-[var(--color-text-primary)]">{{ avgLlmScore }}%</span>
                  </div>
                  <div class="h-2 bg-[var(--color-surface-4)] rounded-full overflow-hidden mb-3">
                    <div class="h-full bg-yellow-500 rounded-full" :style="{ width: avgLlmScore + '%' }"></div>
                  </div>
                  <div class="flex items-center gap-4">
                    <span class="flex items-center gap-1 font-mono text-[11px] text-red-400"><XCircle :size="11" /> Intent Vagueness</span>
                    <span class="flex items-center gap-1 font-mono text-[11px] text-[var(--color-brand-green)]"><CheckCircle :size="11" /> Technical Clarity</span>
                    <span class="flex items-center gap-1 font-mono text-[11px] text-yellow-400"><AlertCircle :size="11" /> Verb Conjugation</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quality trend placeholder -->
            <div class="bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded-lg p-5">
              <div class="flex items-center justify-between mb-4">
                <h2 class="font-mono text-sm font-bold text-[var(--color-text-primary)]">Quality Trend</h2>
                <div class="flex gap-1">
                  <button class="font-mono text-[10px] px-2 py-1 bg-[var(--color-surface-3)] border border-[var(--color-brand-green)]/30 text-[var(--color-brand-green)] rounded">30D</button>
                  <button class="font-mono text-[10px] px-2 py-1 text-[var(--color-text-dim)] hover:text-[var(--color-text-muted)] rounded">90D</button>
                </div>
              </div>
              <!-- Simple bar chart -->
              <div class="flex items-end gap-1 h-28">
                <div
                  v-for="(bar, i) in trendBars" :key="i"
                  class="flex-1 rounded-t transition-all duration-700"
                  :style="{ height: bar + '%', background: `rgba(74,222,128,${0.3 + bar/200})` }"
                ></div>
              </div>
              <div class="flex justify-between mt-2">
                <span class="font-mono text-[10px] text-[var(--color-text-dim)]">Start</span>
                <span class="font-mono text-[10px] text-[var(--color-text-dim)]">Recent</span>
              </div>
            </div>
          </div>

          <!-- Commits table -->
          <div class="bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded-lg overflow-hidden">
            <div class="flex items-center justify-between px-5 py-4 border-b border-[var(--color-border)]">
              <h2 class="font-mono text-sm font-bold text-[var(--color-text-primary)]">Recent Commits Audit</h2>
              <div class="flex items-center gap-2">
                <button class="p-1.5 rounded border border-[var(--color-border)] text-[var(--color-text-dim)] hover:text-[var(--color-text-primary)] hover:border-[var(--color-text-muted)] transition-colors">
                  <Filter :size="13" />
                </button>
                <button class="p-1.5 rounded border border-[var(--color-border)] text-[var(--color-text-dim)] hover:text-[var(--color-text-primary)] hover:border-[var(--color-text-muted)] transition-colors">
                  <SlidersHorizontal :size="13" />
                </button>
              </div>
            </div>
            <!-- Column headers -->
            <div class="grid grid-cols-[auto_1fr_auto_auto_auto] gap-4 px-4 py-2 border-b border-[var(--color-border)] bg-[var(--color-surface-2)]">
              <span class="font-mono text-[10px] text-[var(--color-text-dim)] tracking-wider w-16">STATUS</span>
              <span class="font-mono text-[10px] text-[var(--color-text-dim)] tracking-wider">COMMIT MESSAGE</span>
              <span class="font-mono text-[10px] text-[var(--color-text-dim)] tracking-wider w-36">AUTHOR</span>
              <span class="font-mono text-[10px] text-[var(--color-text-dim)] tracking-wider w-12 text-right">SCORE</span>
              <span class="font-mono text-[10px] text-[var(--color-text-dim)] tracking-wider w-8">ACTION</span>
            </div>
            <CommitRow
              v-for="c in displayCommits" :key="c.commit.sha"
              :commit="c"
              @detail="selectedCommit = c"
            />
            <div v-if="commits.length > displayCommits.length" class="py-4 text-center border-t border-[var(--color-border)]">
              <button @click="loadMore" class="font-mono text-xs text-[var(--color-brand-green)] hover:underline">
                View {{ commits.length - displayCommits.length }} more commits
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Commit detail modal -->
    <CommitDetailModal v-if="selectedCommit" :commit="selectedCommit" @close="selectedCommit = null" />
  </div>
</template>

<script setup>
import { LayoutDashboard, Trophy, Star, Settings, Plus, GitCommit, AlertTriangle, Download, RefreshCw, CheckCircle, XCircle, AlertCircle, Filter, SlidersHorizontal } from '@lucide/vue'

const route = useRoute()
const { getCommits, pollUntilComplete, startAnalysis } = useApi()

const jobId = ref(route.query.job || '')
const repoUrl = ref(route.query.repo ? decodeURIComponent(route.query.repo) : '')
const jobStatus = ref(jobId.value ? 'running' : '')
const jobProgress = ref(0)
const commits = ref([])
const displayCount = ref(10)
const selectedCommit = ref(null)
const activeSection = ref('overview')

const sideNav = [
  { key: 'overview', label: 'Overview', icon: LayoutDashboard },
  { key: 'leaderboard', label: 'Leaderboard', icon: Trophy },
  { key: 'fame', label: 'Hall of Fame', icon: Star },
  { key: 'settings', label: 'Settings', icon: Settings },
]

const repoName = computed(() => {
  try { return new URL(repoUrl.value).pathname.slice(1) } catch { return repoUrl.value }
})
const repoShortName = computed(() => repoName.value.split('/').pop() || 'Repo')

const displayCommits = computed(() => commits.value.slice(0, displayCount.value))
const globalScore = computed(() => {
  if (!commits.value.length) return 0
  return commits.value.reduce((s, c) => s + c.composite.final_score, 0) / commits.value.length
})
const avgRuleScore = computed(() => {
  if (!commits.value.length) return 0
  return Math.round(commits.value.reduce((s, c) => s + c.composite.rule_score, 0) / commits.value.length)
})
const avgLlmScore = computed(() => {
  if (!commits.value.length) return 0
  return Math.round(commits.value.reduce((s, c) => s + c.composite.llm_score, 0) / commits.value.length)
})
const contributorCount = computed(() => new Set(commits.value.map(c => c.commit.author.email)).size)
const passRate = computed(() => {
  if (!commits.value.length) return 0
  return Math.round(commits.value.filter(c => c.composite.final_score >= 70).length / commits.value.length * 100)
})
const trendBars = computed(() => {
  if (commits.value.length < 2) return Array(12).fill(50)
  const chunk = Math.ceil(commits.value.length / 12)
  const bars = []
  for (let i = 0; i < 12; i++) {
    const slice = commits.value.slice(i * chunk, (i + 1) * chunk)
    if (!slice.length) { bars.push(40); continue }
    bars.push(slice.reduce((s, c) => s + c.composite.final_score, 0) / slice.length)
  }
  return bars
})

function loadMore() { displayCount.value += 20 }

async function retrigger() {
  if (!repoUrl.value) return
  jobStatus.value = 'running'
  jobProgress.value = 0
  commits.value = []
  const job = await startAnalysis(repoUrl.value)
  jobId.value = job.job_id
  await load()
}

async function load() {
  if (!jobId.value) return
  await pollUntilComplete(jobId.value, (job) => {
    jobStatus.value = job.status
    jobProgress.value = job.progress
  })
  const data = await getCommits(jobId.value, 0, 200)
  commits.value = data
}

onMounted(load)
</script>

<script>
// StatPill sub-component defined inline for simplicity
</script>
