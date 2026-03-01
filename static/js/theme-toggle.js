// ------------------------------
// THEME TOGGLE WITH PERSISTENCE
// ------------------------------

const THEME_KEY = "gmars-theme";

// Apply saved theme on page load
(function () {
  const savedTheme = localStorage.getItem(THEME_KEY);
  if (savedTheme === "light") {
    document.body.classList.add("light-theme");
  }
})();

// Toggle theme + save preference
function toggleTheme() {
  const isLight = document.body.classList.toggle("light-theme");

  // Save preference
  localStorage.setItem(THEME_KEY, isLight ? "light" : "dark");
}
function toggleTheme() {
  document.body.classList.toggle("light-theme");

  const mode = document.body.classList.contains("light-theme")
    ? "light"
    : "dark";

  localStorage.setItem("admin-theme", mode);
}

document.addEventListener("DOMContentLoaded", () => {
  const saved = localStorage.getItem("admin-theme");
  if (saved === "light") {
    document.body.classList.add("light-theme");
  }
});
