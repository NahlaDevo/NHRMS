document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");

    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();
            const errorMsg = document.getElementById("errorMsg");

            try {
                const data = await apiRequest("/auth/login", "POST", { username, password });
                setAuth(data.access_token, data.username, data.role);
                window.location.href = data.role === "admin"
                    ? "/static/pages/dashboard.html"
                    : "/static/pages/dashboard.html";
            } catch (err) {
                errorMsg.textContent = err.message;
                errorMsg.classList.remove("d-none");
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const username = document.getElementById("username").value.trim();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;
            const confirmPassword = document.getElementById("confirmPassword").value;
            const errorMsg = document.getElementById("errorMsg");
            const successMsg = document.getElementById("successMsg");

            errorMsg.classList.add("d-none");
            successMsg.classList.add("d-none");

            if (password !== confirmPassword) {
                errorMsg.textContent = "Passwords do not match!";
                errorMsg.classList.remove("d-none");
                return;
            }

            try {
                const data = await apiRequest("/auth/register", "POST", { username, email, password });
                successMsg.textContent = "Registration successful! Redirecting to login...";
                successMsg.classList.remove("d-none");
                setTimeout(() => { window.location.href = "/static/pages/login.html"; }, 2000);
            } catch (err) {
                errorMsg.textContent = err.message;
                errorMsg.classList.remove("d-none");
            }
        });
    }
});
