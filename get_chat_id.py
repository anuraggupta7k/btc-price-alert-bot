#!/usr/bin/env python3

import requests
import json
import sys
import os

def get_chat_id():
    """
    Get your Telegram chat ID by fetching recent messages from your bot.
    Make sure to send a message to your bot first!
    
    Usage: 
    export TELEGRAM_BOT_TOKEN="your-bot-token"
    python get_chat_id.py
    """
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        print("\nPlease set your bot token first:")
        print("export TELEGRAM_BOT_TOKEN='your-bot-token-here'")
        print("\nThen run this script again.")
        sys.exit(1)
    
    return BOT_TOKEN

def get_updates(bot_token):
    """Get updates from Telegram bot to find chat ID"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("ok") and data.get("result"):
            print("Recent messages:")
            for update in data["result"][-5:]:  # Show last 5 messages
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    username = msg["from"].get("username", "Unknown")
                    text = msg.get("text", "No text")
                    print(f"Chat ID: {chat_id}, From: @{username}, Message: {text}")
            
            # Get the most recent chat ID
            if data["result"]:
                latest_chat_id = data["result"][-1]["message"]["chat"]["id"]
                print(f"\n🎯 Your Chat ID is: {latest_chat_id}")
                return str(latest_chat_id)
        else:
            print("No messages found. Please send a message to your bot first.")
            print("Go to Telegram and send any message to your bot, then run this script again.")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return None

if __name__ == "__main__":
    print("Getting your Telegram Chat ID...")
    print("If no messages are found, send a message to your bot first!")
    print("-" * 50)
    
    bot_token = get_chat_id()
    chat_id = get_updates(bot_token)
    if chat_id:
        print(f"\n✅ Found your Chat ID: {chat_id}")
        print("You can now use this Chat ID for the bot setup.")
    else:
        print("\n❌ Could not find Chat ID. Please:")
        print("1. Go to Telegram")
        print("2. Find your bot (search for the bot name)")
        print("3. Send any message to the bot (like 'hello')")
        print("4. Run this script again")