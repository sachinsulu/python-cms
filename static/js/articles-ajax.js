(function () {
    let ajaxController = null;
    const container = document.getElementById('articles-list-container');
    const loader = document.getElementById('ajax-loader');
    const searchInput = document.getElementById('article-search');
    const perPageSelect = document.querySelector('#per-page-form select[name="per_page"]');
    const homepageSelect = document.querySelector('#homepage-filter-form select[name="homepage"]');

    if (!container) return;

    function showLoader() { if (loader) loader.style.display = 'block'; }
    function hideLoader() { if (loader) loader.style.display = 'none'; }

    async function fetchAndReplace(url, push = true) {
        if (ajaxController) ajaxController.abort();
        ajaxController = new AbortController();
        showLoader();
        try {
            const res = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                signal: ajaxController.signal
            });
            // Detect auth redirects / forbidden responses
            if (res.status === 401 || res.status === 403) {
                if (typeof showFlashMessage === 'function') showFlashMessage('Session expired or access denied.', 'error');
                // Redirect to login or reload
                window.location = '/login/?next=' + encodeURIComponent(window.location.pathname + window.location.search);
                return;
            }

            const html = await res.text();

            // If server redirected to login page (fetch follows redirects), detect it
            try {
                if (res.url && res.url.indexOf('/login') !== -1) {
                    if (typeof showFlashMessage === 'function') showFlashMessage('Session expired — redirecting to login.', 'error');
                    setTimeout(() => window.location = res.url, 700);
                    return;
                }
            } catch (e) {
                // ignore
            }

            if (!res.ok) throw new Error('Network error');
            
            // 1. Update DOM
            container.innerHTML = html;
            
            // 2. Re-initialize Sortable immediately after DOM update
            if (typeof window.initSortable === 'function') {
                window.initSortable();
            }

            if (push) history.pushState(null, '', url);
        } catch (err) {
            if (err.name !== 'AbortError') console.error('AJAX fetch failed', err);
        } finally {
            hideLoader();
        }
    }

    // Intercept pagination links
    document.addEventListener('click', function (e) {
        const a = e.target.closest && e.target.closest('a.ajax-page');
        if (!a) return;
        e.preventDefault();
        fetchAndReplace(a.href);
    });

    // Debounce helper
    function debounce(fn, wait){ let t; return (...args)=>{ clearTimeout(t); t=setTimeout(()=>fn(...args), wait); }; }

    // Build URL preserving pathname and other filters
    function buildUrlWithQuery(q) {
        const url = new URL(window.location.href);
        if (q && q.length) url.searchParams.set('q', q);
        else url.searchParams.delete('q');

        if (perPageSelect) url.searchParams.set('per_page', perPageSelect.value);
        if (homepageSelect) url.searchParams.set('homepage', homepageSelect.value);

        // Reset to first page when searching
        url.searchParams.delete('page');
        return url.toString();
    }

    if (searchInput) {
        const onSearch = debounce(function () {
            const q = searchInput.value.trim();
            const url = buildUrlWithQuery(q);
            fetchAndReplace(url);
        }, 350);

        // Capture-phase listener to stop other handlers and prevent full-page navigation
        searchInput.addEventListener('input', function (e) {
            // Prevent other input handlers (like legacy script) from running and causing navigation
            if (e.stopImmediatePropagation) e.stopImmediatePropagation();
            if (e.stopPropagation) e.stopPropagation();
            onSearch();
        }, true);

        // Prevent Enter key from submitting any parent form and trigger AJAX instead
        searchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                onSearch();
            }
        });
    }

    // When per-page or homepage filters change, perform AJAX request
    if (perPageSelect) perPageSelect.addEventListener('change', function () {
        const url = buildUrlWithQuery(searchInput ? searchInput.value.trim() : '');
        fetchAndReplace(url);
    });
    if (homepageSelect) homepageSelect.addEventListener('change', function () {
        const url = buildUrlWithQuery(searchInput ? searchInput.value.trim() : '');
        fetchAndReplace(url);
    });

    // Prevent native form submit for filters and use AJAX instead (progressive enhancement)
    const homepageForm = document.getElementById('homepage-filter-form');
    const perPageForm = document.getElementById('per-page-form');

    function handleFilterSubmit(e) {
        e.preventDefault();
        const q = searchInput ? searchInput.value.trim() : '';
        const url = buildUrlWithQuery(q);
        fetchAndReplace(url);
    }

    if (homepageForm) homepageForm.addEventListener('submit', handleFilterSubmit);
    if (perPageForm) perPageForm.addEventListener('submit', handleFilterSubmit);

    // Handle back/forward
    window.addEventListener('popstate', function () {
        fetchAndReplace(location.href, false);
    });

})();