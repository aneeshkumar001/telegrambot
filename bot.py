import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Put your admin user ID here
ADMIN_ID = 1851017428

# Bot token will be set from environment variable BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# In-memory user balances and states (use DB for real app)
user_balances = {}
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_balances.setdefault(user_id, 0)
    keyboard = [
        [InlineKeyboardButton("▶️ Watch Ads", callback_data='watch_ads')],
        [InlineKeyboardButton("💰 Check Balance", callback_data='check_balance')],
        [InlineKeyboardButton("💸 Withdraw Earnings", callback_data='withdraw')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to Money Bucks Bot!\nChoose an option:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in user_balances:
        user_balances[user_id] = 0

    if query.data == 'watch_ads':
        # Simulate earning
        user_balances[user_id] += 5
        await query.edit_message_text(f"Thanks for watching ads! You earned 5 USDT.\nYour balance: {user_balances[user_id]} USDT")

    elif query.data == 'check_balance':
        balance = user_balances.get(user_id, 0)
        await query.edit_message_text(f"Your current balance is: {balance} USDT")

    elif query.data == 'withdraw':
        balance = user_balances.get(user_id, 0)
        if balance < 10:
            await query.edit_message_text("Minimum withdrawal is 10 USDT. Earn more to withdraw.")
        else:
            user_states[user_id] = 'awaiting_withdraw_address'
            await query.edit_message_text("Please send your BEP20 USDT wallet address to withdraw.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_states.get(user_id) == 'awaiting_withdraw_address':
        # Handle withdrawal address input
        balance = user_balances.get(user_id, 0)
        if balance < 10:
            await update.message.reply_text("You do not have enough balance to withdraw.")
        else:
            # In real app: process withdrawal request here
            user_balances[user_id] = 0
            user_states[user_id] = None
            await update.message.reply_text(f"Withdrawal request received for address:\n{text}\nOur team will process it soon.")
    else:
        await update.message.reply_text("Please use the buttons to interact with the bot. Send /start to see menu.")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    text = (
        "Admin Panel:\n"
        "- /users : Show users\n"
        "- /setreward <amount> : Set reward per ad\n"
        "- /setmin <amount> : Set minimum withdrawal\n"
        "- /withdraws : Show withdrawal requests (mock)\n"
    )
    await update.message.reply_text(text)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I didn't understand that command.")

def main():
    import os
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN environment variable not set.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
