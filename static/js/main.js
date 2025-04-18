document.addEventListener('DOMContentLoaded', function () {

    let tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    let tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });


    const formFields = {
        'title': 'form-control',
        'description': 'form-control',
        'status': 'form-select',
        'deadline': 'form-control',
        'assigned_to': 'form-select',
        'project': 'form-select',
        'tags': 'form-control'
    };

    for (const [field, className] of Object.entries(formFields)) {
        const element = document.getElementById('id_' + field);
        if (element) {
            element.classList.add(className);
        }
    }


    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        }
    });


    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });


    const deleteButtons = document.querySelectorAll('.btn-delete-confirm');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            if (!confirm('Ви впевнені, що хочете видалити цей елемент? Ця дія незворотна.')) {
                e.preventDefault();
            }
        });
    });


    const tableSearch = document.getElementById('tableSearch');
    if (tableSearch) {
        tableSearch.addEventListener('keyup', function () {
            const searchText = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('table tbody tr');

            tableRows.forEach(row => {
                const rowText = row.textContent.toLowerCase();
                if (rowText.includes(searchText)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});


function confirmTagDelete(tagId, tagName) {
    if (confirm(`Ви впевнені, що хочете видалити тег "${tagName}"? Це може вплинути на пов'язані завдання.`)) {
        document.getElementById('deleteTagForm_' + tagId).submit();
    }
}


function changeTaskStatus(taskId, status) {
    const statusMap = {
        'to_do': 'До виконання', 'in_progress': 'В процесі', 'done': 'Виконано'
    };

    if (confirm(`Змінити статус завдання на "${statusMap[status]}"?`)) {
        window.location.href = `/tasks/${taskId}/quick-update/?status=${status}`;
    }
} 