# Mobile Money Integration - MTN & Orange Cameroon

This document describes the mobile money integration for MTN and Orange Cameroon mobile money services in the BlackGerm Investment Platform.

## Features

### ✅ Supported Services
- **MTN Mobile Money** - Deposits and withdrawals
- **Orange Money** - Deposits and withdrawals
- **Phone Number Validation** - Cameroon format validation
- **Transaction Limits** - Configurable min/max amounts
- **Fee Calculation** - Automatic fee calculation
- **Transaction Tracking** - Real-time status updates
- **Callback Handling** - Webhook support for status updates

### 📱 Supported Phone Number Formats
- Local format: `6XX XXX XXX` (9 digits)
- International format: `+237 6XX XXX XXX` (12 digits)
- Both MTN and Orange use the same number ranges in Cameroon

## API Endpoints

### MTN Mobile Money

#### Deposit
```http
POST /api/mobile-money/deposit/mtn
Content-Type: application/json
Authorization: Bearer <token>

{
  "phone_number": "237612345678",
  "amount": 1000.0,
  "provider": "MTN"
}
```

#### Withdrawal
```http
POST /api/mobile-money/withdrawal/mtn
Content-Type: application/json
Authorization: Bearer <token>

{
  "phone_number": "237612345678",
  "amount": 500.0,
  "provider": "MTN"
}
```

### Orange Money

#### Deposit
```http
POST /api/mobile-money/deposit/orange
Content-Type: application/json
Authorization: Bearer <token>

{
  "phone_number": "237698765432",
  "amount": 1500.0,
  "provider": "Orange"
}
```

#### Withdrawal
```http
POST /api/mobile-money/withdrawal/orange
Content-Type: application/json
Authorization: Bearer <token>

{
  "phone_number": "237698765432",
  "amount": 750.0,
  "provider": "Orange"
}
```

### Transaction Management

#### Check Transaction Status
```http
GET /api/mobile-money/transaction/{transaction_id}
Authorization: Bearer <token>
```

#### Get User Transactions
```http
GET /api/mobile-money/transactions?skip=0&limit=10
Authorization: Bearer <token>
```

### Callback Endpoints

#### MTN Callback
```http
POST /api/mobile-money/callback/mtn
Content-Type: application/json

{
  "transaction_id": "MTN_DEP_1234567890_1",
  "status": "completed",
  "amount": 1000.0,
  "phone_number": "237612345678"
}
```

#### Orange Callback
```http
POST /api/mobile-money/callback/orange
Content-Type: application/json

{
  "transaction_id": "ORANGE_DEP_1234567890_1",
  "status": "completed",
  "amount": 1500.0,
  "phone_number": "237698765432"
}
```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# MTN Mobile Money
MTN_API_KEY=your_mtn_api_key_here
MTN_API_SECRET=your_mtn_api_secret_here
MTN_BASE_URL=https://api.mtn.com/v1
MTN_MERCHANT_ID=your_mtn_merchant_id_here

# Orange Money
ORANGE_API_KEY=your_orange_api_key_here
ORANGE_API_SECRET=your_orange_api_secret_here
ORANGE_BASE_URL=https://api.orange.com/v1
ORANGE_MERCHANT_ID=your_orange_merchant_id_here

# Callback URLs (update with your domain)
MTN_CALLBACK_URL=https://your-domain.com/api/mobile-money/mtn/callback
ORANGE_CALLBACK_URL=https://your-domain.com/api/mobile-money/orange/callback
```

### Transaction Limits

| Transaction Type | Minimum | Maximum |
|------------------|---------|---------|
| Deposit | 100 XAF | 500,000 XAF |
| Withdrawal | 100 XAF | 500,000 XAF |

### Transaction Fees

| Provider | Deposit Fee | Withdrawal Fee |
|----------|-------------|----------------|
| MTN | 0 XAF | 50 XAF |
| Orange | 0 XAF | 50 XAF |

## Database Schema

### Transaction Table Updates

The `transactions` table has been extended with mobile money fields:

```sql
ALTER TABLE transactions ADD COLUMN currency VARCHAR DEFAULT 'XAF';
ALTER TABLE transactions ADD COLUMN transaction_id VARCHAR;
ALTER TABLE transactions ADD COLUMN phone_number VARCHAR;
ALTER TABLE transactions ADD COLUMN provider VARCHAR;
ALTER TABLE transactions ADD COLUMN description TEXT;
ALTER TABLE transactions ADD COLUMN updated_at TIMESTAMP;
```

## Testing

### Run Mobile Money Tests

```bash
cd black_germ_backend
python test_mobile_money.py
```

### Test Coverage

The test suite covers:
- ✅ User registration and authentication
- ✅ MTN deposit and withdrawal
- ✅ Orange deposit and withdrawal
- ✅ Transaction status checking
- ✅ Phone number validation
- ✅ Amount validation
- ✅ Error handling

## Security Features

### 🔐 Authentication
- JWT token-based authentication required for all endpoints
- User-specific transaction access

### 🛡️ Validation
- Phone number format validation for Cameroon
- Amount limits enforcement
- Balance verification for withdrawals

### 🔒 Transaction Security
- Unique transaction IDs
- HMAC signature verification
- Callback URL validation

## Error Handling

### Common Error Responses

#### Invalid Phone Number
```json
{
  "detail": "Invalid MTN phone number format"
}
```

#### Invalid Amount
```json
{
  "detail": "Invalid deposit amount. Must be between 100 and 500,000 XAF"
}
```

#### Insufficient Balance
```json
{
  "detail": "Insufficient balance for withdrawal"
}
```

#### API Error
```json
{
  "detail": "MTN API error: 400"
}
```

## Integration Steps

### 1. Setup Configuration
```bash
# Copy environment template
cp mobile_money_config.py .env

# Edit with your API credentials
nano .env
```

### 2. Update Database
```bash
# The database will be automatically updated when you start the server
python -m app.main
```

### 3. Test Integration
```bash
# Run the test suite
python test_mobile_money.py
```

### 4. Configure Callbacks
Update the callback URLs in your environment variables to point to your production domain.

## Production Deployment

### SSL Requirements
- HTTPS is required for callback URLs
- Valid SSL certificate needed

### API Credentials
- Use production API keys from MTN and Orange
- Store credentials securely (use environment variables)
- Rotate keys regularly

### Monitoring
- Monitor transaction success rates
- Log all mobile money transactions
- Set up alerts for failed transactions

## Troubleshooting

### Common Issues

#### 1. Import Error
```
ModuleNotFoundError: No module named 'mobile_money_config'
```
**Solution**: Make sure the `mobile_money_config.py` file is in the backend root directory.

#### 2. Database Migration Error
```
sqlalchemy.exc.OperationalError: no such column
```
**Solution**: Delete the database file and restart the server to recreate tables.

#### 3. API Connection Error
```
httpx.ConnectError: Connection failed
```
**Solution**: Check if the mobile money API endpoints are accessible and credentials are correct.

#### 4. Phone Number Validation Error
```
Invalid phone number format
```
**Solution**: Ensure phone numbers are in Cameroon format (6XX XXX XXX or +237 6XX XXX XXX).

## Support

For issues with mobile money integration:

1. Check the logs in the console output
2. Verify API credentials are correct
3. Test with the provided test script
4. Ensure phone numbers are in correct format

## License

This mobile money integration is part of the BlackGerm Investment Platform and follows the same license terms. 