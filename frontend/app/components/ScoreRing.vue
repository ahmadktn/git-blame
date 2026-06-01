<template>
  <div class="relative flex items-center justify-center" :style="{ width: size + 'px', height: size + 'px' }">
    <svg :width="size" :height="size" class="-rotate-90" viewBox="0 0 120 120">
      <!-- Track -->
      <circle cx="60" cy="60" :r="radius" fill="none" stroke="rgba(42,58,42,0.8)" :stroke-width="strokeWidth" />
      <!-- Progress -->
      <circle
        cx="60" cy="60" :r="radius" fill="none"
        :stroke="scoreColor"
        :stroke-width="strokeWidth"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        class="transition-all duration-1000"
      />
    </svg>
    <div class="absolute inset-0 flex flex-col items-center justify-center">
      <span class="font-mono font-bold leading-none" :style="{ fontSize: numSize + 'px', color: scoreColor }">{{ displayScore }}</span>
      <span class="font-mono text-[10px] text-[var(--color-text-dim)] mt-0.5">/ 100</span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  score: { type: Number, default: 0 },
  size: { type: Number, default: 160 },
  strokeWidth: { type: Number, default: 8 },
})

const radius = computed(() => (120 / 2) - (props.strokeWidth / 2) * (120 / props.size))
const circumference = computed(() => 2 * Math.PI * radius.value)
const dashOffset = computed(() => circumference.value - (props.score / 100) * circumference.value)
const numSize = computed(() => props.size * 0.28)

const scoreColor = computed(() => {
  if (props.score >= 80) return '#4ade80'
  if (props.score >= 60) return '#86efac'
  if (props.score >= 40) return '#eab308'
  if (props.score >= 20) return '#f97316'
  return '#ef4444'
})

const displayScore = computed(() => Math.round(props.score))
</script>
