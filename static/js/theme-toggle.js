/**
 * 🌓 G-MARS GLOBAL THEME TOGGLE
 * Handles theme persistence across all dashboard and experiment pages.
 * Default: Dark Mode (Black)
 */

const THEME_STORAGE_KEY = 'gmars-theme-preference';
const LIGHT_MODE_CLASS = 'light-mode';

/**
 * Toggles the theme and saves preference to localStorage.
 */
function toggleTheme() {
    const isLight = document.body.classList.toggle(LIGHT_MODE_CLASS);
    localStorage.setItem(THEME_STORAGE_KEY, isLight ? 'light' : 'dark');
    
    // Optional: Dispatch event for other listeners
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: isLight ? 'light' : 'dark' } }));
}

/**
 * Initialize theme based on saved preference.
 * This can be called multiple times safely.
 */
function initTheme() {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    if (savedTheme === 'light') {
        document.body.classList.add(LIGHT_MODE_CLASS);
    } else {
        document.body.classList.remove(LIGHT_MODE_CLASS);
    }
}

// Initialize on script load
initTheme();
