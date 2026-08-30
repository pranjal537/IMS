/**
 * Damak Municipality Intern Management System (IMS)
 * Main JavaScript utilities & responsive sidebar controls
 */

document.addEventListener('DOMContentLoaded', () => {
    // Mobile sidebar toggling
    const sidebarToggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('imsSidebar');
    const backdrop = document.getElementById('imsSidebarBackdrop');

    function toggleSidebar() {
        if (sidebar) {
            sidebar.classList.toggle('show');
        }
        if (backdrop) {
            backdrop.classList.toggle('show');
        }
    }

    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', toggleSidebar);
    }

    if (backdrop) {
        backdrop.addEventListener('click', toggleSidebar);
    }

    // Auto-dismiss alert notifications after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            try {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            } catch (e) {
                // bootstrap may not be initialized yet
            }
        }, 5000);
    });
});
