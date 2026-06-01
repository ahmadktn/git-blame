<template>
  <div>
    <p class="font-mono text-[10px] text-[var(--color-text-dim)] tracking-wider">{{ label }}</p>
    <p class="font-mono text-lg font-bold text-[var(--color-text-primary)]">{{ value }}</p>
  </div>
</template>
<script setup>
defineProps({ label: String, value: String })
</script>
