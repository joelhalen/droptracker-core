from datetime import datetime
import pymysql
pymysql.install_as_MySQLdb()

from sqlalchemy import UniqueConstraint, create_engine, Column, Table, Integer, Boolean, String, ForeignKey, DateTime, Float, text
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import func
from dotenv import load_dotenv
import os
load_dotenv()

Base = declarative_base()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


def get_current_partition() -> int:
    """
        Returns the naming scheme for a partition of drops
        Based on the current month
    """
    now = datetime.now()
    return now.year * 100 + now.month


""" Define associations between users and players """
user_group_association = Table(
    'user_group_association', Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('player_id', Integer, ForeignKey('players.player_id'), nullable=True),
    Column('user_id', Integer, ForeignKey('users.user_id'), nullable=True),
    Column('group_id', Integer, ForeignKey('groups.group_id'), nullable=False),
    UniqueConstraint('player_id', 'user_id', 'group_id', name='uq_user_group_player')
)

class NpcList(Base):
    """
        Stores the list of valid NPCs that are 
        being tracked individually for ranking purposes
        :param: npc_id: ID of the NPC based on OSRS Reboxed
        :param: npc_name: Name of the NPC based on OSRS Reboxed
    """
    __tablename__ = 'npc_list'
    npc_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    npc_name = Column(String(60), nullable=False)

class ItemList(Base):
    __tablename__ = 'items'
    item_id = Column(Integer, primary_key=True,nullable=False, index=True)
    item_name = Column(String(125), index=True)
    noted = Column(Boolean, nullable=False)

class NotifiedSubmission(Base):
    """
    Drops that have exceeded the necessary threshold to have a notification
    sent to a Discord channel are stored in this table to allow modifications
    to be made to the message, drop, etc.
    """
    __tablename__ = 'notified'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    channel_id = Column(String(35), nullable=False)
    message_id = Column(String(35))
    group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=False)
    status = Column(String(15))  # 'sent', 'removed', or 'pending'
    date_added = Column(DateTime, index=True, default=func.now())
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())
    edited_by = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    
    # Nullable foreign keys to allow only one relationship to be defined
    drop_id = Column(Integer, ForeignKey('drops.drop_id'), nullable=True)
    clog_id = Column(Integer, ForeignKey('collection.log_id'), nullable=True)
    ca_id = Column(Integer, ForeignKey('combat_achievement.id'), nullable=True)
    pb_id = Column(Integer, ForeignKey('personal_best.id'), nullable=True)

    # Relationships
    drop = relationship("Drop", back_populates="notified_drops")
    clog = relationship("CollectionLogEntry", back_populates="notified_clog")
    ca = relationship("CombatAchievementEntry", back_populates="notified_ca")
    pb = relationship("PersonalBestEntry", back_populates="notified_pb")

    def __init__(self, channel_id: str, 
                 message_id: str, 
                 group_id: int,
                 status: str, 
                 drop=None, 
                 clog=None, 
                 ca=None, 
                 pb=None):
        """
        Ensure that only one of drop, clog, ca, or pb can be defined.
        """
        if sum([bool(drop), bool(clog), bool(ca), bool(pb)]) > 1:
            raise ValueError("Only a single association can be provided to a NotifiedSubmission.")
        self.channel_id = channel_id
        self.message_id = message_id
        self.group_id = group_id
        self.status = status
        self.drop = drop
        self.clog = clog
        self.ca = ca
        self.pb = pb


class Drop(Base):
    """
        :param: item_id
        :param: player_id
        :param: npc_id
        :param: value
        :param: quantity
        :param: image_url (nullable)
    """
    __tablename__ = 'drops'
    drop_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('items.item_id'), index=True)
    player_id = Column(Integer, ForeignKey('players.player_id'), index=True, nullable=False)
    date_added = Column(DateTime, index=True, default=func.now())
    npc_id = Column(Integer, ForeignKey('npc_list.npc_id'), index=True)
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())
    value = Column(Integer)
    quantity = Column(Integer)
    image_url = Column(String(150), nullable=True)
    authed = Column(Boolean, default=False)
    partition = Column(Integer, default=get_current_partition, index=True)
    
    player = relationship("Player", back_populates="drops")
    notified_drops = relationship("NotifiedSubmission", back_populates="drop")


class CollectionLogEntry(Base):
    """ 
        :param: item_id: The item ID for the item the user received
        :param: source: The NPC or source name that the drop was received from
        :param: player_id: The ID of the player who received the drop
        :param: reported_slots: The total log slots the user had when the submission arrived
    """
    __tablename__ = 'collection'
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, index=True, nullable=False)
    npc_id = Column(Integer, ForeignKey('npc_list.npc_id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.player_id'), index=True, nullable=False)
    reported_slots = Column(Integer)
    image_url = Column(String(255), nullable=True)
    date_added = Column(DateTime, index=True, default=func.now())
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())

    player = relationship("Player", back_populates="clogs")
    notified_clog = relationship("NotifiedSubmission", back_populates="clog")


class CombatAchievementEntry(Base):
    """
        :param: player_id: Player ID who received this achievement
        :param: task_name: The name of the task they completed

    """
    __tablename__ = 'combat_achievement'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.player_id'))
    task_name = Column(String(255), nullable=False)
    image_url = Column(String(255), nullable=True)
    date_added = Column(DateTime, index=True, default=func.now())

    player = relationship("Player", back_populates="cas")
    notified_ca = relationship("NotifiedSubmission", back_populates="ca")


class PersonalBestEntry(Base):
    """
        Stores kill-time data for users
    """
    __tablename__ = 'personal_best'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.player_id'))
    npc_id = Column(Integer, ForeignKey('npc_list.npc_id'))
    kill_time = Column(Integer, nullable=False)
    personal_best = Column(Integer, nullable=False)
    new_pb = Column(Boolean, default=False)
    image_url = Column(String(150), nullable=True)

    player = relationship("Player", back_populates="pbs")
    notified_pb = relationship("NotifiedSubmission", back_populates="pb")

class Player(Base):
    """ 
    :param: wom_id: The player's WiseOldMan ID
    :param: player_name: The DISPLAY NAME of the player, exactly as it appears
    :param: user_id: The ID of the associated User object, if one exists
    :param: log_slots: Stored number of collected log slots
    :param: total_level: Account total level based on the last update with WOM.
        Defines the player object, which is instantly created any time a unique username
        submits a new drop/etc, and their WiseOldMan user ID doesn't already exist in our database.
    """
    __tablename__ = 'players'
    player_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    wom_id = Column(Integer, unique=True)
    account_hash = Column(String(100), nullable=True, unique=True)
    player_name = Column(String(20), index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    log_slots = Column(Integer)
    total_level = Column(Integer)
    date_added = Column(DateTime, default=func.now())
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())

    pbs = relationship("PersonalBestEntry", back_populates="player")
    cas = relationship("CombatAchievementEntry", back_populates="player")
    clogs = relationship("CollectionLogEntry", back_populates="player")  # Add this line
    
    user = relationship("User", back_populates="players")
    drops = relationship("Drop", back_populates="player")
    groups = relationship("Group", secondary=user_group_association, back_populates="players")

    def add_group(self, group):
        # Check if the association already exists by querying the user_group_association table
        existing_association = session.query(user_group_association).filter_by(
            player_id=self.player_id, group_id=group.group_id).first()
        if self.user:
            tuser: User = self.user
            tuser.add_group(group)
        if not existing_association:
            # Only add the group if no association exists
            self.groups.append(group)
            session.commit()

    def __init__(self, wom_id, player_name, account_hash, user_id=None, user=None, log_slots=0, total_level=0, group=None):
        self.wom_id = wom_id
        self.player_name = player_name
        self.account_hash = account_hash
        self.user_id = user_id
        self.user = user
        self.log_slots = log_slots
        self.total_level = total_level
        self.group = group

class User(Base):
    """
        :param: discord_id: The string formatted representation of the user's Discord ID
        :param: username: The user's Discord display name
        :param: patreon: The patreon subscription status of the user
    """
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    discord_id = Column(String(35))
    date_added = Column(DateTime, default=func.now())
    auth_token = Column(String(16), nullable=False)
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())
    username = Column(String(20))
    xf_user_id = Column(Integer, nullable=True)

    players = relationship("Player", back_populates="user")
    groups = relationship("Group", secondary=user_group_association, back_populates="users", overlaps="groups")
    configurations = relationship("UserConfiguration", back_populates="user")
    group_patreon = relationship("GroupPatreon", back_populates="user")

    def add_group(self, group):
        # Check if the association already exists by querying the user_group_association table
        existing_association = session.query(user_group_association).filter_by(
            user_id=self.user_id, group_id=group.group_id).first()

        if not existing_association:
            # Only add the group if no association exists
            self.groups.append(group)
            session.commit()


class Group(Base):
    """
    :param: group_name: Publicly-displayed name of the group
    :param: wom_id: WiseOldMan group ID associated with the Group
    :param: guild_id: Discord Guild ID, if one is associated with it
    """
    __tablename__ = 'groups'
    group_id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String(30), index=True)
    description = Column(String(255), nullable=True)
    date_added = Column(DateTime, default=func.now())
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())
    wom_id = Column(Integer, default=None)
    guild_id = Column(String(255), default=None, nullable=True)

    # Relationships
    configurations = relationship("GroupConfiguration", back_populates="group")
    # drops = relationship("Drop", back_populates="group")
    players = relationship("Player", secondary=user_group_association, back_populates="groups", overlaps="groups", lazy='dynamic')
    users = relationship("User", secondary=user_group_association, back_populates="groups", overlaps="groups,players")
    group_patreon = relationship("GroupPatreon", back_populates="group")
    group_embeds = relationship("GroupEmbed", back_populates="group")
    # One-to-One relationship with Guild
    guild = relationship("Guild", back_populates="group", uselist=False, cascade="all, delete-orphan")

    def add_player(self, player):
        # Check if the association already exists
        existing_association = self.players.filter(user_group_association.c.player_id == player.player_id).first()
        if not existing_association:
            # Only add the player if no association exists
            self.players.append(player)
            session.commit()

    def __init__(self, group_name, wom_id, guild_id, description: str= "An Old School RuneScape group."):
        self.group_name = group_name
        self.wom_id = wom_id
        self.guild_id = guild_id
        self.description = description
        
    def after_insert(self):
        """Call this after the group has been committed to the database"""
        pass


class GroupPatreon(Base):
    __tablename__ = 'group_patreon'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=True)
    patreon_tier = Column(Integer, nullable=False)  ## A user needs to be tier 2 
    date_added = Column(DateTime, default=func.now())
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())

    user = relationship("User", back_populates="group_patreon")
    group = relationship("Group", back_populates="group_patreon")
    


class GroupConfiguration(Base):
    __tablename__ = 'group_configurations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=False)
    config_key = Column(String(60), nullable=False)
    config_value = Column(String(255), nullable=False)
    long_value = Column(LONGTEXT, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    group = relationship("Group", back_populates="configurations")


class UserConfiguration(Base):

    __tablename__ = 'user_configurations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    config_key = Column(String(60), nullable=False)
    config_value = Column(String(255), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="configurations")

class Guild(Base):
    """
    :param: guild_id: Discord guild_id, string-formatted.
    :param: group_id: Respective group_id, if one already exists
    :param: date_added: Time the guild was generated
    :param: initialized: Status of the guild's registration (do they have a Group associated?)
    """
    __tablename__ = 'guilds'
    guild_id = Column(String(255), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=True)
    date_added = Column(DateTime, default=func.now())
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())
    initialized = Column(Boolean, default=False)

    # One-to-One relationship with Group
    group = relationship("Group", back_populates="guild", single_parent=True, uselist=False)


class GroupEmbed(Base):
    """
        Represents an embed that is sent for drops, collection logs, loot leaderboards, etc.
        :param: color: Hexidecimal representation of the color
        :param: title: String title of the embed
        :param: description: String description of the embed
        :param: thumbnail String url: 'https://i.imgur.com/AfFp7pu.png'
        :param: timestamp: Boolean - true = displayed
        :param: image: String url: 'https://i.imgur.com/AfFp7pu.png'
    """
    __tablename__ = 'group_embeds'
    embed_id = Column(Integer, primary_key=True, autoincrement=True)
    embed_type = Column(String(10)) # "lb", "drop", "clog", "ca", "pb"
    group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=False, default=1)
    color = Column(String(7),nullable=True)
    title = Column(String(255),nullable=False)
    description = Column(String(1000),nullable=True)
    thumbnail = Column(String(200))
    timestamp = Column(Boolean,nullable=True,default=False)
    image = Column(String(200),nullable=True)

    fields = relationship("Field", back_populates="embed", cascade="all, delete-orphan")
    group = relationship("Group", back_populates="group_embeds")

class Field(Base):
    __tablename__ = "group_embed_fields"
    field_id = Column(Integer, primary_key=True, autoincrement=True)
    embed_id = Column(Integer, ForeignKey('group_embeds.embed_id'), nullable=False)
    field_name = Column(String(256), nullable=False)
    field_value = Column(String(1024), nullable=False)
    inline = Column(Boolean, default=True)

    embed = relationship("GroupEmbed", back_populates="fields")

class Webhook(Base):
    __tablename__ = 'webhooks'
    webhook_id = Column(Integer, primary_key=True)
    webhook_url = Column(String(255), unique=True)
    date_added = Column(DateTime, default=func.now())
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())


# Setup database connection and create tables
engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASS}@localhost:3306/data', pool_size=20, max_overflow=10)
Base.metadata.create_all(engine)
Session = scoped_session(sessionmaker(bind=engine))
session = Session()