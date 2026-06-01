<template>
  <div class="relative overflow-hidden">
    <!-- Background grid -->
    <div class="absolute inset-0 opacity-[0.03]" style="background-image: linear-gradient(var(--color-brand-green) 1px, transparent 1px), linear-gradient(90deg, var(--color-brand-green) 1px, transparent 1px); background-size: 48px 48px;"></div>

    <!-- Hero -->
    <section class="relative max-w-4xl mx-auto px-6 pt-24 pb-16 text-center">
      <!-- System badge -->
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded border border-[var(--color-brand-green)]/40 bg-[var(--color-brand-green)]/8 mb-10">
        <span class="w-1.5 h-1.5 rounded-full bg-[var(--color-brand-green)] animate-pulse"></span>
        <span class="font-mono text-[11px] text-[var(--color-brand-green)] tracking-widest">SYSTEM ONLINE: V0.4.2-ALPHA</span>
      </div>

      <h1 class="font-mono text-5xl md:text-6xl font-bold text-[var(--color-text-primary)] leading-tight mb-3">
        Technically Rigorous.
      </h1>
      <h2 class="font-mono text-5xl md:text-6xl font-bold text-[var(--color-brand-green)] leading-tight mb-8">
        Unapologetically Honest.
      </h2>

      <p class="text-[var(--color-text-muted)] text-base max-w-lg mx-auto leading-relaxed mb-12">
        Audit.git dissects your repository's history, commit hygiene, and code patterns. No fluff,
        just hard data and a slight amount of digital judgment.
      </p>

      <!-- Input -->
      <div class="max-w-xl mx-auto">
        <div class="flex gap-0 border border-[var(--color-border)] rounded-lg overflow-hidden focus-within:border-[var(--color-brand-green)] transition-colors bg-[var(--color-surface-2)]">
          <div class="flex items-center px-4 shrink-0">
            <Link2 :size="16" class="text-[var(--color-text-dim)]" />
          </div>
          <input
            v-model="repoUrl"
            placeholder="https://github.com/username/repo"
            class="flex-1 py-3.5 text-sm font-mono bg-transparent text-[var(--color-text-primary)] placeholder-[var(--color-text-dim)] focus:outline-none"
            @keydown.enter="analyze"
          />
          <button
            @click="analyze"
            :disabled="loading"
            class="flex items-center gap-2 px-5 py-3.5 bg-[var(--color-brand-green)] text-[var(--color-surface-0)] font-mono text-sm font-bold hover:bg-[var(--color-brand-green-dim)] transition-colors disabled:opacity-50"
          >
            <Loader2 v-if="loading" :size="14" class="animate-spin" />
            <Zap v-else :size="14" />
            Analyze
          </button>
        </div>
        <div class="flex items-center justify-center gap-6 mt-3">
          <span class="flex items-center gap-1.5 font-mono text-[11px] text-[var(--color-text-dim)]">
            <ShieldOff :size="11" /> No Auth Required
          </span>
          <span class="flex items-center gap-1.5 font-mono text-[11px] text-[var(--color-text-dim)]">
            <Globe :size="11" /> Public Repos Only
          </span>
        </div>
        <p v-if="error" class="mt-3 font-mono text-xs text-red-400">{{ error }}</p>
      </div>
    </section>

    <!-- Stats bar -->
    <section class="border-y border-[var(--color-border)] bg-[var(--color-surface-1)]">
      <div class="max-w-7xl mx-auto grid grid-cols-4">
        <div v-for="(stat, i) in stats" :key="i" class="px-8 py-6 border-r border-[var(--color-border)] last:border-r-0 text-center">
          <p class="font-mono text-3xl font-bold" :class="stat.color">{{ stat.value }}</p>
          <p class="font-mono text-[10px] tracking-widest text-[var(--color-text-dim)] mt-1">{{ stat.label }}</p>
        </div>
      </div>
    </section>

    <!-- Live feed -->
    <section class="max-w-7xl mx-auto px-6 py-8">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
          <span class="w-1.5 h-1.5 bg-[var(--color-brand-green)] rounded-full animate-pulse"></span>
          <span class="font-mono text-xs text-[var(--color-text-muted)] tracking-wider">Live Audit Feed</span>
        </div>
        <a href="#" class="font-mono text-xs text-[var(--color-brand-green)] hover:underline">View All Activity</a>
      </div>
      <div class="flex gap-3 overflow-x-auto pb-2">
        <div v-for="item in liveFeed" :key="item.repo" class="shrink-0 flex items-center gap-3 px-4 py-2.5 bg-[var(--color-surface-2)] border border-[var(--color-border)] rounded-lg min-w-[200px]">
          <span class="font-mono text-[10px] font-bold px-1.5 py-0.5 rounded text-[var(--color-surface-0)]" :style="{ background: langColor(item.lang) }">{{ item.lang }}</span>
          <div class="flex-1 min-w-0">
            <p class="font-mono text-xs text-[var(--color-text-primary)] truncate">{{ item.repo }}</p>
            <p class="font-mono text-[10px] text-[var(--color-text-dim)]">{{ item.ago }}</p>
          </div>
          <GradeTag :grade="item.grade" />
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section class="max-w-7xl mx-auto px-6 py-16">
      <h3 class="font-mono text-xl font-bold text-center text-[var(--color-text-primary)] mb-2">Under the Hood</h3>
      <div class="w-10 h-0.5 bg-[var(--color-brand-green)] mx-auto mb-12"></div>

      <div class="grid grid-cols-3 gap-6">
        <div v-for="step in steps" :key="step.num" class="bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded-lg p-6 hover:border-[var(--color-brand-green)]/40 transition-colors">
          <span class="font-mono text-xs font-bold" :class="step.numColor">{{ step.num }}</span>
          <component :is="step.icon" :size="32" class="text-[var(--color-surface-4)] my-3 opacity-60" />
          <h4 class="font-mono text-sm font-bold text-[var(--color-text-primary)] mb-2">{{ step.title }}</h4>
          <p class="text-[var(--color-text-muted)] text-sm leading-relaxed">{{ step.desc }}</p>
          <div class="flex gap-2 mt-4">
            <span v-for="tag in step.tags" :key="tag" class="font-mono text-[10px] px-2 py-0.5 bg-[var(--color-surface-3)] border border-[var(--color-border)] rounded text-[var(--color-text-dim)]">{{ tag }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="max-w-5xl mx-auto px-6 pb-16">
      <div class="border border-[var(--color-border)] rounded-lg p-12 text-center bg-[var(--color-surface-1)]">
        <h3 class="font-mono text-2xl font-bold text-[var(--color-text-primary)] mb-3">Ready for the Verdict?</h3>
        <p class="text-[var(--color-text-muted)] mb-8">Join thousands of developers who were brave enough to face their own repository history.</p>
        <div class="flex items-center justify-center gap-4">
          <button @click="$router.push('/dashboard')" class="flex items-center gap-2 px-6 py-3 bg-[var(--color-surface-3)] border border-[var(--color-border)] text-[var(--color-text-primary)] font-mono text-sm font-bold rounded hover:border-[var(--color-brand-green)] transition-colors">
            Audit My Repo
            <ArrowRight :size="14" />
          </button>
          <NuxtLink to="/demo" class="flex items-center gap-2 px-6 py-3 border border-[var(--color-border)] text-[var(--color-text-muted)] font-mono text-sm rounded hover:text-[var(--color-text-primary)] transition-colors">
            View Sample Audit
          </NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { Link2, Zap, ShieldOff, Globe, Loader2, Download, Shuffle, Settings, ArrowRight } from 'lucide-vue-next'

const router = useRouter()
const { startAnalysis } = useApi()

const repoUrl = ref('')
const loading = ref(false)
const error = ref('')

async function analyze() {
  if (!repoUrl.value.trim()) return
  loading.value = true
  error.value = ''
  try {
    const job = await startAnalysis(repoUrl.value.trim())
    router.push(`/dashboard?job=${job.job_id}&repo=${encodeURIComponent(repoUrl.value)}`)
  } catch (e) {
    error.value = e.message || 'Failed to start analysis'
  } finally {
    loading.value = false
  }
}

const stats = [
  { value: '12.4k', label: 'REPOS AUDITED', color: 'text-[var(--color-text-primary)]' },
  { value: '842k', label: 'COMMITS SCORED', color: 'text-[var(--color-text-primary)]' },
  { value: 'A+', label: 'HIGHEST GRADE', color: 'text-[var(--color-brand-green)]' },
  { value: 'F', label: 'LOWEST GRADE', color: 'text-red-400' },
]

const liveFeed = [
  { lang: 'JS', repo: 'facebook/react', ago: '2 MINS AGO', grade: 'B+' },
  { lang: 'TS', repo: 'microsoft/typescript', ago: '5 MINS AGO', grade: 'A' },
  { lang: 'PY', repo: 'unknown/messy-script', ago: '8 MINS AGO', grade: 'D-' },
  { lang: 'GO', repo: 'docker/cli', ago: '12 MINS AGO', grade: 'A-' },
  { lang: 'TS', repo: 'vuejs/core', ago: 'RECENT', grade: 'A' },
]

function langColor(lang) {
  const map = { JS: '#f0db4f', TS: '#3178c6', PY: '#3776ab', GO: '#00acd7', RS: '#f46623' }
  return map[lang] || '#4ade80'
}

const steps = [
  {
    num: '01', numColor: 'text-[var(--color-brand-green)]',
    icon: Download, title: 'THE FETCH',
    desc: 'We clone your public repository history using high-performance worker nodes. Every commit, every branch, and every line of diff is ingested into our temporary auditor buffer.',
    tags: ['GIT_CLONE', 'DIFF_WALK'],
  },
  {
    num: '02', numColor: 'text-yellow-400',
    icon: Shuffle, title: 'RULE ENGINE',
    desc: 'Hard-coded heuristics check for commit message hygiene, giant monolith files, nested callback hell, and sensitive data leaks. No exceptions, no mercy.',
    tags: ['AST_PARSING', 'SEMANTIC_SEARCH'],
  },
  {
    num: '03', numColor: 'text-orange-400',
    icon: Settings, title: 'LLM ANALYSIS',
    desc: 'Our specialized LLM agent reviews your "vibe." It looks for architectural consistency and writes a brutally honest (sometimes funny) summary of your engineering choices.',
    tags: ['AI_CRITIQUE', 'GPT_4_TURBO'],
  },
]
</script>
