# models/groups/group.py
from sqlalchemy import Column, Integer, String, DateTime, func, event
from sqlalchemy.orm import relationship
from ..base import Base
from ..associations import user_group_association
from cache.player_stats import PlayerStatsCache

cache = PlayerStatsCache()

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

    configurations = relationship("GroupConfiguration", back_populates="group")
    players = relationship("Player", secondary=user_group_association, back_populates="groups", overlaps="groups", lazy='dynamic')
    users = relationship("User", secondary=user_group_association, back_populates="groups", overlaps="groups,players")
    group_patreon = relationship("GroupPatreon", back_populates="group")
    group_embeds = relationship("GroupEmbed", back_populates="group")
    guild = relationship("Guild", back_populates="group", uselist=False, cascade="all, delete-orphan")

    def add_player(self, player):
        from ..base import session
        existing_association = self.players.filter(user_group_association.c.player_id == player.player_id).first()
        if not existing_association:
            self.players.append(player)
            session.commit()

@event.listens_for(Group, 'after_insert')    
def after_group_insert(mapper, connection, target: Group) -> None:
    """Event listener for group creation
    
    Args:
        mapper: The Mapper object
        connection: The Connection object
        target (Group): The newly created Group instance
    """
    print(f"Group {target.group_id} has been created successfully")
    
