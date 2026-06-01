<template>
  <span
    class="inline-flex items-center justify-center font-mono font-bold border rounded px-2 py-0.5 text-xs"
    :class="gradeClass"
  >{{ grade }}</span>
</template>

<script setup>
const props = defineProps({ grade: String, size: { type: String, default: 'sm' } })
const gradeClass = computed(() => {
  const map = { A: 'grade-bg-a grade-a', B: 'grade-bg-b grade-b', C: 'grade-bg-c grade-c', D: 'grade-bg-d grade-d', F: 'grade-bg-f grade-f' }
  const g = (props.grade || 'F').charAt(0).toUpperCase()
  return map[g] || map.F
})
</script>
