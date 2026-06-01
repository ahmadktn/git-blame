<template>
  <div class="flex items-center gap-2">
    <span class="font-mono text-[10px] text-[var(--color-text-dim)] w-28 shrink-0 truncate">{{ label }}</span>
    <div class="flex-1 h-1 bg-[var(--color-surface-4)] rounded-full overflow-hidden">
      <div class="h-full rounded-full transition-all duration-700" :style="{ width: value + '%', background: barColor }" />
    </div>
    <span class="font-mono text-[10px] text-[var(--color-text-muted)] w-8 text-right">{{ Math.round(value) }}</span>
  </div>
</template>

<script setup>
const props = defineProps({ label: String, value: { type: Number, default: 0 } })
const barColor = computed(() => {
  if (props.value >= 70) return '#4ade80'
  if (props.value >= 40) return '#eab308'
  return '#ef4444'
})
</script>
