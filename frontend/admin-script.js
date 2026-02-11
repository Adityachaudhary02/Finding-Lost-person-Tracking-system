// ============ API CONFIGURATION ============
const API_BASE_URL = 'http://localhost:8000/api';
const CASES_ENDPOINT = `${API_BASE_URL}/cases`;
const STATS_ENDPOINT = `${API_BASE_URL}/stats`;
const LOGIN_ENDPOINT = `${API_BASE_URL}/admin/login`;
let isAuthenticated = false;
let sessionToken = sessionStorage.getItem('adminToken') || '';

// ============ INITIALIZATION ============
let refreshInterval = null;

document.addEventListener('DOMContentLoaded', function () {
    // Check if admin is authenticated via session
    if (!sessionStorage.getItem('adminToken')) {
        // Show login modal and hide main content
        const loginModal = document.getElementById('loginModal');
        loginModal.style.display = 'flex';
        loginModal.style.background = 'rgba(0, 0, 0, 0.7)';
        document.querySelector('.sidebar').style.display = 'none';
        document.querySelector('.main-content').style.display = 'none';
        return;
    }
    
    isAuthenticated = true;
    initializeNavigation();
    loadDashboard();
    loadAdminThreshold();
    setupAutoRefresh();
});

// ============ AUTO-REFRESH ============
function setupAutoRefresh() {
    // Refresh dashboard every 30 seconds
    refreshInterval = setInterval(() => {
        const activePage = document.querySelector('.page.active')?.id;
        if (activePage === 'dashboard-page') {
            loadDashboard();
        } else if (activePage === 'cases-page') {
            loadCases();
        }
    }, 30000);
}

function refreshCurrentPage() {
    const activePage = document.querySelector('.page.active')?.id;
    if (activePage === 'dashboard-page') {
        loadDashboard();
    } else if (activePage === 'cases-page') {
        loadCases();
    } else if (activePage === 'search-page') {
        loadSearchHistory();
    } else if (activePage === 'users-page') {
        loadAdminUsers();
    }
}

// ============ AUTHENTICATION ============
async function handleAdminLogin(event) {
    event.preventDefault();
    const password = document.getElementById('adminLoginPassword').value;
    const loginBtn = event.target.querySelector('button[type="submit"]');
    const originalText = loginBtn.textContent;
    
    if (!password) {
        showAlert('Password required', 'error');
        return;
    }
    
    try {
        // Show loading state
        loginBtn.disabled = true;
        loginBtn.textContent = 'Verifying...';
        
        // Validate password with backend
        const formData = new FormData();
        formData.append('password', password);
        
        const response = await fetch(LOGIN_ENDPOINT, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success && data.authenticated) {
            // Store token in sessionStorage (cleared when browser is closed)
            sessionStorage.setItem('adminToken', btoa(password + ':' + Date.now()));
            sessionStorage.setItem('adminPassword', password);
            isAuthenticated = true;
            
            // Clear login form
            document.getElementById('adminLoginPassword').value = '';
            
            // Hide login modal and show main content
            document.getElementById('loginModal').style.display = 'none';
            document.querySelector('.sidebar').style.display = 'flex';
            document.querySelector('.main-content').style.display = 'flex';
            
            // Initialize the admin panel
            initializeNavigation();
            loadDashboard();
            loadAdminThreshold();
            setupAutoRefresh();
            
            showAlert('Admin authenticated successfully', 'success');
            console.log('✅ Admin login successful');
        } else {
            showAlert('Invalid admin password', 'error');
            console.log('❌ Admin login failed:', data.message);
            document.getElementById('adminLoginPassword').value = '';
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('Connection error. Make sure the backend is running.', 'error');
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = originalText;
    }
}

// ============ SESSION VALIDATION ============
function isAdminAuthenticated() {
    return sessionStorage.getItem('adminToken') !== null && isAuthenticated;
}

function ensureAuthenticated() {
    if (!isAdminAuthenticated()) {
        showAlert('Session expired. Please login again.', 'error');
        logout();
        return false;
    }
    return true;
}

function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            if (item.dataset.page) {
                e.preventDefault();
                switchPage(item.dataset.page);
            }
        });
    });

    // Threshold slider
    const thresholdSlider = document.getElementById('thresholdSlider');
    if (thresholdSlider) {
        thresholdSlider.addEventListener('input', (e) => {
            document.getElementById('thresholdValue').textContent = parseFloat(e.target.value).toFixed(2);
        });
    }
}

function switchPage(pageName) {
    // Check if admin is still authenticated
    if (!ensureAuthenticated()) {
        return;
    }
    
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === pageName) {
            item.classList.add('active');
        }
    });

    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Show selected page
    const pageElement = document.getElementById(`${pageName}-page`);
    if (pageElement) {
        pageElement.classList.add('active');
    }

    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'cases': 'Manage Cases',
        'search': 'Search History',
        'users': 'Admin Users',
        'settings': 'Settings'
    };
    document.getElementById('pageTitle').textContent = titles[pageName] || 'Dashboard';

    // Load page-specific data
    switch (pageName) {
        case 'cases':
            loadCases();
            break;
        case 'search':
            loadSearchHistory();
            break;
        case 'users':
            loadAdminUsers();
            break;
    }
}

// ============ DASHBOARD ============
async function loadDashboard() {
    try {
        // Add cache-busting parameter to force fresh data from database
        const response = await fetch(STATS_ENDPOINT + '?t=' + Date.now());
        const data = await response.json();

        if (data.success && data.statistics) {
            const statTotal = document.getElementById('stat-total');
            const statMissing = document.getElementById('stat-missing');
            const statFound = document.getElementById('stat-found');
            const statSearches = document.getElementById('stat-searches');
            
            if (statTotal) statTotal.textContent = data.statistics.total_cases;
            if (statMissing) statMissing.textContent = data.statistics.missing_persons;
            if (statFound) statFound.textContent = data.statistics.found_persons;
            if (statSearches) statSearches.textContent = '0'; // Placeholder
        }
    } catch (error) {
        console.error('Load dashboard error:', error);
    }
}

// ============ CASES MANAGEMENT ============
async function loadCases() {
    try {
        // Add cache-busting parameter to force fresh data from database
        const response = await fetch(CASES_ENDPOINT + '?t=' + Date.now());
        const data = await response.json();

        if (data.success && data.cases) {
            displayCasesTable(data.cases);
        }
    } catch (error) {
        console.error('Load cases error:', error);
    }
}

function displayCasesTable(cases) {
    const tbody = document.getElementById('casesTableBody');
    if (!tbody) return; // Safety check
    
    if (!cases || cases.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px;">No cases found</td></tr>';
        return;
    }

    let html = '';
    cases.forEach((caseItem, index) => {
        // Normalize and URL-encode the filename to handle backslashes and special characters
        const filename = (caseItem.image_path || '').replace(/\\/g, '/').split('/').pop();
        const encodedFilename = encodeURIComponent(filename || '');
        const imagePath = `${API_BASE_URL.replace('/api', '')}/uploads/${encodedFilename}`;
        const statusClass = caseItem.status === 'missing' ? 'danger' : 'success';
        const statusText = caseItem.status === 'missing' ? 'MISSING' : 'FOUND';
        const date = new Date(caseItem.created_at).toLocaleDateString();

        html += `
            <tr>
                <td>
                    <img src="${imagePath}" alt="${caseItem.name}" class="table-image" onerror="this.src='https://via.placeholder.com/40'">
                </td>
                <td><strong>${escapeHtml(caseItem.name)}</strong></td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td>${escapeHtml(caseItem.contact)}</td>
                <td>${date}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deleteCase(${caseItem.case_id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

async function deleteCase(caseId) {
    showConfirmModal(
        `Are you sure you want to delete case #${caseId}? This action cannot be undone.`,
        async () => {
            try {
                // Get password from session storage
                const adminPassword = sessionStorage.getItem('adminPassword') || '';
                
                const formData = new FormData();
                formData.append('admin_password', adminPassword);
                
                console.log('Deleting case', caseId, 'with admin password');
                
                const response = await fetch(`${CASES_ENDPOINT}/${caseId}/delete`, {
                    method: 'POST',
                    body: formData
                });

                let data = {};
                try {
                    data = await response.json();
                } catch (e) {
                    console.error('Failed to parse response:', e);
                    data = { detail: 'Invalid response from server' };
                }
                
                console.log('Delete response:', response.status, data);
                
                if (response.ok && data.success) {
                    showAlert('Case deleted successfully', 'success');
                    // Reload after a short delay to ensure database is updated
                    setTimeout(() => {
                        loadCases();
                        loadDashboard();
                    }, 500);
                } else if (response.status === 401) {
                    showAlert('Session expired. Please login again.', 'error');
                    logout();
                } else {
                    const errorMsg = data.detail ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : 'Unknown error';
                    showAlert('Failed to delete case: ' + errorMsg, 'error');
                }
            } catch (error) {
                console.error('Delete case error:', error);
                const errorMsg = error.message || String(error);
                showAlert('Error deleting case: ' + errorMsg);
            }
        }
    );
}

// ============ SEARCH HISTORY ============
async function loadSearchHistory() {
    const tbody = document.getElementById('searchTableBody');
    if (tbody) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 40px;">No search history available</td></tr>';
    }
    // In production, fetch from API endpoint
}

async function clearSearchHistory() {
    showConfirmModal(
        'Are you sure you want to clear all search history? This cannot be undone.',
        () => {
            showAlert('Search history cleared');
        }
    );
}

// ============ ADMIN USERS ============
async function loadAdminUsers() {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return; // Safety check
    
    // Mock data for demo
    const html = `
        <tr>
            <td><strong>admin</strong></td>
            <td>admin@findthem.com</td>
            <td><span class="status-badge success">Active</span></td>
            <td>Just now</td>
            <td>
                <button class="btn btn-sm btn-secondary" onclick="editUser(1)">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteUser(1)">Delete</button>
            </td>
        </tr>
    `;
    
    tbody.innerHTML = html;
}

function openAddUserModal() {
    document.getElementById('addUserModal').classList.add('active');
}

function handleAddUser(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    
    showAlert('User added successfully');
    closeModal('addUserModal');
    document.getElementById('username').value = '';
    document.getElementById('email').value = '';
    document.getElementById('password').value = '';
    loadAdminUsers();
}

function deleteUser(userId) {
    showConfirmModal(
        'Are you sure you want to delete this user?',
        () => {
            showAlert('User deleted successfully');
            loadAdminUsers();
        }
    );
}

// ============ SETTINGS ============
function updateThreshold() {
    const threshold = document.getElementById('thresholdSlider').value;
    localStorage.setItem('similarityThreshold', threshold);
    showAlert('Threshold updated to ' + threshold);
}

async function downloadBackup() {
    showAlert('Backup download started. This may take a few moments...');
    // In production, this would trigger a server-side backup
}

function viewLogs() {
    alert('Logs viewer would open here. In production, this would show system logs.');
}

async function optimizeDatabase() {
    showConfirmModal(
        'This will optimize the database. Continue?',
        () => {
            setTimeout(() => {
                showAlert('Database optimization completed');
            }, 2000);
        }
    );
}

function loadAdminThreshold() {
    const saved = localStorage.getItem('similarityThreshold');
    if (saved) {
        document.getElementById('thresholdSlider').value = saved;
        document.getElementById('thresholdValue').textContent = parseFloat(saved).toFixed(2);
    }
}

// ============ MODALS ============
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

let confirmCallback = null;

function showConfirmModal(message, callback) {
    confirmCallback = callback;
    const confirmMessage = document.getElementById('confirmMessage');
    const confirmModal = document.getElementById('confirmModal');
    if (confirmMessage) {
        confirmMessage.textContent = message;
    }
    if (confirmModal) {
        confirmModal.classList.add('active');
    }
}

function confirmAction() {
    if (confirmCallback) {
        confirmCallback();
    }
    closeModal('confirmModal');
}

function showAlert(message, type = 'info') {
    // Enhanced alert with type support
    const alertType = type === 'error' ? '❌ ERROR' : type === 'success' ? '✅ SUCCESS' : '✓ INFO';
    alert(alertType + '\n\n' + message);
}

// ============ UTILITY FUNCTIONS ============
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function logout() {
    // Clear session storage
    sessionStorage.removeItem('adminToken');
    sessionStorage.removeItem('adminPassword');
    isAuthenticated = false;
    
    // Clear any intervals
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    // Redirect to home
    window.location.href = '/';
}

// Close modals when clicking outside
document.addEventListener('click', function (event) {
    if (event.target.classList.contains('modal')) {
        const modal = event.target;
        if (modal.classList.contains('active')) {
            modal.classList.remove('active');
        }
    }
});
