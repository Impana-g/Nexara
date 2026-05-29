# Nexara Authentication System - Complete Guide

## Overview

This document describes the secure registration and login system implemented in the Nexara Platform. The system includes:

- **Secure Registration (Sign Up)** - `/register/` (HTML form) and `/api/auth/register/` (API)
- **Secure Login** - `/login/` (HTML form) and `/api/auth/login/` (API)
- **Token-based Authentication** - Django REST Framework Token Authentication
- **Protected Routes** - Only authenticated users can access protected endpoints
- **Responsive UI** - Mobile-friendly, modern design with accessibility support
- **Client-side Validation** - Real-time validation on registration and login forms
- **Server-side Validation** - Comprehensive backend validation and security checks

## Architecture

### Backend Components

#### 1. **Serializers** (`core/serializers.py`)
- `RegistrationSerializer` - Validates registration input and creates users
  - Validates email format
  - Checks for duplicate emails (case-insensitive)
  - Validates password strength (minimum 8 characters)
  - Ensures password and confirm_password match
  - Securely hashes passwords using Django's `User.objects.create_user()`
  - Stores full name split into first_name and last_name

#### 2. **Views** (`core/views.py`)
- `register_form_view()` - Renders the registration HTML form
- `login_form_view()` - Renders the login HTML form
- `register_view()` - API endpoint for user registration
  - Accepts: full_name, email, password, confirm_password
  - Returns: success message or validation errors
  - Status: 201 Created on success, 400 Bad Request on error
- `login_view()` - API endpoint for user login (already implemented)
  - Accepts: username (email), password
  - Returns: auth token, user data, tenant info
  - Status: 200 OK on success, 401 Unauthorized on failure

#### 3. **URLs** (`core/urls.py`)
```
GET/POST  /register/            → register_form_view()
GET/POST  /login/               → login_form_view()
POST      /api/auth/register/   → register_view()
POST      /api/auth/login/      → login_view()
POST      /api/auth/logout/     → logout_view()
GET       /api/auth/me/         → me_view()
```

#### 4. **Authentication Decorators** (`core/auth_decorators.py`)
- `@login_required_view` - Protects HTML views (redirects to login)
- `@login_required_api` - Protects API views (returns 401 Unauthorized)

### Frontend Components

#### 1. **Registration Form** (`templates/core/register.html`)
- Full Name input
- Email input (with format validation)
- Password input (minimum 8 characters)
- Confirm Password input (must match password)
- Real-time validation feedback
- Security features information panel
- Link to login page

#### 2. **Login Form** (`templates/core/login.html`)
- Email input
- Password input
- Real-time validation feedback
- Security features information panel
- Link to registration page

#### 3. **Styling** (`static/css/auth.css`)
- Responsive design (mobile-first)
- Gradient background
- Card-based layout with shadows
- Smooth animations and transitions
- Dark mode support
- Accessibility features (reduced motion support)

#### 4. **JavaScript** (`static/js/auth.js`)
- Client-side form validation
- Email format validation
- Password strength validation
- CSRF token handling
- API calls with error handling
- Real-time field validation
- Loading states and user feedback

## Security Features

### Backend Security

1. **Password Hashing**
   - Uses Django's `make_password()` which defaults to PBKDF2 algorithm
   - Never stores plain-text passwords
   - Passwords validated against Django's password validators

2. **Duplicate Email Prevention**
   - Case-insensitive email check using `User.objects.filter(email__iexact=value)`
   - Returns 400 Bad Request if email already exists

3. **Input Validation**
   - Email format validation using DRF's EmailField
   - Password minimum length: 8 characters
   - Full name required and non-empty
   - Password confirmation must match

4. **CSRF Protection**
   - Django middleware prevents CSRF attacks
   - Each form includes CSRF token
   - API calls require CSRF token in headers

5. **Token-based Authentication**
   - Uses Django REST Framework TokenAuthentication
   - Tokens created on successful login
   - Tokens linked to user and never exposed
   - Can be revoked on logout

6. **Middleware Protection**
   - `TenantMiddleware` ensures multi-tenant isolation
   - `AuthenticationMiddleware` verifies user authentication
   - `SessionMiddleware` manages sessions securely

### Frontend Security

1. **Form Validation**
   - Client-side validation for better UX
   - Server-side validation is authoritative
   - Real-time feedback on password match
   - Email format validation before submit

2. **CSRF Token**
   - Extracted from Django's CSRF cookie
   - Sent with all API requests
   - Required for POST operations

3. **Secure Token Storage**
   - Token stored in localStorage after login
   - Used in Authorization header for protected API calls
   - Cleared on logout

4. **Error Handling**
   - Generic error messages to prevent user enumeration
   - Specific field-level errors for validation failures
   - Sensitive info (password hints) never exposed in errors

## Usage

### For Users

#### Registration Flow
1. Click "Sign Up" or navigate to `/register/`
2. Enter full name, email, password, and confirm password
3. Click "Create Account"
4. On success, redirected to login page after 2 seconds
5. Log in with registered email and password

#### Login Flow
1. Navigate to `/login/`
2. Enter email and password
3. Click "Log In"
4. On success, redirected to dashboard after 2 seconds
5. Token stored in localStorage for future requests

### For Developers

#### Protecting Views

**HTML Views (redirect to login if not authenticated):**
```python
from core.auth_decorators import login_required_view

@login_required_view
def dashboard_view(request):
    return render(request, 'dashboard.html')
```

**API Views (return 401 if not authenticated):**
```python
from rest_framework import permissions

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def protected_api_view(request):
    return Response({'data': 'only authenticated users see this'})
```

**Class-based Views:**
```python
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

class ProtectedListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
```

#### Making Authenticated API Calls

**From JavaScript:**
```javascript
const token = localStorage.getItem('authToken');
const response = await fetch('/api/protected/', {
    headers: {
        'Authorization': `Token ${token}`,
        'X-CSRFToken': getCookie('csrftoken'),
    }
});
```

**From Python/Requests:**
```python
import requests

token = 'user-token-here'
headers = {'Authorization': f'Token {token}'}
response = requests.get('/api/protected/', headers=headers)
```

## Database Schema

### User Model (Django Built-in)
```
User
├── id (primary key)
├── username (email)
├── email
├── password (hashed)
├── first_name
├── last_name
├── is_active
├── is_staff
├── is_superuser
├── date_joined
└── last_login
```

### Token Model (Django REST Framework)
```
Token
├── key (token string)
├── user (foreign key → User)
└── created
```

### TenantMembership Model
```
TenantMembership
├── id
├── user (one-to-one with User)
├── tenant (foreign key)
├── role (admin, member, viewer)
└── created_at
```

## Configuration

### Required Settings (in `settings.py`)

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework.authtoken',
    # ...
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### Optional: Custom User Model
If you want to use a custom User model, update `AUTH_USER_MODEL` in settings:
```python
AUTH_USER_MODEL = 'core.CustomUser'
```

## Troubleshooting

### Issue: "CSRF token missing or incorrect"
**Solution:** Ensure `csrftoken` cookie is being sent with requests. Check browser DevTools → Application → Cookies.

### Issue: "Email already exists" error on registration
**Solution:** That email is already registered. Use a different email or use the forgot password flow (if implemented).

### Issue: "Invalid credentials" on login
**Solution:** Verify email and password are correct. Password is case-sensitive.

### Issue: API returns 401 Unauthorized
**Solution:** Token might be expired or invalid. Log out and log back in to get a new token.

### Issue: Protected routes not working
**Solution:** Ensure views have `@permission_classes([permissions.IsAuthenticated])` or `@login_required_view`.

## Future Enhancements

1. **Email Verification**
   - Send verification email on registration
   - Require email confirmation before account activation

2. **Password Reset**
   - Forgot password flow with email reset link
   - Secure token-based password reset

3. **Two-Factor Authentication (2FA)**
   - TOTP/SMS-based 2FA
   - Backup codes for account recovery

4. **OAuth Integration**
   - Google Sign-In
   - GitHub/Microsoft authentication

5. **Rate Limiting**
   - Limit login attempts to prevent brute force
   - Limit registration to prevent spam

6. **Audit Logging**
   - Log all authentication events
   - Track login history and IP addresses

## Support

For issues or questions, refer to:
- Django Authentication Documentation: https://docs.djangoproject.com/en/stable/topics/auth/
- Django REST Framework: https://www.django-rest-framework.org/
- Security Best Practices: https://owasp.org/www-project-authentication-cheat-sheet/
