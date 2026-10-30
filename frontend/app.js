const config = window.HIRELOOP_CONFIG || {};
const API = (config.apiBaseUrl || "").replace(/\/$/, "");
const authEnabled = Boolean(config.supabaseUrl && config.supabaseAnonKey);
let supabase = null;
let accessToken = null;
let profileId = localStorage.getItem("hireloop.profileId") || "";
const $ = (selector) => document.querySelector(selector);
if (authEnabled) {
    $("#authPanel").hidden = false;
    $("#appShell").hidden = true;
}

const escapeHtml = (value = "") => {
    const node = document.createElement("span");
    node.textContent = String(value ?? "");
    return node.innerHTML;
};

async function api(path, options = {}) {
    if (!API) throw new Error("Set apiBaseUrl in frontend/config.js");
    const headers = new Headers(options.headers || {});
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
    if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
    const response = await fetch(`${API}${path}`, { ...options, headers });
    if (!response.ok) {
        let message = `Request failed (${response.status})`;
        try { message = (await response.json()).detail || message; } catch {}
        if (response.status === 401 && authEnabled) {
            accessToken = null;
            showAuth();
            if (supabase) await supabase.auth.signOut();
        }
        throw new Error(message);
    }
    return response;
}

function showAuth() {
    $("#authPanel").hidden = authEnabled && !accessToken;
    $("#appShell").hidden = authEnabled && !accessToken;
    $("#signOutButton").hidden = !authEnabled || !accessToken;
}

function setPage(pageName) {
    document.querySelectorAll(".page").forEach((page) => page.classList.toggle("active", page.id === pageName));
    document.querySelectorAll(".nav-link").forEach((button) => button.classList.toggle("active", button.dataset.page === pageName));
    if (pageName === "tracker") loadTracker();
}

document.querySelectorAll(".nav-link").forEach((button) => {
    button.addEventListener("click", () => setPage(button.dataset.page));
});

async function uploadResume(file) {
    if (!file) return;
    const status = $("#status");
    const allowed = /\.(pdf|docx)$/i.test(file.name);
    if (!allowed) {
        status.textContent = "Choose a PDF or DOCX resume.";
        return;
    }
    status.textContent = "Reading your resume and finding jobs…";
    const form = new FormData();
    form.append("file", file);
    try {
        const response = await api("/upload", { method: "POST", body: form });
        const result = await response.json();
        profileId = result.profile_id;
        localStorage.setItem("hireloop.profileId", profileId);
        const profile = result.profile;
        const skills = (profile.skills || []).slice(0, 12);
        $("#profileSummary").hidden = false;
        $("#profileSummaryText").innerHTML = `<strong>Resume read</strong><span>${escapeHtml(skills.length ? skills.join(" · ") : "No common skills detected; you can still search by role.")}</span>`;
        status.textContent = "Profile saved privately to your account. Matches are ranked using resume evidence.";
        await loadJobs();
        setPage("jobs");
    } catch (error) {
        status.textContent = error.message;
    }
}

const uploadZone = $("#uploadZone");
uploadZone.addEventListener("click", () => $("#resumeFile").click());
uploadZone.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") $("#resumeFile").click();
});
uploadZone.addEventListener("dragover", (event) => { event.preventDefault(); uploadZone.classList.add("dragging"); });
uploadZone.addEventListener("dragleave", () => uploadZone.classList.remove("dragging"));
uploadZone.addEventListener("drop", (event) => {
    event.preventDefault();
    uploadZone.classList.remove("dragging");
    uploadResume(event.dataTransfer.files[0]);
});
$("#resumeFile").addEventListener("change", (event) => uploadResume(event.target.files[0]));

$("#deleteDataButton").addEventListener("click", async () => {
    if (!confirm("Delete your saved resume profile and all tracked applications? This cannot be undone.")) return;
    try {
        await api("/account/data", { method: "DELETE" });
        profileId = "";
        localStorage.removeItem("hireloop.profileId");
        $("#profileSummary").hidden = true;
        $("#status").textContent = "Your stored resume profile and application records were deleted.";
        await loadJobs();
    } catch (error) { $("#status").textContent = error.message; }
});

async function loadJobs() {
    const grid = $("#jobsGrid");
    const query = $("#jobQuery").value.trim();
    grid.innerHTML = '<p class="empty-state">Searching public job boards…</p>';
    $("#tailorResult").hidden = true;
    try {
        const response = await api("/jobs", {
            method: "POST",
            body: JSON.stringify({ query, ...(profileId ? { profile_id: profileId } : {}) }),
        });
        const { jobs } = await response.json();
        if (!jobs.length) {
            grid.innerHTML = '<p class="empty-state">No roles matched this search. Try a broader keyword or refresh in a moment.</p>';
            return;
        }
        grid.innerHTML = jobs.map((job) => {
            const score = Number.isFinite(job.match_score) ? `<span class="job-badge">${Math.round(job.match_score)}% match</span>` : '<span class="job-badge muted-badge">Upload a resume to match</span>';
            const reasons = job.match_reasons?.length ? `<p class="match-reasons">${escapeHtml(job.match_reasons.join(" · "))}</p>` : "";
            return `<article class="job-card">
                <div class="job-title">${escapeHtml(job.title)}</div>
                <div class="job-company">${escapeHtml(job.company)}</div>
                <div class="job-meta"><span>${escapeHtml(job.location || "Location not listed")}</span><span>·</span><span>${escapeHtml(job.source)}</span></div>
                ${score}${reasons}
                <div class="card-actions">
                    <button class="btn btn-secondary" data-action="tailor" data-job="${escapeHtml(job.id)}">Tailor & apply kit</button>
                    <button class="btn" data-action="save" data-job="${escapeHtml(job.id)}" data-score="${Number(job.match_score) || 0}">Save job</button>
                    <a class="job-link" href="${escapeHtml(job.url || "#")}" target="_blank" rel="noopener noreferrer">View posting ↗</a>
                </div>
            </article>`;
        }).join("");
    } catch (error) {
        grid.innerHTML = `<p class="empty-state">${escapeHtml(error.message)}</p>`;
    }
}

$("#searchJobsButton").addEventListener("click", loadJobs);
$("#jobQuery").addEventListener("keydown", (event) => { if (event.key === "Enter") loadJobs(); });

$("#jobsGrid").addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const jobId = button.dataset.job;
    if (!profileId) {
        $("#status").textContent = "Upload your resume before saving or tailoring a job.";
        setPage("home");
        return;
    }
    button.disabled = true;
    try {
        if (button.dataset.action === "save") {
            const article = button.closest(".job-card");
            const title = article.querySelector(".job-title").textContent;
            const company = article.querySelector(".job-company").textContent;
            const url = article.querySelector(".job-link").href;
            const job = (await (await api("/jobs")).json()).jobs.find((item) => item.id === jobId);
            await api("/tracker", { method: "POST", body: JSON.stringify({
                id: crypto.randomUUID(), profile_id: profileId, company, role: title, url,
                match_score: Number(button.dataset.score) || 0, status: "saved", resume_version: profileId,
            }) });
            button.textContent = "Saved";
        } else {
            const [tailoredResponse, kitResponse] = await Promise.all([
                api(`/tailor?profile_id=${encodeURIComponent(profileId)}&job_id=${encodeURIComponent(jobId)}`, { method: "POST" }),
                api(`/apply-kit/${encodeURIComponent(profileId)}/${encodeURIComponent(jobId)}`),
            ]);
            const tailored = await tailoredResponse.json();
            const kit = await kitResponse.json();
            const bullets = tailored.bullets.map((bullet) => `<li>${escapeHtml(bullet.text)} <small>Source: ${escapeHtml(bullet.source_ids.join(", "))}</small></li>`).join("");
            const verification = tailored.faithfulness;
            $("#tailorResult").hidden = false;
            $("#tailorResult").innerHTML = `<button class="close-result" id="closeResult" aria-label="Close">×</button>
                <h3>Apply kit · ${escapeHtml(kit.job_title || "Selected role")}</h3>
                <p class="verification ${verification?.overall_score === 1 ? "verified" : "review"}">${verification ? `${Math.round(verification.overall_score * 100)}% source supported · ${verification.supported_bullets}/${verification.total_bullets} bullets` : "Review every bullet before using this draft."}</p>
                <h4>Resume bullets</h4><ul>${bullets || "<li>No resume bullets were detected. Add a detailed resume for a useful draft.</li>"}</ul>
                <h4>Cover letter draft</h4><pre>${escapeHtml(kit.cover_letter || "Add an LLM_API_KEY to generate an AI cover letter, or update your resume bullets for the factual template.")}</pre>
                <div class="card-actions"><button class="btn btn-secondary" id="downloadResumeButton">Download resume draft</button><button class="btn btn-secondary" id="downloadLetterButton">Download cover letter</button></div>
                <p class="privacy-note">Review the wording and submit manually on the employer’s site. HireLoop never applies for you.</p>`;
            $("#closeResult").addEventListener("click", () => { $("#tailorResult").hidden = true; });
            const resumeText = [
                kit.job_title || "Tailored resume draft",
                "",
                ...(tailored.summary ? [tailored.summary, ""] : []),
                ...tailored.bullets.map((bullet) => `• ${bullet.text} [Sources: ${bullet.source_ids.join(", ")}]`),
            ].join("\n");
            $("#downloadResumeButton").addEventListener("click", () => downloadText("hireloop-resume-draft.txt", resumeText));
            $("#downloadLetterButton").addEventListener("click", () => downloadText("hireloop-cover-letter.txt", kit.cover_letter || ""));
            $("#tailorResult").scrollIntoView({ behavior: "smooth", block: "start" });
        }
    } catch (error) {
        alert(error.message);
    } finally {
        button.disabled = false;
    }
});

function downloadText(filename, text) {
    const url = URL.createObjectURL(new Blob([text], { type: "text/plain;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

const trackerStatuses = ["saved", "applied", "interview", "rejected", "offer", "archived"];
async function loadTracker() {
    const list = $("#trackerList");
    list.innerHTML = '<p class="empty-state">Loading applications…</p>';
    try {
        const { items } = await (await api("/tracker")).json();
        if (!items.length) {
            list.innerHTML = '<p class="empty-state">No saved jobs yet. Save a match to start your tracker.</p>';
            return;
        }
        list.innerHTML = items.map((item) => `<article class="tracker-item" data-id="${escapeHtml(item.id)}">
            <div class="tracker-info"><h3>${escapeHtml(item.role)} at ${escapeHtml(item.company)}</h3><p>${Math.round(item.match_score)}% match · Saved ${new Date(item.date).toLocaleDateString()}</p>
            ${item.url ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">View job posting ↗</a>` : ""}</div>
            <select aria-label="Application status" data-id="${escapeHtml(item.id)}">${trackerStatuses.map((status) => `<option value="${status}" ${status === item.status ? "selected" : ""}>${status[0].toUpperCase() + status.slice(1)}</option>`).join("")}</select>
        </article>`).join("");
    } catch (error) {
        list.innerHTML = `<p class="empty-state">${escapeHtml(error.message)}</p>`;
    }
}

$("#trackerList").addEventListener("change", async (event) => {
    const select = event.target.closest("select[data-id]");
    if (!select) return;
    const id = select.dataset.id;
    try {
        const item = await (await api(`/tracker/${encodeURIComponent(id)}`)).json();
        item.status = select.value;
        await api(`/tracker/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify(item) });
    } catch (error) { alert(error.message); loadTracker(); }
});

$("#exportTrackerButton").addEventListener("click", async () => {
    try {
        const response = await api("/tracker/export?format=csv");
        const url = URL.createObjectURL(await response.blob());
        const link = document.createElement("a");
        link.href = url;
        link.download = "hireloop-applications.csv";
        link.click();
        URL.revokeObjectURL(url);
    } catch (error) { alert(error.message); }
});

if (authEnabled) {
    try {
        const { createClient } = await import("https://esm.sh/@supabase/supabase-js@2");
        supabase = createClient(config.supabaseUrl, config.supabaseAnonKey);
        const { data } = await supabase.auth.getSession();
        accessToken = data.session?.access_token || null;
        supabase.auth.onAuthStateChange((_event, session) => {
            accessToken = session?.access_token || null;
            showAuth();
            if (accessToken) loadJobs();
        });
    } catch {
        $("#authStatus").textContent = "Could not connect to Supabase Auth. Check the frontend configuration.";
    }
    $("#authForm").addEventListener("submit", async (event) => {
        event.preventDefault();
        const email = $("#authEmail").value;
        const password = $("#authPassword").value;
        $("#authStatus").textContent = "Signing in…";
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        $("#authStatus").textContent = error?.message || "Signed in.";
    });
    $("#signupButton").addEventListener("click", async () => {
        const email = $("#authEmail").value;
        const password = $("#authPassword").value;
        if (!email || password.length < 8) {
            $("#authStatus").textContent = "Enter an email and a password with at least 8 characters.";
            return;
        }
        $("#authStatus").textContent = "Creating account…";
        const { data, error } = await supabase.auth.signUp({ email, password });
        $("#authStatus").textContent = error?.message || (data.session ? "Account created." : "Check your email to confirm your account, then sign in.");
    });
    $("#googleSignInButton").addEventListener("click", async () => {
        const { error } = await supabase.auth.signInWithOAuth({
            provider: "google",
            options: { redirectTo: `${location.origin}${location.pathname}` },
        });
        if (error) $("#authStatus").textContent = error.message;
    });
    $("#signOutButton").addEventListener("click", async () => { await supabase.auth.signOut(); });
} else {
    $("#authPanel").hidden = true;
    $("#appShell").hidden = false;
    if (location.protocol !== "file:") {
        $("#status").textContent = "Local mode. Configure Supabase Auth before accepting real resumes.";
    }
}

showAuth();
if (!authEnabled || accessToken) {
    if (profileId) {
        api(`/profile/${encodeURIComponent(profileId)}`).then(async (response) => {
            const profile = await response.json();
            const skills = profile.skills || [];
            $("#profileSummary").hidden = false;
            $("#profileSummaryText").innerHTML = `<strong>Resume on file</strong><span>${escapeHtml(skills.join(" · ") || "Upload a new resume to see matching skills")}</span>`;
        }).catch(() => {
            profileId = "";
            localStorage.removeItem("hireloop.profileId");
            loadJobs();
        });
    }
    loadJobs();
}
