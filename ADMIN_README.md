# Black Germ Admin Dashboard Backend

## Overview

The Black Germ Admin Dashboard provides comprehensive administrative capabilities for managing the investment platform, including user management, transaction monitoring, security alerts, and system analytics.

## Features

### 🔐 Authentication & Authorization
- **JWT-based authentication** for admin users
- **Role-based access control** (Super Admin, Admin, Moderator)
- **Permission-based authorization** for specific features
- **Secure password hashing** using bcrypt

### 📊 Dashboard Statistics
- **Real-time platform metrics**
- **User growth analytics**
- **Revenue tracking**
- **Transaction monitoring**
- **System health monitoring**

### 👥 User Management
- **View all users** with search and filtering
- **User details** with transaction history
- **Balance management**
- **Bulk user operations**
- **User activity tracking**

### 💰 Transaction Management
- **View all transactions** with filtering
- **Transaction approval/rejection**
- **Status updates**
- **Transaction notes and comments**
- **Mobile money integration monitoring**

### 🛡️ Security & Monitoring
- **Security alerts** management
- **System logs** viewing
- **Failed login attempts** tracking
- **Suspicious activity** detection
- **IP address monitoring**

### 📈 Analytics & Reports
- **Revenue analytics** (daily, weekly, monthly, yearly)
- **User growth analytics**
- **Mobile money performance**
- **AI assistant usage statistics**
- **Export functionality** (JSON, CSV)

### 🔔 Notifications
- **Send notifications** to users
- **Email/SMS/In-app** notifications
- **Scheduled notifications**
- **Bulk messaging**

### ⚙️ System Management
- **System health monitoring**
- **Database status**
- **API performance metrics**
- **Error rate tracking**

## API Endpoints

### Authentication
```
POST /api/admin/login
```

### Dashboard
```
GET /api/admin/dashboard/stats
```

### User Management
```
GET /api/admin/users
GET /api/admin/users/{user_id}
PUT /api/admin/users/{user_id}
POST /api/admin/users/bulk-action
```

### Transaction Management
```
GET /api/admin/transactions
PUT /api/admin/transactions/{transaction_id}
```

### Analytics
```
GET /api/admin/analytics/revenue
GET /api/admin/analytics/user-growth
```

### Security
```
GET /api/admin/security/alerts
PUT /api/admin/security/alerts/{alert_id}/resolve
```

### System
```
GET /api/admin/system/health
GET /api/admin/system/logs
```

### Mobile Money
```
GET /api/admin/mobile-money/status
```

### AI Assistant
```
GET /api/admin/ai/analytics
```

### Notifications
```
POST /api/admin/notifications
```

### Reports
```
POST /api/admin/reports/generate
GET /api/admin/export/users
```

### Admin Management
```
POST /api/admin/admins
```

## Database Schema

### Admin Table
```sql
CREATE TABLE admins (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    role VARCHAR DEFAULT 'admin',
    permissions TEXT,
    is_active VARCHAR DEFAULT 'active',
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
```

### Security Alerts Table
```sql
CREATE TABLE security_alerts (
    id INTEGER PRIMARY KEY,
    alert_type VARCHAR NOT NULL,
    severity VARCHAR DEFAULT 'medium',
    message TEXT NOT NULL,
    user_id INTEGER,
    ip_address VARCHAR,
    resolved VARCHAR DEFAULT 'false',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    resolved_by INTEGER
);
```

### System Logs Table
```sql
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY,
    log_type VARCHAR NOT NULL,
    message TEXT NOT NULL,
    details TEXT,
    admin_id INTEGER,
    user_id INTEGER,
    ip_address VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Admin Notifications Table
```sql
CREATE TABLE admin_notifications (
    id INTEGER PRIMARY KEY,
    title VARCHAR NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR DEFAULT 'email',
    target_users TEXT,
    scheduled_at DATETIME,
    sent_at DATETIME,
    status VARCHAR DEFAULT 'pending',
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Admin Database
```bash
python init_admin.py
```

### 3. Start the Server
```bash
python -m uvicorn app.main:app --reload
```

### 4. Access Admin API
- **Base URL**: `http://localhost:8000/api/admin`
- **Documentation**: `http://localhost:8000/docs`

## Default Admin Credentials

After running `init_admin.py`, you'll have a super admin account:
- **Email**: admin@blackgerm.com
- **Password**: admin123

**⚠️ Change these credentials in production!**

## Permissions System

### Available Permissions
- `user_management` - Manage users
- `transaction_management` - Manage transactions
- `system_monitoring` - Monitor system health
- `security_monitoring` - Monitor security alerts
- `notifications` - Send notifications
- `reports` - Generate reports
- `admin_management` - Manage other admins

### Role Hierarchy
1. **Super Admin** - All permissions
2. **Admin** - Assigned permissions
3. **Moderator** - Limited permissions

## Security Features

### Authentication
- JWT tokens with expiration
- Secure password hashing
- Session management

### Authorization
- Role-based access control
- Permission-based authorization
- API endpoint protection

### Monitoring
- Security alerts
- System logs
- Activity tracking
- IP monitoring

## Environment Variables

Create a `.env` file with:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./black_germ.db
OPENAI_API_KEY=your-openai-api-key
```

## Production Considerations

### Security
- Change default admin credentials
- Use strong SECRET_KEY
- Enable HTTPS
- Implement rate limiting
- Add IP whitelisting

### Performance
- Use PostgreSQL instead of SQLite
- Implement caching (Redis)
- Add database indexing
- Monitor API performance

### Monitoring
- Set up logging
- Implement health checks
- Add error tracking
- Monitor system resources

## API Documentation

The complete API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Testing

Test the admin endpoints using the provided test files:
```bash
python test_backend.py
```

## Support

For issues or questions:
1. Check the logs in `system_logs` table
2. Review security alerts
3. Monitor system health endpoint
4. Check API documentation

## Next Steps

1. **Frontend Development** - Build the admin dashboard UI
2. **Enhanced Security** - Add 2FA, IP whitelisting
3. **Advanced Analytics** - Implement more detailed reporting
4. **Automation** - Add automated alerts and actions
5. **Integration** - Connect with external monitoring tools 