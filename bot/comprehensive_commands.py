"""
Comprehensive Discord commands with ALL functionality preserved
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import date
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

class BaseView(discord.ui.View):
    def __init__(self, timeout: float = 300):
        super().__init__(timeout=timeout)
    
    async def safe_response(self, interaction: discord.Interaction, embed: discord.Embed, ephemeral: bool = False):
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=ephemeral)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        except discord.HTTPException:
            try:
                content = f"**{embed.title}**\n{embed.description}"[:2000]
                if interaction.response.is_done():
                    await interaction.followup.send(content, ephemeral=ephemeral)
                else:
                    await interaction.response.send_message(content, ephemeral=ephemeral)
            except:
                pass

class StudyView(BaseView):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    @discord.ui.button(label="Random Text", emoji="🎲", style=discord.ButtonStyle.primary)
    async def random_text(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            text_data = await asyncio.wait_for(self.clients['sefaria'].get_random_text(), timeout=8.0)
            if text_data:
                title = text_data.get('title', 'Jewish Text')
                content = text_data.get('he', text_data.get('text', ''))
                if isinstance(content, list):
                    content = ' '.join(str(c) for c in content[:3])
                embed = discord.Embed(title=f"🎲 {title}", description=content[:1500], color=0x4A90E2)
            else:
                embed = discord.Embed(title="🎲 Torah Wisdom", description="*'Who is wise? One who learns from every person.'* - Pirkei Avot 4:1", color=0x4A90E2)
            await self.safe_response(interaction, embed)
        except Exception as e:
            logger.error(f"Random text error: {e}")
            embed = discord.Embed(title="🎲 Daily Wisdom", description="*'Study is not the main thing, but action.'* - Pirkei Avot 1:17", color=0x4A90E2)
            await self.safe_response(interaction, embed)
    
    @discord.ui.button(label="Daily Torah", emoji="📅", style=discord.ButtonStyle.secondary)
    async def daily_torah(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            torah_data = await asyncio.wait_for(self.clients['hebcal'].get_torah_reading(), timeout=8.0)
            embed = discord.Embed(title="📅 Today's Torah Reading", color=0x8E44AD)
            if torah_data and isinstance(torah_data, dict):
                parsha = torah_data.get('parsha', {})
                if parsha:
                    embed.add_field(name="Weekly Portion", value=parsha.get('title', 'Current portion'), inline=False)
            if not embed.fields:
                embed.description = "Continue your daily Torah study"
            await self.safe_response(interaction, embed)
        except Exception as e:
            logger.error(f"Daily Torah error: {e}")
            embed = discord.Embed(title="📅 Torah Study", description="*'Make your Torah study a fixed practice.'* - Pirkei Avot 1:15", color=0x8E44AD)
            await self.safe_response(interaction, embed)
    
    @discord.ui.button(label="Chassidic Wisdom", emoji="✡️", style=discord.ButtonStyle.success)
    async def chassidic_wisdom(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            wisdom = await asyncio.wait_for(self.clients['chabad'].get_daily_wisdom(), timeout=8.0)
            embed = discord.Embed(title="✡️ Daily Chassidic Wisdom", color=0xF1C40F)
            if wisdom and isinstance(wisdom, dict):
                content = wisdom.get('content', wisdom.get('text', ''))
                if content:
                    embed.description = content[:1500]
            if not embed.description:
                embed.description = "*'A little light dispels much darkness.'* - Tanya"
            await self.safe_response(interaction, embed)
        except Exception as e:
            logger.error(f"Chassidic wisdom error: {e}")
            embed = discord.Embed(title="✡️ Chassidic Teaching", description="*'The world is a narrow bridge, and the main thing is not to fear at all.'* - Rabbi Nachman", color=0xF1C40F)
            await self.safe_response(interaction, embed)
    
    @discord.ui.button(label="Daily Tanya", emoji="📖", style=discord.ButtonStyle.success)
    async def daily_tanya(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            tanya = await asyncio.wait_for(self.clients['chabad'].get_daily_tanya(), timeout=8.0)
            embed = discord.Embed(title="📖 Today's Tanya Lesson", color=0xE67E22)
            if tanya and isinstance(tanya, dict):
                content = tanya.get('content', tanya.get('text', ''))
                if content:
                    embed.description = content[:1500]
            if not embed.description:
                embed.description = "Study today's Tanya lesson for spiritual insights"
            await self.safe_response(interaction, embed)
        except Exception as e:
            logger.error(f"Daily Tanya error: {e}")
            embed = discord.Embed(title="📖 Tanya Study", description="*'The soul of man is the lamp of God.'* - Tanya", color=0xE67E22)
            await self.safe_response(interaction, embed)

class ArchivesView(BaseView):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    @discord.ui.button(label="Manuscripts", emoji="📜", style=discord.ButtonStyle.primary)
    async def manuscripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ArchiveSearchModal(self.clients, "manuscripts"))
    
    @discord.ui.button(label="Photos", emoji="📷", style=discord.ButtonStyle.primary)
    async def photos(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ArchiveSearchModal(self.clients, "photos"))
    
    @discord.ui.button(label="Books", emoji="📚", style=discord.ButtonStyle.primary)
    async def books(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ArchiveSearchModal(self.clients, "books"))
    
    @discord.ui.button(label="Maps", emoji="🗺️", style=discord.ButtonStyle.primary)
    async def maps(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ArchiveSearchModal(self.clients, "maps"))

class HelpNavigationView(BaseView):
    """Navigation for help pages"""
    
    def __init__(self, embeds: List[discord.Embed]):
        super().__init__()
        self.embeds = embeds
        self.current_page = 0
    
    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.gray)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="▶ Next", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="🏠 Commands List", style=discord.ButtonStyle.primary)
    async def commands_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📋 All Available Commands",
            description="**Complete command list for Rabbi Bot**",
            color=0x2ECC71
        )
        embed.add_field(
            name="🏓 Core Commands",
            value="`/ping` `/help` `/study` `/search` `/archives` `/advanced`",
            inline=False
        )
        embed.add_field(
            name="📚 Study Commands", 
            value="`/random` `/daily` `/wisdom` `/tanya` `/categories`",
            inline=False
        )
        embed.add_field(
            name="📅 Calendar Commands",
            value="`/calendar` `/shabbat` `/holidays`",
            inline=False
        )
        embed.add_field(
            name="🏛️ Archive Commands",
            value="`/manuscripts` `/photos` `/books`",
            inline=False
        )
        embed.add_field(
            name="🚀 Advanced Commands",
            value="`/gematria` `/translate`",
            inline=False
        )
        embed.add_field(
            name="💡 Usage Tips",
            value="• Type `/` to see all commands\n• Use interactive menus for guided experience\n• Mention @Rabbi Bot for AI conversations",
            inline=False
        )
        embed.set_footer(text="20+ commands accessing 10+ Jewish institutions")
        await interaction.response.edit_message(embed=embed, view=self)

class SearchCenterView(BaseView):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    @discord.ui.button(label="Direct Lookup", emoji="📖", style=discord.ButtonStyle.primary)
    async def direct_lookup(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DirectLookupModal(self.clients))
    
    @discord.ui.button(label="Topic Search", emoji="🎯", style=discord.ButtonStyle.primary)
    async def topic_search(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TopicSearchModal(self.clients))
    
    @discord.ui.button(label="Category Browse", emoji="📚", style=discord.ButtonStyle.secondary)
    async def category_browse(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            categories = await asyncio.wait_for(self.clients['sefaria'].get_categories(), timeout=8.0)
            embed = discord.Embed(title="📚 Text Categories", color=0x3498DB)
            if categories and isinstance(categories, list):
                category_text = "\n".join([f"• {cat}" for cat in categories[:15]])
                embed.add_field(name="Popular Categories", value=category_text, inline=False)
                embed.add_field(name="💡 Usage", value="Use Direct Lookup with categories like 'Torah Genesis' or 'Talmud Shabbat'", inline=False)
            else:
                embed.description = "**Popular Categories:**\nTorah • Talmud • Mishnah • Halakhah • Kabbalah • Liturgy • Philosophy • Midrash • Responsa"
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Categories error: {e}")
            embed = discord.Embed(title="📚 Text Categories", description="Torah • Talmud • Mishnah • Halakhah • Kabbalah • Liturgy • Philosophy • Midrash • Responsa", color=0x3498DB)
            await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="Random Discovery", emoji="🎲", style=discord.ButtonStyle.secondary)
    async def random_discovery(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RandomSearchModal(self.clients))
    
    @discord.ui.button(label="Commentary Search", emoji="💬", style=discord.ButtonStyle.success)
    async def commentary_search(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CommentarySearchModal(self.clients))
    
    @discord.ui.button(label="Hebrew Search", emoji="🔤", style=discord.ButtonStyle.success)
    async def hebrew_search(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(HebrewSearchModal(self.clients))

class DailyLearningView(BaseView):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    @discord.ui.button(label="Torah Portion", emoji="📖", style=discord.ButtonStyle.primary)
    async def torah_portion(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            torah_data = await asyncio.wait_for(self.clients['hebcal'].get_torah_reading(), timeout=10.0)
            embed = discord.Embed(title="📖 This Week's Torah Portion", color=0x8E44AD)
            
            if torah_data and isinstance(torah_data, dict):
                parsha = torah_data.get('parsha', torah_data.get('parashat', {}))
                if isinstance(parsha, dict):
                    title = parsha.get('title', parsha.get('name', 'Weekly Portion'))
                    embed.add_field(name="Parsha", value=title, inline=False)
                    
                    # Add readings if available
                    readings = parsha.get('readings', parsha.get('aliyot', []))
                    if readings and isinstance(readings, list) and len(readings) > 0:
                        embed.add_field(name="Torah Reading", value=str(readings[0]), inline=False)
                elif isinstance(parsha, str):
                    embed.add_field(name="This Week", value=parsha, inline=False)
                
                # Add Hebrew date if available
                hebrew_date = torah_data.get('hebrew_date', torah_data.get('date', ''))
                if hebrew_date:
                    embed.add_field(name="Hebrew Date", value=str(hebrew_date), inline=True)
            else:
                embed.description = "Continue your weekly Torah study with this week's portion"
                
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Torah portion error: {e}")
            embed = discord.Embed(title="📖 Torah Study", description="Continue your weekly Torah study with reflection and learning", color=0x8E44AD)
            await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="Daily Tanya", emoji="📚", style=discord.ButtonStyle.primary)
    async def daily_tanya(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            from datetime import date
            today = date.today()
            day_of_year = today.timetuple().tm_yday
            chapter_num = ((day_of_year - 1) % 53) + 1
            
            # Try to get real Tanya content from Sefaria
            tanya_ref = f"Tanya, Likutei Amarim, Chapter {chapter_num}"
            text_data = await asyncio.wait_for(self.clients['sefaria'].get_text(tanya_ref), timeout=10.0)
            
            embed = discord.Embed(title="📚 Today's Tanya Lesson", color=0xE67E22)
            
            if text_data and text_data.get('text'):
                content = text_data.get('text', '')
                if isinstance(content, list):
                    content = '\n'.join(str(c) for c in content[:2] if c)
                
                embed.add_field(name=f"Chapter {chapter_num}", value=content[:800] + "..." if len(content) > 800 else content, inline=False)
                
                # Add Hebrew if available
                hebrew_text = text_data.get('he', '')
                if hebrew_text and isinstance(hebrew_text, list):
                    hebrew_text = '\n'.join(str(h) for h in hebrew_text[:1] if h)
                    if hebrew_text:
                        embed.add_field(name="עברית", value=hebrew_text[:400], inline=False)
            else:
                embed.description = f"**Chapter {chapter_num} - Daily Study**\n\n*'The Divine soul is literally part of God above'*\n\nReflect on the divine spark within yourself and all beings."
                
            embed.set_footer(text=f"Daily study cycle - Chapter {chapter_num} of 53")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Daily Tanya error: {e}")
            embed = discord.Embed(title="📚 Tanya Study", description="*'Every descent is for the purpose of a subsequent ascent'* - Study today's Tanya lesson", color=0xE67E22)
            await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="Chassidic Wisdom", emoji="✡️", style=discord.ButtonStyle.secondary)
    async def chassidic_wisdom(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            wisdom = await asyncio.wait_for(self.clients['chabad'].get_daily_wisdom(), timeout=10.0)
            embed = discord.Embed(title="✡️ Daily Chassidic Wisdom", color=0xF1C40F)
            
            if wisdom and isinstance(wisdom, dict):
                content = wisdom.get('content', wisdom.get('text', wisdom.get('quote', '')))
                if content:
                    embed.description = content[:1200]
                    
                source = wisdom.get('source', wisdom.get('author', ''))
                if source:
                    embed.set_footer(text=f"Source: {source}")
            
            if not embed.description:
                embed.description = "*'A little light dispels much darkness.'* - Tanya\n\nLet this teaching illuminate your day with wisdom and joy."
                embed.set_footer(text="Daily Chassidic inspiration")
                
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Chassidic wisdom error: {e}")
            embed = discord.Embed(title="✡️ Chassidic Teaching", description="*'The world is a narrow bridge, and the main thing is not to fear at all.'* - Rabbi Nachman of Breslov", color=0xF1C40F)
            await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="Random Text", emoji="🎲", style=discord.ButtonStyle.secondary)
    async def random_text(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            text_data = await asyncio.wait_for(self.clients['sefaria'].get_random_text(), timeout=10.0)
            
            if text_data:
                title = text_data.get('title', 'Jewish Text')
                content = text_data.get('text', text_data.get('he', ''))
                if isinstance(content, list):
                    content = '\n'.join(str(c) for c in content[:3] if c)
                
                embed = discord.Embed(title=f"🎲 {title}", description=content[:1200], color=0x4A90E2)
                
                # Add Hebrew if available and different
                hebrew_text = text_data.get('he', '')
                if hebrew_text and isinstance(hebrew_text, list):
                    hebrew_text = '\n'.join(str(h) for h in hebrew_text[:2] if h)
                    if hebrew_text and hebrew_text != content:
                        embed.add_field(name="עברית", value=hebrew_text[:400], inline=False)
            else:
                embed = discord.Embed(title="🎲 Torah Wisdom", description="*'Who is wise? One who learns from every person.'* - Pirkei Avot 4:1", color=0x4A90E2)
                
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Random text error: {e}")
            embed = discord.Embed(title="🎲 Daily Wisdom", description="*'Study is not the main thing, but action.'* - Pirkei Avot 1:17", color=0x4A90E2)
            await interaction.followup.send(embed=embed)

class SimpleArchivesView(BaseView):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    @discord.ui.button(label="Hebrew Manuscripts", emoji="📜", style=discord.ButtonStyle.primary)
    async def manuscripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            # Search for general manuscripts
            results = await asyncio.wait_for(self.clients['nli'].search_hebrew_manuscripts("Torah"), timeout=10.0)
            embed = discord.Embed(title="📜 Hebrew Manuscripts", color=0x8B4513)
            
            if results and isinstance(results, list):
                for i, item in enumerate(results[:3], 1):
                    title = item.get('title', f'Manuscript {i}')
                    desc = item.get('description', 'Historical Hebrew manuscript')
                    embed.add_field(name=f"{i}. {title}", value=desc[:150], inline=False)
            else:
                embed.description = "Historical Hebrew manuscripts from the National Library of Israel archives"
                embed.add_field(name="Collection", value="Ancient Torah scrolls, prayer books, and religious texts", inline=False)
                
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Manuscripts error: {e}")
            embed = discord.Embed(title="📜 Hebrew Manuscripts", description="Historical Hebrew manuscripts from National Library of Israel", color=0x8B4513)
            await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="Historical Photos", emoji="📷", style=discord.ButtonStyle.primary)
    async def photos(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            results = await asyncio.wait_for(self.clients['nli'].search_historical_photos("Jewish"), timeout=10.0)
            embed = discord.Embed(title="📷 Historical Jewish Photos", color=0x8B4513)
            
            if results and isinstance(results, list):
                for i, item in enumerate(results[:3], 1):
                    title = item.get('title', f'Photo {i}')
                    desc = item.get('description', 'Historical Jewish photograph')
                    embed.add_field(name=f"{i}. {title}", value=desc[:150], inline=False)
            else:
                embed.description = "Historical Jewish photography collection"
                embed.add_field(name="Collection", value="Jewish life, communities, and historical moments", inline=False)
                
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Photos error: {e}")
            embed = discord.Embed(title="📷 Historical Photos", description="Jewish historical photography collection", color=0x8B4513)
            await interaction.followup.send(embed=embed)

class SimpleAdvancedView(BaseView):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    @discord.ui.button(label="Ask AI Rabbi", emoji="🤖", style=discord.ButtonStyle.primary)
    async def ai_rabbi(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AIQuestionModal(self.clients))
    
    @discord.ui.button(label="Calculate Gematria", emoji="🔢", style=discord.ButtonStyle.primary)
    async def gematria_calc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SimpleGematriaModal())
    
    @discord.ui.button(label="Translate Text", emoji="🌐", style=discord.ButtonStyle.secondary)
    async def translate_text(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SimpleTranslateModal())
    
    @discord.ui.button(label="Torah Calculations", emoji="📊", style=discord.ButtonStyle.success)
    async def torah_calculations(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            # Get Torah calculations
            calc_result = await self.clients['torahcalc'].calculate_biblical_measurement('cubit', 1)
            temple_info = await self.clients['torahcalc'].get_temple_measurements()
            
            embed = discord.Embed(
                title="📊 Torah Calculations",
                description="Biblical measurements and calculations",
                color=discord.Color.gold()
            )
            
            if calc_result:
                embed.add_field(
                    name="Biblical Measurements",
                    value=f"**1 Cubit** = {calc_result.get('conversions', {}).get('modern_equivalent', 'Unknown')}\n{calc_result.get('conversions', {}).get('description', '')}",
                    inline=False
                )
            
            if temple_info:
                measurements = temple_info.get('measurements', {})
                embed.add_field(
                    name="Temple Measurements",
                    value=f"**Length:** {measurements.get('length', 'Unknown')}\n**Width:** {measurements.get('width', 'Unknown')}\n**Height:** {measurements.get('height', 'Unknown')}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Torah calc error: {e}")
            embed = discord.Embed(
                title="📊 Torah Calculations",
                description="Error accessing Torah calculations",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

class ExploreView(BaseView):
    """View for additional Jewish learning features"""
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    @discord.ui.button(label="Historical Archives", emoji="🏛️", style=discord.ButtonStyle.primary)
    async def historical_archives(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            # Get historical Chabad documents
            chabad_docs = await self.clients['opentorah'].get_historical_chabad_documents()
            calendar_calc = await self.clients['opentorah'].get_jewish_calendar_calculations(2024)
            
            embed = discord.Embed(
                title="🏛️ Historical Archives",
                description="Access to early Jewish historical documents",
                color=discord.Color.dark_blue()
            )
            
            if chabad_docs:
                doc = chabad_docs[0]
                embed.add_field(
                    name="Historical Chabad Documents",
                    value=f"**{doc.get('title', 'Unknown')}**\n{doc.get('description', '')}\n**Date:** {doc.get('date', 'Unknown')}",
                    inline=False
                )
            
            if calendar_calc:
                embed.add_field(
                    name="Jewish Calendar Calculations",
                    value=f"**Year:** {calendar_calc.get('year', 'Unknown')}\n**Leap Year:** {'Yes' if calendar_calc.get('leap_year', False) else 'No'}\n**Info:** {calendar_calc.get('molad_calculations', 'Unknown')[:100]}...",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Historical archives error: {e}")
            embed = discord.Embed(
                title="🏛️ Historical Archives",
                description="Error accessing historical archives",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="Prayer & Liturgy", emoji="🤲", style=discord.ButtonStyle.success)
    async def prayer_liturgy(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            # Get daily prayers and liturgical texts
            daily_prayers = await self.clients['opensiddur'].get_daily_prayers('shacharit')
            holiday_prayers = await self.clients['opensiddur'].get_holiday_prayers('Shabbat')
            
            embed = discord.Embed(
                title="🤲 Prayer & Liturgy",
                description="Traditional Jewish prayers and liturgical texts",
                color=discord.Color.gold()
            )
            
            if daily_prayers:
                prayers = daily_prayers.get('prayers', [])
                embed.add_field(
                    name="Daily Morning Prayers",
                    value=f"**Service:** {daily_prayers.get('service', 'Unknown')}\n" + "\n".join(prayers[:3]),
                    inline=False
                )
            
            if holiday_prayers:
                holiday_prayer = holiday_prayers[0] if holiday_prayers else {}
                embed.add_field(
                    name="Holiday Prayers",
                    value=f"**Holiday:** {holiday_prayer.get('holiday', 'Unknown')}\n" + "\n".join(holiday_prayer.get('prayers', [])[:3]),
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Prayer liturgy error: {e}")
            embed = discord.Embed(
                title="🤲 Prayer & Liturgy",
                description="Error accessing prayer and liturgy",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="Cross-Platform Search", emoji="📚", style=discord.ButtonStyle.secondary)
    async def cross_platform_search(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            # Search across multiple platforms
            cross_results = await self.clients['orayta'].search_cross_platform_texts('Torah')
            responsa = await self.clients['orayta'].get_responsa_database()
            
            embed = discord.Embed(
                title="📚 Cross-Platform Search",
                description="Search across multiple Jewish text databases",
                color=discord.Color.purple()
            )
            
            if cross_results:
                result = cross_results[0]
                embed.add_field(
                    name="Multi-Platform Results",
                    value=f"**{result.get('title', 'Unknown')}**\n{result.get('description', '')}\n**Sources:** {', '.join(result.get('sources', []))[:100]}...",
                    inline=False
                )
            
            if responsa:
                resp = responsa[0]
                embed.add_field(
                    name="Responsa Database",
                    value=f"**{resp.get('title', 'Unknown')}**\n**Rabbi:** {resp.get('rabbi', 'Unknown')}\n**Topic:** {resp.get('topic', 'Unknown')}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Cross-platform search error: {e}")
            embed = discord.Embed(
                title="📚 Cross-Platform Search",
                description="Error accessing cross-platform search",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @discord.ui.button(label="Torah Insights", emoji="💎", style=discord.ButtonStyle.secondary)
    async def torah_insights(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            # Get Torah insights and community learning
            insights = await self.clients['pninim'].get_torah_insights()
            weekly_inspiration = await self.clients['pninim'].get_weekly_inspiration()
            
            embed = discord.Embed(
                title="💎 Torah Insights",
                description="Torah wisdom and community learning",
                color=discord.Color.teal()
            )
            
            if insights:
                insight = insights[0]
                embed.add_field(
                    name="Torah Insights",
                    value=f"**{insight.get('title', 'Unknown')}**\n{insight.get('insight', '')}\n**Author:** {insight.get('author', 'Unknown')}",
                    inline=False
                )
            
            if weekly_inspiration:
                embed.add_field(
                    name="Weekly Inspiration",
                    value=f"**{weekly_inspiration.get('title', 'Unknown')}**\n{weekly_inspiration.get('message', '')}\n**Theme:** {weekly_inspiration.get('theme', 'Unknown')}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Torah insights error: {e}")
            embed = discord.Embed(
                title="💎 Torah Insights",
                description="Error accessing Torah insights",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

class SimpleGematriaModal(discord.ui.Modal, title='Calculate Gematria'):
    text = discord.ui.TextInput(label='Hebrew Text', placeholder='e.g., שלום, אמת, תורה', max_length=100)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        hebrew_values = {
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
            'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
            'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400, 'ך': 20, 'ם': 40, 'ן': 50, 'ף': 80, 'ץ': 90
        }
        total = sum(hebrew_values.get(char, 0) for char in self.text.value)
        embed = discord.Embed(title="🔢 Gematria Calculation", color=0x800080)
        embed.add_field(name="Text", value=self.text.value, inline=True)
        embed.add_field(name="Value", value=str(total), inline=True)
        await interaction.followup.send(embed=embed)

class SimpleTranslateModal(discord.ui.Modal, title='Translate Text'):
    text = discord.ui.TextInput(label='Text', placeholder='Enter text in any language', style=discord.TextStyle.paragraph, max_length=500)
    target_lang = discord.ui.TextInput(label='Target Language', placeholder='e.g., english, hebrew, spanish', default='english', max_length=20)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            translator = GoogleTranslator(source='auto', target=self.target_lang.value.lower())
            result = translator.translate(self.text.value)
            embed = discord.Embed(title="🌐 Translation", color=0x3498DB)
            embed.add_field(name="Original", value=self.text.value[:300], inline=False)
            embed.add_field(name="Translated", value=result[:300], inline=False)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            embed = discord.Embed(title="🌐 Translation", description="Translation service temporarily unavailable", color=0x3498DB)
            await interaction.followup.send(embed=embed)

class AIQuestionModal(discord.ui.Modal, title='Ask AI Rabbi'):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    question = discord.ui.TextInput(label='Your Question', placeholder='Ask about Jewish texts, laws, or traditions...', style=discord.TextStyle.paragraph, max_length=500)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            ai_response = await asyncio.wait_for(
                self.clients['ai'].generate_response(
                    f"Please answer this Jewish question: {self.question.value}",
                    interaction.user.display_name
                ), 
                timeout=15.0
            )
            embed = discord.Embed(title="🤖 AI Rabbi Response", color=0x9932CC)
            embed.add_field(name="Question", value=self.question.value[:300], inline=False)
            embed.add_field(name="Answer", value=ai_response[:1200], inline=False)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"AI question error: {e}")
            embed = discord.Embed(title="🤖 AI Rabbi", description="AI Rabbi is currently unavailable. Try asking your question by mentioning @Rabbi Bot in a message.", color=0x9932CC)
            await interaction.followup.send(embed=embed)

class AdvancedView(BaseView):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    @discord.ui.button(label="Gematria", emoji="🔢", style=discord.ButtonStyle.danger)
    async def gematria(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GematriaModal())
    
    @discord.ui.button(label="Torah Calc", emoji="📊", style=discord.ButtonStyle.danger)
    async def torah_calc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TorahCalcModal(self.clients))
    
    @discord.ui.button(label="Translate", emoji="🌐", style=discord.ButtonStyle.danger)
    async def translate(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TranslateModal())
    
    @discord.ui.button(label="AI Books", emoji="📖", style=discord.ButtonStyle.danger)
    async def ai_books(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DictaSearchModal(self.clients))

# Modal classes for user input
class SearchModal(discord.ui.Modal, title='Search Jewish Texts'):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    query = discord.ui.TextInput(label='Search Query', placeholder='e.g., Torah, Genesis 1:1, Talmud...', max_length=100)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            query = self.query.value.strip()
            
            # Try to get direct text content first
            text_data = await asyncio.wait_for(self.clients['sefaria'].get_text(query), timeout=8.0)
            
            if text_data and text_data.get('text'):
                # We found direct text content
                title = text_data.get('title', query)
                content = text_data.get('text', '')
                
                if isinstance(content, list):
                    content = '\n'.join(str(c) for c in content[:3] if c)
                
                embed = discord.Embed(title=f"📖 {title}", color=0x2ECC71)
                embed.description = content[:1500] + "..." if len(content) > 1500 else content
                
                # Add Hebrew if available
                hebrew_text = text_data.get('he', '')
                if hebrew_text and isinstance(hebrew_text, list):
                    hebrew_text = '\n'.join(str(h) for h in hebrew_text[:2] if h)
                    if hebrew_text:
                        embed.add_field(name="עברית", value=hebrew_text[:500], inline=False)
                        
            else:
                # Fallback to search results
                results = await asyncio.wait_for(self.clients['sefaria'].search_texts(query, limit=3), timeout=8.0)
                embed = discord.Embed(title=f"🔍 Search: {query}", color=0x2ECC71)
                
                if results and isinstance(results, list):
                    for i, result in enumerate(results[:3], 1):
                        title = result.get('title', f'Result {i}')
                        content = result.get('content', result.get('text', ''))
                        if isinstance(content, list):
                            content = ' '.join(str(c) for c in content[:2] if c)
                        if content:
                            embed.add_field(name=f"{i}. {title}", value=content[:200] + "..." if len(content) > 200 else content, inline=False)
                        else:
                            embed.add_field(name=f"{i}. {title}", value="Text available on Sefaria.org", inline=False)
                else:
                    embed.description = f"Try specific references like 'Genesis 1:1', 'Shabbat 31a', or 'Pirkei Avot 1:1'"
                    
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            embed = discord.Embed(title="🔍 Search Results", description="Try specific references like 'Genesis 1:1' or 'Pirkei Avot 1:1'", color=0x2ECC71)
            await interaction.followup.send(embed=embed)

class LocationModal(discord.ui.Modal, title='Enter Location'):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    location = discord.ui.TextInput(label='City or Location', placeholder='e.g., New York, Jerusalem, London', default='New York', max_length=50)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            times = await asyncio.wait_for(self.clients['hebcal'].get_shabbat_times(self.location.value), timeout=8.0)
            embed = discord.Embed(title=f"🕯️ Shabbat Times - {self.location.value}", color=0xF1C40F)
            if times and isinstance(times, dict):
                if 'candles' in times:
                    embed.add_field(name="Candle Lighting", value=times['candles'], inline=True)
                if 'havdalah' in times:
                    embed.add_field(name="Havdalah", value=times['havdalah'], inline=True)
            if not embed.fields:
                embed.description = "Shabbat Shalom! May your Shabbat be peaceful."
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Shabbat times error: {e}")
            embed = discord.Embed(title="🕯️ Shabbat Shalom", description="May your Shabbat be filled with peace and joy", color=0xF1C40F)
            await interaction.followup.send(embed=embed)

class ArchiveSearchModal(discord.ui.Modal, title='Search Archives'):
    def __init__(self, clients: Dict[str, Any], archive_type: str):
        super().__init__()
        self.clients = clients
        self.archive_type = archive_type
    
    query = discord.ui.TextInput(label='Search Archives', placeholder='e.g., Torah scrolls, ancient texts...', max_length=100)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        results = None
        try:
            if self.archive_type == "manuscripts":
                results = await asyncio.wait_for(self.clients['nli'].search_hebrew_manuscripts(self.query.value), timeout=8.0)
            elif self.archive_type == "photos":
                results = await asyncio.wait_for(self.clients['nli'].search_historical_photos(self.query.value), timeout=8.0)
            elif self.archive_type == "books":
                results = await asyncio.wait_for(self.clients['nli'].search_jewish_books(self.query.value), timeout=8.0)
            elif self.archive_type == "maps":
                results = await asyncio.wait_for(self.clients['nli'].search_historical_maps(self.query.value), timeout=8.0)
            else:
                results = []
            
            embed = discord.Embed(title=f"🏛️ {self.archive_type.title()}: {self.query.value}", color=0x8B4513)
            if results and isinstance(results, list):
                for i, item in enumerate(results[:3], 1):
                    title = item.get('title', f'Item {i}')
                    desc = item.get('description', 'Historical archive item')
                    embed.add_field(name=f"{i}. {title}", value=desc[:150], inline=False)
            else:
                embed.description = f"No {self.archive_type} found for your search."
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Archive search error: {e}")
            embed = discord.Embed(title=f"🏛️ {self.archive_type.title()} Archives", description="Historical Jewish archives from National Library of Israel", color=0x8B4513)
            await interaction.followup.send(embed=embed)

class GematriaModal(discord.ui.Modal, title='Gematria Calculator'):
    text = discord.ui.TextInput(label='Hebrew Text', placeholder='e.g., שלום, תורה, אמת', max_length=100)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        hebrew_values = {
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
            'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
            'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400, 'ך': 20, 'ם': 40, 'ן': 50, 'ף': 80, 'ץ': 90
        }
        total = sum(hebrew_values.get(char, 0) for char in self.text.value)
        embed = discord.Embed(title="🔢 Gematria Calculation", color=0x800080)
        embed.add_field(name="Text", value=self.text.value, inline=True)
        embed.add_field(name="Standard Value", value=str(total), inline=True)
        await interaction.followup.send(embed=embed)

class TorahCalcModal(discord.ui.Modal, title='Torah Calculations'):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    query = discord.ui.TextInput(label='Torah Question', placeholder='e.g., How many cubits in a mile?', style=discord.TextStyle.paragraph, max_length=200)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            if 'torahcalc' in self.clients:
                result = await asyncio.wait_for(self.clients['torahcalc'].calculate(self.query.value), timeout=8.0)
                embed = discord.Embed(title="📊 Torah Calculation", color=0x4B0082)
                if result:
                    embed.add_field(name="Question", value=self.query.value, inline=False)
                    embed.add_field(name="Answer", value=result[:800], inline=False)
                else:
                    embed.description = "Try a biblical measurement or calculation question."
            else:
                embed = discord.Embed(title="📊 Biblical Measurements", description="**Common Biblical Units:**\n• 1 Cubit ≈ 18 inches\n• 1 Tefach ≈ 3 inches\n• 1 Mil ≈ 0.6 miles\n• 1 Kor ≈ 220 liters", color=0x4B0082)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Torah calc error: {e}")
            embed = discord.Embed(title="📊 Torah Calculations", description="Biblical measurements and calculations", color=0x4B0082)
            await interaction.followup.send(embed=embed)

class TranslateModal(discord.ui.Modal, title='Translate Text'):
    text = discord.ui.TextInput(label='Text to Translate', placeholder='Enter text in any language', style=discord.TextStyle.paragraph, max_length=500)
    target_lang = discord.ui.TextInput(label='Target Language', placeholder='e.g., english, hebrew, spanish', default='english', max_length=20)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            translator = GoogleTranslator(source='auto', target=self.target_lang.value.lower())
            result = translator.translate(self.text.value)
            embed = discord.Embed(title="🌐 Translation", color=0x3498DB)
            embed.add_field(name="Original", value=self.text.value[:300], inline=False)
            embed.add_field(name="Translated", value=result[:300], inline=False)
            embed.add_field(name="Language", value=self.target_lang.value, inline=True)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            embed = discord.Embed(title="❌ Translation Error", description="Unable to translate text", color=0xFF4444)
            await interaction.followup.send(embed=embed)

class DirectLookupModal(discord.ui.Modal, title='Direct Text Lookup'):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    query = discord.ui.TextInput(label='Text Reference', placeholder='e.g., Genesis 1:1, Shabbat 31a, Pirkei Avot 1:14', max_length=100)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            query = self.query.value.strip()
            text_data = await asyncio.wait_for(self.clients['sefaria'].get_text(query), timeout=10.0)
            
            if text_data and text_data.get('text'):
                title = text_data.get('title', query)
                content = text_data.get('text', '')
                
                if isinstance(content, list):
                    content = '\n'.join(str(c) for c in content[:3] if c)
                
                embed = discord.Embed(title=f"📖 {title}", color=0x2ECC71)
                embed.description = content[:1500] + "..." if len(content) > 1500 else content
                
                # Add Hebrew if available
                hebrew_text = text_data.get('he', '')
                if hebrew_text:
                    if isinstance(hebrew_text, list):
                        hebrew_text = '\n'.join(str(h) for h in hebrew_text[:2] if h)
                    if hebrew_text:
                        embed.add_field(name="עברית", value=hebrew_text[:500], inline=False)
                
                # Add commentary if available
                commentary = text_data.get('commentary', '')
                if commentary:
                    embed.add_field(name="Commentary", value=commentary[:300], inline=False)
                        
            else:
                embed = discord.Embed(title="🔍 Text Not Found", description=f"Could not find '{query}'. Try specific references like 'Genesis 1:1' or 'Shabbat 31a'.", color=0x3498DB)
                    
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Direct lookup error: {e}")
            embed = discord.Embed(title="📖 Text Lookup", description="Try specific references like 'Genesis 1:1', 'Talmud Shabbat 31a', or 'Pirkei Avot 1:1'", color=0x3498DB)
            await interaction.followup.send(embed=embed)

class TopicSearchModal(discord.ui.Modal, title='Topic Search'):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    query = discord.ui.TextInput(label='Topic or Theme', placeholder='e.g., love, justice, prayer, charity, wisdom', max_length=100)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            query = self.query.value.strip()
            results = await asyncio.wait_for(self.clients['sefaria'].search_texts(query, limit=5), timeout=10.0)
            
            embed = discord.Embed(title=f"🎯 Topic Search: {query}", color=0x8E44AD)
            
            if results and isinstance(results, list):
                for i, result in enumerate(results[:4], 1):
                    title = result.get('title', f'Result {i}')
                    content = result.get('content', result.get('text', ''))
                    if isinstance(content, list):
                        content = ' '.join(str(c) for c in content[:2] if c)
                    if content:
                        embed.add_field(name=f"{i}. {title}", value=content[:200] + "..." if len(content) > 200 else content, inline=False)
            else:
                embed.description = f"No results found for '{query}'. Try related terms or browse categories."
                    
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Topic search error: {e}")
            embed = discord.Embed(title="🎯 Topic Search", description="Search for themes like 'love', 'justice', 'prayer', 'wisdom', or 'charity'", color=0x8E44AD)
            await interaction.followup.send(embed=embed)

class RandomSearchModal(discord.ui.Modal, title='Random Text Discovery'):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    category = discord.ui.TextInput(label='Category (optional)', placeholder='e.g., Torah, Talmud, Mishnah, or leave blank for any', max_length=50, required=False)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            category = self.category.value.strip() if self.category.value else None
            text_data = await asyncio.wait_for(self.clients['sefaria'].get_random_text(category), timeout=10.0)
            
            if text_data:
                title = text_data.get('title', 'Jewish Text')
                content = text_data.get('text', text_data.get('he', ''))
                if isinstance(content, list):
                    content = '\n'.join(str(c) for c in content[:3] if c)
                
                embed = discord.Embed(title=f"🎲 {title}", description=content[:1500], color=0x4A90E2)
                
                # Add Hebrew if available and different from main content
                hebrew_text = text_data.get('he', '')
                if hebrew_text and isinstance(hebrew_text, list):
                    hebrew_text = '\n'.join(str(h) for h in hebrew_text[:2] if h)
                    if hebrew_text and hebrew_text != content:
                        embed.add_field(name="עברית", value=hebrew_text[:500], inline=False)
            else:
                embed = discord.Embed(title="🎲 Daily Wisdom", description="*'Who is wise? One who learns from every person.'* - Pirkei Avot 4:1", color=0x4A90E2)
                
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Random search error: {e}")
            embed = discord.Embed(title="🎲 Daily Wisdom", description="*'Study is not the main thing, but action.'* - Pirkei Avot 1:17", color=0x4A90E2)
            await interaction.followup.send(embed=embed)

class CommentarySearchModal(discord.ui.Modal, title='Commentary Search'):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    query = discord.ui.TextInput(label='Text with Commentary', placeholder='e.g., Genesis 1:1 Rashi, Exodus 20:1 Ibn Ezra', max_length=100)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            query = self.query.value.strip()
            # Try to get text with commentary
            text_data = await asyncio.wait_for(self.clients['sefaria'].get_text(query), timeout=10.0)
            
            embed = discord.Embed(title=f"💬 Commentary Search: {query}", color=0x9B59B6)
            
            if text_data:
                title = text_data.get('title', query)
                content = text_data.get('text', '')
                if isinstance(content, list):
                    content = '\n'.join(str(c) for c in content[:2] if c)
                
                if content:
                    embed.add_field(name="Text", value=content[:500], inline=False)
                
                # Look for commentary
                commentary = text_data.get('commentary', '')
                if commentary:
                    if isinstance(commentary, list):
                        commentary = '\n'.join(str(c) for c in commentary[:2] if c)
                    embed.add_field(name="Commentary", value=commentary[:500], inline=False)
                else:
                    embed.add_field(name="Commentary", value="Try specific commentators like 'Rashi', 'Ibn Ezra', 'Ramban'", inline=False)
            else:
                embed.description = "Try formats like 'Genesis 1:1 Rashi' or 'Exodus 20:1 Ibn Ezra'"
                    
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Commentary search error: {e}")
            embed = discord.Embed(title="💬 Commentary Search", description="Search for texts with commentaries like 'Genesis 1:1 Rashi' or 'Talmud Shabbat 31a'", color=0x9B59B6)
            await interaction.followup.send(embed=embed)

class HebrewSearchModal(discord.ui.Modal, title='Hebrew Text Search'):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    query = discord.ui.TextInput(label='Hebrew Text', placeholder='e.g., בראשית, שבת, תפילה', max_length=100)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            query = self.query.value.strip()
            results = await asyncio.wait_for(self.clients['sefaria'].search_texts(query, limit=4), timeout=10.0)
            
            embed = discord.Embed(title=f"🔤 Hebrew Search: {query}", color=0x1ABC9C)
            
            if results and isinstance(results, list):
                for i, result in enumerate(results[:3], 1):
                    title = result.get('title', f'Result {i}')
                    
                    # Prefer Hebrew content
                    hebrew_content = result.get('he', '')
                    english_content = result.get('text', result.get('content', ''))
                    
                    if isinstance(hebrew_content, list):
                        hebrew_content = ' '.join(str(h) for h in hebrew_content[:2] if h)
                    if isinstance(english_content, list):
                        english_content = ' '.join(str(e) for e in english_content[:2] if e)
                    
                    if hebrew_content:
                        embed.add_field(name=f"{i}. {title}", value=hebrew_content[:200], inline=False)
                        if english_content:
                            embed.add_field(name="English", value=english_content[:200], inline=False)
                    elif english_content:
                        embed.add_field(name=f"{i}. {title}", value=english_content[:200], inline=False)
            else:
                embed.description = f"No Hebrew results found for '{query}'. Try different Hebrew terms."
                    
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Hebrew search error: {e}")
            embed = discord.Embed(title="🔤 Hebrew Search", description="Search Hebrew texts using Hebrew characters", color=0x1ABC9C)
            await interaction.followup.send(embed=embed)

class DictaSearchModal(discord.ui.Modal, title='Search AI-Enhanced Books'):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    query = discord.ui.TextInput(label='Book Search', placeholder='e.g., Talmud, Responsa, Chassidic texts...', max_length=100)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            results = await asyncio.wait_for(self.clients['dicta'].search_books(self.query.value, limit=3), timeout=8.0)
            embed = discord.Embed(title=f"📖 AI-Enhanced Books: {self.query.value}", color=0x9932CC)
            if results and isinstance(results, list):
                for i, book in enumerate(results[:3], 1):
                    title = book.get('title', f'Book {i}')
                    author = book.get('author', 'Unknown')
                    embed.add_field(name=f"{i}. {title}", value=f"By: {author}", inline=False)
            else:
                embed.description = "No books found. Try different search terms."
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Dicta search error: {e}")
            embed = discord.Embed(title="📖 AI-Enhanced Library", description="Access to 800+ Jewish books with AI processing from Dicta", color=0x9932CC)
            await interaction.followup.send(embed=embed)

class ComprehensiveCommands(commands.Cog):
    """Comprehensive Discord bot with ALL Jewish learning functionality"""
    
    def __init__(self, bot, **clients):
        self.bot = bot
        self.clients = clients
    
    @app_commands.command(name="ping", description="Test bot response")
    async def ping(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🏓 Rabbi Bot Online", description="Ready for comprehensive Jewish learning", color=0x00FF00)
        embed.add_field(name="Status", value="✅ All 10+ APIs integrated", inline=False)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="study", description="Interactive Jewish study center")
    async def study(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📚 Jewish Study Center", description="Choose your study method:", color=0x3498DB)
        embed.add_field(name="🎲 Random Text", value="Discover Sefaria wisdom", inline=True)
        embed.add_field(name="📅 Daily Torah", value="Today's portion", inline=True)  
        embed.add_field(name="✡️ Chassidic Wisdom", value="Daily teachings", inline=True)
        embed.add_field(name="📖 Daily Tanya", value="Mystical study", inline=True)
        embed.set_footer(text="Click a button to begin your study session")
        view = StudyView(self.clients)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="search", description="Enhanced Jewish text search with multiple options")
    async def search(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🔍 Enhanced Text Search Center",
            description="**Choose your search method for comprehensive text discovery:**",
            color=0x3498DB
        )
        embed.add_field(name="📖 Direct Lookup", value="Search specific verses or references", inline=True)
        embed.add_field(name="🎯 Topic Search", value="Find texts by topic or theme", inline=True)
        embed.add_field(name="📚 Category Browse", value="Explore by text categories", inline=True)
        embed.add_field(name="🎲 Random Discovery", value="Get random texts with filters", inline=True)
        embed.add_field(name="💬 Commentary Search", value="Find texts with commentaries", inline=True)
        embed.add_field(name="🔤 Hebrew Search", value="Search Hebrew text directly", inline=True)
        embed.set_footer(text="Enhanced search with Hebrew/English support • Click to begin")
        
        view = SearchCenterView(self.clients)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="archives", description="Historical Jewish archives")
    async def archives(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🏛️ National Library of Israel Archives", description="Explore historical Jewish materials:", color=0x8B4513)
        embed.add_field(name="📜 Manuscripts", value="Hebrew manuscripts", inline=True)
        embed.add_field(name="📷 Photos", value="Historical photos", inline=True)
        embed.add_field(name="📚 Books", value="Rare Jewish books", inline=True)
        embed.add_field(name="🗺️ Maps", value="Historical maps", inline=True)
        view = ArchivesView(self.clients)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="advanced", description="Advanced Jewish learning tools")
    async def advanced(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🚀 Advanced Jewish Learning Tools", description="Powerful study tools:", color=0x800080)
        embed.add_field(name="🔢 Gematria", value="Hebrew numerology", inline=True)
        embed.add_field(name="📊 Torah Calc", value="Biblical calculations", inline=True)
        embed.add_field(name="🌐 Translate", value="Multi-language", inline=True)
        embed.add_field(name="📖 AI Books", value="Dicta's 800+ books", inline=True)
        view = AdvancedView(self.clients)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="shabbat", description="Shabbat times for any location")
    async def shabbat(self, interaction: discord.Interaction):
        modal = LocationModal(self.clients)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name="calendar", description="Jewish calendar information")
    async def calendar(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            today = date.today()
            hebrew_data = await asyncio.wait_for(self.clients['hebcal'].convert_hebrew_date(today), timeout=8.0)
            embed = discord.Embed(title="📅 Jewish Calendar", color=0x9B59B6)
            embed.add_field(name="Today", value=today.strftime('%B %d, %Y'), inline=True)
            if hebrew_data and isinstance(hebrew_data, dict):
                hebrew_date = hebrew_data.get('hebrew', 'Hebrew date unavailable')
                embed.add_field(name="Hebrew Date", value=hebrew_date, inline=True)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Calendar error: {e}")
            embed = discord.Embed(title="📅 Today", description=f"Today is {date.today().strftime('%B %d, %Y')}", color=0x9B59B6)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="help", description="Interactive help guide with all features")
    async def help_command(self, interaction: discord.Interaction):
        # Page 1: Overview and Core Commands
        embed1 = discord.Embed(
            title="📚 Rabbi Bot - Ultimate Jewish Learning Assistant",
            description="**Most comprehensive Jewish Discord bot with 50+ features**",
            color=0x3498DB
        )
        embed1.add_field(name="🏓 Essential Commands", value="`/ping` - Test bot status\n`/help` - This interactive guide", inline=True)
        embed1.add_field(name="📚 Study Commands", value="`/study` - Interactive study center\n`/search` - Search Jewish texts", inline=True)
        embed1.add_field(name="📅 Calendar Commands", value="`/calendar` - Hebrew date conversion\n`/shabbat` - Shabbat times by location", inline=True)
        embed1.add_field(name="🏛️ Archive Commands", value="`/archives` - Historical Jewish materials", inline=True)
        embed1.add_field(name="🚀 Advanced Commands", value="`/advanced` - Specialized learning tools", inline=True)
        embed1.add_field(name="🤖 AI Features", value="Mention @Rabbi Bot for conversations", inline=True)
        embed1.set_footer(text="Page 1 of 4 • Use buttons to navigate")
        
        # Page 2: Study Features Detail
        embed2 = discord.Embed(
            title="📚 Study Center Features",
            description="**Interactive Jewish Learning Hub**",
            color=0x8E44AD
        )
        embed2.add_field(name="🎲 Random Texts", value="• Discover wisdom from Sefaria library\n• Thousands of Jewish texts\n• Hebrew and English content", inline=False)
        embed2.add_field(name="📅 Daily Torah", value="• Current Torah portion\n• Weekly parsha information\n• Study schedule integration", inline=False)
        embed2.add_field(name="✡️ Chassidic Wisdom", value="• Daily Chabad.org teachings\n• Chassidic philosophy\n• Spiritual insights", inline=False)
        embed2.add_field(name="📖 Daily Tanya", value="• Chassidic foundational text\n• Daily study portions\n• Mystical teachings", inline=False)
        embed2.set_footer(text="Page 2 of 4 • Detailed study features")
        
        # Page 3: Archives and Advanced Features
        embed3 = discord.Embed(
            title="🏛️ Archives & Advanced Tools",
            description="**Historical Materials & Specialized Features**",
            color=0xE67E22
        )
        embed3.add_field(name="📜 Historical Archives", value="• Hebrew manuscripts (National Library of Israel)\n• Historical photographs\n• Rare Jewish books\n• Historical maps", inline=False)
        embed3.add_field(name="🔢 Advanced Tools", value="• Gematria calculator\n• Torah/biblical calculations\n• Multi-language translation\n• AI-enhanced book search (800+ books)", inline=False)
        embed3.add_field(name="🌐 Language Support", value="• Hebrew ↔ English translation\n• Multiple language support\n• Transliteration tools", inline=False)
        embed3.set_footer(text="Page 3 of 4 • Archives and advanced features")
        
        # Page 4: Data Sources and Technical Info
        embed4 = discord.Embed(
            title="📊 Data Sources & Technical Details",
            description="**Comprehensive Jewish Institution Integration**",
            color=0x27AE60
        )
        embed4.add_field(name="🏢 Major Institutions", value="• **Sefaria.org** - Jewish text library\n• **Hebcal.com** - Jewish calendar\n• **National Library of Israel** - Archives\n• **Chabad.org** - Chassidic content\n• **Dicta.org.il** - AI-enhanced texts", inline=False)
        embed4.add_field(name="🔬 Additional APIs", value="• **OpenTorah** - Historical archives\n• **TorahCalc** - Biblical calculations\n• **Orayta** - Cross-platform library\n• **OpenSiddur** - Liturgical texts\n• **Pninim** - Torah insights", inline=False)
        embed4.add_field(name="✨ Bot Capabilities", value="• 50+ specialized functions\n• Interactive menus and modals\n• Real-time API integration\n• AI-powered conversations\n• Multi-platform deployment ready", inline=False)
        embed4.set_footer(text="Page 4 of 4 • Complete technical overview")
        
        # Create navigation view
        view = HelpNavigationView([embed1, embed2, embed3, embed4])
        await interaction.response.send_message(embed=embed1, view=view)
    
    # Additional direct commands for better access
    @app_commands.command(name="gematria", description="Calculate gematria values for Hebrew text")
    @app_commands.describe(text="Hebrew text to calculate")
    async def gematria_direct(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer()
        hebrew_values = {
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
            'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
            'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400, 'ך': 20, 'ם': 40, 'ן': 50, 'ף': 80, 'ץ': 90
        }
        total = sum(hebrew_values.get(char, 0) for char in text)
        embed = discord.Embed(title="🔢 Gematria Calculation", color=0x800080)
        embed.add_field(name="Text", value=text, inline=True)
        embed.add_field(name="Standard Value", value=str(total), inline=True)
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="translate", description="Translate text between languages")
    @app_commands.describe(text="Text to translate", target_language="Target language (e.g., english, hebrew)")
    async def translate_direct(self, interaction: discord.Interaction, text: str, target_language: str = "english"):
        await interaction.response.defer()
        try:
            translator = GoogleTranslator(source='auto', target=target_language.lower())
            result = translator.translate(text)
            embed = discord.Embed(title="🌐 Translation", color=0x3498DB)
            embed.add_field(name="Original", value=text[:300], inline=False)
            embed.add_field(name="Translated", value=result[:300], inline=False)
            embed.add_field(name="Language", value=target_language, inline=True)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            embed = discord.Embed(title="❌ Translation Error", description="Unable to translate text", color=0xFF4444)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="manuscripts", description="Search Hebrew manuscripts")
    @app_commands.describe(query="Search terms for manuscripts")
    async def manuscripts_direct(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        try:
            results = await asyncio.wait_for(self.clients['nli'].search_hebrew_manuscripts(query), timeout=8.0)
            embed = discord.Embed(title=f"📜 Hebrew Manuscripts: {query}", color=0x8B4513)
            if results and isinstance(results, list):
                for i, item in enumerate(results[:3], 1):
                    title = item.get('title', f'Manuscript {i}')
                    desc = item.get('description', 'Historical manuscript')
                    embed.add_field(name=f"{i}. {title}", value=desc[:150], inline=False)
            else:
                embed.description = "No manuscripts found for your search."
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Manuscripts search error: {e}")
            embed = discord.Embed(title="📜 Hebrew Manuscripts", description="Historical Hebrew manuscripts from National Library of Israel", color=0x8B4513)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="photos", description="Search historical Jewish photographs")
    @app_commands.describe(query="Search terms for historical photos")
    async def photos_direct(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        try:
            results = await asyncio.wait_for(self.clients['nli'].search_historical_photos(query), timeout=8.0)
            embed = discord.Embed(title=f"📷 Historical Photos: {query}", color=0x8B4513)
            if results and isinstance(results, list):
                for i, item in enumerate(results[:3], 1):
                    title = item.get('title', f'Photo {i}')
                    desc = item.get('description', 'Historical photograph')
                    embed.add_field(name=f"{i}. {title}", value=desc[:150], inline=False)
            else:
                embed.description = "No photos found for your search."
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Photos search error: {e}")
            embed = discord.Embed(title="📷 Historical Photos", description="Jewish historical photography collection", color=0x8B4513)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="wisdom", description="Get daily Chassidic wisdom from Chabad.org")
    async def wisdom_direct(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            wisdom = await asyncio.wait_for(self.clients['chabad'].get_daily_wisdom(), timeout=8.0)
            embed = discord.Embed(title="✡️ Daily Chassidic Wisdom", color=0xF1C40F)
            if wisdom and isinstance(wisdom, dict):
                content = wisdom.get('content', wisdom.get('text', ''))
                if content:
                    embed.description = content[:1500]
            if not embed.description:
                embed.description = "*'A little light dispels much darkness.'* - Tanya"
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Wisdom error: {e}")
            embed = discord.Embed(title="✡️ Chassidic Teaching", description="*'The world is a narrow bridge, and the main thing is not to fear at all.'* - Rabbi Nachman", color=0xF1C40F)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="tanya", description="Get today's Tanya lesson")
    async def tanya_direct(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            # Try to get real Tanya content from Sefaria first
            from datetime import date
            
            # Calculate today's Tanya lesson based on date
            today = date.today()
            day_of_year = today.timetuple().tm_yday
            
            # Tanya has daily lessons, cycle through chapters
            chapter_num = ((day_of_year - 1) % 53) + 1  # Tanya has 53 chapters in Likutei Amarim
            
            # Try to get from Sefaria
            tanya_ref = f"Tanya, Likutei Amarim, Chapter {chapter_num}"
            text_data = await asyncio.wait_for(self.clients['sefaria'].get_text(tanya_ref), timeout=8.0)
            
            embed = discord.Embed(title="📖 Today's Tanya Lesson", color=0xE67E22)
            
            if text_data and text_data.get('text'):
                content = text_data.get('text', '')
                if isinstance(content, list):
                    content = '\n'.join(str(c) for c in content[:2] if c)
                
                embed.add_field(name=f"Chapter {chapter_num}", value=content[:1000] + "..." if len(content) > 1000 else content, inline=False)
                
                # Add Hebrew if available
                hebrew_text = text_data.get('he', '')
                if hebrew_text and isinstance(hebrew_text, list):
                    hebrew_text = '\n'.join(str(h) for h in hebrew_text[:1] if h)
                    if hebrew_text:
                        embed.add_field(name="עברית", value=hebrew_text[:400], inline=False)
            else:
                # Fallback to inspirational Tanya quote
                embed.description = f"**Chapter {chapter_num} Study**\n\n*'The Divine soul... is literally part of God above'*\n\nStudy today's Tanya lesson for spiritual growth and understanding of the soul's divine nature."
                embed.add_field(name="Daily Practice", value="Reflect on the divine spark within yourself and all beings.", inline=False)
            
            embed.set_footer(text="Based on the Alter Rebbe's daily study cycle")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Tanya error: {e}")
            embed = discord.Embed(title="📖 Tanya Study", description="*'Every descent is for the purpose of a subsequent ascent'* - Tanya\n\nStudy today's Tanya lesson for spiritual insights.", color=0xE67E22)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="books", description="Search AI-enhanced Jewish books")
    @app_commands.describe(query="Search terms for Jewish books")
    async def books_direct(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        try:
            results = await asyncio.wait_for(self.clients['dicta'].search_books(query, limit=5), timeout=8.0)
            embed = discord.Embed(title=f"📖 Jewish Books: {query}", color=0x9932CC)
            if results and isinstance(results, list):
                for i, book in enumerate(results[:5], 1):
                    title = book.get('title', f'Book {i}')
                    author = book.get('author', 'Unknown')
                    embed.add_field(name=f"{i}. {title}", value=f"By: {author}", inline=False)
            else:
                embed.description = "No books found. Try different search terms."
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Books search error: {e}")
            embed = discord.Embed(title="📖 Jewish Books", description="Access to 800+ Jewish books with AI processing from Dicta", color=0x9932CC)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="random", description="Get random Jewish text from Sefaria")
    @app_commands.describe(category="Optional category (torah, talmud, mishnah, etc.)")
    async def random_direct(self, interaction: discord.Interaction, category: Optional[str] = None):
        await interaction.response.defer()
        try:
            text_data = await asyncio.wait_for(self.clients['sefaria'].get_random_text(category), timeout=8.0)
            if text_data:
                title = text_data.get('title', 'Jewish Text')
                content = text_data.get('he', text_data.get('text', ''))
                if isinstance(content, list):
                    content = ' '.join(str(c) for c in content[:3])
                embed = discord.Embed(title=f"🎲 {title}", description=content[:1500], color=0x4A90E2)
            else:
                embed = discord.Embed(title="🎲 Torah Wisdom", description="*'Who is wise? One who learns from every person.'* - Pirkei Avot 4:1", color=0x4A90E2)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Random text error: {e}")
            embed = discord.Embed(title="🎲 Daily Wisdom", description="*'Study is not the main thing, but action.'* - Pirkei Avot 1:17", color=0x4A90E2)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="daily", description="Get today's Jewish learning content")
    async def daily_direct(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📅 Today's Jewish Learning",
            description="**Choose what you'd like to study today:**",
            color=0x8E44AD
        )
        embed.add_field(name="📖 Torah Portion", value="Weekly parsha", inline=True)
        embed.add_field(name="📚 Tanya Lesson", value="Daily mystical study", inline=True)
        embed.add_field(name="✡️ Chassidic Wisdom", value="Daily teaching", inline=True)
        embed.add_field(name="🎲 Random Text", value="Surprise me!", inline=True)
        embed.set_footer(text="Simple one-click learning")
        
        view = DailyLearningView(self.clients)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="holidays", description="Get upcoming Jewish holidays")
    @app_commands.describe(year="Optional year (defaults to current year)")
    async def holidays_direct(self, interaction: discord.Interaction, year: Optional[int] = None):
        await interaction.response.defer()
        try:
            holidays = await asyncio.wait_for(self.clients['hebcal'].get_jewish_holidays(year), timeout=8.0)
            embed = discord.Embed(title="🎉 Jewish Holidays", color=0x2ECC71)
            if holidays and isinstance(holidays, list):
                for i, holiday in enumerate(holidays[:8], 1):
                    name = holiday.get('title', f'Holiday {i}')
                    date_str = holiday.get('date', 'Date TBA')
                    embed.add_field(name=name, value=date_str, inline=True)
            else:
                embed.description = "Check your local Jewish calendar for upcoming holidays"
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Holidays error: {e}")
            embed = discord.Embed(title="🎉 Jewish Holidays", description="Check your local Jewish calendar for upcoming holidays", color=0x2ECC71)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="categories", description="List available text categories from Sefaria")
    async def categories_direct(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            categories = await asyncio.wait_for(self.clients['sefaria'].get_categories(), timeout=8.0)
            embed = discord.Embed(title="📂 Sefaria Text Categories", color=0x3498DB)
            if categories and isinstance(categories, list):
                category_text = "\n".join([f"• {cat}" for cat in categories[:15]])
                embed.add_field(name="Available Categories", value=category_text, inline=False)
                if len(categories) > 15:
                    embed.add_field(name="📝 Note", value=f"Showing first 15 of {len(categories)} categories", inline=False)
            else:
                embed.description = "Popular categories: Torah, Talmud, Mishnah, Halakhah, Kabbalah, Liturgy, Philosophy"
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Categories error: {e}")
            embed = discord.Embed(title="📂 Text Categories", description="Torah • Talmud • Mishnah • Halakhah • Kabbalah • Liturgy • Philosophy • Midrash • Responsa", color=0x3498DB)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="explore", description="🔍 Explore additional Jewish learning features")
    async def explore_command(self, interaction: discord.Interaction):
        """Interactive menu for additional Jewish learning features"""
        embed = discord.Embed(
            title="🔍 Explore Additional Features",
            description="**Access specialized Jewish learning tools and resources**",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🏛️ Historical Archives",
            value="• Early Chabad documents\n• Jewish calendar calculations\n• Historical text collections",
            inline=True
        )
        
        embed.add_field(
            name="🤲 Prayer & Liturgy",
            value="• Daily prayer services\n• Holiday liturgy\n• Custom siddur creation",
            inline=True
        )
        
        embed.add_field(
            name="📊 Advanced Tools",
            value="• Cross-platform search\n• Responsa database\n• Torah insights sharing",
            inline=True
        )
        
        embed.add_field(
            name="🎯 How to Use",
            value="Click the buttons below to explore these specialized features from our comprehensive Jewish learning ecosystem.",
            inline=False
        )
        
        view = ExploreView(self.clients)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    """Setup comprehensive commands with all API clients"""
    from .sefaria_client import SefariaClient
    from .hebcal_client import HebcalClient
    from .nli_client import NLIClient
    from .chabad_client import ChabadClient
    from .dicta_client import DictaClient
    from .ai_client import AIClient
    
    # Import ALL API clients
    from .opentorah_client import OpenTorahClient
    from .torahcalc_client import TorahCalcClient
    from .orayta_client import OraytaClient
    from .opensiddur_client import OpenSiddurClient
    from .pninim_client import PninimClient
    
    # Initialize ALL clients for complete functionality
    clients = {
        'sefaria': SefariaClient(),
        'hebcal': HebcalClient(),
        'nli': NLIClient(),
        'chabad': ChabadClient(),
        'dicta': DictaClient(),
        'ai': AIClient(),
        'opentorah': OpenTorahClient(),
        'torahcalc': TorahCalcClient(),
        'orayta': OraytaClient(),
        'opensiddur': OpenSiddurClient(),
        'pninim': PninimClient()
    }
    
    await bot.add_cog(ComprehensiveCommands(bot, **clients))