from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import sqlite3

# Connect to your database
conn = sqlite3.connect('user_history.db', check_same_thread=False)
cursor = conn.cursor()

# Create a table for storing user interactions
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

# Command: Start
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    log_interaction(user.id, user.username, "Started bot")
    update.message.reply_text(f"Hello {user.first_name}! I'm here to manage your history.")

# Command: Show all history
def show_history(update: Update, context: CallbackContext) -> None:
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

# Command: Clear all history
def clear_history(update: Update, context: CallbackContext) -> None:
    cursor.execute("DELETE FROM user_history")
    conn.commit()
    update.message.reply_text("All history has been cleared.")

# Command: Show my history
def my_history(update: Update, context: CallbackContext) -> None:
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

# Command: Delete history for a specific user
def delete_user_history(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        update.message.reply_text("Usage: /deleteuserhistory <user_id>")
        return
    
    user_id = context.args[0]
    cursor.execute("DELETE FROM user_history WHERE user_id = ?", (user_id,))
    conn.commit()
    update.message.reply_text(f"History for user ID {user_id} has been deleted.")

# Main function to run the bot
def main():
    TOKEN = "7860010014:AAHc9iMV9d88VA9elIktiGkF6yF-eaYvkX0"
    updater = Updater(TOKEN)
    
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("showhistory", show_history))
    dispatcher.add_handler(CommandHandler("clearhistory", clear_history))
    dispatcher.add_handler(CommandHandler("myhistory", my_history))
    dispatcher.add_handler(CommandHandler("deleteuserhistory", delete_user_history))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
  
