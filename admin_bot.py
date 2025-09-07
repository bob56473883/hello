import discord
from discord.ext import commands
import requests
import asyncio
import os

# Bot token - get from environment variable or use default
TOKEN = os.getenv('DISCORD_TOKEN', "MTQxNDE2MjYyMzUwMjc0NTY0MQ.Gfau7R.1joJy8tjBmAh1TuB-D_7Fm5UuMh6X4jXLbxcDc")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Store the status message ID for editing
status_message_id = None

# Admin user IDs (add your Discord user ID here)
ADMIN_IDS = [1414311018405953647, 1342943488718798999]  # Your Discord user IDs

# Alternative: Check if user is server owner
def is_admin_or_owner(ctx):
    """Check if user is admin or server owner"""
    return ctx.author.id in ADMIN_IDS or ctx.author == ctx.guild.owner

def is_admin(ctx):
    """Check if user is admin"""
    return ctx.author.id in ADMIN_IDS

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Admin bot is ready!')
    
    # Create admin commands channel if it doesn't exist
    for guild in bot.guilds:
        channel_exists = False
        for channel in guild.channels:
            if channel.name == "admin-cmds" and isinstance(channel, discord.TextChannel):
                channel_exists = True
                break
        
        if not channel_exists:
            try:
                await guild.create_text_channel("admin-cmds")
                print(f"Created admin-cmds channel in {guild.name}")
            except:
                print(f"Could not create admin-cmds channel in {guild.name}")

# Admin user IDs - only these users can use commands
ADMIN_USER_IDS = [
    1414311018405953647,  # Your Discord user ID
    1342943488718798999   # Your Discord user ID
]

def is_admin_user(ctx):
    """Check if user is authorized admin"""
    return ctx.author.id in ADMIN_USER_IDS

def is_admin_channel(ctx):
    """Check if command is used in admin-cmds channel"""
    return ctx.channel.name == "admin-cmds"

@bot.command(name='disable')
@commands.check(is_admin_channel)
@commands.check(is_admin_user)
async def disable_command(ctx):
    """Disable the loader (admin only)"""
    global status_message_id
    try:
        # Check if already disabled
        if status_message_id:
            try:
                message = await ctx.channel.fetch_message(status_message_id)
                if message.embeds and "DISABLED" in message.embeds[0].description:
                    await ctx.send("Loader is already disabled!")
                    return
            except:
                pass
        
        # Status is now controlled by Discord embed messages only
        
        embed = discord.Embed(
            title="Loader Status",
            description="Loader has been **DISABLED**",
            color=0xff0000,  # Red color
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(
            name="Status",
            value="❌ DISABLED",
            inline=True
        )
        embed.add_field(
            name="Action",
            value="Users will now get syntax errors when trying to run the loader",
            inline=False
        )
        embed.set_footer(text=f"Last updated by {ctx.author.display_name}")
        
        # Edit existing message or send new one
        if status_message_id:
            try:
                message = await ctx.channel.fetch_message(status_message_id)
                await message.edit(embed=embed)
            except:
                msg = await ctx.send(embed=embed)
                status_message_id = msg.id
        else:
            msg = await ctx.send(embed=embed)
            status_message_id = msg.id
        
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name='enable')
@commands.check(is_admin_channel)
@commands.check(is_admin_user)
async def enable_command(ctx):
    """Enable the loader (admin only)"""
    global status_message_id
    try:
        # Check if already enabled
        if status_message_id:
            try:
                message = await ctx.channel.fetch_message(status_message_id)
                if message.embeds and "ENABLED" in message.embeds[0].description:
                    await ctx.send("Loader is already enabled!")
                    return
            except:
                pass
        
        # Status is now controlled by Discord embed messages only
        
        embed = discord.Embed(
            title="Loader Status",
            description="Loader has been **ENABLED**",
            color=0x00ff00,  # Green color
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(
            name="Status",
            value="✅ ENABLED",
            inline=True
        )
        embed.add_field(
            name="Action",
            value="Users can now run the loader without errors",
            inline=False
        )
        embed.set_footer(text=f"Last updated by {ctx.author.display_name}")
        
        # Edit existing message or send new one
        if status_message_id:
            try:
                message = await ctx.channel.fetch_message(status_message_id)
                await message.edit(embed=embed)
            except:
                msg = await ctx.send(embed=embed)
                status_message_id = msg.id
        else:
            msg = await ctx.send(embed=embed)
            status_message_id = msg.id
        
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name='status')
@commands.check(is_admin_channel)
@commands.check(is_admin_user)
async def status_command(ctx):
    """Check current loader status (admin only)"""
    try:
        # Check Discord embed messages for status
        try:
            # Look for recent status embed in admin-cmds channel
            status_found = False
            async for message in ctx.channel.history(limit=10):
                if message.embeds and message.embeds[0].title == "Loader Status":
                    embed = message.embeds[0]
                    if "DISABLED" in embed.description:
                        status = "❌ DISABLED"
                        color = 0xff0000
                        description = "Loader is currently **DISABLED**"
                    elif "ENABLED" in embed.description:
                        status = "✅ ENABLED"
                        color = 0x00ff00
                        description = "Loader is currently **ENABLED**"
                    else:
                        status = "⚠️ UNKNOWN"
                        color = 0xffff00
                        description = "Loader status is unknown"
                    status_found = True
                    break
            
            if not status_found:
                status = "❓ NO STATUS FOUND"
                color = 0xffff00
                description = "No status message found in this channel"
        except Exception as e:
            status = "❓ ERROR"
            color = 0xffff00
            description = f"Error checking status: {e}"
        
        embed = discord.Embed(
            title="Loader Status Check",
            description=description,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(
            name="Current Status",
            value=status,
            inline=True
        )
        embed.add_field(
            name="Status Source",
            value="Local file" if os.path.exists('loader_status.txt') else "Pastebin",
            inline=True
        )
        embed.set_footer(text=f"Status checked by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"Error checking status: {e}")

@disable_command.error
@enable_command.error
@status_command.error
async def admin_error(ctx, error):
    """Handle admin command errors"""
    if isinstance(error, commands.CheckFailure):
        # Check which specific check failed
        if not is_admin_channel(ctx):
            embed = discord.Embed(
                title="Wrong Channel",
                description="❌ This command can only be used in the **admin-cmds** channel.",
                color=0xff0000
            )
            embed.add_field(
                name="Required Channel",
                value="#admin-cmds",
                inline=True
            )
            await ctx.send(embed=embed)
        elif not is_admin_user(ctx):
            embed = discord.Embed(
                title="Access Denied",
                description="❌ You do not have permission to use this command.",
                color=0xff0000
            )
            embed.add_field(
                name="Authorized Users",
                value="@solis and @.",
                inline=True
            )
            await ctx.send(embed=embed)
    else:
        await ctx.send(f"An error occurred: {error}")

if __name__ == "__main__":
    bot.run(TOKEN)
