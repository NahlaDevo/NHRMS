let deptChartInstance = null;
let statusChartInstance = null;
let hiringChartInstance = null;
let salaryChartInstance = null;

document.addEventListener("DOMContentLoaded", function () {
    if (!redirectIfNotLoggedIn()) return;
    document.getElementById("userDisplay").textContent = `Welcome, ${getUsername()}`;
    loadAnalytics();
});

async function loadAnalytics() {
    try {
        const data = await apiRequest("/analytics/dashboard");

        document.getElementById("totalEmployees").textContent = data.total_employees || 0;
        document.getElementById("totalDepartments").textContent = data.by_department
            ? Object.keys(data.by_department).length : 0;
        document.getElementById("activeEmployees").textContent = data.by_status?.Active || 0;
        document.getElementById("avgSalary").textContent = data.salary_stats
            ? `$${Math.round(data.salary_stats.avg).toLocaleString()}` : "$0";

        if (data.by_department && Object.keys(data.by_department).length > 0) {
            renderDeptChart(data.by_department);
        }
        if (data.by_status && Object.keys(data.by_status).length > 0) {
            renderStatusChart(data.by_status);
        }
        if (data.hiring_trends && Object.keys(data.hiring_trends).length > 0) {
            renderHiringChart(data.hiring_trends);
        }
        if (data.salary_stats && data.salary_stats.avg) {
            renderSalaryChart(data.salary_stats);
        }
    } catch (err) {
        console.error("Failed to load analytics:", err);
    }
}

function renderDeptChart(data) {
    const ctx = document.getElementById("deptChart").getContext("2d");
    if (deptChartInstance) deptChartInstance.destroy();
    const colors = ["#0d6efd", "#198754", "#ffc107", "#dc3545", "#0dcaf0", "#6610f2", "#fd7e14", "#20c997"];
    deptChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: "Employees",
                data: Object.values(data),
                backgroundColor: Object.keys(data).map((_, i) => colors[i % colors.length]),
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            }
        }
    });
}

function renderStatusChart(data) {
    const ctx = document.getElementById("statusChart").getContext("2d");
    if (statusChartInstance) statusChartInstance.destroy();
    const colors = { "Active": "#198754", "Inactive": "#ffc107", "Terminated": "#dc3545", "On Leave": "#0dcaf0" };
    statusChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: Object.keys(data).map(k => colors[k] || "#6c757d"),
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: "bottom" }
            }
        }
    });
}

function renderHiringChart(data) {
    const ctx = document.getElementById("hiringChart").getContext("2d");
    if (hiringChartInstance) hiringChartInstance.destroy();
    hiringChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: "Hires",
                data: Object.values(data),
                borderColor: "#0d6efd",
                backgroundColor: "rgba(13, 110, 253, 0.1)",
                fill: true,
                tension: 0.4,
                pointRadius: 4,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            }
        }
    });
}

function renderSalaryChart(data) {
    const ctx = document.getElementById("salaryChart").getContext("2d");
    if (salaryChartInstance) salaryChartInstance.destroy();
    salaryChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Average", "Median", "Min", "Max"],
            datasets: [{
                label: "Salary ($)",
                data: [data.avg, data.median, data.min, data.max],
                backgroundColor: ["#0d6efd", "#198754", "#ffc107", "#dc3545"],
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: v => "$" + v.toLocaleString() }
                }
            }
        }
    });
}
