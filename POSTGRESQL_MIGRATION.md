# PostgreSQL Migration Guide

This project has been migrated from SQLite to PostgreSQL. Follow these steps to set up your environment.

## Prerequisites

- Python 3.8+
- PostgreSQL 12+

## Installation Steps

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS (with Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Start PostgreSQL Service

```bash
# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS
brew services start postgresql
```

### 3. Create Database and User

```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# Create a new user (replace with your preferred username/password)
CREATE USER black_germ_user WITH PASSWORD 'your_secure_password';
ALTER USER black_germ_user CREATEDB;

# Create the database
CREATE DATABASE black_germ_db OWNER black_germ_user;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE black_germ_db TO black_germ_user;

# Exit PostgreSQL
\q
```

### 4. Install Python Dependencies

```bash
# Install PostgreSQL adapter and environment loader
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root (copy from `env_example.txt`):

```bash
cp env_example.txt .env
```

Update the `.env` file with your PostgreSQL credentials:

```env
DATABASE_URL=postgresql://black_germ_user:your_secure_password@localhost:5432/black_germ_db
```

### 6. Test Database Connection

```bash
python test_db_connection.py
```

### 7. Run the Application

```bash
python -m app.main
```

The application will automatically create all necessary database tables on first run.

## Environment Variables

The following environment variables are now used:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `TRANSACTION_FEE_PERCENTAGE`: Platform transaction fee
- `MIN_TRANSACTION_AMOUNT`: Minimum transaction amount
- `MAX_TRANSACTION_AMOUNT`: Maximum transaction amount
- `WITHDRAWAL_APPROVAL_THRESHOLD`: Threshold for withdrawal approval
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `MTN_API_KEY`: MTN mobile money API key
- `ORANGE_API_KEY`: Orange mobile money API key
- `SMTP_HOST`: Email SMTP host
- `SMTP_PORT`: Email SMTP port
- `SMTP_USERNAME`: Email username
- `SMTP_PASSWORD`: Email password
- `ALLOWED_ORIGINS`: CORS allowed origins
- `TRON_NETWORK`: TRON network (mainnet/testnet)
- `BSC_NETWORK`: BSC network (mainnet/testnet)
- `PLATFORM_TRC20_WALLET`: Platform TRC20 wallet address
- `PLATFORM_BEP20_WALLET`: Platform BEP20 wallet address
- `PLATFORM_TRC20_PRIVATE_KEY`: Platform TRC20 private key
- `PLATFORM_BEP20_PRIVATE_KEY`: Platform BEP20 private key

## Migration from SQLite

If you have existing data in SQLite, you'll need to:

1. Export data from SQLite database
2. Import data into PostgreSQL
3. Update any hardcoded references

## Troubleshooting

### Connection Issues

1. Verify PostgreSQL is running: `sudo systemctl status postgresql`
2. Check firewall settings
3. Verify database credentials in `.env` file
4. Test connection: `python test_db_connection.py`

### Permission Issues

1. Ensure user has proper database privileges
2. Check PostgreSQL authentication settings in `pg_hba.conf`

### Port Issues

Default PostgreSQL port is 5432. If using a different port, update the `DATABASE_URL` accordingly.

## Production Deployment

For production deployment:

1. Use a managed PostgreSQL service (AWS RDS, Google Cloud SQL, etc.)
2. Set strong passwords and use environment-specific credentials
3. Enable SSL connections
4. Configure proper backup strategies
5. Monitor database performance

## Security Notes

- Never commit `.env` files to version control
- Use strong, unique passwords
- Regularly rotate database credentials
- Enable SSL in production
- Use connection pooling for better performance
