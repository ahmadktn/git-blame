<template>
  <div class="grid grid-cols-[auto_1fr_auto_auto_auto] gap-4 items-center px-4 py-3 border-b border-[var(--color-border)] hover:bg-[var(--color-surface-2)] transition-colors group">
    <!-- Status -->
    <span class="font-mono text-[10px] font-bold px-2 py-0.5 rounded border" :class="statusClass">
      {{ statusLabel }}
    </span>

    <!-- Message -->
    <div class="min-w-0">
      <p class="font-mono text-sm text-[var(--color-text-primary)] truncate">{{ commit.commit.message.split('\n')[0] }}</p>
      <p class="font-mono text-[11px] text-[var(--color-text-dim)] mt-0.5">hash: {{ commit.commit.sha.slice(0, 7) }}</p>
    </div>

    <!-- Author -->
    <div class="flex items-center gap-2 min-w-0 w-36">
      <div class="w-6 h-6 rounded bg-[var(--color-surface-4)] border border-[var(--color-border)] flex items-center justify-center shrink-0">
        <User :size="12" class="text-[var(--color-text-muted)]" />
      </div>
      <span class="font-mono text-xs text-[var(--color-text-muted)] truncate">{{ commit.commit.author.name }}</span>
    </div>

    <!-- Score -->
    <span class="font-mono text-sm font-bold w-12 text-right" :class="scoreColor">{{ Math.round(commit.composite.final_score) }}</span>

    <!-- Action -->
    <button
      class="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded border border-[var(--color-border)] hover:border-[var(--color-brand-green)] text-[var(--color-text-dim)] hover:text-[var(--color-brand-green)]"
      @click="$emit('detail', commit)"
    >
      <BarChart2 :size="13" />
    </button>
  </div>
</template>

<script setup>
import { User, BarChart2 } from '@lucide/vue'
defineEmits(['detail'])
const props = defineProps({ commit: Object })

const statusLabel = computed(() => {
  const s = props.commit.composite.final_score
  if (s >= 70) return 'PASSED'
  if (s >= 40) return 'WARN'
  return 'FAILED'
})

const statusClass = computed(() => {
  const s = props.commit.composite.final_score
  if (s >= 70) return 'status-passed'
  if (s >= 40) return 'status-warn'
  return 'status-failed'
})

const scoreColor = computed(() => {
  const s = props.commit.composite.final_score
  if (s >= 80) return 'text-[#4ade80]'
  if (s >= 60) return 'text-[#86efac]'
  if (s >= 40) return 'text-[#eab308]'
  if (s >= 20) return 'text-[#f97316]'
  return 'text-[#ef4444]'
})
</script>
