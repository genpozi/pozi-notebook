# Authentication & User Management

Open Notebook v1.1+ includes a complete multi-user authentication system with secure JWT tokens and data isolation.

## Overview

The authentication system provides:
- **User Accounts**: Each user has their own account with email and password
- **Data Isolation**: Users can only see their own notebooks, sources, and notes
- **Secure Authentication**: Passwords hashed with Argon2, JWT tokens for API access
- **Admin Account**: System administrator account for user management
- **Session Management**: 7-day token expiration with automatic renewal

## Getting Started

### First Time Setup

When you first start Open Notebook v1.1+, a default admin account is automatically created:

- **Email**: `admin@localhost`
- **Password**: `change-me-immediately`

⚠️ **IMPORTANT**: You should change this password immediately after your first login!

### Creating a User Account

1. Navigate to the signup page: `http://your-server:8502/signup`
2. Fill in the registration form:
   - **Full Name**: Your display name
   - **Email**: Your email address (used for login)
   - **Password**: Minimum 8 characters
   - **Confirm Password**: Must match your password
3. Click "Sign Up"
4. You'll be automatically logged in and redirected to the dashboard

### Signing In

1. Go to the login page: `http://your-server:8502/login`
2. Enter your email and password
3. Click "Sign In"
4. You'll be redirected to your notebooks

### Signing Out

Click the "Sign Out" button in the sidebar at any time to log out of your account.

## User Profile

Your user profile is displayed in the sidebar and shows:
- Your full name
- Your email address
- Your role (user or admin)

## Security Features

### Password Security

- **Hashing**: Passwords are hashed using Argon2, a memory-hard algorithm resistant to GPU attacks
- **No Plain Text**: Passwords are never stored in plain text
- **Secure Comparison**: Password verification uses constant-time comparison to prevent timing attacks

### JWT Tokens

- **Stateless**: Tokens contain all necessary user information
- **Expiration**: Tokens expire after 7 days
- **Secure Storage**: Tokens are stored in browser localStorage
- **Bearer Authentication**: Tokens are sent in the Authorization header

### Data Isolation

- **User-Owned Resources**: Each notebook, source, and note belongs to a specific user
- **Query Filtering**: All database queries automatically filter by user_id
- **Admin Override**: Admin users can access all data for management purposes

## Admin Features

Admin accounts have special privileges:

- **User Management**: View and manage all user accounts (coming soon)
- **System Access**: Access to all notebooks and sources
- **Configuration**: Manage system-wide settings

### Changing Admin Password

To change the admin password:

1. Sign in with the admin account
2. Go to Settings (coming soon)
3. Update your password
4. Save changes

## API Authentication

When using the REST API, include your JWT token in the Authorization header:

```bash
curl -X GET http://localhost:5055/api/notebooks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

To get your JWT token:
1. Sign in through the web interface
2. Open browser developer tools (F12)
3. Go to Application → Local Storage → auth-storage
4. Copy the token value

## Troubleshooting

### "Invalid email or password"

- Check that you're using the correct email address
- Passwords are case-sensitive
- Make sure Caps Lock is off
- Try resetting your password (coming soon)

### "Unable to connect to server"

- Ensure the API is running on port 5055
- Check that `API_URL` environment variable is set correctly
- Verify network connectivity

### Session Expired

- JWT tokens expire after 7 days
- Simply sign in again to get a new token
- Your data is preserved

### Can't Access Notebooks

- Make sure you're signed in
- Check that you're viewing your own notebooks
- Admin users can see all notebooks

## Migration from Previous Versions

If you're upgrading from a version without authentication:

1. **Existing Data**: All existing notebooks, sources, and notes are automatically assigned to the admin user
2. **Admin Account**: The admin account is created on first startup
3. **User Accounts**: Create new user accounts through the signup page
4. **No Data Loss**: All your existing data is preserved

## Best Practices

### For Users

- ✅ Use a strong, unique password
- ✅ Don't share your account credentials
- ✅ Sign out when using shared computers
- ✅ Keep your email address up to date

### For Administrators

- ✅ Change the default admin password immediately
- ✅ Create individual accounts for each user
- ✅ Regularly review user accounts
- ✅ Keep the system updated
- ✅ Back up the database regularly

## Technical Details

### Database Schema

The user table includes:
- `id`: Unique user identifier
- `email`: User's email address (unique)
- `password`: Argon2 hashed password
- `name`: User's display name
- `role`: User role (user or admin)
- `created`: Account creation timestamp
- `updated`: Last update timestamp

### JWT Token Structure

JWT tokens contain:
- `ID`: User's database ID
- `email`: User's email address
- `role`: User's role
- `exp`: Token expiration time
- `iat`: Token issued at time

### API Endpoints

- `GET /api/auth/status` - Check if authentication is enabled
- `POST /api/auth/signup` - Register a new user account
- `POST /api/auth/signin` - Authenticate and get JWT token

## Future Enhancements

Planned features for future releases:

- 🔄 Password reset via email
- 👥 User management interface for admins
- 🔐 Two-factor authentication (2FA)
- 📧 Email verification
- 👤 User profile editing
- 🔑 API key management
- 👥 Team/organization support
- 🔗 OAuth integration (Google, GitHub, etc.)

## Support

Need help with authentication?

- 📖 Check the [Troubleshooting Guide](../troubleshooting/quick-fixes.md)
- 💬 Join our [Discord Server](https://discord.gg/37XJPXfz2w)
- 🐛 Report issues on [GitHub](https://github.com/lfnovo/open-notebook/issues)

---

**Security Notice**: If you discover a security vulnerability, please email security@open-notebook.ai instead of creating a public issue.
