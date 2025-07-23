#!/bin/bash

echo "🚀 Starting Updated ID Card Bot System..."

# Start the updated Telegram bot in background
echo "📱 Starting Updated Telegram Bot..."
python3 updated_bot.py &
BOT_PID=$!

# Wait a moment for bot to initialize
sleep 3

# Start the admin panel
echo "🔧 Starting Admin Panel..."
cd admin_panel
source venv/bin/activate
python src/main.py &
ADMIN_PID=$!

echo "✅ Updated system started successfully!"
echo "📱 Telegram Bot PID: $BOT_PID"
echo "🔧 Admin Panel PID: $ADMIN_PID"
echo "🌐 Admin Panel: http://localhost:5000"
echo ""
echo "🆕 New Features:"
echo "   📸 Photo upload support"
echo "   🎨 Improved ID card templates"
echo "   🚫 Fixed duplicate fields"
echo ""
echo "To stop the system, run: kill $BOT_PID $ADMIN_PID"

# Wait for user input to stop
read -p "Press Enter to stop the system..."

# Stop both processes
kill $BOT_PID $ADMIN_PID 2>/dev/null
echo "🛑 System stopped."

