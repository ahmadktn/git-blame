<template>
  <div class="flex items-center gap-2">
    <component :is="icon" :size="12" :class="iconClass" />
    <span class="font-mono text-[11px] text-[var(--color-text-muted)]">{{ label }}</span>
    <span v-if="detail" class="font-mono text-[11px] text-[var(--color-brand-green)] ml-auto">{{ detail }}</span>
  </div>
</template>

<script setup>
import { CheckCircle, XCircle, AlertCircle } from '@lucide/vue'
const props = defineProps({ label: String, active: Boolean, warn: Boolean, detail: String })
const icon = computed(() => {
  if (props.active && props.warn) return AlertCircle
  if (props.active) return CheckCircle
  return XCircle
})
const iconClass = computed(() => {
  if (props.active && props.warn) return 'text-[var(--color-brand-yellow)]'
  if (props.active) return 'text-[var(--color-brand-green)]'
  return 'text-[var(--color-text-dim)]'
})
</script>
