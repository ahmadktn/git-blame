<template>
  <div class="max-w-7xl mx-auto px-6 py-10">
    <div class="mb-8">
      <h1 class="font-mono text-2xl font-bold text-[var(--color-text-primary)]">Hall of Fame & Shame</h1>
      <p class="text-[var(--color-text-muted)] text-sm mt-1">A curated archive of clinical precision and absolute chaos. Behold the commits that defined our culture this week.</p>
    </div>

    <div class="grid grid-cols-2 gap-6">
      <!-- Left: THE ELITE -->
      <div>
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <Trophy :size="16" class="text-[var(--color-brand-green)]" />
            <span class="font-mono text-sm font-bold text-[var(--color-brand-green)]">THE ELITE</span>
          </div>
          <span class="font-mono text-[10px] px-2 py-0.5 border border-[var(--color-brand-green)]/30 text-[var(--color-brand-green)] rounded">HIGHEST PRECISION</span>
        </div>

        <div class="space-y-4">
          <CommitCard
            v-for="c in eliteCommits" :key="c.sha"
            :commit="c"
            variant="elite"
          />
        </div>
      </div>

      <!-- Right: THE OPAQUE -->
      <div>
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <AlertOctagon :size="16" class="text-red-400" />
            <span class="font-mono text-sm font-bold text-red-400">THE OPAQUE</span>
          </div>
          <span class="font-mono text-[10px] px-2 py-0.5 border border-red-500/30 text-red-400 rounded">CRITICAL TURBULENCE</span>
        </div>

        <div class="space-y-4">
          <CommitCard
            v-for="c in shameCommits" :key="c.sha"
            :commit="c"
            variant="shame"
          />
        </div>
      </div>
    </div>

    <!-- Broadcast CTA -->
    <div class="mt-12 border border-dashed border-[var(--color-border)] rounded-lg p-8 text-center">
      <h3 class="font-mono text-base font-bold text-[var(--color-text-primary)] mb-1">Ready to broadcast the findings?</h3>
      <div class="flex items-center justify-center gap-3 mt-4">
        <button class="flex items-center gap-2 px-4 py-2 bg-[#1DA1F2]/15 border border-[#1DA1F2]/30 text-[#1DA1F2] font-mono text-xs rounded hover:bg-[#1DA1F2]/25 transition-colors">
          <Share2 :size="13" /> Export to X
        </button>
        <button class="flex items-center gap-2 px-4 py-2 bg-purple-500/15 border border-purple-500/30 text-purple-400 font-mono text-xs rounded hover:bg-purple-500/25 transition-colors">
          <MessageSquare :size="13" /> Push to Slack
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Trophy, AlertOctagon, Share2, MessageSquare } from '@lucide/vue'

const eliteCommits = [
  {
    sha: 'a82f1bc', author: '@lex_dev_01', score: 98, grade: 'A+',
    message: 'Refactor: Abstract database layer to support multi-tenant horizontal scaling',
    critique: 'Exceptional atomic commit. Documentation updates perfectly mirror the architectural shift. Decoupling logic is robust and shows foresight for Tier-1 infrastructure.',
    tags: ['REFACTOR'],
  },
  {
    sha: 'f2991dd', author: '@sarah_codes', score: 94, grade: 'A',
    message: 'Fix: Resolve memory leak in WebSocket handshake timeout handler',
    critique: 'Precise identification of the heap allocation issue. The unit tests added cover the edge case explicitly. High technical rigor observed.',
    tags: ['PERFORMANCE'],
  },
]

const shameCommits = [
  {
    sha: 'de45f12', author: '@cowboy_coder', score: 12, grade: 'F',
    message: '"fix"',
    critique: 'Vague intent: \'fix\' provides no context for future maintainers. The diff includes 4,000 lines of unrelated changes. This is an auditing nightmare.',
    tags: ['CHAOS'],
  },
  {
    sha: 'ff88a22', author: '@intern_042', score: 28, grade: 'E-',
    message: 'WIP: testing stuff in production because local is broken',
    critique: 'A direct violation of security protocols. Hardcoded API keys found in plaintext. Testing in production is a cardinal sin. Repent immediately.',
    tags: ['SECURITY'],
  },
]
</script>
