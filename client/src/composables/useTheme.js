import { ref, watchEffect } from 'vue'

// Load saved theme from localStorage, default to 'light'
const savedTheme = localStorage.getItem('app-theme') || 'light'
const currentTheme = ref(savedTheme)

watchEffect(() => {
  document.documentElement.setAttribute('data-theme', currentTheme.value)
  localStorage.setItem('app-theme', currentTheme.value)
})

export function useTheme() {
  const toggleTheme = () => {
    currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light'
  }

  const setTheme = (theme) => {
    currentTheme.value = theme
  }

  return {
    currentTheme,
    toggleTheme,
    setTheme
  }
}
