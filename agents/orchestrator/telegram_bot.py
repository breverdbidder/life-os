#!/usr/bin/env python3
"""
LIFE OS TELEGRAM BOT
Routes ALL user requests through the orchestrator.
User NEVER touches Claude.ai directly.

This achieves TRUE zero human-in-loop for context management.
"""

import os
import json
import asyncio
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Token limits
MAX_CONTEXT_TOKENS = 150000
CHECKPOINT_THRESHOLD = 0.6  # 60%

class LifeOSBot:
    def __init__(self):
        self.conversations = {}  # user_id -> conversation state
        self.token_counts = {}   # user_id -> current token count
        
    async def call_claude(self, user_id: int, message: str) -> str:
        """Call Claude API with automatic token monitoring"""
        
        # Get or create conversation
        if user_id not in self.conversations:
            self.conversations[user_id] = []
            self.token_counts[user_id] = 0
        
        # Add user message
        self.conversations[user_id].append({"role": "user", "content": message})
        
        # Check if we need to checkpoint BEFORE calling
        if self.token_counts[user_id] > MAX_CONTEXT_TOKENS * CHECKPOINT_THRESHOLD:
            await self.checkpoint(user_id)
            await self.compress_conversation(user_id)
        
        # Call Claude API
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 4096,
                    "system": self.get_system_prompt(user_id),
                    "messages": self.conversations[user_id]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_message = data["content"][0]["text"]
                
                # Track token usage (THIS IS THE KEY - we CAN see this via API)
                input_tokens = data["usage"]["input_tokens"]
                output_tokens = data["usage"]["output_tokens"]
                self.token_counts[user_id] = input_tokens  # Update running count
                
                # Add assistant response to history
                self.conversations[user_id].append({"role": "assistant", "content": assistant_message})
                
                # Check health AFTER response
                health = self.check_health(user_id)
                
                # Auto-checkpoint if needed
                if health["action"]:
                    await self.checkpoint(user_id)
                    if health["action"] == "COMPRESS":
                        await self.compress_conversation(user_id)
                
                return assistant_message, health
            else:
                return f"Error: {response.status_code}", {"status": "error"}
    
    def check_health(self, user_id: int) -> dict:
        """Check token health - THIS WORKS because we control the API"""
        tokens = self.token_counts.get(user_id, 0)
        ratio = tokens / MAX_CONTEXT_TOKENS
        
        health = {
            "status": "healthy",
            "token_ratio": ratio,
            "tokens_used": tokens,
            "action": None
        }
        
        if ratio >= 0.9:
            health["status"] = "critical"
            health["action"] = "COMPRESS"
        elif ratio >= 0.7:
            health["status"] = "warning"
            health["action"] = "CHECKPOINT"
        elif ratio >= CHECKPOINT_THRESHOLD:
            health["status"] = "caution"
            health["action"] = "CHECKPOINT"
        
        return health
    
    async def checkpoint(self, user_id: int):
        """Save checkpoint to Supabase"""
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{SUPABASE_URL}/rest/v1/insights",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "user_id": 1,
                    "insight_type": "TELEGRAM_CHECKPOINT",
                    "title": f"Auto-checkpoint for user {user_id}",
                    "description": json.dumps({
                        "user_id": user_id,
                        "token_count": self.token_counts.get(user_id, 0),
                        "message_count": len(self.conversations.get(user_id, [])),
                        "last_messages": self.conversations.get(user_id, [])[-4:]
                    }),
                    "priority": "high",
                    "status": "active",
                    "source": "telegram_bot"
                }
            )
    
    async def compress_conversation(self, user_id: int):
        """Compress conversation to free up context"""
        if user_id not in self.conversations:
            return
        
        conv = self.conversations[user_id]
        if len(conv) <= 4:
            return
        
        # Keep system context + last 4 messages
        # Summarize the rest
        old_messages = conv[:-4]
        summary_prompt = f"Summarize this conversation context in 2-3 sentences:\n\n"
        for msg in old_messages[-10:]:  # Last 10 of old messages
            summary_prompt += f"{msg['role']}: {msg['content'][:200]}...\n"
        
        # Get summary from Claude
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-haiku-4-5-20251001",  # Use Haiku for compression
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": summary_prompt}]
                }
            )
            
            if response.status_code == 200:
                summary = response.json()["content"][0]["text"]
                # Replace conversation with summary + recent messages
                self.conversations[user_id] = [
                    {"role": "user", "content": f"[Previous context: {summary}]"},
                    {"role": "assistant", "content": "Understood, I have the context."}
                ] + conv[-4:]
                self.token_counts[user_id] = 2000  # Reset estimate
    
    def get_system_prompt(self, user_id: int) -> str:
        return """You are Claude, integrated with Ariel Shapira's Life OS via Telegram.
        
You have FULL context awareness - the bot monitors your token usage and auto-checkpoints.
Never worry about context limits - they're handled automatically.

Domains: BUSINESS (BidDeed.AI, foreclosures), MICHAEL (D1 swimming), FAMILY, PERSONAL
Style: Direct, no softening, action-oriented."""


# Telegram handlers
bot = LifeOSBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Life OS Bot Active\n\n"
        "This bot routes through Claude API with automatic checkpointing.\n"
        "No context limits - I monitor and manage automatically.\n\n"
        "Just send any message to start."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text
    
    # Send typing indicator
    await update.message.chat.send_action("typing")
    
    # Call Claude with monitoring
    response, health = await bot.call_claude(user_id, message)
    
    # Add health indicator
    health_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] in ["caution", "warning"] else "🔴"
    
    # Send response
    await update.message.reply_text(
        f"{response}\n\n"
        f"─────────────────\n"
        f"{health_icon} {health['token_ratio']:.1%} context used"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    health = bot.check_health(user_id)
    msg_count = len(bot.conversations.get(user_id, []))
    
    await update.message.reply_text(
        f"📊 **Session Status**\n\n"
        f"Messages: {msg_count}\n"
        f"Tokens: {health['tokens_used']:,} / {MAX_CONTEXT_TOKENS:,}\n"
        f"Usage: {health['token_ratio']:.1%}\n"
        f"Status: {health['status'].upper()}\n"
        f"Action: {health['action'] or 'None needed'}"
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await bot.checkpoint(user_id)  # Save before clearing
    bot.conversations[user_id] = []
    bot.token_counts[user_id] = 0
    await update.message.reply_text("✅ Conversation cleared and checkpointed")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Life OS Telegram Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
