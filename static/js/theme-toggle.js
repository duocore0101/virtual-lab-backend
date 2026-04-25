/**
 * 🌓 G-MARS GLOBAL THEME TOGGLE & UI MODERNIZER
 * Handles theme persistence and upgrades legacy buttons to premium sliding toggles.
 */

const THEME_STORAGE_KEY = 'gmars-theme-preference';
const LIGHT_MODE_CLASS = 'light-mode';

// Inject Toggle Styles Globally
const toggleStyles = `
.theme-switch-wrapper { display: flex; align-items: center; }
.theme-switch { display: inline-block; height: 38px; position: relative; width: 76px; }
.theme-switch input { display: none; }
.slider-pill { background-color: #222; bottom: 0; cursor: pointer; left: 0; position: absolute; right: 0; top: 0; transition: .4s; border-radius: 34px; display: flex; align-items: center; justify-content: space-around; padding: 0 8px; border: 1px solid rgba(255, 255, 255, 0.15); box-shadow: inset 0 2px 4px rgba(0,0,0,0.4); }
.slider-pill .ball { background-color: #007bff; bottom: 4px; content: ""; height: 30px; left: 4px; position: absolute; transition: .4s; width: 30px; border-radius: 50%; z-index: 2; box-shadow: 0 2px 8px rgba(0, 123, 255, 0.6); display: flex; align-items: center; justify-content: center; }
.slider-pill .ball svg { width: 18px; height: 18px; color: white; }
input:checked + .slider-pill { background-color: #e0e0e0; border: 1px solid rgba(0, 0, 0, 0.1); box-shadow: inset 0 2px 4px rgba(0,0,0,0.1); }
input:checked + .slider-pill .ball { transform: translateX(38px); }
.slider-pill .icon-static { z-index: 1; width: 18px; height: 18px; transition: .3s; color: #666; }
input:checked + .slider-pill .sun-static { color: #999; }
input:not(:checked) + .slider-pill .moon-static { color: #999; }
.ball .sun-icon, .ball .moon-icon { display: none; }
input:not(:checked) + .slider-pill .ball .sun-icon { display: block; }
input:checked + .slider-pill .ball .moon-icon { display: block; }
`;

function injectStyles() {
    if (document.getElementById('gmars-toggle-styles')) return;
    const style = document.createElement('style');
    style.id = 'gmars-toggle-styles';
    style.textContent = toggleStyles;
    document.head.appendChild(style);
}

/**
 * Toggles the theme and saves preference to localStorage.
 */
function toggleTheme() {
    const isLight = document.body.classList.toggle(LIGHT_MODE_CLASS);
    localStorage.setItem(THEME_STORAGE_KEY, isLight ? 'light' : 'dark');
    
    const themeCheckboxes = document.querySelectorAll('#themeCheckbox');
    themeCheckboxes.forEach(cb => cb.checked = isLight);

    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: isLight ? 'light' : 'dark' } }));
}

/**
 * Initialize theme based on saved preference.
 */
function initTheme() {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    if (savedTheme === 'light') {
        document.body.classList.add(LIGHT_MODE_CLASS);
    } else {
        document.body.classList.remove(LIGHT_MODE_CLASS);
    }
}

/**
 * Modernizes the top-right UI by injecting sliding toggles into .top-actions.
 */
function upgradeTopActionsUI() {
    injectStyles();
    const topActions = document.querySelector('.top-actions');
    if (!topActions || topActions.getAttribute('data-modernized')) return;

    const toggleHTML = `
        <div class="theme-switch-wrapper">
            <label class="theme-switch" for="themeCheckbox">
                <input type="checkbox" id="themeCheckbox">
                <div class="slider-pill">
                    <svg class="icon-static sun-static" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
                    <svg class="icon-static moon-static" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
                    <div class="ball">
                        <svg class="sun-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
                        <svg class="moon-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
                    </div>
                </div>
            </label>
        </div>
        <div class="theme-switch-wrapper">
            <label class="theme-switch" for="fullscreenCheckbox">
                <input type="checkbox" id="fullscreenCheckbox">
                <div class="slider-pill">
                    <svg class="icon-static sun-static" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path></svg>
                    <svg class="icon-static moon-static" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3"></path></svg>
                    <div class="ball">
                        <svg class="sun-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path></svg>
                        <svg class="moon-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3"></path></svg>
                    </div>
                </div>
            </label>
        </div>
    `;

    topActions.insertAdjacentHTML('beforeend', toggleHTML);
    topActions.setAttribute('data-modernized', 'true');
    topActions.style.alignItems = 'center';
    topActions.style.gap = '20px';

    const themeCheckbox = document.getElementById('themeCheckbox');
    const fullscreenCheckbox = document.getElementById('fullscreenCheckbox');

    themeCheckbox.checked = document.body.classList.contains(LIGHT_MODE_CLASS);
    themeCheckbox.addEventListener('change', toggleTheme);

    fullscreenCheckbox.checked = !!document.fullscreenElement;
    fullscreenCheckbox.addEventListener('change', () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(() => {
                alert("Fullscreen not supported");
                fullscreenCheckbox.checked = false;
            });
        } else {
            document.exitFullscreen();
        }
    });

    document.addEventListener('fullscreenchange', () => {
        fullscreenCheckbox.checked = !!document.fullscreenElement;
    });
}

window.toggleFullscreen = function() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => alert("Fullscreen not supported"));
    } else {
        document.exitFullscreen();
    }
};

initTheme();

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', upgradeTopActionsUI);
} else {
    upgradeTopActionsUI();
}
