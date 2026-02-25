/**
 * Global Configuration
 */
const CONFIG = {
    images: {
        maxSize: 2 * 1024 * 1024, // 2MB
        allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp','image/heic'],
        allowedExtensions: ['jpg', 'jpeg', 'png', 'gif', 'webp','heic']
    },
    limits: {
        'id_title': 100,
        'id_meta_title': 60,
        'id_meta_description': 160,
        'id_meta_keywords': 205
    }
};

/* ==========================================================================
   GLOBAL UTILITIES (Helpers)
   ========================================================================== */

/**
 * Robust CSRF Token Fetcher
 * Checks Cookie first, then falls back to Body Data Attribute
 */
function getCSRFToken() {
    let cookieValue = null;
    const name = 'csrftoken';
    
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
    
    // Fallback for some setups
    if (!cookieValue && document.body && document.body.dataset.csrfToken) {
        cookieValue = document.body.dataset.csrfToken;
    }
    return cookieValue;
}

/**
 * Universal Flash Message Handler
 * Displays a toast message in the container
 */
function showFlashMessage(text, type = 'info') {
    let container = document.getElementById('messages-container');

    if (!container) {
        container = document.createElement('div');
        container.id = 'messages-container';
        container.style.cssText = 'position:fixed;top:20px;right:20px;z-index:9999;min-width:280px;';
        document.body.appendChild(container);
    }

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    msgDiv.innerText = text;
    container.appendChild(msgDiv);

    setTimeout(() => {
        msgDiv.style.opacity = '0';
        msgDiv.style.transition = 'opacity 0.6s';
        setTimeout(() => msgDiv.remove(), 600);
    }, 3000);
}

/* ==========================================================================
   GLOBAL ACTIONS (Functions called via onclick="" in HTML)
   ========================================================================== */
function toggleStatus(el) {
    const url = el.dataset.url;
    const targetId = el.dataset.target;

    fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken() }
    })
    .then(res => res.json())
    .then(data => {
        const icon = el.querySelector("i");
        if (data.status) {
            icon.classList.replace("fa-toggle-off", "fa-toggle-on");
            icon.style.color = "#22c55e";
        } else {
            icon.classList.replace("fa-toggle-on", "fa-toggle-off");
            icon.style.color = "#9ca3af";
        }

        // Update Status Text Cell if it exists
        if (targetId) {
            const statusCell = document.getElementById(targetId);
            if (statusCell) {
                statusCell.innerText = data.status ? "Active" : "Inactive";
                statusCell.className = data.status ? "status-active" : "status-inactive";
            }
        }
        
        // Show feedback
        if (data.message) {
            showFlashMessage(data.message, data.status ? 'success' : 'info');
        }
    })
    .catch(err => console.error("Toggle failed:", err));
}

/**
 * Delete Modal Logic
 */
function openDeleteModal(modelName, itemNameOrCount, url, isBulk = false) {
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    const modalText = document.getElementById('modal-text');
    if (!modal || !form || !modalText) return;

    form.querySelectorAll('input[name="ids"]').forEach(i => i.remove());

    if (isBulk) {
        const selected = Array.from(document.querySelectorAll('.row-checkbox:checked'))
                              .map(cb => cb.value);
        if (!selected.length) {
            showFlashMessage("Please select at least one item to delete.", "warning");
            return;
        }

        modalText.textContent = `Are you sure you want to delete ${selected.length} ${modelName}(s)?`;

        const idsInput = document.createElement('input');
        idsInput.type = 'hidden';
        idsInput.name = 'ids';
        idsInput.value = selected.join(',');
        form.appendChild(idsInput);
    } else {
        modalText.textContent = `Are you sure you want to delete "${itemNameOrCount}"?`;
    }

    form.action = url;
    modal.style.display = 'flex';
    requestAnimationFrame(() => modal.classList.add('show'));
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    if (!modal) return;
    modal.classList.remove('show');
    setTimeout(() => modal.style.display = 'none', 300);
}

/* ==========================================================================
   MAIN INITIALIZATION (DOMContentLoaded)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    console.log("App Loaded");

    /* 1. Sidebar Toggler */
    const toggleBtn = document.getElementById("toggleSidebar");
    const sidebar = document.getElementById("sidebar");
    const main = document.getElementById("main");
    if (toggleBtn && sidebar && main) {
        toggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("collapsed");
            main.classList.toggle("collapsed");
        });
    }
    const homepageForm = document.getElementById('homepage-filter-form');
        if (homepageForm) {
            const homepageSelect = homepageForm.querySelector('select[name="homepage"]');
            if (homepageSelect) {
                homepageSelect.addEventListener('change', function() {
                    homepageForm.submit();
                });
            }
        }

    /* 2. Modal Outside Click Closer */
    window.onclick = function(event) {
        const modal = document.getElementById('deleteModal');
        if (event.target === modal) closeDeleteModal();
    };

    /* 3. Auto-Dismiss Existing Server Messages */
    const alerts = document.querySelectorAll('.message');
    if (alerts.length > 0) {
        alerts.forEach(alert => {
            setTimeout(() => {
                alert.style.opacity = '0';
                setTimeout(() => alert.style.display = 'none', 600);
            }, 3000);
        });
    }

    /* 4. Image Preview & Validation */
    (function initImagePreview() {
        const imageInput = document.querySelector('input[type="file"][name="image"]');
        const imagePreview = document.getElementById('imagePreview');
        const removeInput = document.getElementById('remove_image');
        
        if (!imageInput || !imagePreview) return;

        const imageLabel = imageInput.previousElementSibling;
        
        // Check if there's an existing image URL in the data attribute
        const existingImageUrl = imageInput.dataset.existingImage;

        function toggleInputVisibility(show) {
            if (show) {
                imageInput.style.opacity = '1';
                imageInput.style.height = 'auto';
                imageInput.style.position = 'static';
                if (imageLabel) imageLabel.style.display = 'block';
            } else {
                imageInput.style.opacity = '0';
                imageInput.style.height = '0';
                imageInput.style.position = 'absolute';
                if (imageLabel) imageLabel.style.display = 'none';
            }
        }

        function renderPreview(src, isExisting = false) {
            const label = isExisting ? 'Current image' : 'New image selected';
            imagePreview.innerHTML = `
                <div class="preview-wrapper" style="position:relative; display:inline-block; margin-top: 10px;">
                    <img src="${src}" style="max-width:300px; max-height:200px; border:1px solid #e5e7eb; border-radius:4px; display: block;">
                    <span class="remove-image" style="position:absolute; top:-8px; right:-8px; background:#ef4444; color:white; border-radius:50%; width:24px; height:24px; text-align:center; line-height:24px; cursor:pointer; font-weight:bold; font-size: 16px;">×</span>
                    <p style="margin-top: 5px; font-size: 12px; color: #666;">${label}</p>
                </div>`;
            toggleInputVisibility(false);
        }

        // Event: Remove Image
        imagePreview.addEventListener('click', function(e) {
            if (e.target.closest('.remove-image')) {
                e.preventDefault();
                removeInput.value = '1';
                imagePreview.innerHTML = '<p class="no-image text-muted">No image selected</p>';
                imageInput.value = '';
                // Remove the data attribute so it doesn't show again
                imageInput.removeAttribute('data-existing-image');
                toggleInputVisibility(true);
            }
        });

        // Event: Upload New Image
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (!file) return;

            // Validations
            if (file.size > CONFIG.images.maxSize) {
                alert(`File too large! Max size: 2MB. Your file is ${(file.size / (1024 * 1024)).toFixed(1)}MB`);
                this.value = '';
                return;
            }
            if (!CONFIG.images.allowedTypes.includes(file.type)) {
                alert('Invalid file type! Allowed: JPG, PNG, GIF, WebP, HEIC');
                this.value = '';
                return;
            }

            // Success -> Show Preview
            removeInput.value = '0';
            const reader = new FileReader();
            reader.onload = (e) => renderPreview(e.target.result, false);
            reader.readAsDataURL(file);
        });

        // Initial State: Show existing image if present
        if (existingImageUrl) {
            renderPreview(existingImageUrl, true);
        } else if (imagePreview.querySelector('img')) {
            // If there's already an img tag in the preview (server-rendered)
            toggleInputVisibility(false);
        }
    })();

    /* 5. Slug Generation */
function setFormAction(action) {
    document.getElementById('form-action').value = action;
}

(function initSlugGenerator() {
    const titleInput = document.getElementById("id_title");
    const slugInput = document.getElementById("id_slug");
    const slugMessage = document.getElementById("slug-message");
    const articleIdInput = document.getElementById("article-id"); // Ensure these exist in your HTML or handle nulls
    const modelNameInput = document.getElementById("model-name");

    if (!titleInput || !slugInput) return;

    const objectId = articleIdInput ? articleIdInput.value : "";
    const modelName = modelNameInput ? modelNameInput.value : "article";
    
    let debounceTimer;
    let slugManuallyEdited = false;

    // Helper function to create slug (if you don't have one globally)
    function slugify(text) {
        return text.toString().toLowerCase()
            .trim()
            .replace(/\s+/g, '-')           // Replace spaces with -
            .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
            .replace(/\-\-+/g, '-')         // Replace multiple - with single -
            .replace(/^-+/, '')             // Trim - from start of text
            .replace(/-+$/, '');            // Trim - from end of text
    }

    // Function to check slug availability via AJAX
    function checkSlugAvailability(slug) {
        if (!slug) {
            if (slugMessage) slugMessage.textContent = "";
            return;
        }

        fetch(`/ajax/check-slug/${modelName}/?slug=${encodeURIComponent(slug)}&object_id=${objectId}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    if (slugMessage) {
                        slugMessage.textContent = `⚠️ ${data.error}`;
                        slugMessage.style.color = "#f59e0b";
                    }
                    return;
                }
                
                if (slugMessage) {
                    if (data.exists) {
                        slugMessage.textContent = `❌ Slug already in use`;
                        slugMessage.style.color = "#dc2626";
                    } else {
                        slugMessage.textContent = `✅ Slug available`;
                        slugMessage.style.color = "#16a34a";
                    }
                }
            })
            .catch(err => console.error("Slug check failed:", err));
    }

    // When slug field is manually edited
    slugInput.addEventListener("input", function () {
        const slug = slugInput.value.trim();

        // FIX: If the user clears the slug, reset the flag so Title can generate it again
        if (slug === "") {
            slugManuallyEdited = false;
            if (slugMessage) slugMessage.textContent = ""; // Clear message
        } else {
            slugManuallyEdited = true;
        }
        
        clearTimeout(debounceTimer);

        debounceTimer = setTimeout(() => {
            if (!slug) return;
            checkSlugAvailability(slug);
        }, 400);
    });

    // When title changes - auto-generate slug and check availability
    titleInput.addEventListener("input", function () {
        clearTimeout(debounceTimer);
        
        // Auto-fill slug from title if not manually edited
        if (!slugManuallyEdited) {
            slugInput.value = slugify(titleInput.value);
        }

        debounceTimer = setTimeout(() => {
            const slug = slugInput.value.trim();
            
            if (!slug) {
                if (slugMessage) slugMessage.textContent = "";
                return;
            }

            // Check availability of the current slug
            checkSlugAvailability(slug);
        }, 400);
    });

    // Validate on blur
    slugInput.addEventListener("blur", function () {
        const slug = slugInput.value.trim();
        if (slug) {
            checkSlugAvailability(slug);
        }
    });
})();


    



    /* 9. CKEditor "Read More" Button */
    const readMoreBtn = document.getElementById('readMore');
    if (readMoreBtn) {
        readMoreBtn.addEventListener('click', function (e) {
            e.preventDefault();
            if (typeof CKEDITOR !== 'undefined' && CKEDITOR.instances['id_content']) {
                const editor = CKEDITOR.instances['id_content'];
                const content = editor.getData();
                
                if (content.includes('read-more-separator')) {
                    showFlashMessage('Read More separator already exists.', 'info');
                    return;
                }
                
                editor.insertHtml('<hr class="read-more-separator" style="border: 1px dashed #f60;" />');
                editor.focus();
            }
        });
    }

    /* 10. Meta / SEO Toggles & Validation */
    (function initSEOToggle() {
        const toggleBtn = document.getElementById('toggleMeta');
        const metaContent = document.getElementById('metaContent');
        const statusIcon = document.getElementById('metaStatusIcon');
        
        if (!toggleBtn || !metaContent) return;

        const metaInputs = metaContent.querySelectorAll('input, textarea');
        const form = document.querySelector('form[data-model="article"]');

        toggleBtn.addEventListener('click', function () {
            const isHidden = metaContent.style.display === "none";
            metaContent.style.display = isHidden ? "block" : "none";
            statusIcon.textContent = isHidden ? "▲" : "▼";

            // Toggle Required Attributes
            metaInputs.forEach(input => {
                if (isHidden) input.setAttribute('required', '');
                else {
                    input.removeAttribute('required');
                    input.classList.remove('input-error');
                }
            });
        });

        if (form) {
            form.addEventListener('submit', function (e) {
                if (metaContent.style.display === "none") return;

                let invalid = false;
                metaInputs.forEach(input => {
                    if (input.hasAttribute('required') && !input.value.trim()) {
                        input.classList.add('input-error');
                        invalid = true;
                    } else {
                        input.classList.remove('input-error');
                    }
                });

                if (invalid) {
                    e.preventDefault();
                    alert("Please fill out all visible SEO / Meta fields.");
                }
            });
        }
    })();


/* 11. Character Counters */

    Object.keys(CONFIG.limits).forEach(fieldId => {
        const inputField = document.getElementById(fieldId);
        if (!inputField) return;

        let counterId = '';
        if (fieldId === 'id_title') counterId = 'title-counter';
        else if (fieldId === 'id_meta_title') counterId = 'meta-title-counter';
        else if (fieldId === 'id_meta_description') counterId = 'meta-desc-counter';
        else if (fieldId === 'id_meta_keywords') counterId = 'meta-keywords-counter';

        const counter = document.getElementById(counterId);
        if (!counter) return;

        let maxChars = CONFIG.limits[fieldId];
        let minChars = 0;

        // Meta title rules
        if (fieldId === 'id_meta_title') {
            minChars = 20;
            maxChars = 60;
        }

        function updateCounter() {
            let currentLength = inputField.value.length;
            let remaining = maxChars - currentLength;

            // Hard max limit
            if (currentLength > maxChars) {
                inputField.value = inputField.value.substring(0, maxChars);
                counter.textContent = "Limit reached";
                counter.style.color = "#dc2626";
                counter.style.fontWeight = "bold";
                return;
            }

            // Show min message ONLY after typing starts
            if (
                fieldId === 'id_meta_title' &&
                currentLength > 0 &&
                currentLength < minChars
            ) {
                counter.textContent = "More than 20 characters required";
                counter.style.color = "#dc2626";
                counter.style.fontWeight = "bold";
                return;
            }

            // Normal states
            if (remaining === 0) {
                counter.textContent = "Limit reached";
                counter.style.color = "#dc2626";
            } else if (remaining <= 10) {
                counter.textContent = remaining + " characters remaining";
                counter.style.color = "#f59e0b";
            } else {
                counter.textContent = remaining + " characters remaining";
                counter.style.color = "#000000";
            }

            counter.style.fontWeight = "bold";
        }

        updateCounter();
        inputField.addEventListener("input", updateCounter);
    });




});

document.querySelectorAll('.sidebar-parent').forEach(function(toggle) {
    toggle.addEventListener('click', function(e) {
        e.preventDefault();

        const submenu = this.nextElementSibling;
        const icon = this.querySelector('.submenu-toggle');

        submenu.classList.toggle('open');
        icon.classList.toggle('rotate');
    });
});