$(document).ready(function () {

    // ========================
    // 1. Initialize DataTable
    // ========================
    var table = $('#packageTable').DataTable({
        paging: true,
        pageLength: 10,
        lengthMenu: [10, 20, 50, 100],
        ordering: true,
        order: [[2, 'asc']],  // Sort by Title column
        columnDefs: [
            { orderable: false, targets: [0, 1, 5] },    // Drag, checkbox, actions
            { searchable: false, targets: [0, 1, 4, 5] } // Only search title & type
        ],
        language: {
            emptyTable: "No packages found. Create one!",
            zeroRecords: "No matching packages found.",
        }
    });

    // ========================
    // 2. Initialize SortableJS
    // ========================
    var tbody = document.querySelector('#packageTable tbody');
    if (tbody) {
        Sortable.create(tbody, {
            handle: '.drag-handle',
            animation: 150,
            ghostClass: 'sortable-ghost',
            onEnd: function () {
                var sortUrl = tbody.dataset.sortUrl;
                if (!sortUrl) return;

                var order = [];
                tbody.querySelectorAll('tr').forEach(function (row) {
                    var id = row.getAttribute('data-id');
                    if (id) order.push(parseInt(id));
                });

                fetch(sortUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken(),
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({ order: order })
                })
                .then(function (res) { return res.json(); })
                .then(function (data) {
                    if (data.status === 'success') {
                        var msg = document.getElementById('saveMsg');
                        if (msg) {
                            msg.style.display = 'block';
                            setTimeout(function () {
                                msg.style.display = 'none';
                            }, 2000);
                        }
                    }
                })
                .catch(function (err) {
                    console.error('Sort failed:', err);
                });
            }
        });
    }

    // ========================
    // 3. Select All Checkbox
    // ========================
    $('#select-all').on('change', function () {
        var checked = this.checked;
        table.rows({ search: 'applied' }).nodes().each(function (row) {
            $(row).find('.row-checkbox').prop('checked', checked);
        });
    });

    $('#packageTable').on('change', '.row-checkbox', function () {
        var allBoxes = table.rows({ search: 'applied' }).nodes().to$().find('.row-checkbox');
        var checkedBoxes = allBoxes.filter(':checked');
        var selectAll = $('#select-all');

        selectAll.prop('checked', allBoxes.length === checkedBoxes.length);
        selectAll.prop('indeterminate', checkedBoxes.length > 0 && checkedBoxes.length < allBoxes.length);
    });
});