document.addEventListener("DOMContentLoaded", function() {
    const toggleFormButton = document.getElementById("toggle-form");
    const authForm = document.getElementById("auth-form");
    const formTitle = document.getElementById("form-title");
    const passwordInput = document.getElementById("password");
    const togglePassword = document.getElementById("toggle-password");
    const eyeIcon = document.getElementById("eye-icon");

    toggleFormButton.addEventListener("click", function() {
        if (formTitle.textContent === "SignUp") {
            formTitle.textContent = "Login";
            toggleFormButton.textContent = "SignUp";
            authForm.reset(); // Reset the form fields
        } else {
            formTitle.textContent = "SignUp";
            toggleFormButton.textContent = "Login";
            authForm.reset(); // Reset the form fields
        }
    });

    togglePassword.addEventListener("click", function() {
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
        passwordInput.setAttribute("type", type);
        eyeIcon.classList.toggle("fa-eye");
        eyeIcon.classList.toggle("fa-eye-slash");
    });
});
