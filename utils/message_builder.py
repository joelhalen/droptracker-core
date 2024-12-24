from datetime import datetime
from typing import Dict, List, Optional
import interactions
from interactions import Embed, Button, ButtonStyle, InteractionType, Message, SlashContext

from models import Log
from utils.num import format_number


def build_default(title: str, description: str, thumb: bool = True):
    """
        Builds a default embed with the DropTracker logo and footer
    """
    embed = Embed(
        title=title,
        description=description,
        color=0x00FF00
    )
    embed.set_author(
        name="DropTracker",
        icon_url="https://joelhalen.github.io/droptracker-small.gif"
    )
    embed.set_footer("Powered by the DropTracker | https://www.droptracker.io/")
    if thumb:
        embed.set_thumbnail(url="https://joelhalen.github.io/droptracker-small.gif")
    return embed

def create_metrics_embed(metrics: dict) -> Embed:
    """Create formatted embed for metrics display"""
    embed = Embed(
        title="DropTracker Status",
        description=f"Started: <t:{metrics['system']['uptime']['start_time']}:R>",
        color=0x00ff00
    )
    embed.add_field(name="Last updated:", value=f"<t:{int(datetime.now().timestamp())}:R>")
    
    # Add system metrics
    sys_metrics = metrics['system']
    embed.add_field(
        name="System Resources",
        value=f"""
        **Memory Usage:** `{sys_metrics['memory']['rss']:.1f}MB`
        **CPU Usage:** `{sys_metrics['memory']['cpu_percent']:.1f}%`
        **Threads:** `{sys_metrics['memory']['threads']}`
        **System CPU:** `{sys_metrics['system']['cpu_percent']:.1f}%`
        **System Memory:** `{sys_metrics['system']['memory_percent']:.1f}%`
        """.strip(),
        inline=False
    )
    
    # Add metrics for each type
    for metric_type in ['drops', 'logs', 'achievements', 'pbs']:
        data = metrics[metric_type]
        embed.add_field(
            name=f"{metric_type.title()} Stats",
            value=f"""
            **Total:** `{format_number(data['total']['count'])}`
            **Avg/Hour:** `{format_number(data['total']['avg_per_hour'])}/hr`
            **Last Hour:** `{format_number(data['rolling']['last_hour']['count'])}` (`{format_number(data['rolling']['last_hour']['avg_per_minute'])}/min`)
            **Last Day:** `{format_number(data['rolling']['last_day']['count'])}` (`{format_number(data['rolling']['last_day']['avg_per_hour'])}/hr`)
            """.strip(),
            inline=True
        )
    
    # Add current period stats
    current_stats = "\n".join([
        f"**{metric_type.title()}:** `{format_number(metrics[metric_type]['current']['hourly'])}`"
        for metric_type in ['drops', 'logs', 'achievements', 'pbs']
    ])
    
    embed.add_field(
        name="Current Hour",
        value=current_stats,
        inline=False
    )
    
    return embed

async def create_log_embed(
    logs: List[Log], 
    source: Optional[str] = None, 
    level: Optional[str] = None,
    limit: int = 100
) -> List[Embed]:
    """
    Create formatted embeds for log display
    
    Args:
        logs: List of Log objects to format
        source: Optional source to filter logs by (e.g. 'check_player')
        level: Optional level to filter logs by (e.g. 'ERROR', 'INFO')
        limit: Maximum number of logs to display (default 100)
        
    Returns:
        List of Embed objects containing formatted logs
    """
    embeds = []
    current_embed = Embed(
        title="DropTracker logs",
        color=0x00ff00
    )
    
    # Filter logs based on parameters
    filtered_logs = logs
    if source:
        filtered_logs = [log for log in filtered_logs if log.source == source]
    if level:
        filtered_logs = [log for log in filtered_logs if log.level == level.upper()]
    
    # Apply limit after filtering
    filtered_logs = filtered_logs[-limit:]
    
    # Add filter info to first embed
    filter_text = []
    if source:
        filter_text.append(f"Source: `{source}`")
    if level:
        filter_text.append(f"Level: `{level.upper()}`")
    if filter_text:
        current_embed.description = "Filtered by: " + " | ".join(filter_text)
    
    for log in filtered_logs:
        log_message = (
            f"**Level:** `{log.level}`\n"
            f"**Source:** `{log.source}`\n"
            f"**Message:** `{log.message}`\n"
        )
        
        # Only add details if they exist
        if log.details:
            log_message += f"**Details:** ```{log.details}```\n"
            
        log_message += f"**Timestamp:** <t:{log.timestamp}:R>"
        
        if len(current_embed.fields) < 25:  # Discord limit for fields in an embed
            current_embed.add_field(
                name=f"Log #{log.id}",
                value=log_message,
                inline=False
            )
        else:
            embeds.append(current_embed)
            current_embed = Embed(
                title="DropTracker logs",
                color=0x00ff00
            )
            current_embed.add_field(
                name=f"Log #{log.id}",
                value=log_message,
                inline=False
            )
    
    if current_embed.fields:  # If there are any fields in the last embed
        embeds.append(current_embed)
        
    # Add page numbers
    for i, embed in enumerate(embeds):
        embed.set_footer(text=f"Page {i+1}/{len(embeds)}")
    
    return embeds


async def generate_lootboard_embed(total_players: int) -> Embed:
    """
    Generate a leaderboard embed
    """
    current_time = datetime.now()
    ten_minutes_from_now = current_time.timestamp() + 600
    embed = Embed(
        title="Loot Leaderboard",
        color=0x00ff00
    )
    embed.add_field(name="Refreshes", value=f"<t:{int(ten_minutes_from_now)}:R>", inline=True)
    embed.add_field(name="Members tracked:", value=f"{total_players}", inline=True)
    embed.add_field(name="Sign up!", value=f"Use the `/claim-rsn` command & install [our plugin](https://www.github.com/joelhalen/droptracker-plugin)", inline=True)
    embed.set_footer(text="Powered by the DropTracker | https://www.droptracker.io/")
    embed.set_thumbnail(url="https://joelhalen.github.io/droptracker-small.gif")
    return embed