"""
Simple AI message handler for @mention conversations
"""
import discord
from discord.ext import commands
import logging
import asyncio

logger = logging.getLogger(__name__)

class AIMessageHandler(commands.Cog):
    """Handle AI conversations when bot is mentioned"""
    
    def __init__(self, bot, ai_client):
        self.bot = bot
        self.ai_client = ai_client
        self.processed_messages = set()
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle @mention conversations"""
        # Ignore bot messages and duplicates
        if message.author.bot or message.id in self.processed_messages:
            return
        
        # Check if bot is mentioned
        if self.bot.user in message.mentions:
            self.processed_messages.add(message.id)
            
            try:
                # Clean the message content
                content = message.content.replace(f'<@{self.bot.user.id}>', '').strip()
                if not content:
                    content = "Hello! How can I help you with Jewish learning today?"
                
                # Generate AI response
                async with message.channel.typing():
                    response = await asyncio.wait_for(
                        self.ai_client.generate_response(content, message.author.display_name),
                        timeout=15.0
                    )
                
                # Send response
                if response:
                    await message.reply(response[:2000])  # Discord message limit
                else:
                    await message.reply("I'm here to help with Jewish learning! Try asking about Torah, Talmud, or Jewish traditions.")
                    
            except asyncio.TimeoutError:
                await message.reply("I'm processing your question... Try asking about specific Jewish texts or topics!")
            except Exception as e:
                logger.error(f"AI response error: {e}")
                await message.reply("I'm here to help with Jewish learning! Try using the `/help` command to see what I can do.")

async def setup(bot):
    """Setup function for loading the cog"""
    # Only add if AI client is available
    pass  # Will be loaded by main bot if available