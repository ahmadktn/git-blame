<template>
  <div class="flex flex-col items-center w-56" :class="gold ? 'relative' : ''">
    <div v-if="gold" class="font-mono text-[10px] tracking-widest text-[var(--color-brand-green)] border border-[var(--color-brand-green)]/40 bg-[var(--color-brand-green)]/10 px-3 py-0.5 rounded mb-3">GOLD STANDARD</div>
    <div
      class="w-full border rounded-lg p-5 text-center transition-colors"
      :class="gold ? 'border-[var(--color-brand-green)]/50 bg-[var(--color-surface-2)]' : 'border-[var(--color-border)] bg-[var(--color-surface-1)]'"
    >
      <div class="font-mono text-[10px] text-[var(--color-text-dim)] mb-3">RANK #{{ rank }}</div>
      <!-- Avatar -->
      <div class="w-16 h-16 rounded mx-auto mb-3 border flex items-center justify-center"
        :class="gold ? 'border-[var(--color-brand-green)]/50 bg-[var(--color-surface-3)]' : 'border-[var(--color-border)] bg-[var(--color-surface-3)]'"
      >
        <User :size="24" :class="gold ? 'text-[var(--color-brand-green)]' : 'text-[var(--color-text-muted)]'" />
      </div>
      <p class="font-mono text-sm font-bold" :class="gold ? 'text-[var(--color-brand-green)]' : 'text-[var(--color-text-primary)]'">{{ contributor.name }}</p>
      <div class="flex items-center justify-between mt-3 mb-1">
        <span class="font-mono text-[10px] text-[var(--color-text-dim)]">AVG SCORE</span>
        <span class="font-mono text-sm font-bold" :class="gold ? 'text-[var(--color-brand-green)]' : 'text-[var(--color-text-primary)]'">{{ contributor.avgScore }}</span>
      </div>
      <div v-if="contributor.bestCommit" class="flex items-center justify-between">
        <span class="font-mono text-[10px] text-[var(--color-text-dim)]">BEST COMMIT</span>
        <GradeTag :grade="contributor.bestCommit" />
      </div>
      <p v-if="contributor.bio" class="font-mono text-[11px] text-[var(--color-text-dim)] mt-3 italic leading-relaxed">{{ contributor.bio }}</p>
    </div>
    <div class="mt-3 text-[var(--color-text-dim)]">
      <Medal v-if="gold" :size="20" class="text-[var(--color-brand-green)]" />
      <Star v-else :size="16" />
    </div>
  </div>
</template>

<script setup>
import { User, Medal, Star } from 'lucide-vue-next'
defineProps({ contributor: Object, rank: [String, Number], gold: Boolean })
</script>
