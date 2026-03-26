$(document).ready(function () {
    // 1. Get CSRF Token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // 2. Initialize DataTable
    // We disable pagination and ordering so SortableJS has full control
    const table = $('#listTable').DataTable({
        paging: true,
        ordering: false,
        pageLength: 10,
        lengthMenu: [
            [10, 25, 50, -1],  // -1 tells DataTables to show all rows
            [10, 25, 50, "All"] // The labels displayed in the dropdown
        ]
    });





    // 3. Initialize SortableJS on the tbody
    const el = document.querySelector('#listTable tbody');
    const sortUrl = $('#listTable').data('sort-url');
    Sortable.create(el, {
        handle: '.drag-handle', // <--- This restricts drag to the handle
        animation: 200,         // Smooth sliding animation (ms)
        ghostClass: 'sortable-ghost',
        onEnd: function () {
            let newOrder = [];

            // Loop through parent rows only (skip child-group rows)
            $('#listTable tbody tr').each(function () {
                if ($(this).hasClass('child-group')) return;
                const id = $(this).data('id');
                if (id) newOrder.push(id);
            });

            // 4. Send the new ID list to the server
            $.ajax({
                url: sortUrl,
                method: "POST",
                headers: { "X-CSRFToken": csrftoken },
                contentType: "application/json",
                data: JSON.stringify({ order: newOrder }),
                success: function () {
                    $('#saveMsg').fadeIn().delay(800).fadeOut();
                },
                error: function () {
                    alert('Save failed. Please refresh and try again.');
                }
            });
        }
    });

    // 4. Select All Checkbox Logic
    $('#select-all').on('change', function () {
        const checked = this.checked;
        table.rows({ search: 'applied' }).nodes().each(function (row) {
            $(row).find('.row-checkbox').prop('checked', checked);
        });
    });

    $('#listTable').on('change', '.row-checkbox', function () {
        const allBoxes = table.rows({ search: 'applied' }).nodes().to$().find('.row-checkbox');
        const checkedBoxes = allBoxes.filter(':checked');
        const selectAll = $('#select-all');
        selectAll.prop('checked', allBoxes.length === checkedBoxes.length);
        selectAll.prop('indeterminate', checkedBoxes.length > 0 && checkedBoxes.length < allBoxes.length);
    });
});