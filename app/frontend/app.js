const state = {
  jobs: [],
  profiles: [],
  applications: [],
  selectedJobId: null,
  selectedProfileId: null,
};

const $ = (selector) => document.querySelector(selector);

function lines(value) {
  return value
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function showToast(message, isError = false) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.toggle("is-error", isError);
  toast.classList.add("is-visible");
  window.setTimeout(() => toast.classList.remove("is-visible"), 2800);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const payload = await response.json();
      detail = payload.detail || JSON.stringify(payload);
    } catch (_error) {
      detail = await response.text();
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function pretty(value) {
  return JSON.stringify(value, null, 2);
}

function formatJob(job) {
  return `${job.title} at ${job.company}`;
}

function profileLabel(profile) {
  const role = profile.target_roles[0] || "Profile";
  return `${role} #${profile.id}`;
}

function renderList(target, items, renderer, emptyText) {
  const element = $(target);
  element.innerHTML = "";

  if (!items.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = emptyText;
    element.appendChild(empty);
    return;
  }

  items.forEach((item) => element.appendChild(renderer(item)));
}

function renderSelect(selector, items, labeler, selectedId) {
  const select = $(selector);
  select.innerHTML = "";

  items.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = labeler(item);
    option.selected = item.id === selectedId;
    select.appendChild(option);
  });
}

function jobCard(job) {
  const card = document.createElement("article");
  card.className = "card";
  const requirements = (job.requirements || []).slice(0, 5);

  card.innerHTML = `
    <div class="card-title">
      <div>
        <h3>${escapeHtml(job.title)}</h3>
        <div class="meta">${escapeHtml(job.company)}${job.location ? ` · ${escapeHtml(job.location)}` : ""}</div>
      </div>
      <button class="secondary" type="button" data-select-job="${job.id}">Select</button>
    </div>
    <div class="meta">${escapeHtml(job.seniority || "Unspecified")} · ${escapeHtml(job.source || "manual")}</div>
    <div class="chips">${requirements.map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("")}</div>
  `;

  return card;
}

function profileCard(profile) {
  const card = document.createElement("article");
  card.className = "card";
  const skills = (profile.skills || []).slice(0, 8);

  card.innerHTML = `
    <div class="card-title">
      <div>
        <h3>${escapeHtml(profile.target_roles.join(", ") || "Profile #" + profile.id)}</h3>
        <div class="meta">${escapeHtml((profile.experience_summary || "").slice(0, 120))}</div>
      </div>
      <button class="secondary" type="button" data-select-profile="${profile.id}">Select</button>
    </div>
    <div class="chips">${skills.map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("")}</div>
  `;

  return card;
}

function applicationCard(application) {
  const job = state.jobs.find((item) => item.id === application.job_id);
  const card = document.createElement("article");
  card.className = "card";

  card.innerHTML = `
    <div class="card-title">
      <div>
        <h3>${escapeHtml(job ? formatJob(job) : "Job #" + application.job_id)}</h3>
        <div class="meta">${escapeHtml(application.status)}${application.next_action ? ` · ${escapeHtml(application.next_action)}` : ""}</div>
      </div>
    </div>
    <div class="meta">${escapeHtml(application.notes || "No notes")}</div>
  `;

  return card;
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function render() {
  $("#job-count").textContent = state.jobs.length;
  $("#profile-count").textContent = state.profiles.length;
  $("#application-count").textContent = state.applications.length;

  const selectedJob = state.jobs.find((job) => job.id === state.selectedJobId);
  $("#selected-job-label").textContent = selectedJob ? selectedJob.title : "None";

  renderList("#jobs-list", state.jobs, jobCard, "No jobs yet.");
  renderList("#dashboard-jobs", state.jobs.slice(-4).reverse(), jobCard, "No jobs yet.");
  renderList("#profiles-list", state.profiles, profileCard, "No profiles yet.");
  renderList("#applications-list", state.applications, applicationCard, "No applications yet.");
  renderList("#dashboard-applications", state.applications.slice(-4).reverse(), applicationCard, "No applications yet.");

  renderSelect("#analysis-profile", state.profiles, profileLabel, state.selectedProfileId);
  renderSelect("#context-profile", state.profiles, profileLabel, state.selectedProfileId);
  renderSelect("#analysis-job", state.jobs, formatJob, state.selectedJobId);
  renderSelect("#context-job", state.jobs, formatJob, state.selectedJobId);
  renderSelect("#application-job", state.jobs, formatJob, state.selectedJobId);
}

async function loadData() {
  const [jobs, profiles, applications] = await Promise.all([
    api("/jobs"),
    api("/profiles"),
    api("/applications"),
  ]);

  state.jobs = jobs;
  state.profiles = profiles;
  state.applications = applications;
  state.selectedJobId = state.selectedJobId || jobs[0]?.id || null;
  state.selectedProfileId = state.selectedProfileId || profiles[0]?.id || null;
  render();
}

function activateTab(name) {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.tab === name);
  });
  document.querySelectorAll(".panel").forEach((panel) => {
    panel.classList.toggle("is-active", panel.id === `${name}-panel`);
  });
}

function getSelectedIds(profileSelector = "#analysis-profile", jobSelector = "#analysis-job") {
  const profileId = Number($(profileSelector).value);
  const jobId = Number($(jobSelector).value);

  if (!profileId || !jobId) {
    throw new Error("Select a profile and job first.");
  }

  return { profile_id: profileId, job_id: jobId };
}

function bindNavigation() {
  document.querySelectorAll("[data-tab]").forEach((button) => {
    button.addEventListener("click", () => activateTab(button.dataset.tab));
  });

  document.querySelectorAll("[data-tab-target]").forEach((button) => {
    button.addEventListener("click", () => activateTab(button.dataset.tabTarget));
  });
}

function bindSelection() {
  document.body.addEventListener("click", (event) => {
    const jobButton = event.target.closest("[data-select-job]");
    const profileButton = event.target.closest("[data-select-profile]");

    if (jobButton) {
      state.selectedJobId = Number(jobButton.dataset.selectJob);
      render();
      showToast("Job selected");
    }

    if (profileButton) {
      state.selectedProfileId = Number(profileButton.dataset.selectProfile);
      render();
      showToast("Profile selected");
    }
  });
}

function bindForms() {
  $("#job-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const payload = {
      title: form.get("title"),
      company: form.get("company"),
      location: form.get("location") || null,
      source: form.get("source") || "manual",
      source_url: form.get("source_url") || null,
      seniority: form.get("seniority") || null,
      description: form.get("description") || null,
      requirements: lines(form.get("requirements") || ""),
    };

    try {
      const job = await api("/jobs", { method: "POST", body: JSON.stringify(payload) });
      state.selectedJobId = job.id;
      event.currentTarget.reset();
      await loadData();
      showToast("Job added");
    } catch (error) {
      showToast(error.message, true);
    }
  });

  $("#profile-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);

    try {
      let projects = [];

      if ((form.get("projects_json") || "").trim()) {
        projects = JSON.parse(form.get("projects_json"));
      }

      const payload = {
        target_roles: lines(form.get("target_roles") || ""),
        skills: lines(form.get("skills") || ""),
        experience_summary: form.get("experience_summary") || null,
        projects,
      };

      const profile = await api("/profiles", { method: "POST", body: JSON.stringify(payload) });
      state.selectedProfileId = profile.id;
      event.currentTarget.reset();
      await loadData();
      showToast("Profile added");
    } catch (error) {
      showToast(error.message, true);
    }
  });

  $("#application-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const payload = {
      job_id: Number(form.get("job_id")),
      status: form.get("status"),
      next_action: form.get("next_action") || null,
      notes: form.get("notes") || null,
    };

    try {
      await api("/applications", { method: "POST", body: JSON.stringify(payload) });
      event.currentTarget.reset();
      await loadData();
      showToast("Application added");
    } catch (error) {
      showToast(error.message, true);
    }
  });

  $("#import-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);

    try {
      const payload = {
        source_name: form.get("source_name") || "manual-bulk-import",
        jobs: JSON.parse(form.get("jobs_json") || "[]"),
      };
      const result = await api("/imports/jobs", { method: "POST", body: JSON.stringify(payload) });
      event.currentTarget.reset();
      await loadData();
      showToast(`Imported ${result.imported_count}, skipped ${result.skipped_count}`);
    } catch (error) {
      showToast(error.message, true);
    }
  });
}

function bindAnalysis() {
  $("#run-match").addEventListener("click", async () => {
    try {
      const result = await api("/analysis/match", {
        method: "POST",
        body: JSON.stringify(getSelectedIds()),
      });
      $("#match-result").textContent = pretty(result);
    } catch (error) {
      showToast(error.message, true);
    }
  });

  $("#run-cv").addEventListener("click", async () => {
    try {
      const result = await api("/analysis/cv-suggestions", {
        method: "POST",
        body: JSON.stringify(getSelectedIds()),
      });
      $("#cv-result").textContent = pretty(result);
    } catch (error) {
      showToast(error.message, true);
    }
  });

  $("#run-interview").addEventListener("click", async () => {
    try {
      const result = await api("/analysis/interview-prep", {
        method: "POST",
        body: JSON.stringify(getSelectedIds()),
      });
      $("#interview-result").textContent = pretty(result);
    } catch (error) {
      showToast(error.message, true);
    }
  });
}

function bindSearch() {
  $("#index-jobs").addEventListener("click", async () => {
    try {
      const result = await api("/semantic-search/jobs/index", { method: "POST", body: "{}" });
      $("#search-result").textContent = pretty(result);
      showToast("Jobs indexed");
    } catch (error) {
      showToast(error.message, true);
    }
  });

  $("#search-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);

    try {
      const result = await api("/semantic-search/jobs/search", {
        method: "POST",
        body: JSON.stringify({ query: form.get("query"), limit: 5 }),
      });
      $("#search-result").textContent = pretty(result);
    } catch (error) {
      showToast(error.message, true);
    }
  });

  $("#get-context").addEventListener("click", async () => {
    try {
      const selected = getSelectedIds("#context-profile", "#context-job");
      const result = await api("/semantic-search/profile-context", {
        method: "POST",
        body: JSON.stringify({ ...selected, limit: 5 }),
      });
      $("#context-result").textContent = pretty(result);
    } catch (error) {
      showToast(error.message, true);
    }
  });
}

function bindReload() {
  ["#refresh-data", "#reload-jobs", "#reload-profiles", "#reload-applications"].forEach((selector) => {
    $(selector).addEventListener("click", async () => {
      try {
        await loadData();
        showToast("Data refreshed");
      } catch (error) {
        showToast(error.message, true);
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  bindNavigation();
  bindSelection();
  bindForms();
  bindAnalysis();
  bindSearch();
  bindReload();

  try {
    await loadData();
  } catch (error) {
    showToast(error.message, true);
  }
});
