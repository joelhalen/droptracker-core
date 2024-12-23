"""Initial migration

Revision ID: 6beaaf6cff08
Revises: 
Create Date: 2024-12-21 05:24:31.679509

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '6beaaf6cff08'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('groups',
    sa.Column('group_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('group_name', sa.String(length=30), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('date_updated', sa.DateTime(), nullable=True),
    sa.Column('wom_id', sa.Integer(), nullable=True),
    sa.Column('guild_id', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('group_id')
    )
    op.create_index(op.f('ix_groups_group_name'), 'groups', ['group_name'], unique=False)
    op.create_table('items',
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('item_name', sa.String(length=125), nullable=True),
    sa.Column('noted', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('item_id')
    )
    op.create_index(op.f('ix_items_item_id'), 'items', ['item_id'], unique=False)
    op.create_index(op.f('ix_items_item_name'), 'items', ['item_name'], unique=False)
    op.create_table('metric_snapshots',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('drops', sa.Integer(), nullable=True),
    sa.Column('collections', sa.Integer(), nullable=True),
    sa.Column('pbs', sa.Integer(), nullable=True),
    sa.Column('achievements', sa.Integer(), nullable=True),
    sa.Column('missed', sa.Integer(), nullable=True),
    sa.Column('total', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.BigInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_metric_snapshots_timestamp'), 'metric_snapshots', ['timestamp'], unique=False)
    op.create_table('npc_list',
    sa.Column('npc_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('npc_name', sa.String(length=60), nullable=False),
    sa.PrimaryKeyConstraint('npc_id')
    )
    op.create_index(op.f('ix_npc_list_npc_id'), 'npc_list', ['npc_id'], unique=False)
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('discord_id', sa.String(length=35), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('auth_token', sa.String(length=16), nullable=False),
    sa.Column('date_updated', sa.DateTime(), nullable=True),
    sa.Column('username', sa.String(length=20), nullable=True),
    sa.Column('xf_user_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('webhooks',
    sa.Column('webhook_id', sa.Integer(), nullable=False),
    sa.Column('webhook_url', sa.String(length=255), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('date_updated', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('webhook_id'),
    sa.UniqueConstraint('webhook_url')
    )
    op.create_table('group_configurations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('config_key', sa.String(length=60), nullable=False),
    sa.Column('config_value', sa.String(length=255), nullable=False),
    sa.Column('long_value', mysql.LONGTEXT(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.group_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('group_embeds',
    sa.Column('embed_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('embed_type', sa.String(length=10), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('color', sa.String(length=7), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.Column('thumbnail', sa.String(length=200), nullable=True),
    sa.Column('timestamp', sa.Boolean(), nullable=True),
    sa.Column('image', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.group_id'], ),
    sa.PrimaryKeyConstraint('embed_id')
    )
    op.create_table('group_patreon',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('patreon_tier', sa.Integer(), nullable=False),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('date_updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.group_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('guilds',
    sa.Column('guild_id', sa.String(length=255), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('date_updated', sa.DateTime(), nullable=True),
    sa.Column('initialized', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.group_id'], ),
    sa.PrimaryKeyConstraint('guild_id')
    )
    op.create_table('players',
    sa.Column('player_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('wom_id', sa.Integer(), nullable=True),
    sa.Column('account_hash', sa.String(length=100), nullable=True),
    sa.Column('player_name', sa.String(length=20), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('log_slots', sa.Integer(), nullable=True),
    sa.Column('total_level', sa.Integer(), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('date_updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('player_id'),
    sa.UniqueConstraint('account_hash'),
    sa.UniqueConstraint('wom_id')
    )
    op.create_index(op.f('ix_players_player_id'), 'players', ['player_id'], unique=False)
    op.create_index(op.f('ix_players_player_name'), 'players', ['player_name'], unique=False)
    op.create_table('user_configurations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('config_key', sa.String(length=60), nullable=False),
    sa.Column('config_value', sa.String(length=255), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('collection',
    sa.Column('log_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('npc_id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('reported_slots', sa.Integer(), nullable=True),
    sa.Column('image_url', sa.String(length=255), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('date_updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['npc_id'], ['npc_list.npc_id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['players.player_id'], ),
    sa.PrimaryKeyConstraint('log_id')
    )
    op.create_index(op.f('ix_collection_date_added'), 'collection', ['date_added'], unique=False)
    op.create_index(op.f('ix_collection_item_id'), 'collection', ['item_id'], unique=False)
    op.create_index(op.f('ix_collection_player_id'), 'collection', ['player_id'], unique=False)
    op.create_table('combat_achievement',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.Column('task_name', sa.String(length=255), nullable=False),
    sa.Column('image_url', sa.String(length=255), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['player_id'], ['players.player_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_combat_achievement_date_added'), 'combat_achievement', ['date_added'], unique=False)
    op.create_table('drops',
    sa.Column('drop_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('npc_id', sa.Integer(), nullable=True),
    sa.Column('date_updated', sa.DateTime(), nullable=True),
    sa.Column('value', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('image_url', sa.String(length=150), nullable=True),
    sa.Column('authed', sa.Boolean(), nullable=True),
    sa.Column('partition', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['items.item_id'], ),
    sa.ForeignKeyConstraint(['npc_id'], ['npc_list.npc_id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['players.player_id'], ),
    sa.PrimaryKeyConstraint('drop_id')
    )
    op.create_index(op.f('ix_drops_date_added'), 'drops', ['date_added'], unique=False)
    op.create_index(op.f('ix_drops_item_id'), 'drops', ['item_id'], unique=False)
    op.create_index(op.f('ix_drops_npc_id'), 'drops', ['npc_id'], unique=False)
    op.create_index(op.f('ix_drops_partition'), 'drops', ['partition'], unique=False)
    op.create_index(op.f('ix_drops_player_id'), 'drops', ['player_id'], unique=False)
    op.create_table('group_embed_fields',
    sa.Column('field_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('embed_id', sa.Integer(), nullable=False),
    sa.Column('field_name', sa.String(length=256), nullable=False),
    sa.Column('field_value', sa.String(length=1024), nullable=False),
    sa.Column('inline', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['embed_id'], ['group_embeds.embed_id'], ),
    sa.PrimaryKeyConstraint('field_id')
    )
    op.create_table('personal_best',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.Column('npc_id', sa.Integer(), nullable=True),
    sa.Column('kill_time', sa.Integer(), nullable=False),
    sa.Column('personal_best', sa.Integer(), nullable=False),
    sa.Column('new_pb', sa.Boolean(), nullable=True),
    sa.Column('image_url', sa.String(length=150), nullable=True),
    sa.ForeignKeyConstraint(['npc_id'], ['npc_list.npc_id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['players.player_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_group_association',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.group_id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['players.player_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('player_id', 'user_id', 'group_id', name='uq_user_group_player')
    )
    op.create_table('notified',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('channel_id', sa.String(length=35), nullable=False),
    sa.Column('message_id', sa.String(length=35), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=15), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('date_updated', sa.DateTime(), nullable=True),
    sa.Column('edited_by', sa.Integer(), nullable=True),
    sa.Column('drop_id', sa.Integer(), nullable=True),
    sa.Column('clog_id', sa.Integer(), nullable=True),
    sa.Column('ca_id', sa.Integer(), nullable=True),
    sa.Column('pb_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['ca_id'], ['combat_achievement.id'], ),
    sa.ForeignKeyConstraint(['clog_id'], ['collection.log_id'], ),
    sa.ForeignKeyConstraint(['drop_id'], ['drops.drop_id'], ),
    sa.ForeignKeyConstraint(['edited_by'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['groups.group_id'], ),
    sa.ForeignKeyConstraint(['pb_id'], ['personal_best.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notified_date_added'), 'notified', ['date_added'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_notified_date_added'), table_name='notified')
    op.drop_table('notified')
    op.drop_table('user_group_association')
    op.drop_table('personal_best')
    op.drop_table('group_embed_fields')
    op.drop_index(op.f('ix_drops_player_id'), table_name='drops')
    op.drop_index(op.f('ix_drops_partition'), table_name='drops')
    op.drop_index(op.f('ix_drops_npc_id'), table_name='drops')
    op.drop_index(op.f('ix_drops_item_id'), table_name='drops')
    op.drop_index(op.f('ix_drops_date_added'), table_name='drops')
    op.drop_table('drops')
    op.drop_index(op.f('ix_combat_achievement_date_added'), table_name='combat_achievement')
    op.drop_table('combat_achievement')
    op.drop_index(op.f('ix_collection_player_id'), table_name='collection')
    op.drop_index(op.f('ix_collection_item_id'), table_name='collection')
    op.drop_index(op.f('ix_collection_date_added'), table_name='collection')
    op.drop_table('collection')
    op.drop_table('user_configurations')
    op.drop_index(op.f('ix_players_player_name'), table_name='players')
    op.drop_index(op.f('ix_players_player_id'), table_name='players')
    op.drop_table('players')
    op.drop_table('guilds')
    op.drop_table('group_patreon')
    op.drop_table('group_embeds')
    op.drop_table('group_configurations')
    op.drop_table('webhooks')
    op.drop_table('users')
    op.drop_index(op.f('ix_npc_list_npc_id'), table_name='npc_list')
    op.drop_table('npc_list')
    op.drop_index(op.f('ix_metric_snapshots_timestamp'), table_name='metric_snapshots')
    op.drop_table('metric_snapshots')
    op.drop_index(op.f('ix_items_item_name'), table_name='items')
    op.drop_index(op.f('ix_items_item_id'), table_name='items')
    op.drop_table('items')
    op.drop_index(op.f('ix_groups_group_name'), table_name='groups')
    op.drop_table('groups')
    # ### end Alembic commands ###
