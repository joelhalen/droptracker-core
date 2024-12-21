
# DropTracker.io

The DropTracker is an all-in-one solution for tracking Old School RuneScape drops, achievements, and personal best(s), for players and groups alike.

This repository hosts the core of the project--the Discord bot itself alongside all of the necessary logic in order for it to operate.

## Navigating the Codebase

The project is organized into several directories:

- `api/`: Contains the Discord bot and all of the logic for it to operate.
- `cache/`: Contains the logic for caching data in order to reduce database load and tracking metrics.
- `cogs/`: Contains the logic for the Discord bot's commands and events.
- `models/`: Contains the logic for the database models.
- `utils/`: Contains the logic for the project's utilities.
- `events.py`: Contains the logic for the Discord bot's events.
- `main.py`: Entry point for the app.
- `models/__init__.py`: Entry point for database models.
- `models/base.py`: Base class for all database models/session.
- `utils/message_builder.py`: Utility class for building messages.
- `utils/num.py`: Utility class for number formatting.

## Current list of to-dos:

- [ ] Finalize methods of tracking loot accurately and efficiently with `cache/player_stats.py`.
- [ ] Implement proper leaderboards for personal bests at various bosses.
- [ ] Create command-based configuration structure for groups to set their servers up.

