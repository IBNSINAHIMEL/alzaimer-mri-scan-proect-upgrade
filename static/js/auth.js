// ====================================================================
// FUNCTIONS
// ====================================================================

// Login form handling
function initializeLoginForm() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const loadingSpinner = document.getElementById('loadingSpinner');
        const submitButton = this.querySelector('button[type="submit"]');
        
        // Show loading
        submitButton.disabled = true;
        // Use an 'auth-card' or similar to hide the form if a spinner replaces it, or just use the spinner inside the button
        if (loadingSpinner) loadingSpinner.classList.remove('hidden'); 
        
        try {
            const formData = new FormData(this);
            
            const response = await fetch('/login', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                if (loadingSpinner) {
                    loadingSpinner.innerHTML = `
                        <div class="text-green-500 text-4xl mb-2">✅</div>
                        <p class="text-green-600 font-semibold">Login Successful!</p>
                        <p class="text-gray-600">Redirecting to dashboard...</p>
                    `;
                }
                
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1500);
            } else {
                throw new Error(result.message);
            }

        } catch (error) {
            // Hide loading and re-enable button on error
            if (loadingSpinner) loadingSpinner.classList.add('hidden'); 
            submitButton.disabled = false;
            
            // Show elegant error message
            showErrorToast('Login failed: ' + error.message);
        }
    });
}

// Error toast notification function (replaces simple alert for better UX)
function showErrorToast(message) {
    const toast = document.createElement('div');
    // NOTE: This uses Tailwind CSS classes for styling (fixed position, red background, animation)
    toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg transform translate-x-full transition-transform duration-300 z-50';
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-exclamation-triangle mr-2"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300); // Wait for the transition out
    }, 5000);
}

// Function to handle the registration form submission
function initializeRegisterForm() {
    const registerForm = document.getElementById('registerForm');
    if (!registerForm) return;

    const loadingSpinner = document.getElementById('loadingSpinner');
    const successMessage = document.getElementById('successMessage');

    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Basic validation
        const password = registerForm.password.value;
        const confirmPassword = registerForm.confirm_password.value;

        if (password !== confirmPassword) {
            showErrorToast('Passwords do not match!');
            return;
        }

        if (password.length < 6) {
            showErrorToast('Password must be at least 6 characters long!');
            return;
        }

        // Show loading (Assuming loadingSpinner and successMessage exist in the HTML)
        registerForm.classList.add('hidden');
        if (loadingSpinner) loadingSpinner.classList.remove('hidden');

        try {
            const formData = new FormData(registerForm);
            
            const response = await fetch('/register', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                // Show success message
                if (loadingSpinner) loadingSpinner.classList.add('hidden');
                if (successMessage) successMessage.classList.remove('hidden');
                
                // Redirect to login after 2 seconds
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                throw new Error(result.message);
            }

        } catch (error) {
            if (loadingSpinner) loadingSpinner.classList.add('hidden');
            registerForm.classList.remove('hidden');
            showErrorToast('Registration failed: ' + error.message);
        }
    });
}

// Function to handle input animations and real-time validation
function initializeInputEffects(formElement) {
    if (!formElement) return;

    // Input animations (Focus/Blur)
    formElement.querySelectorAll('input').forEach(input => {
        input.addEventListener('focus', function() {
            // Assuming the input is wrapped in a container that needs the ring effect
            this.parentElement.classList.add('ring-2', 'ring-blue-200');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('ring-2', 'ring-blue-200');
        });
    });

    // Real-time validation (for required fields)
    formElement.querySelectorAll('input, select').forEach(input => {
        input.addEventListener('blur', function() {
            // Check if value is empty (or similar simple validation)
            if (!this.value) {
                this.classList.add('border-red-300');
            } else {
                this.classList.remove('border-red-300');
            }
        });
    });
}

// Function to handle the password toggle button
function initializePasswordToggle() {
    const togglePassword = document.getElementById('togglePassword');
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            // Find the password input relative to the toggle button (or globally)
            const passwordInput = document.querySelector('input[name="password"]'); 
            const icon = this.querySelector('i');
            
            if (passwordInput && icon) {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    passwordInput.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            }
        });
    }
}

// ====================================================================
// INITIALIZATION
// ====================================================================
document.addEventListener('DOMContentLoaded', function() {
    // 1. Initialize Login Form Handler
    initializeLoginForm();
    
    // 2. Initialize Register Form Handler
    initializeRegisterForm();
    
    // 3. Initialize Password Toggle
    initializePasswordToggle();
    
    // 4. Initialize Input Animations/Validation for both forms
    initializeInputEffects(document.getElementById('loginForm'));
    initializeInputEffects(document.getElementById('registerForm'));
});