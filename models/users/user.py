# models/users/user.py
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from ..base import Base
from ..associations import user_group_association

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
        from ..base import session
        existing_association = session.query(user_group_association).filter_by(
            user_id=self.user_id, group_id=group.group_id).first()

        if not existing_association:
            self.groups.append(group)
            session.commit()