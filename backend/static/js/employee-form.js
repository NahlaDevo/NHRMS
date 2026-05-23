document.addEventListener("DOMContentLoaded", function () {
    if (!redirectIfNotLoggedIn()) return;
    document.getElementById("userDisplay").textContent = `Welcome, ${getUsername()}`;

    const urlParams = new URLSearchParams(window.location.search);
    const editId = urlParams.get("edit");

    if (editId) {
        document.getElementById("isEdit").value = "true";
        document.getElementById("editId").value = editId;
        document.getElementById("submitBtn").innerHTML = '<i class="bi bi-pencil me-2"></i>Update Record';
        loadEmployeeData(editId);
    }

    const form = document.getElementById("employeeForm");
    form.addEventListener("submit", handleSubmit);
});

async function loadEmployeeData(id) {
    try {
        const emp = await apiRequest(`/employees/${id}`);
        document.getElementById("employee_id").value = emp.employee_id;
        document.getElementById("employee_id").readOnly = true;
        document.getElementById("full_name").value = emp.full_name;
        document.getElementById("department").value = emp.department;
        document.getElementById("position").value = emp.position;
        document.getElementById("email").value = emp.email;
        document.getElementById("phone_number").value = emp.phone_number;
        document.getElementById("address").value = emp.address;
        document.getElementById("national_id").value = emp.national_id;
        document.getElementById("date_of_birth").value = emp.date_of_birth;
        document.getElementById("hiring_date").value = emp.hiring_date;
        document.getElementById("salary").value = emp.salary;
        document.getElementById("employment_status").value = emp.employment_status;
        document.getElementById("manager_name").value = emp.manager_name;
        document.getElementById("emergency_contact").value = emp.emergency_contact;
        document.getElementById("notes").value = emp.notes;
    } catch (err) {
        showError("Failed to load employee data: " + err.message);
    }
}

async function handleSubmit(e) {
    e.preventDefault();
    hideMessages();

    const isEdit = document.getElementById("isEdit").value === "true";
    const editId = document.getElementById("editId").value;
    const employeeId = document.getElementById("employee_id").value.trim();

    if (!employeeId) {
        showError("Employee ID is required");
        return;
    }

    const formData = {
        employee_id: employeeId,
        full_name: document.getElementById("full_name").value.trim(),
        department: document.getElementById("department").value,
        position: document.getElementById("position").value.trim(),
        email: document.getElementById("email").value.trim(),
        phone_number: document.getElementById("phone_number").value.trim(),
        address: document.getElementById("address").value.trim(),
        national_id: document.getElementById("national_id").value.trim(),
        date_of_birth: document.getElementById("date_of_birth").value,
        hiring_date: document.getElementById("hiring_date").value,
        salary: document.getElementById("salary").value,
        employment_status: document.getElementById("employment_status").value,
        manager_name: document.getElementById("manager_name").value.trim(),
        emergency_contact: document.getElementById("emergency_contact").value.trim(),
        notes: document.getElementById("notes").value.trim(),
    };

    try {
        if (isEdit) {
            const updateData = { ...formData };
            delete updateData.employee_id;
            await apiRequest(`/employees/${editId}`, "PUT", updateData);
            showSuccess("Record updated successfully!");
        } else {
            await apiRequest("/employees/", "POST", formData);
            showSuccess("Record created successfully!");
            document.getElementById("employeeForm").reset();
        }
    } catch (err) {
        showError(err.message);
    }
}

function showError(msg) {
    const el = document.getElementById("errorMsg");
    el.textContent = msg;
    el.classList.remove("d-none");
}

function showSuccess(msg) {
    const el = document.getElementById("successMsg");
    el.textContent = msg;
    el.classList.remove("d-none");
}

function hideMessages() {
    document.getElementById("errorMsg").classList.add("d-none");
    document.getElementById("successMsg").classList.add("d-none");
}
