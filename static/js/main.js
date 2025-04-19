// Основний JavaScript файл для менеджера завдань

document.addEventListener('DOMContentLoaded', function() {
    // Ініціалізація компонентів
    initTooltips();
    initDatePickers();
    initDropdowns();
    setupFormValidation();
    setupNotifications();

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

// Ініціалізація підказок
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-toggle="tooltip"]');
    
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            const tip = document.createElement('div');
            tip.className = 'tooltip';
            tip.textContent = this.getAttribute('data-tooltip');
            
            const rect = this.getBoundingClientRect();
            tip.style.left = rect.left + (rect.width / 2) - (tip.offsetWidth / 2) + 'px';
            tip.style.top = rect.top - tip.offsetHeight - 10 + 'px';
            
            document.body.appendChild(tip);
            
            this.addEventListener('mouseleave', function() {
                tip.remove();
            }, { once: true });
        });
    });
}

// Ініціалізація вибору дати
function initDatePickers() {
    const datePickers = document.querySelectorAll('.date-picker');
    
    datePickers.forEach(input => {
        // Нативна підтримка type="date" в більшості браузерів
        if (input.type !== 'date') {
            // Простий поліфіл для старих браузерів
            input.addEventListener('focus', function() {
                this.type = 'date';
            });
            
            input.addEventListener('blur', function() {
                if (!this.value) {
                    this.type = 'text';
                }
            });
        }
    });
}

// Ініціалізація випадаючих меню
function initDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    
    dropdowns.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const dropdown = this.nextElementSibling;
            dropdown.classList.toggle('show');
            
            // Закриття випадаючих меню при кліку поза меню
            document.addEventListener('click', function closeDropdown(e) {
                if (!dropdown.contains(e.target) && e.target !== toggle) {
                    dropdown.classList.remove('show');
                    document.removeEventListener('click', closeDropdown);
                }
            });
        });
    });
}

// Валідація форм
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.classList.add('error');
                    
                    // Додаємо повідомлення про помилку, якщо його ще немає
                    if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('error-message')) {
                        const errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        errorMsg.textContent = 'Це поле є обов\'язковим';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                } else {
                    field.classList.remove('error');
                    
                    // Видаляємо повідомлення про помилку, якщо воно є
                    if (field.nextElementSibling && field.nextElementSibling.classList.contains('error-message')) {
                        field.nextElementSibling.remove();
                    }
                }
            });
            
            if (!valid) {
                e.preventDefault();
            }
        });
    });
}

// Сповіщення
function setupNotifications() {
    const notifications = document.querySelectorAll('.notification');
    
    notifications.forEach(notification => {
        // Додаємо кнопку закриття, якщо її немає
        if (!notification.querySelector('.close-btn')) {
            const closeBtn = document.createElement('button');
            closeBtn.className = 'close-btn';
            closeBtn.innerHTML = '&times;';
            closeBtn.addEventListener('click', function() {
                notification.remove();
            });
            notification.appendChild(closeBtn);
        }
        
        // Автоматично закриваємо повідомлення через 5 секунд
        setTimeout(() => {
            notification.remove();
        }, 5000);
    });
}

// Функція для форматування дати
function formatDate(date) {
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    
    return `${day}.${month}.${year}`;
}

// Функція для фільтрації задач
function filterTasks(filterType) {
    const tasks = document.querySelectorAll('.task-item');
    
    tasks.forEach(task => {
        const status = task.getAttribute('data-status');
        
        if (filterType === 'all' || status === filterType) {
            task.style.display = 'block';
        } else {
            task.style.display = 'none';
        }
    });
    
    // Оновлюємо активний фільтр
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        if (btn.getAttribute('data-filter') === filterType) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// Функція для сортування задач
function sortTasks(sortBy) {
    const taskList = document.querySelector('.task-list');
    const tasks = Array.from(taskList.querySelectorAll('.task-item'));
    
    tasks.sort((a, b) => {
        if (sortBy === 'date') {
            const dateA = new Date(a.getAttribute('data-due-date'));
            const dateB = new Date(b.getAttribute('data-due-date'));
            return dateA - dateB;
        } else if (sortBy === 'priority') {
            const priorityMap = { 'high': 3, 'medium': 2, 'low': 1 };
            const priorityA = priorityMap[a.getAttribute('data-priority')];
            const priorityB = priorityMap[b.getAttribute('data-priority')];
            return priorityB - priorityA;
        } else {
            const titleA = a.querySelector('.task-title').textContent;
            const titleB = b.querySelector('.task-title').textContent;
            return titleA.localeCompare(titleB);
        }
    });
    
    // Очищаємо список і додаємо відсортовані задачі
    taskList.innerHTML = '';
    tasks.forEach(task => {
        taskList.appendChild(task);
    });
}

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