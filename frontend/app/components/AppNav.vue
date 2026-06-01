<template>
  <nav class="sticky top-0 z-50 border-b border-[var(--color-border)] bg-[var(--color-surface-0)]/95 backdrop-blur-sm">
    <div class="max-w-7xl mx-auto px-6 h-14 flex items-center gap-8">
      <!-- Logo -->
      <NuxtLink to="/" class="flex items-center gap-2 font-mono text-sm font-bold tracking-widest text-[var(--color-text-primary)] hover:text-[var(--color-brand-green)] transition-colors">
        <GitCommit :size="16" class="text-[var(--color-brand-green)]" />
        AUDIT.GIT
      </NuxtLink>

      <!-- Nav links -->
      <div class="flex items-center gap-6 ml-4">
        <NuxtLink
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="font-mono text-xs tracking-wider text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors relative"
          active-class="!text-[var(--color-brand-green)] after:absolute after:bottom-[-18px] after:left-0 after:right-0 after:h-[2px] after:bg-[var(--color-brand-green)]"
        >
          {{ link.label }}
        </NuxtLink>
      </div>

      <div class="ml-auto flex items-center gap-3">
        <!-- Search -->
        <div v-if="showSearch" class="relative">
          <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-dim)]" />
          <input
            v-model="searchQuery"
            placeholder="Search Repo..."
            class="pl-8 pr-4 py-1.5 text-xs font-mono bg-[var(--color-surface-2)] border border-[var(--color-border)] rounded text-[var(--color-text-primary)] placeholder-[var(--color-text-dim)] focus:outline-none focus:border-[var(--color-brand-green)] w-48 transition-colors"
            @keydown.enter="handleSearch"
          />
        </div>

        <button class="flex items-center gap-2 px-3 py-1.5 text-xs font-mono font-bold border border-[var(--color-brand-green)] text-[var(--color-brand-green)] rounded hover:bg-[var(--color-brand-green)] hover:text-[var(--color-surface-0)] transition-all duration-200">
          <Github :size="13" />
          Connect GitHub
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { GitCommit, Search, Github } from 'lucide-vue-next'
const route = useRoute()
const router = useRouter()

const navLinks = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/leaderboard', label: 'Leaderboard' },
  { to: '/fame-shame', label: 'Fame/Shame' },
  { to: '/docs', label: 'Docs' },
]

const showSearch = computed(() => route.path !== '/')
const searchQuery = ref('')

function handleSearch() {
  if (searchQuery.value.trim()) {
    router.push(`/dashboard?repo=${encodeURIComponent(searchQuery.value)}`)
  }
}
</script>
