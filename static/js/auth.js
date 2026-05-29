/**
 * Nexara Authentication - Client-side validation and API integration
 */

// ─────────────────────────────────────────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────────────────────────────────────────

const API_BASE = '/api/auth';
const REGISTER_ENDPOINT = `${API_BASE}/register/`;
const LOGIN_ENDPOINT = `${API_BASE}/login/`;

// ─────────────────────────────────────────────────────────────────────────────
// Validation Functions
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Validate email format
 */
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Validate password strength
 */
function isValidPassword(password) {
    return password.length >= 8;
}

/**
 * Validate full name
 */
function isValidFullName(fullName) {
    return fullName.trim().length > 0 && fullName.trim().split(' ').length >= 1;
}

/**
 * Clear all error messages
 */
function clearErrors(formType = 'register') {
    if (formType === 'register') {
        document.getElementById('fullNameError').textContent = '';
        document.getElementById('emailError').textContent = '';
        document.getElementById('passwordError').textContent = '';
        document.getElementById('confirmPasswordError').textContent = '';
        document.getElementById('errorMessage').classList.remove('show');
    } else {
        document.getElementById('loginEmailError').textContent = '';
        document.getElementById('loginPasswordError').textContent = '';
        document.getElementById('loginErrorMessage').classList.remove('show');
    }
}

/**
 * Show error message for specific field
 */
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (field) {
        field.textContent = message;
        field.classList.add('show');
    }
}

/**
 * Show general error message
 */
function showGeneralError(message, formType = 'register') {
    const errorBox = formType === 'register' 
        ? document.getElementById('errorMessage')
        : document.getElementById('loginErrorMessage');
    if (errorBox) {
        errorBox.textContent = message;
        errorBox.classList.add('show');
    }
}

/**
 * Show success message
 */
function showSuccessMessage(message, formType = 'register') {
    const successBox = formType === 'register'
        ? document.getElementById('successMessage')
        : document.getElementById('loginSuccessMessage');
    if (successBox) {
        successBox.textContent = message;
        successBox.classList.add('show');
    }
}

/**
 * Disable/Enable submit button
 */
function setButtonLoading(isLoading, formType = 'register') {
    const btn = formType === 'register' 
        ? document.getElementById('submitBtn')
        : document.getElementById('loginSubmitBtn');
    const spinner = formType === 'register'
        ? document.getElementById('loadingSpinner')
        : document.getElementById('loginLoadingSpinner');
    const text = formType === 'register'
        ? document.getElementById('buttonText')
        : document.getElementById('loginButtonText');

    if (btn) {
        btn.disabled = isLoading;
        if (isLoading) {
            spinner.style.display = 'inline-block';
            text.style.display = 'none';
        } else {
            spinner.style.display = 'none';
            text.style.display = 'inline-block';
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Registration Handler
// ─────────────────────────────────────────────────────────────────────────────

async function handleRegister(event) {
    event.preventDefault();
    clearErrors('register');

    // Get form values
    const fullName = document.getElementById('fullName').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    // Client-side validation
    let hasError = false;

    if (!isValidFullName(fullName)) {
        showFieldError('fullNameError', 'Please enter your full name');
        hasError = true;
    }

    if (!isValidEmail(email)) {
        showFieldError('emailError', 'Please enter a valid email address');
        hasError = true;
    }

    if (!isValidPassword(password)) {
        showFieldError('passwordError', 'Password must be at least 8 characters');
        hasError = true;
    }

    if (password !== confirmPassword) {
        showFieldError('confirmPasswordError', 'Passwords do not match');
        hasError = true;
    }

    if (hasError) return;

    // Server-side registration
    setButtonLoading(true, 'register');

    try {
        const response = await fetch(REGISTER_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                full_name: fullName,
                email: email,
                password: password,
                confirm_password: confirmPassword,
            }),
        });

        const data = await response.json();

        if (response.ok) {
            showSuccessMessage('✓ Registration successful! Redirecting to login...', 'register');
            document.getElementById('registerForm').reset();
            
            // Redirect to login after 2 seconds
            setTimeout(() => {
                window.location.href = '{% url "auth-login-form" %}';
            }, 2000);
        } else {
            // Handle server-side validation errors
            if (data.email) {
                showFieldError('emailError', data.email[0] || 'This email is already registered');
            } else if (data.confirm_password) {
                showFieldError('confirmPasswordError', data.confirm_password[0]);
            } else if (data.password) {
                showFieldError('passwordError', data.password[0]);
            } else {
                const errorMsg = Object.values(data).flat().join(', ') || 'Registration failed. Please try again.';
                showGeneralError(errorMsg, 'register');
            }
        }
    } catch (error) {
        console.error('Registration error:', error);
        showGeneralError('An error occurred. Please check your connection and try again.', 'register');
    } finally {
        setButtonLoading(false, 'register');
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Login Handler
// ─────────────────────────────────────────────────────────────────────────────

async function handleLogin(event) {
    event.preventDefault();
    clearErrors('login');

    // Get form values
    const username = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    // Client-side validation
    let hasError = false;

    if (!isValidEmail(username)) {
        showFieldError('loginEmailError', 'Please enter a valid email address');
        hasError = true;
    }

    if (!password) {
        showFieldError('loginPasswordError', 'Please enter your password');
        hasError = true;
    }

    if (hasError) return;

    // Server-side login
    setButtonLoading(true, 'login');

    try {
        const response = await fetch(LOGIN_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                username: username,
                password: password,
            }),
        });

        const data = await response.json();

        if (response.ok) {
            showSuccessMessage('✓ Login successful! Redirecting...', 'login');
            
            // Store token in localStorage
            if (data.token) {
                localStorage.setItem('authToken', data.token);
            }

            // Redirect to dashboard after 2 seconds
            setTimeout(() => {
                window.location.href = '/dashboard/';
            }, 2000);
        } else {
            const errorMsg = data.error || 'Invalid email or password. Please try again.';
            showGeneralError(errorMsg, 'login');
        }
    } catch (error) {
        console.error('Login error:', error);
        showGeneralError('An error occurred. Please check your connection and try again.', 'login');
    } finally {
        setButtonLoading(false, 'login');
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Utility Functions
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Get CSRF token from cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Real-time email validation
 */
document.addEventListener('DOMContentLoaded', function() {
    const emailInput = document.getElementById('email');
    const loginEmailInput = document.getElementById('loginEmail');

    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            if (this.value && !isValidEmail(this.value)) {
                showFieldError('emailError', 'Please enter a valid email address');
            } else {
                document.getElementById('emailError').textContent = '';
                document.getElementById('emailError').classList.remove('show');
            }
        });
    }

    if (loginEmailInput) {
        loginEmailInput.addEventListener('blur', function() {
            if (this.value && !isValidEmail(this.value)) {
                showFieldError('loginEmailError', 'Please enter a valid email address');
            } else {
                document.getElementById('loginEmailError').textContent = '';
                document.getElementById('loginEmailError').classList.remove('show');
            }
        });
    }

    // Password match validation on confirm password blur
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const passwordInput = document.getElementById('password');

    if (confirmPasswordInput && passwordInput) {
        confirmPasswordInput.addEventListener('blur', function() {
            if (this.value && this.value !== passwordInput.value) {
                showFieldError('confirmPasswordError', 'Passwords do not match');
            } else {
                document.getElementById('confirmPasswordError').textContent = '';
                document.getElementById('confirmPasswordError').classList.remove('show');
            }
        });
    }
});
