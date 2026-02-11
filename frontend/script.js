// ============ API CONFIGURATION ============
const API_BASE_URL = 'http://localhost:8000/api';
const UPLOAD_ENDPOINT = `${API_BASE_URL}/upload-case`;
const SEARCH_ENDPOINT = `${API_BASE_URL}/search-face`;
const CASES_ENDPOINT = `${API_BASE_URL}/cases`;
const STATS_ENDPOINT = `${API_BASE_URL}/stats`;

// ============ STATE VARIABLES ============
let selectedPhotoFile = null;
let selectedSearchFile = null;
let currentFilter = 'all';
let refreshInterval = null;

// ============ INITIALIZATION ============
document.addEventListener('DOMContentLoaded', function () {
    console.log('✅ Page loaded, initializing...');
    console.log('API_BASE_URL:', API_BASE_URL);
    console.log('SEARCH_ENDPOINT:', SEARCH_ENDPOINT);

    // Update debug info (if debug elements exist)
    const debugAPI = document.getElementById('debugAPI');
    const debugSearch = document.getElementById('debugSearch');
    if (debugAPI) debugAPI.textContent = API_BASE_URL;
    if (debugSearch) debugSearch.textContent = SEARCH_ENDPOINT;

    // Verify DOM elements exist
    const requiredElements = ['searchInput', 'searchBtn', 'searchResults', 'noResults', 'resultsList', 'matchBanner', 'resultsCount'];
    let allElementsExist = true;
    requiredElements.forEach(id => {
        const elem = document.getElementById(id);
        if (!elem) {
            console.error(`❌ Missing element: #${id}`);
            allElementsExist = false;
        } else {
            console.log(`✅ Found element: #${id}`);
        }
    });

    if (!allElementsExist) {
        console.error('⚠️ Some required elements are missing from HTML!');
    }

    initializeEventListeners();
    loadStatistics();
    loadCases();
    setupAutoRefresh();

    console.log('✅ Initialization complete');
    const debugStatus = document.getElementById('debugStatus');
    if (debugStatus) debugStatus.textContent = 'Ready - Click Search to begin';
});

// ============ AUTO-REFRESH ============
function setupAutoRefresh() {
    // Refresh statistics every 30 seconds
    refreshInterval = setInterval(() => {
        loadStatistics();
        loadCases();
    }, 30000);
}

// ============ EVENT LISTENERS ============
function initializeEventListeners() {
    // Navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });

    // Report form
    const reportForm = document.getElementById('reportForm');
    if (reportForm) {
        console.log('✅ Report form found, attaching submit listener');
        reportForm.addEventListener('submit', handleReportSubmit);
    } else {
        console.error('❌ Report form #reportForm not found!');
    }

    // Photo upload
    const photoInput = document.getElementById('photoInput');
    if (photoInput) {
        console.log('✅ Photo input found, attaching listeners');
        photoInput.addEventListener('change', handlePhotoUpload);
        photoInput.parentElement.addEventListener('click', () => {
            console.log('📁 Photo upload area clicked');
            photoInput.click();
        });
        photoInput.parentElement.addEventListener('dragover', handleDragOver);
        photoInput.parentElement.addEventListener('drop', handlePhotoDrop);
    } else {
        console.error('❌ Photo input #photoInput not found!');
    }

    // Search photo upload
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('change', handleSearchPhotoUpload);
        searchInput.parentElement.addEventListener('click', () => searchInput.click());
        searchInput.parentElement.addEventListener('dragover', handleDragOver);
        searchInput.parentElement.addEventListener('drop', handleSearchPhotoDrop);
    }

    // Search button
    const searchBtn = document.getElementById('searchBtn');
    if (searchBtn) {
        searchBtn.addEventListener('click', handleSearch);
    }

    // Filter buttons (disabled - cases section hidden)
    // const filterBtns = document.querySelectorAll('.filter-btn');
    // filterBtns.forEach(btn => {
    //     btn.addEventListener('click', () => {
    //         filterBtns.forEach(b => b.classList.remove('active'));
    //         btn.classList.add('active');
    //         currentFilter = btn.dataset.filter;
    //         loadCases();
    //     });
    // });
}

// ============ PHOTO UPLOAD HANDLERS ============
function handlePhotoUpload(event) {
    const file = event.target.files[0];
    if (file) {
        if (!isValidImageFile(file)) {
            showAlert('error', 'Invalid File', 'Please upload a JPG, PNG, or GIF image file (max 10MB)');
            document.getElementById('photoInput').value = '';
            return;
        }
        selectedPhotoFile = file;
        console.log('✅ Report photo selected:', file.name);
        displayPhotoPreview(file, 'photoPreview', 'previewImage');
    }
}

function handleSearchPhotoUpload(event) {
    const file = event.target.files[0];
    if (file) {
        if (!isValidImageFile(file)) {
            showAlert('error', 'Invalid File', 'Please upload a JPG, PNG, or GIF image file (max 10MB)');
            return;
        }
        selectedSearchFile = file;
        console.log('✅ Search file selected:', file.name);
        displayPhotoPreview(file, 'searchPhotoPreview', 'searchPreviewImage');
        const searchBtn = document.getElementById('searchBtn');
        if (searchBtn) {
            searchBtn.style.display = 'block';
            console.log('✅ Search button shown');
        } else {
            console.error('❌ Search button element not found!');
        }
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.style.background = 'rgba(99, 102, 241, 0.15)';
}

function handlePhotoDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.style.background = '';
    const file = event.dataTransfer.files[0];
    if (file && isValidImageFile(file)) {
        selectedPhotoFile = file;
        console.log('✅ Report photo dropped:', file.name);
        document.getElementById('photoInput').files = event.dataTransfer.files;
        displayPhotoPreview(file, 'photoPreview', 'previewImage');
    } else {
        showAlert('warning', 'Invalid File', 'Please drop a valid image file (JPG, PNG, GIF - max 10MB)');
    }
}

function handleSearchPhotoDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.style.background = '';
    const file = event.dataTransfer.files[0];
    if (file && isValidImageFile(file)) {
        selectedSearchFile = file;
        console.log('✅ Search file dropped:', file.name);
        document.getElementById('searchInput').files = event.dataTransfer.files;
        displayPhotoPreview(file, 'searchPhotoPreview', 'searchPreviewImage');
        const searchBtn = document.getElementById('searchBtn');
        if (searchBtn) {
            searchBtn.style.display = 'block';
            console.log('✅ Search button shown after drop');
        }
    } else {
        showAlert('warning', 'Invalid File', 'Please drop a valid image file (JPG, PNG, GIF - max 10MB)');
    }
}

function displayPhotoPreview(file, previewId, imageId) {
    const reader = new FileReader();
    reader.onload = (event) => {
        const preview = document.getElementById(previewId);
        const img = document.getElementById(imageId);
        img.src = event.target.result;
        preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

function removePhoto() {
    selectedPhotoFile = null;
    document.getElementById('photoInput').value = '';
    document.getElementById('photoPreview').style.display = 'none';
}

function removeSearchPhoto() {
    console.log('🗑️ Removing search photo');
    selectedSearchFile = null;
    const searchInput = document.getElementById('searchInput');
    if (searchInput) searchInput.value = '';
    const searchPhotoPreview = document.getElementById('searchPhotoPreview');
    if (searchPhotoPreview) searchPhotoPreview.style.display = 'none';
    const searchBtn = document.getElementById('searchBtn');
    if (searchBtn) searchBtn.style.display = 'none';
    const searchResults = document.getElementById('searchResults');
    if (searchResults) searchResults.style.display = 'none';
    const noResults = document.getElementById('noResults');
    if (noResults) noResults.style.display = 'none';
    const searchStatus = document.getElementById('searchStatus');
    if (searchStatus) searchStatus.style.display = 'none';
    console.log('✅ Search photo removed');
}

// ============ FORM SUBMISSION ============
async function handleReportSubmit(event) {
    event.preventDefault();
    console.log('📝 Form submission started');

    // Validate name
    const name = document.getElementById('personName').value.trim();
    if (!name) {
        showAlert('error', 'Name Required', 'Please enter the person\'s name');
        return;
    }

    // Validate status is selected
    const status = document.getElementById('caseStatus').value;
    if (!status || status === '') {
        showAlert('error', 'Status Required', 'Please select whether this is a missing or found person');
        return;
    }

    // Validate description
    const description = document.getElementById('description').value.trim();
    if (!description) {
        showAlert('error', 'Description Required', 'Please provide details about the person');
        return;
    }

    // Validate contact
    const contact = document.getElementById('contact').value.trim();
    if (!contact) {
        showAlert('error', 'Contact Required', 'Please provide email or phone number');
        return;
    }

    // Validate photo
    if (!selectedPhotoFile) {
        showAlert('error', 'Photo Required', 'Please select a photo');
        return;
    }

    if (!isValidImageFile(selectedPhotoFile)) {
        showAlert('error', 'Invalid Photo', 'Photo must be JPG, PNG, or GIF and under 10MB');
        removePhoto();
        return;
    }

    console.log('✅ All validations passed');
    console.log('  - Name:', name);
    console.log('  - Status:', status);
    console.log('  - Photo:', selectedPhotoFile.name);

    const formData = new FormData();
    formData.append('name', name);
    formData.append('status', status);
    formData.append('description', description);
    formData.append('contact', contact);
    formData.append('image', selectedPhotoFile);

    showLoading('Uploading case...');

    try {
        console.log('🚀 Sending upload request to:', UPLOAD_ENDPOINT);

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout

        const response = await fetch(UPLOAD_ENDPOINT, {
            method: 'POST',
            body: formData,
            signal: controller.signal
        });

        clearTimeout(timeoutId);
        console.log('📊 Response status:', response.status);

        let data;
        try {
            data = await response.json();
        } catch (jsonError) {
            console.error('❌ Failed to parse response JSON:', jsonError);
            showAlert('error', 'Error', 'Invalid response from server. Please check if the backend is running.');
            hideLoading();
            return;
        }

        console.log('✅ Response data:', data);

        if (response.ok && data.success) {
            console.log('🎉 Upload successful!');
            showAlert('success', 'Success', `Case uploaded successfully! ${data.faces_detected} face(s) detected.`);
            document.getElementById('reportForm').reset();
            removePhoto();
            setTimeout(() => {
                loadStatistics();
                loadCases();
                scrollToSection('cases');
            }, 1500);
        } else {
            const errorMsg = data ? (data.detail || data.message || 'Failed to upload case') : 'Unknown error';
            console.error('❌ Upload failed:', errorMsg);
            showAlert('error', 'Upload Error', errorMsg);
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.error('❌ Upload timeout');
            showAlert('error', 'Timeout', 'Upload request timed out. Please try again with a smaller image.');
        } else {
            console.error('❌ Upload error:', error);
            showAlert('error', 'Error', 'Connection error. Make sure the backend is running.\n\nError: ' + error.message);
        }
    } finally {
        hideLoading();
    }
}

// ============ SEARCH FUNCTIONALITY ============
async function handleSearch() {
    console.log('🔍 ===== SEARCH INITIATED =====');
    console.log('🔍 handleSearch called');
    console.log('📦 selectedSearchFile:', selectedSearchFile);

    if (!selectedSearchFile) {
        console.warn('⚠️ No file selected for search');
        showAlert('error', 'Photo Required', 'Please select a photo to search');
        return;
    }

    const formData = new FormData();
    formData.append('image', selectedSearchFile);
    await searchWithFormData(formData, selectedSearchFile.name);
}

// Common helper to perform search given a FormData containing an 'image' field
async function searchWithFormData(formData, sourceLabel = 'upload') {
    console.log('🔍 Starting search (source:', sourceLabel, ')');
    const debugStatus = document.getElementById('debugStatus');
    if (debugStatus) debugStatus.textContent = 'Searching...';

    // Show search status
    const searchResultsEl = document.getElementById('searchResults');
    const noResultsEl = document.getElementById('noResults');
    const searchStatusEl = document.getElementById('searchStatus');

    if (searchResultsEl) searchResultsEl.style.display = 'none';
    if (noResultsEl) noResultsEl.style.display = 'none';
    if (searchStatusEl) searchStatusEl.style.display = 'block';

    const statusText = document.getElementById('statusText');
    if (statusText) statusText.textContent = 'Searching for similar faces...';

    try {
        console.log('🔍 Sending search request to:', SEARCH_ENDPOINT);
        // If a similarity threshold is stored in localStorage (admin setting), include it
        const savedThreshold = localStorage.getItem('similarityThreshold');
        if (savedThreshold) {
            formData.append('min_similarity', savedThreshold);
            console.log('🔧 Appended min_similarity from localStorage:', savedThreshold);
        }
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout

        const response = await fetch(SEARCH_ENDPOINT, {
            method: 'POST',
            body: formData,
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        let data;
        try {
            data = await response.json();
        } catch (jsonError) {
            console.error('❌ Failed to parse response JSON:', jsonError);
            const responseText = await response.text();
            console.error('Response text:', responseText);
            showAlert('error', 'Error', 'Invalid response from server. Please check if the backend is running properly.');
            if (searchStatusEl) searchStatusEl.style.display = 'none';
            return;
        }

        if (response.ok && data && data.success) {
            console.log('🎉 Search successful!');
            if (debugStatus) debugStatus.textContent = 'Search completed - ' + (data.matches ? data.matches.length : 0) + ' raw matches found';
            displaySearchResults(data);
        } else {
            const errorMsg = data ? (data.detail || data.message || 'Unknown error') : 'Unknown error';
            if (debugStatus) debugStatus.textContent = 'Search failed: ' + errorMsg;
            showAlert('error', 'Search Error', errorMsg);
            if (searchStatusEl) searchStatusEl.style.display = 'none';
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.error('❌ Search timeout - request took too long');
            showAlert('error', 'Timeout', 'Search request timed out. Please try again or use a smaller image.');
        } else {
            console.error('❌ Search error:', error);
            if (debugStatus) debugStatus.textContent = 'Error: ' + error.message;
            showAlert('error', 'Error', 'Connection error. Make sure the backend is running.\n\nError: ' + error.message);
        }
        if (searchStatusEl) searchStatusEl.style.display = 'none';
    } finally {
        console.log('🔍 ===== SEARCH COMPLETE =====');
    }
}

// Fetch a stored case image from the uploads folder and submit it to the search endpoint
async function findSimilarFromCase(imagePath) {
    try {
        if (!imagePath) {
            console.warn('No imagePath provided to findSimilarFromCase');
            return;
        }

        // Normalize and build absolute URL
        const filename = imagePath.replace(/\\/g, '/').split('/').pop();
        const encodedFilename = encodeURIComponent(filename || '');
        const url = `${API_BASE_URL.replace('/api', '')}/uploads/${encodedFilename}`;

        console.log('📥 Fetching case image from:', url);

        const resp = await fetch(url);
        if (!resp.ok) {
            showAlert('error', 'Fetch Error', 'Failed to fetch image from server for searching.');
            return;
        }

        const blob = await resp.blob();
        const formData = new FormData();
        // Use a filename so backend can infer type
        formData.append('image', blob, filename);

        await searchWithFormData(formData, `case:${filename}`);
    } catch (err) {
        console.error('Error in findSimilarFromCase:', err);
        showAlert('error', 'Error', 'Unable to start search from case image.');
    }
}

function displaySearchResults(data) {
    console.log('===== DISPLAY SEARCH RESULTS =====');
    console.log('📥 Input data:', JSON.stringify(data, null, 2));

    const searchStatus = document.getElementById('searchStatus');
    const searchResults = document.getElementById('searchResults');
    const noResults = document.getElementById('noResults');
    const resultsList = document.getElementById('resultsList');
    const matchBanner = document.getElementById('matchBanner');

    console.log('🔗 DOM Elements check:');
    console.log('  - searchStatus:', searchStatus ? '✅' : '❌');
    console.log('  - searchResults:', searchResults ? '✅' : '❌');
    console.log('  - noResults:', noResults ? '✅' : '❌');
    console.log('  - resultsList:', resultsList ? '✅' : '❌');
    console.log('  - matchBanner:', matchBanner ? '✅' : '❌');

    // Hide status with null check
    if (searchStatus) {
        searchStatus.style.display = 'none';
    } else {
        console.error('❌ searchStatus element not found!');
    }

    // Extract data from the response
    // The backend now returns a single "match" object for the best match
    // or a list of "matches" in the old structure. We handle both for robustness.
    let matches = [];

    if (data.match) {
        // New structure: single best match
        matches = [data.match];
    } else if (data.matches) {
        // Old structure: list of matches at top level
        matches = data.matches;
    }

    // Filter results to show matches (60%+ similarity is good enough)
    const filteredMatches = matches.filter(match => {
        const passes = match.similarity_percentage >= 60;
        console.log(`  - ${match.name}: ${match.similarity_percentage}% ${passes ? '✅ PASS' : '❌ FAIL (below 60%)'}`);
        return passes;
    });

    // Use the normalized `matches` array (handles both `match` and `matches` response shapes)
    console.log(`\n🔍 Filtering Results: ${matches.length} total → ${filteredMatches.length} filtered (60%+)`);

    if (!filteredMatches || filteredMatches.length === 0) {
        console.log('❌ No matches after filtering - displaying no results message');
        if (matchBanner) matchBanner.style.display = 'none';
        if (noResults) {
            noResults.style.display = 'block';
            console.log('✅ No results message displayed');
        }
        if (searchResults) searchResults.style.display = 'block';
        // Scroll to no results section
        setTimeout(() => {
            if (noResults) {
                console.log('📍 Scrolling to no results section...');
                noResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }, 100);
        return;
    }

    console.log(`✅ Found ${filteredMatches.length} matches! Building result cards...`);

    // Build results HTML
    let resultsHTML = '';
    filteredMatches.forEach((match, index) => {
        // Properly construct image path with URL encoding and normalization
        let imagePath = match.image_path || '';
        if (!imagePath.startsWith('http')) {
            // Normalize backslashes to forward slashes and extract filename
            const filename = imagePath.replace(/\\/g, '/').split('/').pop();
            const encodedFilename = encodeURIComponent(filename || '');
            // Use absolute uploads path so it works regardless of current page path
            imagePath = `${API_BASE_URL.replace('/api', '')}/uploads/${encodedFilename}`;
        }

        const statusClass = match.status === 'missing' ? 'status-missing' : 'status-found';
        const statusText = match.status === 'missing' ? 'MISSING' : 'FOUND';
        const matchNumber = index + 1;
        const similarityLevel = match.similarity_percentage >= 80 ? 'Very High' : match.similarity_percentage >= 70 ? 'High' : match.similarity_percentage >= 60 ? 'Good' : 'Fair';

        console.log(`\n📋 Building card ${matchNumber}:`);
        console.log(`  - Name: ${match.name}`);
        console.log(`  - Similarity: ${match.similarity_percentage}%`);
        console.log(`  - Status: ${statusText}`);
        console.log(`  - Original image path: ${match.image_path}`);
        console.log(`  - Constructed URL: ${imagePath}`);
        console.log(`  - Description: ${match.description}`);
        console.log(`  - Contact: ${match.contact}`);

        resultsHTML += `
            <div class="result-card">
                <div style="position: relative;">
                    <img src="${imagePath}" alt="${escapeHtml(match.name)}" class="result-image" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22320%22 height=%22250%22%3E%3Crect fill=%22%23e5e7eb%22 width=%22320%22 height=%22250%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 font-family=%22Arial%22 font-size=%2214%22 fill=%22%236b7280%22%3ENo Image%3C/text%3E%3C/svg%3E'">
                    <span class="result-badge">#${matchNumber} Match</span>
                </div>
                <div class="result-content">
                    <div>
                        <div class="result-header">
                            <div>
                                <div class="result-name">${escapeHtml(match.name)}</div>
                            </div>
                            <span class="result-status ${statusClass}">${statusText}</span>
                        </div>
                        
                        <div class="result-similarity">
                            <div class="similarity-label">Match Confidence (${similarityLevel})</div>
                            <div class="similarity-bar">
                                <div class="similarity-fill" style="width: ${match.similarity_percentage}%"></div>
                            </div>
                            <div class="result-score">${match.similarity_percentage}% Match</div>
                        </div>
                        
                        <div class="result-details">
                            <strong><i class="fas fa-envelope"></i> Contact:</strong><br>
                            ${escapeHtml(match.contact)}
                        </div>
                        
                        <div class="result-details">
                            <strong><i class="fas fa-info-circle"></i> Details:</strong><br>
                            ${escapeHtml(match.description)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    console.log('🖼️ Setting results HTML...');
    if (resultsList) {
        resultsList.innerHTML = resultsHTML;
        console.log('✅ HTML set to resultsList');
    } else {
        console.error('❌ resultsList element not found!');
        return;
    }

    const resultsCountElement = document.getElementById('resultsCount');
    if (resultsCountElement) {
        const resultCountText = filteredMatches.length === 1
            ? `Found <strong>1 potential match</strong> with 60%+ similarity`
            : `Found <strong>${filteredMatches.length} potential matches</strong> with 60%+ similarity`;
        resultsCountElement.innerHTML = resultCountText;
        console.log('📊 Result count text updated:', resultCountText);
    } else {
        console.error('❌ resultsCount element not found!');
    }

    console.log('\n🎉 DISPLAYING RESULTS ON PAGE');
    console.log('  - matchBanner.style.display = "block"');
    console.log('  - searchResults.style.display = "block"');
    console.log('  - noResults.style.display = "none"');

    // Update visibility with null checks
    if (matchBanner) {
        matchBanner.style.display = 'block';
        console.log('✅ matchBanner visible');
    }
    if (searchResults) {
        searchResults.style.display = 'block';
        // Force reflow to ensure display update
        void searchResults.offsetHeight;
        console.log('✅ searchResults visible');
    }
    if (noResults) {
        noResults.style.display = 'none';
    }

    console.log('✅ Visibility updated');

    // Scroll to results
    setTimeout(() => {
        try {
            const targetElement = searchResults || document.getElementById('searchResults');
            if (targetElement) {
                console.log('📍 Auto-scrolling to search results...');
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                console.log('✅ Scroll animation started');
            }
        } catch (scrollError) {
            console.warn('⚠️ Scroll error:', scrollError);
        }
    }, 300);

    console.log('===== DISPLAY COMPLETE =====\n');
}

// ============ CASES DISPLAY ============
function filterPersons(filterType) {
    currentFilter = filterType;

    // Update filter buttons
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-filter') === filterType) {
            btn.classList.add('active');
        }
    });

    loadCases();
}

async function loadCases() {
    try {
        let url = CASES_ENDPOINT + '?t=' + Date.now();  // Cache-busting parameter
        if (currentFilter !== 'all') {
            url += `&status=${currentFilter}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.success && data.cases) {
            displayCases(data.cases);
        } else {
            console.error('Failed to load cases');
            displayCases([]);
        }
    } catch (error) {
        console.error('Load cases error:', error);
        displayCases([]);
    }
}

function displayCases(cases) {
    const casesList = document.getElementById('casesList');
    const noCasesMessage = document.getElementById('noCasesMessage');

    if (!cases || cases.length === 0) {
        casesList.innerHTML = '';
        noCasesMessage.style.display = 'block';
        return;
    }

    noCasesMessage.style.display = 'none';

    let casesHTML = '';
    cases.forEach(caseItem => {
        // Properly construct image path with URL encoding and normalization
        let imagePath = caseItem.image_path || '';
        if (!imagePath.startsWith('http')) {
            const filename = imagePath.replace(/\\/g, '/').split('/').pop();
            const encodedFilename = encodeURIComponent(filename || '');
            imagePath = `${API_BASE_URL.replace('/api', '')}/uploads/${encodedFilename}`;
        }
        const badgeClass = caseItem.status === 'missing' ? 'missing' : 'found';
        const badgeText = caseItem.status === 'missing' ? '🔴 MISSING PERSON' : '🟢 FOUND PERSON';
        const date = new Date(caseItem.created_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        const time = new Date(caseItem.created_at).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });

        casesHTML += `
            <div class="case-card">
                <div class="case-image-container">
                    <img src="${imagePath}" alt="${caseItem.name}" class="case-image" onerror="this.src='https://via.placeholder.com/300x250'">
                    <span class="case-badge ${badgeClass}">${badgeText}</span>
                </div>
                <div class="case-content">
                    <div class="case-header">
                        <h3 class="case-name">${escapeHtml(caseItem.name)}</h3>
                    </div>
                    <div class="case-description-box">
                        <p class="case-description">${escapeHtml(caseItem.description)}</p>
                    </div>
                    <div style="margin-top:8px;">
                        <button class="btn btn-sm btn-secondary" onclick="findSimilarFromCase('${escapeHtml(caseItem.image_path)}')">
                            <i class="fas fa-search"></i> Find Similar
                        </button>
                    </div>
                    <div class="case-details">
                        <div class="case-meta-item">
                            <i class="fas fa-phone-alt"></i>
                            <span title="Contact information">${escapeHtml(caseItem.contact)}</span>
                        </div>
                        <div class="case-meta-item">
                            <i class="fas fa-calendar-alt"></i>
                            <span title="Reported date and time">${date} at ${time}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    casesList.innerHTML = casesHTML;
}

// ============ STATISTICS ============
async function loadStatistics() {
    try {
        // Add cache-busting parameter to force fresh data from database
        const response = await fetch(STATS_ENDPOINT + '?t=' + Date.now());
        const data = await response.json();

        if (data.success && data.statistics) {
            document.getElementById('total-cases').textContent = data.statistics.total_cases;
            document.getElementById('missing-count').textContent = data.statistics.missing_persons;
            document.getElementById('found-count').textContent = data.statistics.found_persons;
        }
    } catch (error) {
        console.error('Load statistics error:', error);
    }
}

// ============ UTILITY FUNCTIONS ============
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

function isValidImageFile(file) {
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp'];
    const maxSize = 10 * 1024 * 1024; // 10MB
    return validTypes.includes(file.type) && file.size <= maxSize;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============ MODALS ============
function showLoading(message = 'Loading...') {
    document.getElementById('loadingText').textContent = message;
    document.getElementById('loadingModal').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingModal').style.display = 'none';
}

function showAlert(type, title, message) {
    const alertModal = document.getElementById('alertModal');
    const alertIcon = document.getElementById('alertIcon');
    const alertTitle = document.getElementById('alertTitle');
    const alertMessage = document.getElementById('alertMessage');

    alertTitle.textContent = title;
    alertMessage.textContent = message;

    // Set icon based on type
    alertIcon.className = 'fas';
    if (type === 'success') {
        alertIcon.classList.add('fa-check-circle');
    } else if (type === 'error') {
        alertIcon.classList.add('fa-times-circle');
    } else if (type === 'warning') {
        alertIcon.classList.add('fa-exclamation-circle');
    }

    alertModal.style.display = 'flex';
}

function closeAlert() {
    document.getElementById('alertModal').style.display = 'none';
}

// Close modal when clicking outside
document.addEventListener('click', function (event) {
    const alertModal = document.getElementById('alertModal');
    if (event.target === alertModal) {
        closeAlert();
    }
});
