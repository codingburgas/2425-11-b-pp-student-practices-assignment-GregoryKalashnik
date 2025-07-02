// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required]');
    
    inputs.forEach(input => {
        if (!input.value) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
});

// Initialize datepickers
document.addEventListener('DOMContentLoaded', function() {
    const datepickers = document.querySelectorAll('.datepicker');
    datepickers.forEach(input => {
        new Datepicker(input, {
            format: 'yyyy-mm-dd',
            autohide: true
        });
    });
});

// Handle form submissions
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (form.classList.contains('needs-validation')) {
        if (!validateForm(form.id)) {
            e.preventDefault();
            e.stopPropagation();
        }
        form.classList.add('was-validated');
    }
});

// Handle table sorting
document.addEventListener('DOMContentLoaded', function() {
    const tables = document.querySelectorAll('.table-sortable');
    tables.forEach(table => {
        new Tablesort(table);
    });
});
