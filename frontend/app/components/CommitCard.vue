<template>
  <div class="border rounded-lg overflow-hidden" :class="variant === 'elite' ? 'border-[var(--color-brand-green)]/30 bg-[var(--color-surface-1)]' : 'border-red-500/30 bg-[var(--color-surface-1)]'">
    <div class="p-4">
      <!-- Author + score -->
      <div class="flex items-start justify-between mb-3">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded border flex items-center justify-center shrink-0" :class="variant === 'elite' ? 'border-[var(--color-brand-green)]/30 bg-[var(--color-surface-3)]' : 'border-red-500/20 bg-[var(--color-surface-3)]'">
            <User :size="14" :class="variant === 'elite' ? 'text-[var(--color-brand-green)]' : 'text-red-400'" />
          </div>
          <div>
            <p class="font-mono text-xs font-bold text-[var(--color-text-primary)]">{{ commit.author }}</p>
            <p class="font-mono text-[10px] text-[var(--color-text-dim)]">#{{ commit.sha }}</p>
          </div>
        </div>
        <div class="text-right">
          <p class="font-mono text-3xl font-bold leading-none" :class="variant === 'elite' ? 'text-[var(--color-brand-green)]' : 'text-red-400'">{{ commit.score }}</p>
          <p class="font-mono text-[10px] text-[var(--color-text-dim)]">AUDIT SCORE</p>
        </div>
      </div>

      <!-- Message -->
      <p class="font-mono text-sm font-bold text-[var(--color-text-primary)] mb-3 leading-snug">{{ commit.message }}</p>

      <!-- Critique -->
      <div class="rounded p-3 border mb-3" :class="variant === 'elite' ? 'bg-[var(--color-surface-2)] border-[var(--color-brand-green)]/20' : 'bg-[var(--color-surface-2)] border-red-500/20'">
        <div class="flex items-center gap-1.5 mb-1.5">
          <component :is="variant === 'elite' ? Bot : AlertTriangle" :size="11" :class="variant === 'elite' ? 'text-[var(--color-brand-green)]' : 'text-red-400'" />
          <span class="font-mono text-[10px] font-bold" :class="variant === 'elite' ? 'text-[var(--color-brand-green)]' : 'text-red-400'">GPT-4o Critique</span>
        </div>
        <p class="text-[var(--color-text-muted)] text-xs italic leading-relaxed">"{{ commit.critique }}"</p>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <GradeTag :grade="commit.grade" />
          <span v-for="tag in commit.tags" :key="tag" class="font-mono text-[10px] px-2 py-0.5 border border-[var(--color-border)] rounded text-[var(--color-text-dim)]">{{ tag }}</span>
        </div>
        <div class="flex items-center gap-2">
          <button class="p-1.5 rounded border border-[var(--color-border)] text-[var(--color-text-dim)] hover:text-[var(--color-text-primary)] hover:border-[var(--color-text-muted)] transition-colors">
            <Share2 :size="12" />
          </button>
          <button v-if="variant === 'shame'" class="p-1.5 rounded border border-[var(--color-border)] text-[var(--color-text-dim)] hover:text-red-400 hover:border-red-400/40 transition-colors">
            <Trash2 :size="12" />
          </button>
          <button v-else class="p-1.5 rounded border border-[var(--color-border)] text-[var(--color-text-dim)] hover:text-[var(--color-brand-green)] hover:border-[var(--color-brand-green)]/40 transition-colors">
            <Download :size="12" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { User, Bot, AlertTriangle, Share2, Trash2, Download } from '@lucide/vue'
defineProps({ commit: Object, variant: { type: String, default: 'elite' } })
</script>
