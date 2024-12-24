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
from utils import logger, wiseoldman
from utils.num import format_number
from models import Player, Group, GroupConfiguration
from models.base import session

logger = logger.Logger()
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
        bg_img, draw = self._load_background_image("assets/img/lootboards/dark.png")
        
        # Calculate total loot
        total_loot = sum(data['player_totals'].values())
        
        # Draw all sections
        bg_img = await self._draw_headers(bg_img, draw, group, total_loot)
        bg_img = await self._draw_items(bg_img, draw, data)
        bg_img = await self._draw_leaderboard(bg_img, draw, data['player_totals'])
        
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

    async def _draw_headers(self, bg_img: Image.Image, draw: ImageDraw.ImageDraw, 
                           group: Group, total_loot: int) -> Image.Image:
        """Draw the header section of the board"""
        current_month = datetime.now().month
        month_string = calendar.month_name[current_month].capitalize()
        this_month = format_number(total_loot)
        
        if not group or group.group_id == 2:
            title = f"Tracked Drops - All Players ({month_string}) - {this_month}"
        else:
            title = f"{group.group_name}'s Tracked Drops for {month_string} ({this_month})"

        # Calculate text size and center
        bbox = draw.textbbox((0, 0), title, font=self.main_font)
        text_width = bbox[2] - bbox[0]
        bg_img_w, _ = bg_img.size
        head_loc_x = int((bg_img_w - text_width) / 2)
        head_loc_y = 20
        
        draw.text((head_loc_x, head_loc_y), title, font=self.main_font, 
                  fill=self.yellow, stroke_width=2, stroke_fill=self.black)
        return bg_img

    async def _draw_items(self, bg_img: Image.Image, draw: ImageDraw.ImageDraw, 
                         data: Dict) -> Image.Image:
        """Draw the items grid section"""
        locations = {}
        
        # Load item positions from CSV
        with open("data/item-mapping.csv", 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                locations[i] = row
        
        # Combine all items from all players
        all_items = defaultdict(lambda: {'quantity': 0, 'value': 0})
        for player_items in data['player_items'].values():
            for item in player_items:
                item_id = item['item_id']
                all_items[item_id]['quantity'] += item['quantity']
                all_items[item_id]['value'] += item['value']
        
        # Sort items by total value and take top 32
        sorted_items = sorted(all_items.items(), 
                             key=lambda x: x[1]['value'], 
                             reverse=True)[:32]
        
        for i, (item_id, item_data) in enumerate(sorted_items):
            if i >= len(locations):
                break
            
            current_pos_x = int(locations[i]['x'])
            current_pos_y = int(locations[i]['y'])
            
            # Load and draw item image
            item_img = await self._load_item_image(item_id)
            if not item_img:
                continue
            
            # Resize and center image
            item_img_resized = item_img.resize(
                (round(item_img.width * 1.1), 
                 round(item_img.height * 1.1)), 
                Image.Resampling.LANCZOS
            )
            fixed_img = self._resize_and_center_image(item_img_resized, 75, 75)
            bg_img.paste(fixed_img, (current_pos_x - 5, current_pos_y - 12), fixed_img)
            
            # Draw quantity and value
            quantity_str = format_number(int(item_data['quantity']))
            value_str = format_number(item_data['value'])
            
            draw.text((current_pos_x + 1, current_pos_y - 10), quantity_str,
                     font=self.amt_font, fill=self.yellow, 
                     stroke_width=2, stroke_fill=self.black)
            draw.text((current_pos_x + 1, current_pos_y + 35), value_str,
                     font=self.small_font, fill=self.yellow,
                     stroke_width=1, stroke_fill=self.black)
        
        return bg_img

    async def _draw_leaderboard(self, bg_img: Image.Image, draw: ImageDraw.ImageDraw, 
                              player_totals: Dict) -> Image.Image:
        """Draw the leaderboard section"""
        # Sort players by total loot value
        top_players = sorted(player_totals.items(), key=lambda x: x[1], reverse=True)[:12]
        
        name_x, name_y = 141, 228
        first_name = True
        
        for i, (player_id, total) in enumerate(top_players):
            # Get player name from database
            player_obj = session.query(Player.player_name).filter(
                Player.player_id == player_id).first()
            player_name = player_obj.player_name if player_obj else "Unknown"
            
            # Format texts
            rank_text = f'{i + 1}'
            value_text = format_number(total)
            
            # Calculate positions
            rank_x = name_x - 104
            value_x = name_x + 106
            
            # Center each text element
            rank_bbox = draw.textbbox((0, 0), rank_text, font=self.small_font)
            name_bbox = draw.textbbox((0, 0), player_name, font=self.small_font)
            value_bbox = draw.textbbox((0, 0), value_text, font=self.small_font)
            
            rank_x = rank_x - (rank_bbox[2] - rank_bbox[0]) // 2
            name_x_centered = name_x - (name_bbox[2] - name_bbox[0]) // 2
            value_x = value_x - (value_bbox[2] - value_bbox[0]) // 2
            
            # Draw texts
            draw.text((rank_x, name_y), rank_text, font=self.small_font, fill=self.yellow)
            draw.text((name_x_centered, name_y), player_name, font=self.small_font, fill=self.yellow)
            draw.text((value_x, name_y), value_text, font=self.small_font, fill=self.yellow)
            
            name_y += 22
        
        return bg_img

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
    partition, _ = get_partition(datetime.now())
        
    # Convert partition to datetime object
    year = partition // 100
    month = partition % 100
    partition_date = datetime(year, month, 1)
        
    player_items = defaultdict(list)
    player_totals = defaultdict(int)
    
    # Fetch data for each player
    for player_id in player_ids:
        cache = get_player_cache(player_id)
        if not cache:
            continue
            
        # Pass datetime object instead of partition number
        partition_keys = cache._get_cache_keys(partition_date)
        
        # Get all items for this player in this partition
        items_data = redis_client.hgetall(partition_keys['items'])
        
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


async def board_generator(group_wom_id, partition: int = None) -> str:
    """
    Generate a leaderboard for a specific group based on the group's Wom ID
    
    Params:
    group_wom_id: The group's Wom ID
    partition: The partition to get data for

    Returns:
    str: The filepath to the generated lootboard image
    """
    if group_wom_id == 1:
        group_members = [player.wom_id for player in session.query(Player.wom_id).all()]
    else:   
        group_members = await get_group_player_ids(group_wom_id)
    total_players = len(group_members)
    # drops = await get_lootboard_data(group_members, partition)
    generator = LootboardGenerator()
    logger.info("board_generator",f"Generating lootboard for group {group_wom_id}")
    return await generator.generate_board(wom_group_id=group_wom_id), total_players
