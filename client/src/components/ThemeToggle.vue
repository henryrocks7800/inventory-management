<template>
  <button
    class="theme-toggle"
    :aria-label="currentTheme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
    @click="toggleTheme"
  >
    <svg
      v-if="currentTheme === 'light'"
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
      class="theme-icon"
    >
      <path d="M10 3V4.5M10 15.5V17M17 10H15.5M4.5 10H3M14.6 5.4L13.5 6.5M6.5 13.5L5.4 14.6M14.6 14.6L13.5 13.5M6.5 6.5L5.4 5.4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <circle cx="10" cy="10" r="3.5" stroke="currentColor" stroke-width="1.5"/>
    </svg>
    <svg
      v-else
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
      class="theme-icon"
    >
      <path d="M17 11.5A7.5 7.5 0 118.5 3a6 6 0 108.5 8.5z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
    </svg>
  </button>
</template>

<script setup>
import { useTheme } from '../composables/useTheme'

const { currentTheme, toggleTheme } = useTheme()
</script>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--color-text-secondary);
}

.theme-toggle:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-border-hover);
}

.theme-icon {
  flex-shrink: 0;
}
</style>
