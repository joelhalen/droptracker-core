from typing import List, Dict, Tuple
from collections import defaultdict
from datetime import datetime
import calendar
import json
import os
import csv
from io import BytesIO
import aiohttp
from PIL import Image, ImageFont, ImageDraw
from interactions import Embed
from utils.message_builder import generate_lootboard_embed
from utils.misc import get_partition, get_player_cache
from cache import redis_client
from utils import wiseoldman
from utils.num import format_number
from models import Player, Group, GroupConfiguration
from models.base import session
    
class LootboardGenerator:
    def __init__(self):
        self.yellow = (255, 255, 0)
        self.black = (0, 0, 0)
        self.font_size = 30
        self.rs_font_path = "assets/fonts/runescape_uf.ttf"
        self.main_font = ImageFont.truetype(self.rs_font_path, self.font_size)
        self.small_font = ImageFont.truetype(self.rs_font_path, 18)
        self.amt_font = ImageFont.truetype(self.rs_font_path, 25)
        
    async def generate_board(self, group_id: int = None, wom_group_id: int = None) -> str:
        """Generate a lootboard for a group"""
        # Get group data
        group = None
        if group_id:
            group = session.query(Group).filter(Group.group_id == group_id).first()
        elif wom_group_id:
            group = session.query(Group).filter(Group.wom_id == wom_group_id).first()
            
        # Get player IDs
        if group:
            player_ids = await get_group_player_ids(group.wom_id)
        else:
            # Get all players if no group specified
            player_ids = [p.player_id for p in session.query(Player.player_id).all()]
            
        # Get lootboard data
        data = await get_lootboard_data(player_ids)
        
        # Generate and save board
        return await self._generate_board_image(data, group)
        
    async def _generate_board_image(self, data: Dict, group: Group = None) -> str:
        """Generate the actual board image"""
        bg_img, draw = self._load_background_image("assets/img/bank-new-clean-dark.png")
        
        # Draw all sections
        bg_img = await self._draw_headers(bg_img, draw, group.group_name if group else None, data)
        bg_img = await self._draw_items(bg_img, draw, data)
        bg_img = await self._draw_leaderboard(bg_img, draw, data)
        
        # Save and return path
        group_id = group.group_id if group else 0
        return self._save_image(bg_img, group_id)
        
    def _load_background_image(self, filepath: str) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
        """Load and prepare background image"""
        bg_img = Image.open(filepath)
        draw = ImageDraw.Draw(bg_img)
        return bg_img, draw
        
    def _save_image(self, image: Image.Image, group_id: int) -> str:
        """Save the generated image"""
        save_dir = f"assets/img/clans/{group_id}/lb"
        os.makedirs(save_dir, exist_ok=True)
        
        current_date = datetime.now()
        filename = f"{current_date.strftime('%d%m%Y')}.png"
        filepath = os.path.join(save_dir, filename)
        
        image.save(filepath)
        return filepath

    async def _load_item_image(self, item_id: int) -> Image.Image:
        """Load item image from cache or download if needed"""
        file_path = f"assets/img/itemdb/{item_id}.png"
        
        if not os.path.exists(file_path):
            await self._download_item_image(item_id)
            
        try:
            return Image.open(file_path)
        except Exception as e:
            print(f"Error loading image for item {item_id}: {e}")
            return None
            
    async def _download_item_image(self, item_id: int):
        """Download item image from RuneLite API"""
        url = f"https://static.runelite.net/cache/item/icon/{item_id}.png"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    image = Image.open(BytesIO(image_data))
                    
                    file_path = f"assets/img/itemdb/{item_id}.png"
                    image.save(file_path, "PNG")
                    
    def _resize_and_center_image(self, image: Image.Image, width: int, height: int) -> Image.Image:
        """Resize and center an image within specified dimensions"""
        # First resize
        scale_factor = 1.8
        new_width = round(image.width * scale_factor)
        new_height = round(image.height * scale_factor)
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Then center
        centered = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        paste_x = (width - resized.width) // 2
        paste_y = (height - resized.height) // 2
        centered.paste(resized, (paste_x, paste_y))
        
        return centered

async def get_lootboard_data(player_ids: List[int], partition: int = None) -> Dict:
    """
    Generate leaderboard data for a group of players for a specific month
    
    Returns:
    {
        'player_items': {
            player_id: [
                {
                    'item_id': item_id,
                    'quantity': total_qty,
                    'value': total_stack_value,
                    'unit_value': value_per_item
                },
                ...  # Sorted by total_stack_value
            ]
        },
        'player_totals': {
            player_id: total_value
        },
        'top_players': [
            (player_id, total_value),
            ...
        ]
    }
    """
    if partition is None:
        partition = get_partition(datetime.now())
        
    # Changed to store items as a list that we'll sort later
    player_items = defaultdict(list)
    player_totals = defaultdict(int)
    
    # Fetch data for each player
    for player_id in player_ids:
        cache = get_player_cache(player_id)
        if not cache:
            continue
            
        # Get partition keys
        partition_keys = cache._get_cache_keys(partition)
        
        # Get all items for this player in this partition
        items_data = await redis_client.hgetall(partition_keys['items'])
        
        # Temporary storage for item data before sorting
        temp_items = defaultdict(lambda: {'quantity': 0, 'value': 0})
        
        # Process each item
        for key, value in items_data.items():
            item_id, stat_type = key.split(':')
            
            if stat_type == 'quantity':
                temp_items[item_id]['quantity'] = int(value)
            elif stat_type == 'value':
                temp_items[item_id]['value'] = int(value)
                player_totals[player_id] += int(value)
        
        # Convert to sorted list
        items_list = []
        for item_id, data in temp_items.items():
            if data['quantity'] > 0:  # Only include items that exist
                items_list.append({
                    'item_id': int(item_id),
                    'quantity': data['quantity'],
                    'value': data['value'],  # Total stack value
                    'unit_value': data['value'] // data['quantity']  # Value per item
                })
        
        # Sort items by total stack value (highest to lowest)
        items_list.sort(key=lambda x: x['value'], reverse=True)
        player_items[player_id] = items_list
    
    # Sort players by total value
    top_players = sorted(
        player_totals.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return {
        'player_items': dict(player_items),
        'player_totals': dict(player_totals),
        'top_players': top_players
    }

async def get_group_player_ids(group_wom_id: int) -> List[int]:
    """
        Get a list of player IDs for a specific group
    """
    return await wiseoldman.fetch_group_members(group_wom_id)


async def get_group_leaderboard(group_wom_id: int) -> Dict:
    """
    Get a leaderboard for a specific group
    """
    player_ids = await get_group_player_ids(group_wom_id)
    return await get_lootboard_data(player_ids)

async def board_generator(group_wom_id, partition: int = None) -> Embed:
    """
    Generate a leaderboard for a specific group based on the group's Wom ID
    
    Params:
    group_wom_id: The group's Wom ID
    partition: The partition to get data for

    Returns:
    Embed: The leaderboard embed
    """
    if group_wom_id == 1:
        group_members = [player.wom_id for player in session.query(Player.wom_id).all()]
    else:   
        group_members = await get_group_player_ids(group_wom_id)
        
    drops = await get_lootboard_data(group_members, partition)
    return await generate_lootboard_embed(drops)
