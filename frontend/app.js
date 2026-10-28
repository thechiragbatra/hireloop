const API_URL = 'https://hireloop-2.onrender.com/api/v1';

function showPage(pageName) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(b => b.classList.remove('active'));
    document.getElementById(pageName).classList.add('active');
    document.querySelector(`.nav-link[data-page="${pageName}"]`).classList.add('active');
}

document.querySelectorAll('.nav-link').forEach(btn => {
    btn.addEventListener('click', () => showPage(btn.dataset.page));
});

// Upload
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('resumeFile');
const status = document.getElementById('status');

uploadZone.addEventListener('click', () => fileInput.click());
uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.style.borderColor = 'var(--accent)'; });
uploadZone.addEventListener('dragleave', () => { uploadZone.style.borderColor = 'var(--border)'; });
uploadZone.addEventListener('drop', e => {
    e.preventDefault();
    uploadZone.style.borderColor = 'var(--border)';
    if (e.dataTransfer.files.length) uploadResume(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', e => {
    if (e.target.files.length) uploadResume(e.target.files[0]);
});

async function uploadResume(file) {
    const formData = new FormData();
    formData.append('file', file);
    status.textContent = 'Processing your resume...';
    try {
        const res = await fetch(`${API_URL}/upload`, { method: 'POST', body: formData });
        if (res.ok) {
            const data = await res.json();
            status.textContent = 'Resume uploaded. Finding jobs...';
            await loadJobs();
            showPage('jobs');
        } else {
            status.textContent = 'Upload failed';
        }
    } catch (e) {
        status.textContent = 'Error: ' + e.message;
    }
}

async function loadJobs() {
    const grid = document.getElementById('jobsGrid');
    grid.innerHTML = '<p style="padding:24px;color:var(--text-secondary);">Loading...</p>';
    try {
        const res = await fetch(`${API_URL}/jobs`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: '{}' });
        const data = await res.json();
        if (data.jobs && data.jobs.length) {
            grid.innerHTML = data.jobs.slice(0, 30).map(job => `
                <div class="job-card">
                    <div class="job-title">${escapeHtml(job.title)}</div>
                    <div class="job-company">${escapeHtml(job.company)}</div>
                    <div class="job-meta">
                        <span>${escapeHtml(job.location || 'Remote')}</span>
                        <span>•</span>
                        <span>${job.source}</span>
                    </div>
                    <span class="job-badge">${job.match_score}% match</span>
                </div>
            `).join('');
        } else {
            grid.innerHTML = '<p style="padding:24px;color:var(--text-secondary);">No jobs found</p>';
        }
    } catch (e) {
        grid.innerHTML = '<p style="padding:24px;color:var(--text-secondary);">Error loading jobs</p>';
    }
}

async function exportTracker() {
    try {
        const res = await fetch(`${API_URL}/tracker/export?format=csv`);
        if (res.ok) {
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'applications.csv';
            a.click();
        }
    } catch (e) {}
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

loadJobs();
