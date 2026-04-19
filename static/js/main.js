// Main JS file
console.log('Autism Learning Platform Loaded');

// Add any global interaction logic here
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle ? themeToggle.querySelector('i') : null;

    // function to update icon
    const updateIcon = (isLight) => {
        if (themeIcon) {
            if (isLight) {
                themeIcon.classList.remove('fa-moon');
                themeIcon.classList.add('fa-sun');
            } else {
                themeIcon.classList.remove('fa-sun');
                themeIcon.classList.add('fa-moon');
            }
        }
    }

    // Apply saved theme
    const theme = localStorage.getItem('theme');
    if (theme === 'light') {
        document.body.classList.add('light-theme');
        updateIcon(true);
    }

    // Toggle logic
    if (themeToggle) {
        themeToggle.addEventListener('click', (e) => {
            e.preventDefault();
            document.body.classList.toggle('light-theme');
            const isLight = document.body.classList.contains('light-theme');

            // Save preference
            localStorage.setItem('theme', isLight ? 'light' : 'dark');

            // Update icon
            updateIcon(isLight);
        });
    }

    // Example: Add fade-in effect to main container
    const main = document.querySelector('main');
    if (main) {
        main.style.opacity = '0';
        main.style.transition = 'opacity 0.5s ease';
        setTimeout(() => {
            main.style.opacity = '1';
        }, 100);
    }

    // Sidebar Toggle Functionality
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');

    // Load saved sidebar state
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (sidebarCollapsed) {
        sidebar.classList.add('collapsed');
        sidebarToggle.classList.add('collapsed');
        mainContent.classList.add('expanded');
    }

    // Toggle sidebar
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            sidebarToggle.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');

            // Save state
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
    }

    // Highlight active sidebar link
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});
