from datetime import datetime
import interactions
from interactions import Embed, Button, ButtonStyle, InteractionType, Message, SlashContext

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