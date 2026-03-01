// ---------------------------------
// SIDEBAR TOGGLE WITH PERSISTENCE
// ---------------------------------

const SIDEBAR_KEY = "gmars-sidebar";

// Apply saved sidebar state on load
(function () {
  const sidebar = document.querySelector(".sa-sidebar");
  const savedState = localStorage.getItem(SIDEBAR_KEY);

  if (savedState === "collapsed" && sidebar) {
    sidebar.classList.add("collapsed");
  }
})();

// Toggle sidebar + save preference
function toggleSidebar() {
  const sidebar = document.querySelector(".sa-sidebar");
  if (!sidebar) return;

  sidebar.classList.toggle("collapsed");

  // Save state
  const isCollapsed = sidebar.classList.contains("collapsed");
  localStorage.setItem(SIDEBAR_KEY, isCollapsed ? "collapsed" : "expanded");
}
// ---------------------------------
// ACTIVE MENU HIGHLIGHT BY URL
// ---------------------------------

(function () {
  const currentPath = window.location.pathname;
  const menuLinks = document.querySelectorAll(".sa-sidebar a");

  menuLinks.forEach(link => {
    link.classList.remove("active");

    const linkPath = link.getAttribute("href");
    if (linkPath && currentPath.startsWith(linkPath)) {
      link.classList.add("active");
    }
  });
})();
// ===============================
// AUTO ACTIVE SIDEBAR LINK
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  const links = document.querySelectorAll(".sa-sidebar nav a");
  const currentPath = window.location.pathname;

  links.forEach(link => {
    if (currentPath.startsWith(link.getAttribute("href"))) {
      link.classList.add("active");
    }
  });
});
