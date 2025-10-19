#!/usr/bin/env python3
"""
Simple script to get your Telegram chat ID.
Run this script and send any message to your bot to get your chat ID.
"""

import requests
import time
import json

BOT_TOKEN = "8287038518:AAEbJHuRW3uAIDOvSccWtX8CYHaL77QiAIM"

def get_updates():
    """Get updates from Telegram bot to find chat ID"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
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
    
    chat_id = get_updates()
    if chat_id:
        print(f"\n✅ Found your Chat ID: {chat_id}")
        print("You can now use this Chat ID for the bot setup.")
    else:
        print("\n❌ Could not find Chat ID. Please:")
        print("1. Go to Telegram")
        print("2. Find your bot (search for the bot name)")
        print("3. Send any message to the bot (like 'hello')")
        print("4. Run this script again")