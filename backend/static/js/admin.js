document.addEventListener("DOMContentLoaded", function () {
    if (!redirectIfNotLoggedIn()) return;

    if (!isAdmin()) {
        alert("Access denied. Admin privileges required.");
        window.location.href = "/static/pages/dashboard.html";
        return;
    }

    document.getElementById("userDisplay").textContent = `Admin: ${getUsername()}`;
    loadUsers();
});

async function loadUsers() {
    try {
        const data = await apiRequest("/admin/users");
        const tbody = document.getElementById("usersTableBody");
        if (data.users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-4">No users found</td></tr>`;
            return;
        }
        tbody.innerHTML = data.users.map(user => `
            <tr>
                <td><strong>${user.username}</strong></td>
                <td>${user.email}</td>
                <td><span class="badge bg-${user.role === 'admin' ? 'danger' : 'primary'}">${user.role}</span></td>
                <td><span class="badge bg-${user.is_active === 'True' ? 'success' : 'secondary'}">${user.is_active === 'True' ? 'Active' : 'Inactive'}</span></td>
                <td>${new Date(user.created_at).toLocaleDateString()}</td>
                <td>
                    <div class="dropdown">
                        <button class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">Actions</button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" onclick="makeAdmin('${user.username}')"><i class="bi bi-shield me-2"></i>Make Admin</a></li>
                            <li><a class="dropdown-item" href="#" onclick="makeEmployee('${user.username}')"><i class="bi bi-person me-2"></i>Make Employee</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="#" onclick="deactivateUser('${user.username}')"><i class="bi bi-person-x me-2"></i>Deactivate</a></li>
                        </ul>
                    </div>
                </td>
            </tr>
        `).join("");
    } catch (err) {
        document.getElementById("usersTableBody").innerHTML =
            `<tr><td colspan="6" class="text-center text-danger py-4">Failed to load users: ${err.message}</td></tr>`;
    }
}

async function makeAdmin(username) {
    try {
        await apiRequest(`/admin/users/${username}/role?role=admin`, "PUT");
        loadUsers();
    } catch (err) { alert(err.message); }
}

async function makeEmployee(username) {
    try {
        await apiRequest(`/admin/users/${username}/role?role=employee`, "PUT");
        loadUsers();
    } catch (err) { alert(err.message); }
}

async function deactivateUser(username) {
    if (!confirm(`Deactivate user "${username}"?`)) return;
    try {
        await apiRequest(`/admin/users/${username}`, "DELETE");
        loadUsers();
    } catch (err) { alert(err.message); }
}

async function loadAuditLogs() {
    document.getElementById("auditLogContent").textContent = "Loading...";
    try {
        const data = await apiRequest("/admin/audit");
        const logs = data.logs || [];
        document.getElementById("auditLogContent").textContent = logs.length
            ? logs.join("")
            : "No log entries found.";
    } catch (err) {
        document.getElementById("auditLogContent").textContent = "Failed to load logs: " + err.message;
    }
}

async function exportExcel() {
    const token = getToken();
    try {
        const response = await fetch(`${API_BASE}/admin/export`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) throw new Error("Export failed");
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `employee_records_${new Date().toISOString().slice(0,10)}.xlsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (err) {
        alert("Export failed: " + err.message);
    }
}

// Load audit logs when tab is shown
document.querySelector('[data-bs-target="#auditTab"]')?.addEventListener("shown.bs.tab", loadAuditLogs);
