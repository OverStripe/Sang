from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
import sqlite3

# Database connection
conn = sqlite3.connect('user_history.db', check_same_thread=False)
cursor = conn.cursor()

# Create table for user history if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_history (
    user_id INTEGER,
    username TEXT,
    interaction TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Function to log user interactions
def log_interaction(user_id, username, interaction):
    cursor.execute("""
    INSERT INTO user_history (user_id, username, interaction)
    VALUES (?, ?, ?)
    """, (user_id, username, interaction))
    conn.commit()

# Command: /start and /help
def start(update: Update, context: CallbackContext) -> None:
    """Handles /start and /help commands."""
    user = update.effective_user
    log_interaction(user.id, user.username, "Started bot or viewed help")
    
    help_text = (
        f"Hello, {user.first_name}!\n\n"
        "Welcome to the Telegram Bot. Here are the commands you can use:\n\n"
        "/start or /help - Show this help message.\n"
        "/myhistory - View your interaction history.\n"
        "/showhistory - View all users' interaction history (admin only).\n"
        "/clearhistory - Clear all history (admin only).\n"
        "/deleteuserhistory <user_id> - Delete a specific user's history (admin only).\n\n"
        "Feel free to reach out if you need help!"
    )
    update.message.reply_text(help_text)

# Command: /myhistory
def my_history(update: Update, context: CallbackContext) -> None:
    """Displays the interaction history of the user."""
    user = update.effective_user
    query = """
    SELECT interaction, timestamp FROM user_history
    WHERE user_id = ?
    ORDER BY timestamp DESC
    """
    cursor.execute(query, (user.id,))
    rows = cursor.fetchall()

    if rows:
        history = "\n".join([f"{row[1]}: {row[0]}" for row in rows])
        update.message.reply_text(f"Your history:\n{history}")
    else:
        update.message.reply_text("You have no history.")

# Command: /showhistory
def show_history(update: Update, context: CallbackContext) -> None:
    """Displays the history of all users."""
    query = """
    SELECT user_id, username, interaction, timestamp FROM user_history
    ORDER BY timestamp DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    if rows:
        history = "\n\n".join(
            [f"User ID: {row[0]}, Username: {row[1]}\n{row[3]}: {row[2]}" for row in rows]
        )
        update.message.reply_text(f"History of all users:\n\n{history}")
    else:
        update.message.reply_text("No history found.")

# Command: /clearhistory
def clear_history(update: Update, context: CallbackContext) -> None:
    """Clears all user history."""
    cursor.execute("DELETE FROM user_history")
    conn.commit()
    update.message.reply_text("All history has been cleared.")

# Command: /deleteuserhistory
def delete_user_history(update: Update, context: CallbackContext) -> None:
    """Deletes the history of a specific user."""
    if len(context.args) != 1:
        update.message.reply_text("Usage: /deleteuserhistory <user_id>")
        return
    
    user_id = context.args[0]
    cursor.execute("DELETE FROM user_history WHERE user_id = ?", (user_id,))
    conn.commit()
    update.message.reply_text(f"History for user ID {user_id} has been deleted.")

# Main function
def main():
    TOKEN = "7860010014:AAHc9iMV9d88VA9elIktiGkF6yF-eaYvkX0"

    # Initialize the bot application
    application = ApplicationBuilder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))  # Alias for /help
    application.add_handler(CommandHandler("myhistory", my_history))
    application.add_handler(CommandHandler("showhistory", show_history))
    application.add_handler(CommandHandler("clearhistory", clear_history))
    application.add_handler(CommandHandler("deleteuserhistory", delete_user_history))

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
