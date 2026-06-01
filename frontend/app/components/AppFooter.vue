<template>
  <footer class="border-t border-[var(--color-border)] py-6 mt-auto">
    <div class="max-w-7xl mx-auto px-6 flex items-center justify-between">
      <span class="font-mono text-xs text-[var(--color-text-dim)] tracking-wider">AUDIT.GIT</span>
      <span class="font-mono text-xs text-[var(--color-text-dim)]">© 2024 Audit.git - technically rigorous, unapologetically honest.</span>
      <div class="flex items-center gap-4">
        <a v-for="l in links" :key="l" href="#" class="font-mono text-xs text-[var(--color-text-dim)] hover:text-[var(--color-text-muted)] transition-colors">{{ l }}</a>
      </div>
    </div>
  </footer>
</template>

<script setup>
const links = ['Privacy', 'Terms', 'API', 'GitHub']
</script>
