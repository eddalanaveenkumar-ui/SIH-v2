// Main JavaScript for Attendance System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Processing...';
                submitBtn.disabled = true;
            }
        });
    });

    // File upload drag and drop functionality
    const fileUploads = document.querySelectorAll('.file-upload');
    fileUploads.forEach(upload => {
        const input = upload.querySelector('input[type="file"]');
        const label = upload.querySelector('.file-upload-label');

        if (input && label) {
            // Update label when files are selected
            input.addEventListener('change', function() {
                if (this.files.length > 0) {
                    if (this.files.length === 1) {
                        label.textContent = this.files[0].name;
                    } else {
                        label.textContent = `${this.files.length} files selected`;
                    }
                } else {
                    label.textContent = 'Choose files or drag them here';
                }
            });

            // Drag and drop functionality
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                upload.addEventListener(eventName, preventDefaults, false);
            });

            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            ['dragenter', 'dragover'].forEach(eventName => {
                upload.addEventListener(eventName, highlight, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                upload.addEventListener(eventName, unhighlight, false);
            });

            function highlight() {
                upload.classList.add('dragover');
            }

            function unhighlight() {
                upload.classList.remove('dragover');
            }

            upload.addEventListener('drop', handleDrop, false);

            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                input.files = files;
                input.dispatchEvent(new Event('change'));
            }
        }
    });

    // Real-time attendance statistics
    if (typeof updateAttendanceStats === 'function') {
        setInterval(updateAttendanceStats, 30000); // Update every 30 seconds
    }

    // Chart initialization
    initializeCharts();

    // Notification system
    initializeNotifications();

    // Search and filter functionality
    initializeSearchFilters();
});

// Chart initialization function
function initializeCharts() {
    const chartCanvases = document.querySelectorAll('canvas');
    chartCanvases.forEach(canvas => {
        const ctx = canvas.getContext('2d');
        const chartType = canvas.dataset.chartType || 'doughnut';

        // Sample chart data - you would replace this with actual data
        const chartData = {
            labels: ['Present', 'Absent', 'Late'],
            datasets: [{
                data: [70, 20, 10],
                backgroundColor: ['#27ae60', '#e74c3c', '#f39c12'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        };

        new Chart(ctx, {
            type: chartType,
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });
    });
}

// Notification system
function initializeNotifications() {
    // Check for new notifications periodically
    setInterval(checkNotifications, 60000); // Check every minute

    // Display notification badge if there are unread notifications
    updateNotificationBadge();
}

function checkNotifications() {
    // This would typically make an API call to check for new notifications
    console.log('Checking for new notifications...');

    // Simulate notification check
    const hasNewNotifications = Math.random() > 0.7;
    if (hasNewNotifications) {
        showNotification('New attendance record added', 'info');
        updateNotificationBadge();
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

function updateNotificationBadge() {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        // Simulate notification count
        const count = Math.floor(Math.random() * 5);
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

// Search and filter functionality
function initializeSearchFilters() {
    const searchInputs = document.querySelectorAll('.table-filter');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const filter = this.value.toLowerCase();
            const table = this.closest('.card').querySelector('table');
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    });

    // Date range filtering
    const dateFilters = document.querySelectorAll('.date-filter');
    dateFilters.forEach(filter => {
        filter.addEventListener('change', function() {
            filterTableByDate(this.value);
        });
    });
}

function filterTableByDate(date) {
    // Implementation for date-based filtering
    console.log('Filtering by date:', date);
}

// Attendance marking functionality
function markAttendance(studentEmail, date, status) {
    showLoading();

    fetch('/attendance/mark', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            student_email: studentEmail,
            date: date,
            status: status
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showNotification('Attendance marked successfully!', 'success');
            // Refresh the table or update specific row
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Error: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        showNotification('Error marking attendance', 'danger');
        console.error('Error:', error);
    });
}

// Loading indicator functions
function showLoading() {
    let loading = document.getElementById('loading-overlay');
    if (!loading) {
        loading = document.createElement('div');
        loading.id = 'loading-overlay';
        loading.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        `;
        loading.innerHTML = '<div class="spinner"></div>';
        document.body.appendChild(loading);
    }
    loading.style.display = 'flex';
}

function hideLoading() {
    const loading = document.getElementById('loading-overlay');
    if (loading) {
        loading.style.display = 'none';
    }
}

// Export functionality
function exportToCSV() {
    const table = document.querySelector('table');
    const rows = table.querySelectorAll('tr');
    let csv = [];

    rows.forEach(row => {
        const rowData = [];
        const cells = row.querySelectorAll('th, td');
        cells.forEach(cell => {
            rowData.push(cell.textContent.trim());
        });
        csv.push(rowData.join(','));
    });

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'attendance_report.csv';
    a.click();
    URL.revokeObjectURL(url);
}

// Print functionality
function printTable() {
    const printContent = document.querySelector('.card').innerHTML;
    const originalContent = document.body.innerHTML;

    document.body.innerHTML = printContent;
    window.print();
    document.body.innerHTML = originalContent;
    location.reload();
}

// Responsive table functionality
function makeTableResponsive() {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        if (table.offsetWidth > table.parentNode.offsetWidth) {
            table.parentNode.classList.add('table-responsive');
        }
    });
}

// Initialize when window resizes
window.addEventListener('resize', makeTableResponsive);

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl + P for print
    if (e.ctrlKey && e.key === 'p') {
        e.preventDefault();
        printTable();
    }

    // Ctrl + E for export
    if (e.ctrlKey && e.key === 'e') {
        e.preventDefault();
        exportToCSV();
    }
});

// Theme switcher (optional)
function toggleTheme() {
    const body = document.body;
    body.classList.toggle('dark-theme');
    localStorage.setItem('theme', body.classList.contains('dark-theme') ? 'dark' : 'light');
}

// Initialize theme
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
}

// Call initialization functions
initializeTheme();
makeTableResponsive();