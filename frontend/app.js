const API_URL = 'https://your-backend-url.onrender.com/api/v1'; // Update this

function showPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    // Remove active from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    // Show selected page
    document.getElementById(pageName).classList.add('active');
    // Activate selected nav button
    event.target.classList.add('active');
}

// Upload functionality
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('resumeFile');
const uploadStatus = document.getElementById('uploadStatus');
const profileDisplay = document.getElementById('profileDisplay');

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.background = '#e8eaff';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.background = '#f8f9ff';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.background = '#f8f9ff';
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    uploadStatus.innerHTML = '<p>⏳ Uploading and parsing...</p>';
    uploadStatus.className = '';
    
    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            uploadStatus.innerHTML = '<p>✅ Resume uploaded successfully!</p>';
            uploadStatus.className = 'success';
            
            profileDisplay.classList.remove('hidden');
            profileDisplay.innerHTML = `
                <h3 style="margin-top: 20px; color: #333;">Profile Extracted</h3>
                <p><strong>Skills:</strong> ${data.profile.skills.join(', ') || 'None detected'}</p>
                <p><strong>Email:</strong> ${data.profile.contact?.email || 'Not found'}</p>
                <p><strong>LinkedIn:</strong> ${data.profile.contact?.linkedin || 'Not found'}</p>
            `;
        } else {
            uploadStatus.innerHTML = '<p>❌ Upload failed</p>';
            uploadStatus.className = 'error';
        }
    } catch (error) {
        uploadStatus.innerHTML = '<p>❌ Error: ' + error.message + '</p>';
        uploadStatus.className = 'error';
    }
}

// Jobs functionality
async function fetchJobs() {
    const role = document.getElementById('jobRole').value;
    const location = document.getElementById('jobLocation').value;
    const jobsList = document.getElementById('jobsList');
    
    jobsList.innerHTML = '<p>⏳ Searching jobs...</p>';
    
    try {
        const response = await fetch(`${API_URL}/jobs`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ role, location, limit: 10 })
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.jobs && data.jobs.length > 0) {
                jobsList.innerHTML = data.jobs.map(job => `
                    <div class="job-card">
                        <h3>${job.title}</h3>
                        <p class="company">${job.company}</p>
                        <p>📍 ${job.location || 'Remote'}</p>
                        <span class="match-score">Match: ${job.match_score || 85}%</span>
                        <button onclick="selectJob('${job.id}')">Tailor Resume</button>
                    </div>
                `).join('');
            } else {
                jobsList.innerHTML = '<p class="empty">No jobs found. Try different filters.</p>';
            }
        } else {
            jobsList.innerHTML = '<p class="error">Failed to fetch jobs</p>';
        }
    } catch (error) {
        jobsList.innerHTML = '<p class="error">Error: ' + error.message + '</p>';
    }
}

function selectJob(jobId) {
    showPage('tailor');
    document.querySelectorAll('.nav-btn').forEach((btn, idx) => {
        btn.classList.toggle('active', idx === 2);
    });
    document.getElementById('tailorContent').innerHTML = `
        <p>✅ Job selected. Tailoring in progress...</p>
        <p style="color: #666; margin-top: 10px;">This will use only facts from your profile with faithfulness checking.</p>
    `;
}

// Tracker functionality
async function exportTracker() {
    try {
        const response = await fetch(`${API_URL}/tracker/export?format=csv`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'tracker.csv';
            a.click();
        }
    } catch (error) {
        alert('Export failed: ' + error.message);
    }
}

// Load tracker on page load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch(`${API_URL}/tracker`);
        if (response.ok) {
            const data = await response.json();
            const trackerList = document.getElementById('trackerList');
            if (data.items && data.items.length > 0) {
                trackerList.innerHTML = data.items.map(item => `
                    <div class="tracker-card">
                        <h3>${item.role} at ${item.company}</h3>
                        <p>Status: <strong>${item.status}</strong></p>
                        <p>Match Score: ${item.match_score}%</p>
                    </div>
                `).join('');
            } else {
                trackerList.innerHTML = '<p class="empty">No applications yet. Start by uploading your resume and finding jobs!</p>';
            }
        }
    } catch (error) {
        document.getElementById('trackerList').innerHTML = '<p class="empty">Connect to backend to see tracker</p>';
    }
});
