<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm" @click.self="$emit('close')">
      <div class="w-full max-w-2xl bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded-lg overflow-hidden animate-slide-up">
        <!-- Header -->
        <div class="flex items-start justify-between p-5 border-b border-[var(--color-border)]">
          <div>
            <p class="font-mono text-[11px] text-[var(--color-text-dim)] mb-1">{{ commit.commit.sha.slice(0, 7) }} · {{ fmtDate(commit.commit.timestamp) }}</p>
            <h3 class="font-mono text-sm text-[var(--color-text-primary)] leading-snug max-w-lg">{{ commit.commit.message.split('\n')[0] }}</h3>
          </div>
          <div class="flex items-center gap-3 ml-4">
            <ScoreRing :score="commit.composite.final_score" :size="72" :stroke-width="6" />
            <button @click="$emit('close')" class="text-[var(--color-text-dim)] hover:text-[var(--color-text-primary)] transition-colors">
              <X :size="18" />
            </button>
          </div>
        </div>

        <div class="p-5 space-y-5 max-h-[70vh] overflow-y-auto">
          <!-- Grade + Tags -->
          <div class="flex items-center gap-2">
            <GradeTag :grade="commit.composite.grade" />
            <span v-if="commit.rule_score.conventional.is_conventional" class="font-mono text-[10px] px-2 py-0.5 rounded border border-[var(--color-brand-green)]/30 text-[var(--color-brand-green)] bg-[var(--color-brand-green)]/10">
              {{ commit.rule_score.conventional.type?.toUpperCase() }}
            </span>
            <span v-if="commit.rule_score.conventional.is_breaking_change" class="font-mono text-[10px] px-2 py-0.5 rounded border border-red-500/30 text-red-400 bg-red-500/10">BREAKING</span>
            <span v-if="commit.nlp_features.is_non_english" class="font-mono text-[10px] px-2 py-0.5 rounded border border-yellow-500/30 text-yellow-400 bg-yellow-500/10">NON-ENGLISH</span>
          </div>

          <!-- Score breakdown -->
          <div class="grid grid-cols-2 gap-3">
            <div class="bg-[var(--color-surface-2)] rounded p-3 border border-[var(--color-border)]">
              <p class="font-mono text-[10px] text-[var(--color-text-dim)] mb-2 tracking-wider">RULE SCORE</p>
              <p class="font-mono text-2xl font-bold text-[var(--color-brand-green)]">{{ Math.round(commit.composite.rule_score) }}</p>
              <div class="mt-3 space-y-1.5">
                <ScoreBar v-for="(val, key) in commit.rule_score.breakdown" :key="key" :label="ruleLabel(key)" :value="val * 100" />
              </div>
            </div>
            <div class="bg-[var(--color-surface-2)] rounded p-3 border border-[var(--color-border)]">
              <p class="font-mono text-[10px] text-[var(--color-text-dim)] mb-2 tracking-wider">LLM SCORE</p>
              <p class="font-mono text-2xl font-bold" :class="commit.llm_score.skipped ? 'text-[var(--color-text-dim)]' : 'text-[var(--color-brand-green)]'">
                {{ commit.llm_score.skipped ? '--' : Math.round(commit.composite.llm_score) }}
              </p>
              <div v-if="!commit.llm_score.skipped" class="mt-3 space-y-1.5">
                <ScoreBar v-for="(val, key) in commit.llm_score.criteria" :key="key" :label="key" :value="val * 5" />
              </div>
              <p v-else class="font-mono text-[11px] text-[var(--color-text-dim)] mt-2">Skipped (too short)</p>
            </div>
          </div>

          <!-- LLM Notes -->
          <div v-if="commit.llm_score.notes" class="bg-[var(--color-surface-2)] rounded p-3 border border-[var(--color-border)]">
            <p class="font-mono text-[10px] text-[var(--color-text-dim)] mb-2 tracking-wider flex items-center gap-1.5">
              <Bot :size="11" /> GPT-4o CRITIQUE
            </p>
            <p class="text-sm text-[var(--color-text-muted)] italic leading-relaxed">"{{ commit.llm_score.notes }}"</p>
          </div>

          <!-- NLP Features -->
          <div class="bg-[var(--color-surface-2)] rounded p-3 border border-[var(--color-border)]">
            <p class="font-mono text-[10px] text-[var(--color-text-dim)] mb-3 tracking-wider">NLP FEATURES</p>
            <div class="grid grid-cols-2 gap-2">
              <NlpBadge label="Imperative Verb" :active="commit.nlp_features.has_imperative_verb" :detail="commit.nlp_features.detected_verb" />
              <NlpBadge label="Code Artifact" :active="commit.nlp_features.has_code_artifact" />
              <NlpBadge label="Past Tense" :active="commit.nlp_features.verb_is_past_tense" :warn="true" />
              <NlpBadge label="Language" :active="true" :detail="commit.nlp_features.language || 'en'" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { X, Bot } from '@lucide/vue'
defineEmits(['close'])
defineProps({ commit: Object })

function fmtDate(d) { return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }
function ruleLabel(k) { return k.replace(/_/g,' ').replace(/\b\w/g, c => c.toUpperCase()) }
</script>
