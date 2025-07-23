# 🚀 Complete Setup Guide - Telegram ID Card Bot

This guide will walk you through setting up the Telegram ID Card Generator Bot from scratch.

## 📋 Prerequisites

Before you begin, ensure you have:
- Python 3.11 or higher installed
- A Telegram account
- Basic command line knowledge
- Internet connection

## 🤖 Step 1: Create Telegram Bot

1. **Open Telegram and search for @BotFather**
2. **Start a conversation and send `/newbot`**
3. **Choose a name for your bot** (e.g., "ID Card Generator")
4. **Choose a username** (must end with 'bot', e.g., "idcard_generator_bot")
5. **Copy the bot token** - you'll need this later
6. **Note: Your current token is already configured:** `7785718358:AAFLAH6wI5PaYn83iMeG7Vhe_7qYk4e6ZIU`

## 💻 Step 2: System Setup

### Option A: Quick Start (Recommended)
```bash
# 1. Navigate to the project directory
cd /path/to/telegram-id-card-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the system
./start_bot.sh
```

### Option B: Manual Setup
```bash
# 1. Install Python dependencies
pip install python-telegram-bot==22.3
pip install qrcode[pil]==8.2
pip install Pillow==11.3.0
pip install flask==3.1.0
pip install flask-cors==5.0.0

# 2. Start Telegram bot
python3 bot.py

# 3. In another terminal, start admin panel
cd admin_panel
source venv/bin/activate
python src/main.py
```

## 🔧 Step 3: Configuration

### Bot Token Configuration
If you need to change the bot token:

1. **Edit `bot.py`:**
   ```python
   # Line 18
   BOT_TOKEN = "YOUR_NEW_BOT_TOKEN_HERE"
   ```

### Admin Credentials
Change the default admin credentials:

1. **Edit `admin_panel/src/routes/admin.py`:**
   ```python
   # Lines 12-13
   ADMIN_USERNAME = "your_username"
   ADMIN_PASSWORD = "your_secure_password"
   ```

## 🎯 Step 4: First Run

### 1. Start the System
```bash
./start_bot.sh
```

You should see:
```
🚀 Starting ID Card Bot System...
📱 Starting Telegram Bot...
🤖 Bot started successfully!
🔗 Bot is running and ready to receive messages
🔧 Starting Admin Panel...
✅ System started successfully!
🌐 Admin Panel: http://localhost:5000
```

### 2. Test the Bot
1. **Find your bot on Telegram** (search for the username you created)
2. **Send `/start`** to begin
3. **You should receive a welcome message**

### 3. Access Admin Panel
1. **Open browser and go to:** `http://localhost:5000`
2. **Login with credentials:**
   - Username: `itzAyush`
   - Password: `admin123` (or your custom password)

## 🎫 Step 5: Generate First Tokens

### Via Admin Panel (Recommended)
1. **Login to admin panel**
2. **Click "Generate 10 Tokens"**
3. **Copy the generated tokens**

### Via Telegram Bot
1. **Send `/admin` to the bot**
2. **Click "Generate 10 Tokens"**
3. **Copy the tokens from the bot message**

## 🎓 Step 6: Generate First ID Card

1. **Send `/generate` to the bot**
2. **Follow the prompts:**
   - Enter your name: `John Doe`
   - Enter father's name: `Robert Doe`
   - Enter phone: `+91 9876543210`
   - Select a college from the options
3. **Enter one of the tokens you generated**
4. **Receive your ID card!**

## 📊 Step 7: Monitor Usage

### Admin Panel Dashboard
- View real-time statistics
- Monitor token usage
- See all generated ID cards
- Manage users

### Bot Commands for Monitoring
- `/mystats` - View your personal statistics
- `/admin` - Quick admin actions (admin only)

## 🔧 Advanced Configuration

### Custom College Templates
To add or modify college templates:

1. **Add college info in `bot.py`:**
   ```python
   COLLEGES = {
       "6": "Your New College Name"
   }
   
   DEPARTMENTS = {
       "6": ["Department 1", "Department 2", "Department 3"]
   }
   ```

2. **Update `enhanced_id_generator.py`:**
   ```python
   self.colleges = {
       "6": {
           "name": "Your New College Name",
           "template": "/path/to/template.png",
           "colors": {"primary": "#1E3A8A", "secondary": "#3B82F6", "text": "#1F2937"},
           "authority": "Academic Office, Your College"
       }
   }
   ```

### Database Customization
The system uses SQLite by default. To use a different database:

1. **Install database driver** (e.g., `pip install psycopg2` for PostgreSQL)
2. **Update connection string in `database.py`**
3. **Modify SQL queries if needed for database-specific syntax**

### Security Enhancements

#### Environment Variables
Create a `.env` file:
```bash
BOT_TOKEN=your_bot_token_here
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
DATABASE_PATH=/path/to/database.db
```

#### HTTPS Setup (Production)
1. **Get SSL certificate** (Let's Encrypt recommended)
2. **Configure reverse proxy** (nginx example):
   ```nginx
   server {
       listen 443 ssl;
       server_name yourdomain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🚀 Production Deployment

### Using PM2 (Recommended)
```bash
# Install PM2
npm install -g pm2

# Start bot with PM2
pm2 start bot.py --name "telegram-bot" --interpreter python3

# Start admin panel with PM2
cd admin_panel
pm2 start src/main.py --name "admin-panel" --interpreter python3

# Save PM2 configuration
pm2 save
pm2 startup
```

### Using systemd
Create service files:

**Bot service (`/etc/systemd/system/telegram-bot.service`):**
```ini
[Unit]
Description=Telegram ID Card Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Admin panel service (`/etc/systemd/system/admin-panel.service`):**
```ini
[Unit]
Description=Admin Panel
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/bot/admin_panel
ExecStart=/path/to/bot/admin_panel/venv/bin/python src/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl enable telegram-bot admin-panel
sudo systemctl start telegram-bot admin-panel
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### Bot Not Starting
**Error:** `RuntimeError: ExtBot is not properly initialized`
**Solution:** This is normal during testing. The bot will work fine when running normally.

#### Permission Denied
**Error:** `Permission denied: './start_bot.sh'`
**Solution:** 
```bash
chmod +x start_bot.sh
```

#### Port Already in Use
**Error:** `Address already in use`
**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>
```

#### Database Locked
**Error:** `database is locked`
**Solution:**
```bash
# Check for zombie processes
ps aux | grep python

# Kill any hanging processes
pkill -f bot.py
pkill -f main.py
```

#### Missing Dependencies
**Error:** `ModuleNotFoundError`
**Solution:**
```bash
pip install -r requirements.txt
```

### Performance Optimization

#### Cleanup Old Files
Add to crontab for automatic cleanup:
```bash
# Edit crontab
crontab -e

# Add cleanup job (runs daily at 2 AM)
0 2 * * * find /path/to/generated_cards -name "*.png" -mtime +7 -delete
```

#### Database Maintenance
```bash
# Backup database
cp id_card_bot.db id_card_bot.db.backup

# Vacuum database (optimize)
sqlite3 id_card_bot.db "VACUUM;"
```

## 📞 Getting Help

### Log Files
Check these locations for error messages:
- Console output where bot is running
- Flask debug messages
- System logs: `/var/log/syslog`

### Testing Commands
```bash
# Test bot connectivity
python3 -c "from telegram import Bot; print(Bot('YOUR_TOKEN').get_me())"

# Test database
python3 -c "from database import Database; db = Database(); print('Database OK')"

# Test ID card generation
python3 -c "from enhanced_id_generator import EnhancedIDCardGenerator; gen = EnhancedIDCardGenerator(); print('Generator OK')"
```

### Support Checklist
Before asking for help, check:
- [ ] All dependencies installed
- [ ] Bot token is correct
- [ ] Admin credentials are set
- [ ] Ports are not blocked
- [ ] Database file permissions
- [ ] Python version (3.11+)
- [ ] Internet connectivity

## 🎉 Success!

If everything is working correctly, you should have:
- ✅ Telegram bot responding to messages
- ✅ Admin panel accessible at http://localhost:5000
- ✅ Ability to generate tokens
- ✅ Ability to create ID cards
- ✅ Database storing all information

**Your Telegram ID Card Bot is now ready for use!**

---

**Need more help?** Contact @itzAyush on Telegram or refer to the main README.md file.

