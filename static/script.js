document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("register-form");
    const loginForm = document.getElementById("login-form");

    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const data = {
                name: document.getElementById("name").value,
                email: document.getElementById("email").value,
                bioid: document.getElementById("bioid").value,
                password: document.getElementById("password").value,
            };

            const response = await fetch("/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });

            const result = await response.json();
            document.getElementById("message").textContent = result.message || result.error;
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const data = {
                email: document.getElementById("email").value,
                password: document.getElementById("password").value,
            };

            const response = await fetch("/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
            });

            const result = await response.json();
            document.getElementById("message").textContent = result.message || result.error;

            if (response.ok) {
                window.location.href = "/dashboard.html";
            }
        });
    }
});
