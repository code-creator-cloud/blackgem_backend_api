# Web3 USDT Integration - TRC20 & BEP20

## 🚀 **Overview**

The Black Germ platform now supports USDT deposits on two major networks:
- **TRC20 (Tron Network)** - Fast and low-fee USDT transfers
- **BEP20 (Binance Smart Chain)** - Popular USDT transfers on BSC

## 🔧 **Features**

### **Supported Networks**
- ✅ **TRC20** - USDT on Tron Network
- ✅ **BEP20** - USDT on Binance Smart Chain
- ✅ **Automatic verification** of blockchain transactions
- ✅ **Real-time balance updates** in USD
- ✅ **Background monitoring** of pending deposits

### **Key Functionality**
- **Create deposits** with network-specific addresses
- **Verify transactions** on-chain
- **Convert USDT to USD** (1:1 ratio)
- **Monitor pending deposits** automatically
- **Get network balances** for any wallet
- **View deposit history** and status
- **Create withdrawals** to user wallets
- **Process withdrawals** automatically
- **Check withdrawal eligibility** before processing
- **View withdrawal history** and status

## 📋 **API Endpoints**

### **Web3 Deposit Management**
```
POST /api/web3/deposit/create     - Create new USDT deposit
POST /api/web3/deposit/verify     - Verify transaction manually
GET  /api/web3/networks           - Get supported networks
GET  /api/web3/balance/{network}  - Get wallet balance
GET  /api/web3/deposits/pending   - Get pending deposits
GET  /api/web3/deposits/history   - Get deposit history
```

### **Web3 Withdrawal Management**
```
POST /api/web3/withdrawal/create      - Create new USDT withdrawal
POST /api/web3/withdrawal/process/{id} - Process pending withdrawal
GET  /api/web3/withdrawal/eligibility - Check withdrawal eligibility
GET  /api/web3/withdrawal/history     - Get withdrawal history
GET  /api/web3/platform/balance/{network} - Get platform balance
```

## 🛠️ **Setup Instructions**

### **1. Install Dependencies**
```bash
pip install web3==6.15.1 tronpy==0.4.0 requests==2.31.0
```

### **2. Configure Environment Variables**
Add to your `.env` file:
```env
# Web3 Configuration
TRON_NETWORK=mainnet
BSC_NETWORK=mainnet
PLATFORM_TRC20_WALLET=TYourPlatformWalletAddress
PLATFORM_BEP20_WALLET=0xYourPlatformWalletAddress
PLATFORM_TRC20_PRIVATE_KEY=your_tron_private_key_here
PLATFORM_BEP20_PRIVATE_KEY=your_bsc_private_key_here
```

### **3. Set Platform Wallet Addresses and Private Keys**
Replace the placeholder addresses and private keys with your actual credentials:
- **TRC20**: Your Tron wallet address (starts with 'T') and private key
- **BEP20**: Your BSC wallet address (starts with '0x') and private key

**⚠️ SECURITY WARNING:** Never commit private keys to version control. Store them securely in environment variables.

## 📊 **Network Information**

### **TRC20 (Tron Network)**
- **Currency**: USDT
- **Decimals**: 6
- **Explorer**: https://tronscan.org
- **Min Deposit**: 1 USDT
- **Max Deposit**: 100,000 USDT
- **Min Withdrawal**: 1 USDT
- **Max Withdrawal**: 100,000 USDT
- **Withdrawal Fee**: 1 USDT
- **Contract**: TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t

### **BEP20 (Binance Smart Chain)**
- **Currency**: USDT
- **Decimals**: 18
- **Explorer**: https://bscscan.com
- **Min Deposit**: 1 USDT
- **Max Deposit**: 100,000 USDT
- **Min Withdrawal**: 1 USDT
- **Max Withdrawal**: 100,000 USDT
- **Withdrawal Fee**: 0.5 USDT
- **Contract**: 0x55d398326f99059fF775485246999027B3197955

## 🔄 **How It Works**

### **1. Deposit Creation**
```json
POST /api/web3/deposit/create
{
  "network": "TRC20",
  "amount": 100.0,
  "user_wallet_address": "TUserWalletAddress"
}
```

**Response:**
```json
{
  "deposit_id": 123,
  "network": "TRC20",
  "amount": 100.0,
  "deposit_address": "TPlatformWalletAddress",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00",
  "notes": "Send exactly 100.0 USDT to TPlatformWalletAddress"
}
```

### **2. Transaction Verification**
```json
POST /api/web3/deposit/verify
{
  "tx_hash": "abc123...",
  "network": "TRC20",
  "amount": 100.0
}
```

**Response:**
```json
{
  "verified": true,
  "usdt_amount": 100.0,
  "usd_amount": 100.0,
  "new_balance": 1100.0,
  "message": "Deposit verified! 100.0 USDT = $100.0 USD"
}
```

### **3. Get Network Information**
```json
GET /api/web3/networks
```

**Response:**
```json
{
  "networks": [
    {
      "code": "TRC20",
      "name": "Tron Network",
      "currency": "USDT",
      "decimals": 6,
      "explorer": "https://tronscan.org",
      "deposit_address": "TPlatformWalletAddress",
      "min_deposit": 1.0,
      "max_deposit": 100000.0,
      "min_withdrawal": 1.0,
      "max_withdrawal": 100000.0,
      "withdrawal_fee": 1.0
    },
    {
      "code": "BEP20",
      "name": "Binance Smart Chain",
      "currency": "USDT",
      "decimals": 18,
      "explorer": "https://bscscan.com",
      "deposit_address": "0xPlatformWalletAddress",
      "min_deposit": 1.0,
      "max_deposit": 100000.0,
      "min_withdrawal": 1.0,
      "max_withdrawal": 100000.0,
      "withdrawal_fee": 0.5
    }
  ]
}
```

### **4. Create Withdrawal**
```json
POST /api/web3/withdrawal/create
{
  "network": "TRC20",
  "amount": 50.0,
  "wallet_address": "TUserWalletAddress"
}
```

**Response:**
```json
{
  "withdrawal_id": 124,
  "network": "TRC20",
  "amount": 50.0,
  "wallet_address": "TUserWalletAddress",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00",
  "notes": "Withdrawal fee: 1.0 USDT, Net amount: 49.0 USDT"
}
```

### **5. Process Withdrawal**
```json
POST /api/web3/withdrawal/process/124
```

**Response:**
```json
{
  "success": true,
  "withdrawal_id": 124,
  "tx_hash": "abc123...",
  "amount": 50.0,
  "network": "TRC20",
  "new_balance": 950.0,
  "message": "Withdrawal successful! 50.0 USDT sent to TUserWalletAddress"
}
```

### **6. Check Withdrawal Eligibility**
```json
GET /api/web3/withdrawal/eligibility?network=TRC20&amount=50.0
```

**Response:**
```json
{
  "eligible": true,
  "platform_balance": 1000.0,
  "withdrawal_fee": 1.0,
  "net_amount": 49.0
}
```

## 🔍 **Background Monitoring**

The system automatically monitors pending deposits every 30 seconds:

1. **Scans pending deposits** in the database
2. **Verifies transactions** on the blockchain
3. **Updates user balances** automatically
4. **Logs verification results**

### **Monitoring Logs:**
```
✅ Auto-verified deposit: 100.0 USDT -> 100.0 USD
❌ Deposit verification failed: Transaction not found
```

## 🛡️ **Security Features**

### **Transaction Verification**
- ✅ **On-chain verification** of all transactions
- ✅ **Amount validation** against expected values
- ✅ **Network-specific validation** for each blockchain
- ✅ **Address validation** for platform wallets

### **Fraud Prevention**
- ✅ **Minimum/maximum deposit limits**
- ✅ **Transaction hash validation**
- ✅ **Network-specific contract validation**
- ✅ **Automatic status updates**

## 📈 **User Experience**

### **For Users:**
1. **Choose network** (TRC20 or BEP20)
2. **Enter amount** (1-100,000 USDT)
3. **Get deposit address** from platform
4. **Send USDT** from their wallet
5. **Verify transaction** (manual or automatic)
6. **See USD balance updated** instantly

### **For Withdrawals:**
1. **Choose network** (TRC20 or BEP20)
2. **Enter amount** and wallet address
3. **Check eligibility** (balance, limits, fees)
4. **Create withdrawal** request
5. **Process withdrawal** (automatic USDT transfer)
6. **Receive USDT** in their wallet

### **For Admins:**
1. **Monitor all deposits** in admin dashboard
2. **View transaction details** with blockchain data
3. **Track conversion rates** (USDT to USD)
4. **Manage platform wallets** securely
5. **Monitor platform balances** for withdrawals
6. **Process withdrawal requests** manually if needed
7. **View withdrawal history** and status

## 🔧 **Configuration Options**

### **Environment Variables**
```env
# Network Configuration
TRON_NETWORK=mainnet          # mainnet or testnet
BSC_NETWORK=mainnet           # mainnet or testnet

# Platform Wallets
PLATFORM_TRC20_WALLET=TYourAddress
PLATFORM_BEP20_WALLET=0xYourAddress

# Platform Private Keys (for withdrawals)
PLATFORM_TRC20_PRIVATE_KEY=your_tron_private_key
PLATFORM_BEP20_PRIVATE_KEY=your_bsc_private_key

# Monitoring
DEPOSIT_CHECK_INTERVAL=30     # seconds
```

### **Customization**
- **Change networks** to testnet for development
- **Update wallet addresses** for production
- **Adjust monitoring intervals** as needed
- **Add new networks** by extending the service

## 🚀 **Production Deployment**

### **1. Set Production Wallets and Private Keys**
```env
PLATFORM_TRC20_WALLET=TProductionWalletAddress
PLATFORM_BEP20_WALLET=0xProductionWalletAddress
PLATFORM_TRC20_PRIVATE_KEY=your_production_tron_private_key
PLATFORM_BEP20_PRIVATE_KEY=your_production_bsc_private_key
```

### **2. Use Mainnet Networks**
```env
TRON_NETWORK=mainnet
BSC_NETWORK=mainnet
```

### **3. Monitor Background Tasks**
- Check logs for deposit verification
- Monitor wallet balances regularly
- Set up alerts for failed verifications
- Monitor platform balances for withdrawals
- Set up alerts for low platform balances

## 📊 **Testing**

### **Testnet Configuration**
```env
TRON_NETWORK=testnet
BSC_NETWORK=testnet
```

### **Test Transactions**
1. **Create test deposit** with small amount
2. **Send test USDT** from testnet wallet
3. **Verify transaction** manually
4. **Check balance update** in database

### **Test Withdrawals**
1. **Create test withdrawal** with small amount
2. **Process withdrawal** to testnet wallet
3. **Verify USDT received** in test wallet
4. **Check balance deduction** in database

## 🔗 **Integration with Frontend**

### **Frontend Implementation:**
1. **Network selection** dropdown
2. **Amount input** with validation
3. **QR code generation** for deposit addresses
4. **Transaction status** tracking
5. **Balance display** in USD
6. **Withdrawal form** with wallet address input
7. **Eligibility checking** before withdrawal
8. **Withdrawal status** tracking

### **Real-time Updates:**
- **WebSocket connection** for status updates
- **Polling** for transaction verification
- **Push notifications** for completed deposits
- **Withdrawal processing** status updates
- **Balance updates** after withdrawals

## 🎯 **Next Steps**

1. **Deploy to production** with real wallet addresses and private keys
2. **Add more networks** (ERC20, Polygon, etc.)
3. **Implement automatic withdrawal processing**
4. **Add transaction fee handling**
5. **Create admin withdrawal interface**
6. **Add withdrawal limits** and KYC requirements
7. **Implement multi-signature** for large withdrawals

**The Web3 integration is now ready for production use!** 🎉 