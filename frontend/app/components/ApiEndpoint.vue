<template>
  <div class="bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded overflow-hidden">
    <div class="flex items-center gap-3 px-4 py-2.5 bg-[var(--color-surface-2)] border-b border-[var(--color-border)]">
      <span class="font-mono text-[10px] font-bold px-2 py-0.5 rounded" :class="methodClass">{{ method }}</span>
      <span class="font-mono text-sm text-[var(--color-text-primary)]">{{ path }}</span>
    </div>
    <div class="p-4">
      <p class="text-[var(--color-text-muted)] text-sm">{{ desc }}</p>
      <div v-if="body" class="mt-3 bg-[var(--color-surface-0)] border border-[var(--color-border)] rounded p-3">
        <p class="font-mono text-xs text-[var(--color-text-muted)]">{{ body }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({ method: String, path: String, desc: String, body: String })
const methodClass = computed(() => {
  const map = { GET: 'bg-[#4ade80]/15 text-[#4ade80]', POST: 'bg-blue-500/15 text-blue-400', DELETE: 'bg-red-500/15 text-red-400' }
  return map[props.method] || 'bg-[var(--color-surface-4)] text-[var(--color-text-muted)]'
})
</script>
