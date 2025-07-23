import logging
import os
import random
import string
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters, ContextTypes
from database import Database
from enhanced_id_generator import EnhancedIDCardGenerator

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "7785718358:AAFLAH6wI5PaYn83iMeG7Vhe_7qYk4e6ZIU"

# Conversation states
WAITING_FOR_NAME, WAITING_FOR_FATHER_NAME, WAITING_FOR_PHONE, WAITING_FOR_PHOTO, WAITING_FOR_COLLEGE, WAITING_FOR_TOKEN = range(6)
ADMIN_WAITING_FOR_TOKEN_COUNT = 100

# Initialize database and ID card generator
db = Database()
id_generator = EnhancedIDCardGenerator()

# College options
COLLEGES = {
    "1": "Indian Institute of Science (IISc) Bangalore",
    "2": "Indian Institute of Technology (IIT) Madras", 
    "3": "Indian Institute of Technology (IIT) Bombay",
    "4": "Indian Institute of Technology (IIT) Delhi",
    "5": "Jawaharlal Nehru University (JNU)"
}

# Departments for each college
DEPARTMENTS = {
    "1": ["Aerospace Engineering", "Biochemistry", "Materials Engineering", "Electrical Engineering", "Computer Science"],
    "2": ["Aerospace Engineering", "Applied Mechanics", "Biotechnology", "Chemical Engineering", "Civil Engineering", "Computer Science and Engineering", "Electrical Engineering", "Mechanical Engineering"],
    "3": ["Aerospace Engineering", "Chemical Engineering", "Chemistry", "Civil Engineering", "Computer Science and Engineering", "Electrical Engineering", "Mechanical Engineering"],
    "4": ["Applied Mechanics", "Biochemical Engineering and Biotechnology", "Chemical Engineering", "Chemistry", "Civil Engineering", "Computer Science and Engineering", "Electrical Engineering", "Mechanical Engineering"],
    "5": ["Arts and Aesthetics", "Biotechnology", "Computer & Systems Sciences", "Environmental Sciences", "International Studies", "Language, Literature & Culture Studies", "Life Sciences", "Physical Sciences", "Social Sciences"]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    user = update.effective_user
    
    # Add user to database
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    welcome_message = f"""
🎓 **Welcome to Enhanced ID Card Generator Bot!** 🎓

Hello {user.first_name}! I can help you generate professional ID cards for top Indian colleges with enhanced features!

**✨ NEW FEATURES:**
📸 Photo upload support
🏛️ College logos integrated
🩸 Blood group included
📝 Enhanced text formatting
🎨 Professional design

**Available Commands:**
🆔 /generate - Generate a new ID card
📊 /mystats - View your ID card history
ℹ️ /help - Get help and information

**Admin Commands (for @itzAyush):**
🔑 /admin - Access admin panel
🎫 /tokens - Generate tokens
📈 /stats - View bot statistics

**How it works:**
1. Use /generate to start creating an ID card
2. Provide your details (Name, Father's Name, Phone)
3. Upload your photo (optional but recommended)
4. Choose from top 5 colleges
5. Enter a valid token
6. Download your high-quality ID card with logo and blood group!

Ready to get started? Use /generate to create your first enhanced ID card! 🚀
"""
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command handler"""
    help_text = """
🆘 **Help & Information** 🆘

**How to generate an enhanced ID card:**
1. Use /generate command
2. Enter your full name
3. Enter your father's name
4. Enter your phone number
5. Upload your photo (optional but recommended)
6. Choose a college from the list
7. Enter a valid token (get from admin)
8. Download your enhanced ID card!

**✨ Enhanced Features:**
✅ High-quality ID card generation with college logos
✅ Photo upload support with automatic processing
✅ QR code embedded for verification
✅ Professional templates for top colleges
✅ Blood group field (randomly assigned)
✅ Enhanced text formatting (bold names, larger institution names)
✅ Student ID numbers
✅ Issue date and authority
✅ Secure token-based system
✅ Download in high resolution (300 DPI)

**Photo Guidelines:**
📸 Clear, front-facing photo
📸 Good lighting
📸 Plain background preferred
📸 JPG, PNG formats supported
📸 Maximum 20MB file size

**Colleges Available:**
1. Indian Institute of Science (IISc) Bangalore
2. Indian Institute of Technology (IIT) Madras
3. Indian Institute of Technology (IIT) Bombay
4. Indian Institute of Technology (IIT) Delhi
5. Jawaharlal Nehru University (JNU)

**Need a token?** Contact the admin @itzAyush

**Commands:**
/start - Welcome message
/generate - Create new enhanced ID card
/mystats - View your cards
/help - This help message
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def generate_id_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start ID card generation process"""
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    await update.message.reply_text(
        "🎓 **Let's create your enhanced ID card!**\n\n"
        "✨ **New Features:** College logos, blood group, enhanced formatting!\n\n"
        "Please enter your **full name** as you want it to appear on the ID card:",
        parse_mode='Markdown'
    )
    
    return WAITING_FOR_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get student name"""
    context.user_data['student_name'] = update.message.text.strip()
    
    await update.message.reply_text(
        "👨‍👦 Great! Now please enter your **father's name**:",
        parse_mode='Markdown'
    )
    
    return WAITING_FOR_FATHER_NAME

async def get_father_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get father's name"""
    context.user_data['father_name'] = update.message.text.strip()
    
    await update.message.reply_text(
        "📱 Perfect! Now please enter your **phone number**:",
        parse_mode='Markdown'
    )
    
    return WAITING_FOR_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get phone number"""
    phone = update.message.text.strip()
    
    # Basic phone validation
    if not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
        await update.message.reply_text(
            "❌ Please enter a valid phone number (digits only):"
        )
        return WAITING_FOR_PHONE
    
    context.user_data['phone'] = phone
    
    # Create photo upload options
    keyboard = [
        [InlineKeyboardButton("📸 Upload Photo", callback_data="upload_photo")],
        [InlineKeyboardButton("⏭️ Skip Photo", callback_data="skip_photo")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📸 **Photo Upload**\n\n"
        "Would you like to upload your photo for the ID card?\n\n"
        "**Recommended:** Upload a clear, front-facing photo for a professional ID card.\n"
        "**Optional:** You can skip this step if you prefer.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return WAITING_FOR_PHOTO

async def photo_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle photo upload choice"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "upload_photo":
        await query.edit_message_text(
            "📸 **Upload Your Photo**\n\n"
            "Please send your photo now. Make sure it's:\n"
            "✅ Clear and well-lit\n"
            "✅ Front-facing\n"
            "✅ Plain background (preferred)\n"
            "✅ JPG or PNG format\n\n"
            "Send the photo as a file or image:",
            parse_mode='Markdown'
        )
        return WAITING_FOR_PHOTO
    
    elif query.data == "skip_photo":
        context.user_data['photo_path'] = None
        return await show_college_selection(query, context)

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get user photo"""
    user_id = update.effective_user.id
    
    try:
        if update.message.photo:
            # Get the largest photo
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()
            
            # Download photo
            photo_path = f"temp_photo_{user_id}.jpg"
            await photo_file.download_to_drive(photo_path)
            
            # Save photo using the generator
            saved_photo_path = id_generator.save_user_photo(photo_path, user_id)
            
            # Clean up temp file
            if os.path.exists(photo_path):
                os.remove(photo_path)
            
            if saved_photo_path:
                context.user_data['photo_path'] = saved_photo_path
                await update.message.reply_text(
                    "✅ **Photo uploaded successfully!**\n\n"
                    "Now let's choose your college..."
                )
            else:
                await update.message.reply_text(
                    "❌ **Error uploading photo.** Continuing without photo..."
                )
                context.user_data['photo_path'] = None
        
        elif update.message.document:
            # Handle document upload
            document = update.message.document
            
            # Check if it's an image
            if document.mime_type and document.mime_type.startswith('image/'):
                document_file = await document.get_file()
                
                # Download document
                photo_path = f"temp_photo_{user_id}.jpg"
                await document_file.download_to_drive(photo_path)
                
                # Save photo using the generator
                saved_photo_path = id_generator.save_user_photo(photo_path, user_id)
                
                # Clean up temp file
                if os.path.exists(photo_path):
                    os.remove(photo_path)
                
                if saved_photo_path:
                    context.user_data['photo_path'] = saved_photo_path
                    await update.message.reply_text(
                        "✅ **Photo uploaded successfully!**\n\n"
                        "Now let's choose your college..."
                    )
                else:
                    await update.message.reply_text(
                        "❌ **Error uploading photo.** Continuing without photo..."
                    )
                    context.user_data['photo_path'] = None
            else:
                await update.message.reply_text(
                    "❌ **Please send an image file (JPG or PNG).**\n\n"
                    "Try again or use the skip option:"
                )
                return WAITING_FOR_PHOTO
        else:
            await update.message.reply_text(
                "❌ **Please send a photo or image file.**\n\n"
                "Try again or use the skip option:"
            )
            return WAITING_FOR_PHOTO
        
        # Show college selection
        return await show_college_selection_message(update, context)
        
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await update.message.reply_text(
            "❌ **Error processing photo.** Continuing without photo..."
        )
        context.user_data['photo_path'] = None
        return await show_college_selection_message(update, context)

async def show_college_selection_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show college selection as a new message"""
    # Create college selection keyboard
    keyboard = []
    for key, college in COLLEGES.items():
        keyboard.append([InlineKeyboardButton(f"{key}. {college}", callback_data=f"college_{key}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🏛️ **Choose your college:**\n\n"
        "Select from the top 5 colleges in India:\n"
        "✨ Each college has its authentic logo and branding!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return WAITING_FOR_COLLEGE

async def show_college_selection(query, context) -> int:
    """Show college selection by editing message"""
    # Create college selection keyboard
    keyboard = []
    for key, college in COLLEGES.items():
        keyboard.append([InlineKeyboardButton(f"{key}. {college}", callback_data=f"college_{key}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🏛️ **Choose your college:**\n\n"
        "Select from the top 5 colleges in India:\n"
        "✨ Each college has its authentic logo and branding!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return WAITING_FOR_COLLEGE

async def college_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle college selection"""
    query = update.callback_query
    await query.answer()
    
    college_id = query.data.split('_')[1]
    college_name = COLLEGES[college_id]
    
    # Randomly assign department
    departments = DEPARTMENTS[college_id]
    selected_department = random.choice(departments)
    
    context.user_data['college'] = college_name
    context.user_data['college_id'] = college_id
    context.user_data['department'] = selected_department
    
    await query.edit_message_text(
        f"✅ **College Selected:** {college_name}\n"
        f"📚 **Department:** {selected_department} (Auto-assigned)\n"
        f"🩸 **Blood Group:** Will be randomly assigned\n"
        f"🏛️ **Logo:** Will be included in your ID card\n\n"
        f"🎫 Now please enter your **token** to generate the enhanced ID card:",
        parse_mode='Markdown'
    )
    
    return WAITING_FOR_TOKEN

async def get_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get and validate token"""
    token = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Validate token
    if not db.use_token(token, user_id):
        await update.message.reply_text(
            "❌ **Invalid or already used token!**\n\n"
            "Please contact the admin @itzAyush to get a valid token.",
            parse_mode='Markdown'
        )
        return WAITING_FOR_TOKEN
    
    # Generate ID card
    await update.message.reply_text("🔄 **Generating your enhanced ID card...** Please wait...")
    
    try:
        # Get user data
        student_name = context.user_data['student_name']
        father_name = context.user_data['father_name']
        phone = context.user_data['phone']
        college = context.user_data['college']
        college_id = context.user_data['college_id']
        department = context.user_data['department']
        photo_path = context.user_data.get('photo_path')
        
        # Generate QR code data
        qr_data = f"Name: {student_name}\nFather: {father_name}\nPhone: {phone}\nCollege: {college}\nDept: {department}\nToken: {token}"
        
        # Generate enhanced ID card
        card_path = await id_generator.generate_id_card(
            college_id=college_id,
            student_name=student_name,
            father_name=father_name,
            phone=phone,
            department=department,
            qr_data=qr_data,
            photo_path=photo_path
        )
        
        # Save to database
        db.save_id_card(
            user_id=user_id,
            student_name=student_name,
            father_name=father_name,
            phone=phone,
            college=college,
            department=department,
            issue_authority="Academic Office",
            qr_data=qr_data,
            card_path=card_path,
            token_used=token
        )
        
        # Send the enhanced ID card
        with open(card_path, 'rb') as card_file:
            photo_status = "✅ With your photo" if photo_path else "📷 Without photo"
            
            await update.message.reply_photo(
                photo=card_file,
                caption=f"🎉 **Your enhanced ID card is ready!** {photo_status}\n\n"
                       f"✨ **Enhanced Features:**\n"
                       f"🏛️ College logo included\n"
                       f"📝 Bold and enlarged name\n"
                       f"🩸 Blood group assigned\n"
                       f"🆔 Student ID number\n"
                       f"📅 Issue date included\n\n"
                       f"👤 **Name:** {student_name}\n"
                       f"👨‍👦 **Father:** {father_name}\n"
                       f"📱 **Phone:** {phone}\n"
                       f"🏛️ **College:** {college}\n"
                       f"📚 **Department:** {department}\n\n"
                       f"✅ High-quality download available (300 DPI)!\n"
                       f"🔒 Enhanced QR code embedded for verification",
                parse_mode='Markdown'
            )
        
        await update.message.reply_text(
            "✨ **Enhanced ID Card Generated Successfully!**\n\n"
            "📥 You can download the high-quality image above\n"
            "🔄 Use /generate to create another enhanced ID card\n"
            "📊 Use /mystats to view all your ID cards\n\n"
            "🎯 **What's new in this version:**\n"
            "• College logos integrated\n"
            "• Bold and enlarged student names\n"
            "• Blood group field added\n"
            "• Enhanced professional design\n"
            "• Better text formatting",
            parse_mode='Markdown'
        )
        
        # Cleanup old files periodically
        id_generator.cleanup_old_cards()
        id_generator.cleanup_old_photos()
        
    except Exception as e:
        logger.error(f"Error generating enhanced ID card: {e}")
        await update.message.reply_text(
            "❌ **Error generating enhanced ID card!**\n\n"
            "Please try again or contact support.",
            parse_mode='Markdown'
        )
    
    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text(
        "❌ **ID card generation cancelled.**\n\n"
        "Use /generate to start again anytime!",
        parse_mode='Markdown'
    )
    context.user_data.clear()
    return ConversationHandler.END

async def my_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's ID card statistics"""
    user_id = update.effective_user.id
    cards = db.get_user_id_cards(user_id)
    
    if not cards:
        await update.message.reply_text(
            "📊 **Your Statistics**\n\n"
            "❌ You haven't generated any ID cards yet.\n\n"
            "Use /generate to create your first enhanced ID card!",
            parse_mode='Markdown'
        )
        return
    
    stats_text = f"📊 **Your Enhanced ID Card Statistics**\n\n"
    stats_text += f"🎫 **Total Cards Generated:** {len(cards)}\n\n"
    
    stats_text += "📋 **Your ID Cards:**\n"
    for i, card in enumerate(cards[:5], 1):  # Show last 5 cards
        stats_text += f"{i}. **{card['student_name']}** - {card['college'][:30]}...\n"
        stats_text += f"   📅 Created: {card['created_at'][:10]}\n\n"
    
    if len(cards) > 5:
        stats_text += f"... and {len(cards) - 5} more cards\n\n"
    
    stats_text += "🔄 Use /generate to create a new enhanced ID card!"
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

# Admin functions
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin panel access"""
    user_id = update.effective_user.id
    
    if not db.is_admin(user_id):
        await update.message.reply_text("❌ Access denied. Admin only.")
        return
    
    # Get statistics
    token_stats = db.get_token_stats()
    all_cards = db.get_all_id_cards()
    
    admin_text = f"""
🔐 **Enhanced Admin Panel**

📊 **Statistics:**
🎫 Total Tokens: {token_stats['total_tokens']}
✅ Used Tokens: {token_stats['used_tokens']}
🆓 Available Tokens: {token_stats['available_tokens']}
🎓 Total Enhanced ID Cards: {len(all_cards)}

✨ **Enhanced Features Active:**
🏛️ College logos integrated
📝 Bold and enlarged names
🩸 Blood group fields
🎨 Professional design

**Admin Commands:**
🎫 /tokens - Generate new tokens
📈 /stats - Detailed statistics
📋 /allcards - View all ID cards

**Quick Actions:**
"""
    
    keyboard = [
        [InlineKeyboardButton("🎫 Generate 10 Tokens", callback_data="gen_tokens_10")],
        [InlineKeyboardButton("🎫 Generate 50 Tokens", callback_data="gen_tokens_50")],
        [InlineKeyboardButton("📊 View All Cards", callback_data="view_all_cards")],
        [InlineKeyboardButton("📈 Detailed Stats", callback_data="detailed_stats")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(admin_text, reply_markup=reply_markup, parse_mode='Markdown')

async def generate_tokens_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate tokens command"""
    user_id = update.effective_user.id
    
    if not db.is_admin(user_id):
        await update.message.reply_text("❌ Access denied. Admin only.")
        return
    
    await update.message.reply_text(
        "🎫 **Enhanced Token Generator**\n\n"
        "How many tokens would you like to generate?\n"
        "Enter a number (1-100):",
        parse_mode='Markdown'
    )

def generate_token_code() -> str:
    """Generate a random token code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle admin panel callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not db.is_admin(user_id):
        await query.edit_message_text("❌ Access denied.")
        return
    
    if query.data.startswith("gen_tokens_"):
        count = int(query.data.split("_")[2])
        
        # Generate tokens
        generated_tokens = []
        for _ in range(count):
            token_code = generate_token_code()
            if db.create_token(token_code, user_id):
                generated_tokens.append(token_code)
        
        if generated_tokens:
            tokens_text = f"✅ **Generated {len(generated_tokens)} tokens:**\n\n"
            tokens_text += "\n".join([f"`{token}`" for token in generated_tokens])
            tokens_text += f"\n\n📋 Copy and share these tokens with users for enhanced ID cards."
            
            await query.edit_message_text(tokens_text, parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ Failed to generate tokens.")
    
    elif query.data == "view_all_cards":
        all_cards = db.get_all_id_cards()
        
        if not all_cards:
            await query.edit_message_text("📋 No enhanced ID cards generated yet.")
            return
        
        cards_text = f"📋 **All Enhanced ID Cards ({len(all_cards)} total)**\n\n"
        
        for i, card in enumerate(all_cards[:10], 1):  # Show first 10
            cards_text += f"{i}. **{card['student_name']}**\n"
            cards_text += f"   🏛️ {card['college'][:30]}...\n"
            cards_text += f"   👤 @{card['username'] or 'N/A'}\n"
            cards_text += f"   📅 {card['created_at'][:10]}\n\n"
        
        if len(all_cards) > 10:
            cards_text += f"... and {len(all_cards) - 10} more enhanced cards"
        
        await query.edit_message_text(cards_text, parse_mode='Markdown')
    
    elif query.data == "detailed_stats":
        token_stats = db.get_token_stats()
        all_cards = db.get_all_id_cards()
        
        # College distribution
        college_count = {}
        for card in all_cards:
            college = card['college']
            college_count[college] = college_count.get(college, 0) + 1
        
        stats_text = f"""
📈 **Enhanced Bot Detailed Statistics**

🎫 **Token Statistics:**
• Total Generated: {token_stats['total_tokens']}
• Used: {token_stats['used_tokens']}
• Available: {token_stats['available_tokens']}
• Usage Rate: {(token_stats['used_tokens']/max(token_stats['total_tokens'], 1)*100):.1f}%

🎓 **Enhanced ID Card Statistics:**
• Total Generated: {len(all_cards)}

🏛️ **College Distribution:**
"""
        
        for college, count in sorted(college_count.items(), key=lambda x: x[1], reverse=True):
            college_short = college.split('(')[0].strip()[:25]
            stats_text += f"• {college_short}: {count}\n"
        
        stats_text += f"\n✨ **Enhanced Features:**\n"
        stats_text += f"• College logos: ✅ Active\n"
        stats_text += f"• Bold names: ✅ Active\n"
        stats_text += f"• Blood groups: ✅ Active\n"
        stats_text += f"• Photo upload: ✅ Active\n"
        
        await query.edit_message_text(stats_text, parse_mode='Markdown')

def main() -> None:
    """Start the enhanced bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler for ID card generation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('generate', generate_id_card)],
        states={
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            WAITING_FOR_FATHER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_father_name)],
            WAITING_FOR_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            WAITING_FOR_PHOTO: [
                CallbackQueryHandler(photo_choice, pattern='^(upload_photo|skip_photo)$'),
                MessageHandler(filters.PHOTO | filters.Document.IMAGE, get_photo)
            ],
            WAITING_FOR_COLLEGE: [CallbackQueryHandler(college_selection, pattern='^college_')],
            WAITING_FOR_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_token)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("mystats", my_stats))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("tokens", generate_tokens_command))
    application.add_handler(CallbackQueryHandler(admin_callback_handler))
    
    # Start the enhanced bot
    print("🤖 Enhanced Bot started successfully!")
    print("✨ Features: College logos, bold names, blood groups, photo upload")
    print("🔗 Bot is running and ready to receive messages")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

