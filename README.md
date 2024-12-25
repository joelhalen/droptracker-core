
# DropTracker.io

The DropTracker is an all-in-one solution for tracking Old School RuneScape drops, achievements, and personal best(s), for players and groups alike.

This repository hosts the core of the project--the Discord bot itself alongside all of the necessary logic in order for it to operate.

## Navigating the Codebase

The project is organized into several directories:

- `cache/`: Contains the logic for redis caching to reduce database load and for tracking metrics.
- `assets/`: Project assets (images, fonts, etc.)
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

- [x] Re-integrate lootboard generation with group-specific and time-based partitioning.
> Allows for lootboards from *previous months* to be generated as well.
- [ ] Create commands to interact with the bot and create/configure groups.
- [ ] Implement a leaderboard system based on boss personal bests.
- [ ] Implement a system for sending notifications based on submissions that exceed group thresholds.
- [ ] Stress-test the system to determine an estimated amount of memory and CPU usage under maximum load (we have 12GB maximum on our machine).
- [ ] Further refine the logging and management system for debugging and inspection purposes.

