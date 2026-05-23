let deleteEmployeeId = null;

document.addEventListener("DOMContentLoaded", function () {
    if (!redirectIfNotLoggedIn()) return;

    document.getElementById("userDisplay").textContent = `Welcome, ${getUsername()}`;

    if (isAdmin()) {
        document.getElementById("adminLink").style.display = "inline-block";
        document.getElementById("adminLink").href = "/static/pages/admin.html";
    }

    loadDashboardStats();
    loadEmployees();
    loadDepartmentFilter();

    document.getElementById("searchInput").addEventListener("input", debounce(loadEmployees, 300));
    document.getElementById("deptFilter").addEventListener("change", loadEmployees);
    document.getElementById("statusFilter").addEventListener("change", loadEmployees);

    document.getElementById("confirmDeleteBtn").addEventListener("click", async function () {
        if (deleteEmployeeId) {
            try {
                await apiRequest(`/employees/${deleteEmployeeId}`, "DELETE");
                bootstrap.Modal.getInstance(document.getElementById("deleteModal")).hide();
                loadEmployees();
                loadDashboardStats();
            } catch (err) {
                alert("Delete failed: " + err.message);
            }
        }
    });
});

function debounce(func, wait) {
    let timeout;
    return function () {
        clearTimeout(timeout);
        timeout = setTimeout(func, wait);
    };
}

async function loadDashboardStats() {
    try {
        const data = await apiRequest("/analytics/dashboard");
        document.getElementById("totalEmployees").textContent = data.total_employees || 0;
        document.getElementById("totalDepartments").textContent = data.by_department
            ? Object.keys(data.by_department).length : 0;
        document.getElementById("activeEmployees").textContent = data.by_status?.Active || 0;
        document.getElementById("avgSalary").textContent = data.salary_stats
            ? `$${Math.round(data.salary_stats.avg).toLocaleString()}` : "$0";
    } catch (err) {
        console.error("Failed to load stats:", err);
    }
}

async function loadEmployees() {
    const search = document.getElementById("searchInput").value.trim();
    const department = document.getElementById("deptFilter").value;
    const status = document.getElementById("statusFilter").value;

    let url = "/employees/?";
    if (search) url += `search=${encodeURIComponent(search)}&`;
    if (department) url += `department=${encodeURIComponent(department)}&`;
    if (status) url += `status=${encodeURIComponent(status)}&`;

    try {
        const data = await apiRequest(url);
        const tbody = document.getElementById("employeeTableBody");
        document.getElementById("recordCount").textContent = `${data.total} records`;

        if (data.total === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-4">No records found</td></tr>`;
            return;
        }

        tbody.innerHTML = data.employees.map(emp => `
            <tr>
                <td><strong>${emp.employee_id}</strong></td>
                <td>${emp.full_name}</td>
                <td>${emp.department}</td>
                <td>${emp.position}</td>
                <td>${emp.email}</td>
                <td><span class="badge bg-${emp.employment_status === 'Active' ? 'success' : emp.employment_status === 'Terminated' ? 'danger' : 'warning'}">${emp.employment_status}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editEmployee('${emp.employee_id}')" title="Edit">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="confirmDelete('${emp.employee_id}', '${emp.full_name}')" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `).join("");
    } catch (err) {
        console.error("Failed to load employees:", err);
    }
}

async function loadDepartmentFilter() {
    try {
        const data = await apiRequest("/analytics/departments");
        const deptFilter = document.getElementById("deptFilter");
        Object.keys(data).forEach(dept => {
            const opt = document.createElement("option");
            opt.value = dept;
            opt.textContent = dept;
            deptFilter.appendChild(opt);
        });
    } catch (err) {
        console.error("Failed to load departments:", err);
    }
}

function editEmployee(id) {
    window.location.href = `/static/pages/employee-form.html?edit=${id}`;
}

function confirmDelete(id, name) {
    deleteEmployeeId = id;
    document.getElementById("deleteEmployeeName").textContent = name;
    new bootstrap.Modal(document.getElementById("deleteModal")).show();
}
