import { Moon, Sun } from 'lucide-react'
import { useTheme } from '../theme/useTheme.js'

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const nextTheme = theme === 'dark' ? 'light' : 'dark'
  const ThemeIcon = theme === 'dark' ? Sun : Moon

  return (
    <button
      className="icon-button theme-toggle"
      type="button"
      onClick={toggleTheme}
      aria-label={`Switch to ${nextTheme} mode`}
      title={`Switch to ${nextTheme} mode`}
    >
      <ThemeIcon size={17} aria-hidden="true" />
    </button>
  )
}

export default ThemeToggle
