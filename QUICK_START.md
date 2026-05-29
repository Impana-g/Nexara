# Quick Start Guide - Nexara Authentication

## Installation & Setup

### 1. Backend Setup (Already Done ✓)

The backend is fully configured. The following have been implemented:

- ✅ Registration API endpoint at `/api/auth/register/`
- ✅ Registration form at `/register/`
- ✅ Login form at `/login/`
- ✅ Login API endpoint at `/api/auth/login/` (existing)
- ✅ Token-based authentication
- ✅ Input validation and duplicate email checks
- ✅ Secure password hashing

### 2. Frontend Setup (Already Done ✓)

- ✅ Responsive Sign Up page with modern UI
- ✅ Responsive Login page with modern UI
- ✅ Client-side validation
- ✅ Real-time form feedback
- ✅ Dark mode support
- ✅ Accessibility features

### 3. Verify Installation

Run the following commands:

```bash
# Navigate to your project directory
cd c:/Users/Impana/OneDrive/Desktop/Nexara

# Ensure database migrations are applied
python manage.py migrate

# (Optional) Create a superuser for admin access
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

### 4. Test the System

1. **Registration:**
   - Open browser: http://localhost:8000/register/
   - Fill in the form with test data
   - Click "Create Account"
   - You should see a success message and redirect to login

2. **Login:**
   - Open browser: http://localhost:8000/login/
   - Enter registered email and password
   - Click "Log In"
   - Token stored in browser's localStorage
   - Redirected to dashboard (if implemented)

3. **API Testing (using curl or Postman):**

   **Register a new user:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/register/ \
     -H "Content-Type: application/json" \
     -d '{
       "full_name": "John Doe",
       "email": "john@example.com",
       "password": "SecurePassword123",
       "confirm_password": "SecurePassword123"
     }'
   ```

   **Login:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{
       "username": "john@example.com",
       "password": "SecurePassword123"
     }'
   ```

   **Access protected endpoint (replace TOKEN with actual token):**
   ```bash
   curl -X GET http://localhost:8000/api/auth/me/ \
     -H "Authorization: Token YOUR_TOKEN_HERE"
   ```

## Protecting Your Routes

### Protect HTML Views (Redirect to Login)

```python
from django.shortcuts import render
from core.auth_decorators import login_required_view

@login_required_view
def dashboard_view(request):
    """Only authenticated users can access this"""
    return render(request, 'dashboard.html', {
        'user': request.user
    })
```

### Protect API Views (Return 401)

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def protected_api_view(request):
    """Only authenticated users can access this"""
    return Response({
        'user': request.user.email,
        'message': 'This is a protected endpoint'
    })
```

### Protect Class-based API Views

```python
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

class ProtectedListView(ListAPIView):
    """Only authenticated users can list items"""
    permission_classes = [IsAuthenticated]
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
```

## Making Authenticated Requests

### From JavaScript/Frontend

```javascript
// Get token from localStorage
const token = localStorage.getItem('authToken');

// Make authenticated API call
fetch('/api/protected-endpoint/', {
    method: 'GET',
    headers: {
        'Authorization': `Token ${token}`,
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json',
    }
})
.then(response => response.json())
.then(data => console.log('Protected data:', data))
.catch(error => console.error('Error:', error));
```

### From Python Backend

```python
from rest_framework.authtoken.models import Token

# Get token for a user
user = User.objects.get(email='john@example.com')
token = Token.objects.get(user=user)
print(f"Token: {token.key}")
```

## File Structure

```
Nexara/
├── templates/
│   ├── base.html                  # Base template
│   └── core/
│       ├── register.html          # Sign Up form
│       └── login.html             # Login form
├── static/
│   ├── css/
│   │   └── auth.css               # Authentication styles
│   └── js/
│       └── auth.js                # Authentication logic
├── core/
│   ├── views.py                   # Updated with form views
│   ├── urls.py                    # Updated with form routes
│   ├── serializers.py             # RegistrationSerializer added
│   ├── auth_decorators.py         # New: Auth decorators
│   └── models.py                  # User model (Django built-in)
├── AUTHENTICATION.md              # Full documentation
├── QUICK_START.md                 # This file
└── manage.py
```

## Common Issues & Solutions

### Issue: Templates not found
**Error:** `TemplateDoesNotExist: core/register.html`
**Solution:** Ensure templates folder is in project root and settings.py has:
```python
'DIRS': [BASE_DIR / 'templates'],
```

### Issue: Static files not loading
**Error:** CSS/JS not loading in browser
**Solution:** Run `python manage.py collectstatic` and check STATIC_URL in settings.py

### Issue: CSRF token mismatch
**Error:** `CSRF verification failed`
**Solution:** Ensure CSRF cookie is being sent and token is included in request headers

### Issue: Email already registered
**Error:** `A user with this email already exists`
**Solution:** Use a different email or reset password if forgot email

## Next Steps

1. **Create Protected Routes:**
   - Add a dashboard view that only authenticated users can access
   - Add API endpoints that require authentication

2. **Email Verification:**
   - Send verification email on registration
   - Require email confirmation before full access

3. **Password Reset:**
   - Implement forgot password flow
   - Allow users to reset forgotten passwords

4. **Rate Limiting:**
   - Add rate limiting to prevent brute force attacks
   - Limit login attempts

5. **Audit Logging:**
   - Log all authentication events
   - Track user login history

## Testing Checklist

- [ ] Registration with valid data works
- [ ] Duplicate email prevention works
- [ ] Password validation (minimum 8 chars) works
- [ ] Password confirmation validation works
- [ ] Login with registered credentials works
- [ ] Token stored in localStorage after login
- [ ] Protected routes redirect to login if not authenticated
- [ ] Protected API endpoints return 401 if not authenticated
- [ ] Responsive design works on mobile
- [ ] Error messages display correctly
- [ ] Success messages display correctly

## Security Checklist

- [ ] Passwords are hashed (never stored in plain text)
- [ ] CSRF protection is enabled
- [ ] HTTPS is configured in production
- [ ] Secret key is configured via environment variables
- [ ] Debug mode is OFF in production
- [ ] Database credentials are in environment variables
- [ ] Sensitive data is not logged
- [ ] Rate limiting is implemented
- [ ] Email verification is implemented
- [ ] SQL injection prevention (using ORM)

## Support & Documentation

- **Django Auth:** https://docs.djangoproject.com/en/stable/topics/auth/
- **DRF TokenAuth:** https://www.django-rest-framework.org/api-guide/authentication/
- **OWASP Guides:** https://owasp.org/www-project-authentication-cheat-sheet/
- **Security Headers:** https://securityheaders.com/

---

**Status:** ✅ Setup Complete and Ready to Use
