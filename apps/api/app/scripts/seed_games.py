"""
Seed script to insert historical Bundesliga match results.

Usage:
    uv run python -m app.scripts.seed_games
"""

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select, func

from app.core.database import async_session
from app.models.game import Game

MATCHES = [
    # Matchday 1 — Aug 2025
    ("Bayern Munich", "Werder Bremen", "2025-08-23", 3, 1),
    ("Borussia Dortmund", "RB Leipzig", "2025-08-23", 2, 2),
    ("Bayer Leverkusen", "VfB Stuttgart", "2025-08-24", 4, 0),
    ("Eintracht Frankfurt", "SC Freiburg", "2025-08-24", 2, 1),
    ("Borussia Mönchengladbach", "Union Berlin", "2025-08-24", 1, 0),
    ("VfL Wolfsburg", "Mainz 05", "2025-08-25", 2, 2),
    ("SC Paderborn", "FC Augsburg", "2025-08-25", 1, 1),
    ("TSG Hoffenheim", "1. FC Heidenheim", "2025-08-25", 3, 0),
    # Matchday 2 — Aug/Sep 2025
    ("RB Leipzig", "Bayer Leverkusen", "2025-08-30", 1, 2),
    ("Werder Bremen", "Borussia Dortmund", "2025-08-30", 0, 3),
    ("VfB Stuttgart", "Bayern Munich", "2025-08-31", 1, 3),
    ("Union Berlin", "SC Paderborn", "2025-08-31", 2, 0),
    ("SC Freiburg", "VfL Wolfsburg", "2025-08-31", 3, 2),
    ("Mainz 05", "Borussia Mönchengladbach", "2025-09-01", 1, 1),
    ("FC Augsburg", "Eintracht Frankfurt", "2025-09-01", 0, 2),
    ("1. FC Heidenheim", "TSG Hoffenheim", "2025-09-01", 2, 2),
    # Matchday 3 — Sep 2025
    ("Bayern Munich", "RB Leipzig", "2025-09-13", 4, 1),
    ("Borussia Dortmund", "Union Berlin", "2025-09-13", 4, 0),
    ("Bayer Leverkusen", "TSG Hoffenheim", "2025-09-14", 3, 1),
    ("Eintracht Frankfurt", "VfB Stuttgart", "2025-09-14", 1, 2),
    ("VfL Wolfsburg", "Werder Bremen", "2025-09-14", 1, 1),
    ("Borussia Mönchengladbach", "SC Freiburg", "2025-09-15", 2, 3),
    ("SC Paderborn", "Mainz 05", "2025-09-15", 1, 0),
    ("FC Augsburg", "1. FC Heidenheim", "2025-09-15", 3, 1),
    # Matchday 4 — Sep 2025
    ("RB Leipzig", "Borussia Mönchengladbach", "2025-09-20", 0, 0),
    ("Union Berlin", "Bayer Leverkusen", "2025-09-20", 1, 3),
    ("Werder Bremen", "SC Paderborn", "2025-09-21", 2, 1),
    ("TSG Hoffenheim", "Bayern Munich", "2025-09-21", 0, 4),
    ("VfB Stuttgart", "Borussia Dortmund", "2025-09-21", 1, 2),
    ("SC Freiburg", "FC Augsburg", "2025-09-22", 2, 0),
    ("Mainz 05", "Eintracht Frankfurt", "2025-09-22", 0, 3),
    ("1. FC Heidenheim", "VfL Wolfsburg", "2025-09-22", 1, 1),
    # Matchday 5 — Sep/Oct 2025
    ("Bayern Munich", "Bayer Leverkusen", "2025-09-27", 1, 1),
    ("Borussia Dortmund", "SC Freiburg", "2025-09-27", 3, 1),
    ("Eintracht Frankfurt", "Union Berlin", "2025-09-28", 2, 0),
    ("VfL Wolfsburg", "TSG Hoffenheim", "2025-09-28", 2, 1),
    ("Borussia Mönchengladbach", "Werder Bremen", "2025-09-28", 1, 2),
    ("SC Paderborn", "RB Leipzig", "2025-09-29", 0, 3),
    ("FC Augsburg", "VfB Stuttgart", "2025-09-29", 1, 1),
    ("Mainz 05", "1. FC Heidenheim", "2025-09-29", 2, 0),
    # Matchday 6 — Oct 2025
    ("Bayer Leverkusen", "Borussia Dortmund", "2025-10-04", 2, 2),
    ("RB Leipzig", "FC Augsburg", "2025-10-04", 4, 0),
    ("Union Berlin", "Bayern Munich", "2025-10-05", 0, 2),
    ("Werder Bremen", "Mainz 05", "2025-10-05", 1, 0),
    ("TSG Hoffenheim", "SC Paderborn", "2025-10-05", 3, 1),
    ("SC Freiburg", "VfB Stuttgart", "2025-10-06", 1, 0),
    ("1. FC Heidenheim", "Borussia Mönchengladbach", "2025-10-06", 2, 1),
    ("VfL Wolfsburg", "Eintracht Frankfurt", "2025-10-06", 0, 0),
    # Matchday 7 — Oct 2025
    ("Bayern Munich", "VfL Wolfsburg", "2025-10-18", 3, 0),
    ("Borussia Dortmund", "TSG Hoffenheim", "2025-10-18", 2, 1),
    ("Eintracht Frankfurt", "Bayer Leverkusen", "2025-10-19", 1, 4),
    ("VfB Stuttgart", "Union Berlin", "2025-10-19", 2, 1),
    ("SC Paderborn", "Borussia Mönchengladbach", "2025-10-19", 1, 2),
    ("Mainz 05", "SC Freiburg", "2025-10-20", 3, 1),
    ("FC Augsburg", "Werder Bremen", "2025-10-20", 0, 2),
    ("RB Leipzig", "1. FC Heidenheim", "2025-10-20", 2, 0),
    # Matchday 8 — Oct 2025
    ("Bayer Leverkusen", "SC Paderborn", "2025-10-25", 5, 0),
    ("Union Berlin", "RB Leipzig", "2025-10-25", 1, 1),
    ("Werder Bremen", "Eintracht Frankfurt", "2025-10-26", 1, 3),
    ("TSG Hoffenheim", "Mainz 05", "2025-10-26", 2, 2),
    ("Borussia Mönchengladbach", "Bayern Munich", "2025-10-26", 1, 4),
    ("SC Freiburg", "1. FC Heidenheim", "2025-10-27", 3, 1),
    ("VfL Wolfsburg", "VfB Stuttgart", "2025-10-27", 1, 2),
    ("FC Augsburg", "Borussia Dortmund", "2025-10-27", 1, 3),
    # Matchday 9 — Oct/Nov 2025
    ("Bayern Munich", "SC Freiburg", "2025-11-01", 4, 0),
    ("Borussia Dortmund", "VfL Wolfsburg", "2025-11-01", 3, 0),
    ("Eintracht Frankfurt", "TSG Hoffenheim", "2025-11-02", 3, 1),
    ("VfB Stuttgart", "Borussia Mönchengladbach", "2025-11-02", 3, 2),
    ("SC Paderborn", "Werder Bremen", "2025-11-02", 0, 2),
    ("Mainz 05", "Bayer Leverkusen", "2025-11-03", 0, 2),
    ("1. FC Heidenheim", "Union Berlin", "2025-11-03", 1, 1),
    ("RB Leipzig", "FC Augsburg", "2025-11-03", 3, 0),
    # Matchday 10 — Nov 2025
    ("Bayer Leverkusen", "1. FC Heidenheim", "2025-11-08", 4, 1),
    ("Union Berlin", "Mainz 05", "2025-11-08", 2, 1),
    ("Werder Bremen", "RB Leipzig", "2025-11-09", 0, 1),
    ("TSG Hoffenheim", "VfB Stuttgart", "2025-11-09", 1, 3),
    ("Borussia Mönchengladbach", "Borussia Dortmund", "2025-11-09", 1, 3),
    ("SC Freiburg", "SC Paderborn", "2025-11-10", 4, 0),
    ("VfL Wolfsburg", "FC Augsburg", "2025-11-10", 2, 0),
    ("Eintracht Frankfurt", "Bayern Munich", "2025-11-10", 2, 2),
    # Matchday 11 — Nov 2025
    ("Bayern Munich", "Borussia Mönchengladbach", "2025-11-22", 3, 0),
    ("Borussia Dortmund", "SC Paderborn", "2025-11-22", 5, 1),
    ("VfB Stuttgart", "Werder Bremen", "2025-11-23", 2, 2),
    ("RB Leipzig", "TSG Hoffenheim", "2025-11-23", 3, 1),
    ("Mainz 05", "Bayern Munich", "2025-11-23", 1, 3),
    ("FC Augsburg", "Union Berlin", "2025-11-24", 2, 1),
    ("1. FC Heidenheim", "Eintracht Frankfurt", "2025-11-24", 0, 3),
    ("SC Paderborn", "VfL Wolfsburg", "2025-11-24", 1, 2),
    # Matchday 12 — Nov/Dec 2025
    ("Bayer Leverkusen", "VfL Wolfsburg", "2025-11-29", 3, 0),
    ("Union Berlin", "SC Freiburg", "2025-11-29", 1, 1),
    ("Werder Bremen", "TSG Hoffenheim", "2025-11-30", 2, 1),
    ("Borussia Mönchengladbach", "FC Augsburg", "2025-11-30", 2, 0),
    ("Eintracht Frankfurt", "RB Leipzig", "2025-11-30", 1, 2),
    ("VfB Stuttgart", "1. FC Heidenheim", "2025-12-01", 4, 0),
    ("SC Paderborn", "Bayern Munich", "2025-12-01", 0, 4),
    ("Mainz 05", "Borussia Dortmund", "2025-12-01", 1, 3),
    # Matchday 13 — Dec 2025
    ("Bayern Munich", "Mainz 05", "2025-12-06", 5, 0),
    ("Borussia Dortmund", "Eintracht Frankfurt", "2025-12-06", 2, 1),
    ("RB Leipzig", "VfB Stuttgart", "2025-12-07", 3, 0),
    ("TSG Hoffenheim", "Borussia Mönchengladbach", "2025-12-07", 1, 2),
    ("SC Freiburg", "Werder Bremen", "2025-12-07", 2, 0),
    ("VfL Wolfsburg", "Union Berlin", "2025-12-08", 0, 1),
    ("FC Augsburg", "Bayer Leverkusen", "2025-12-08", 0, 3),
    ("1. FC Heidenheim", "SC Paderborn", "2025-12-08", 2, 1),
    # Matchday 14 — Dec 2025
    ("Bayer Leverkusen", "Borussia Mönchengladbach", "2025-12-13", 4, 0),
    ("Union Berlin", "TSG Hoffenheim", "2025-12-13", 2, 0),
    ("Werder Bremen", "Bayern Munich", "2025-12-14", 0, 4),
    ("Eintracht Frankfurt", "SC Paderborn", "2025-12-14", 4, 0),
    ("VfB Stuttgart", "SC Freiburg", "2025-12-14", 1, 1),
    ("Mainz 05", "RB Leipzig", "2025-12-15", 1, 2),
    ("FC Augsburg", "VfL Wolfsburg", "2025-12-15", 1, 1),
    ("1. FC Heidenheim", "Borussia Dortmund", "2025-12-15", 0, 4),
    # Matchday 15 — Dec 2025
    ("Bayern Munich", "1. FC Heidenheim", "2025-12-20", 4, 0),
    ("Borussia Dortmund", "Bayer Leverkusen", "2025-12-20", 1, 2),
    ("RB Leipzig", "SC Freiburg", "2025-12-21", 2, 1),
    ("TSG Hoffenheim", "Werder Bremen", "2025-12-21", 1, 1),
    ("Borussia Mönchengladbach", "Eintracht Frankfurt", "2025-12-21", 0, 2),
    ("VfL Wolfsburg", "Mainz 05", "2025-12-22", 3, 0),
    ("SC Paderborn", "VfB Stuttgart", "2025-12-22", 0, 3),
    ("Union Berlin", "FC Augsburg", "2025-12-22", 1, 0),
    # Matchday 16 — Jan 2026
    ("Bayer Leverkusen", "Union Berlin", "2026-01-10", 3, 0),
    ("Werder Bremen", "VfL Wolfsburg", "2026-01-10", 0, 2),
    ("VfB Stuttgart", "TSG Hoffenheim", "2026-01-11", 2, 1),
    ("SC Freiburg", "Borussia Dortmund", "2026-01-11", 0, 3),
    ("Eintracht Frankfurt", "Borussia Mönchengladbach", "2026-01-11", 3, 1),
    ("Mainz 05", "FC Augsburg", "2026-01-12", 2, 0),
    ("1. FC Heidenheim", "RB Leipzig", "2026-01-12", 0, 2),
    ("SC Paderborn", "Bayern Munich", "2026-01-12", 0, 3),
    # Matchday 17 — Jan 2026
    ("Bayern Munich", "Eintracht Frankfurt", "2026-01-17", 3, 0),
    ("Borussia Dortmund", "1. FC Heidenheim", "2026-01-17", 4, 0),
    ("RB Leipzig", "Mainz 05", "2026-01-18", 3, 1),
    ("Union Berlin", "Werder Bremen", "2026-01-18", 1, 0),
    ("TSG Hoffenheim", "SC Freiburg", "2026-01-18", 2, 2),
    ("Borussia Mönchengladbach", "VfB Stuttgart", "2026-01-19", 1, 3),
    ("VfL Wolfsburg", "SC Paderborn", "2026-01-19", 4, 0),
    ("FC Augsburg", "Bayer Leverkusen", "2026-01-19", 0, 3),
    # Matchday 18 — Jan 2026
    ("Bayern Munich", "Borussia Dortmund", "2026-01-24", 2, 1),
    ("Bayer Leverkusen", "RB Leipzig", "2026-01-24", 3, 1),
    ("Werder Bremen", "FC Augsburg", "2026-01-25", 2, 0),
    ("VfB Stuttgart", "Eintracht Frankfurt", "2026-01-25", 2, 2),
    ("SC Freiburg", "Union Berlin", "2026-01-25", 1, 0),
    ("Mainz 05", "VfL Wolfsburg", "2026-01-26", 1, 1),
    ("SC Paderborn", "TSG Hoffenheim", "2026-01-26", 2, 3),
    ("1. FC Heidenheim", "Borussia Mönchengladbach", "2026-01-26", 0, 0),
    # Matchday 19 — Jan/Feb 2026
    ("Borussia Dortmund", "Bayern Munich", "2026-01-31", 1, 1),
    ("RB Leipzig", "Werder Bremen", "2026-01-31", 4, 0),
    ("Union Berlin", "VfB Stuttgart", "2026-02-01", 0, 1),
    ("Eintracht Frankfurt", "Mainz 05", "2026-02-01", 3, 0),
    ("Borussia Mönchengladbach", "SC Paderborn", "2026-02-01", 3, 0),
    ("VfL Wolfsburg", "SC Freiburg", "2026-02-02", 2, 1),
    ("FC Augsburg", "TSG Hoffenheim", "2026-02-02", 2, 2),
    ("1. FC Heidenheim", "Bayer Leverkusen", "2026-02-02", 0, 4),
    # Matchday 20 — Feb 2026
    ("Bayern Munich", "VfB Stuttgart", "2026-02-07", 4, 1),
    ("Bayer Leverkusen", "FC Augsburg", "2026-02-07", 3, 0),
    ("Werder Bremen", "Borussia Mönchengladbach", "2026-02-08", 2, 2),
    ("TSG Hoffenheim", "Eintracht Frankfurt", "2026-02-08", 1, 2),
    ("SC Freiburg", "RB Leipzig", "2026-02-08", 1, 3),
    ("Mainz 05", "Union Berlin", "2026-02-09", 2, 0),
    ("SC Paderborn", "1. FC Heidenheim", "2026-02-09", 1, 0),
    ("VfL Wolfsburg", "Borussia Dortmund", "2026-02-09", 0, 2),
    # Matchday 21 — Feb 2026
    ("RB Leipzig", "SC Paderborn", "2026-02-14", 5, 0),
    ("Union Berlin", "VfL Wolfsburg", "2026-02-14", 2, 1),
    ("VfB Stuttgart", "Mainz 05", "2026-02-15", 3, 1),
    ("Eintracht Frankfurt", "Werder Bremen", "2026-02-15", 2, 0),
    ("Borussia Mönchengladbach", "Bayer Leverkusen", "2026-02-15", 1, 3),
    ("FC Augsburg", "Bayern Munich", "2026-02-16", 0, 4),
    ("1. FC Heidenheim", "SC Freiburg", "2026-02-16", 1, 2),
    ("Borussia Dortmund", "TSG Hoffenheim", "2026-02-16", 4, 0),
    # Matchday 22 — Feb 2026
    ("Bayern Munich", "FC Augsburg", "2026-02-21", 5, 0),
    ("Bayer Leverkusen", "Eintracht Frankfurt", "2026-02-21", 2, 1),
    ("Werder Bremen", "VfB Stuttgart", "2026-02-22", 1, 2),
    ("TSG Hoffenheim", "Union Berlin", "2026-02-22", 2, 0),
    ("SC Freiburg", "Borussia Mönchengladbach", "2026-02-22", 2, 1),
    ("Mainz 05", "SC Paderborn", "2026-02-23", 3, 0),
    ("VfL Wolfsburg", "RB Leipzig", "2026-02-23", 1, 3),
    ("1. FC Heidenheim", "Borussia Dortmund", "2026-02-23", 0, 4),
    # Matchday 23 — Feb/Mar 2026
    ("Borussia Dortmund", "Mainz 05", "2026-02-28", 3, 0),
    ("RB Leipzig", "Bayern Munich", "2026-02-28", 2, 2),
    ("Union Berlin", "Borussia Mönchengladbach", "2026-03-01", 1, 1),
    ("VfB Stuttgart", "Bayer Leverkusen", "2026-03-01", 0, 3),
    ("Eintracht Frankfurt", "VfL Wolfsburg", "2026-03-01", 3, 1),
    ("SC Paderborn", "SC Freiburg", "2026-03-02", 0, 2),
    ("FC Augsburg", "1. FC Heidenheim", "2026-03-02", 1, 0),
    ("TSG Hoffenheim", "Werder Bremen", "2026-03-02", 2, 1),
    # Matchday 24 — Mar 2026
    ("Bayern Munich", "SC Paderborn", "2026-03-07", 5, 0),
    ("Bayer Leverkusen", "TSG Hoffenheim", "2026-03-07", 4, 1),
    ("Werder Bremen", "Union Berlin", "2026-03-08", 1, 0),
    ("Borussia Mönchengladbach", "RB Leipzig", "2026-03-08", 0, 2),
    ("SC Freiburg", "Eintracht Frankfurt", "2026-03-08", 1, 2),
    ("Mainz 05", "VfB Stuttgart", "2026-03-09", 2, 1),
    ("VfL Wolfsburg", "1. FC Heidenheim", "2026-03-09", 3, 0),
    ("FC Augsburg", "Borussia Dortmund", "2026-03-09", 0, 4),
    # Matchday 25 — Mar 2026
    ("Borussia Dortmund", "FC Augsburg", "2026-03-14", 4, 0),
    ("RB Leipzig", "Eintracht Frankfurt", "2026-03-14", 2, 1),
    ("Union Berlin", "Bayer Leverkusen", "2026-03-15", 0, 3),
    ("VfB Stuttgart", "SC Paderborn", "2026-03-15", 4, 1),
    ("TSG Hoffenheim", "VfL Wolfsburg", "2026-03-15", 1, 2),
    ("Mainz 05", "Werder Bremen", "2026-03-16", 1, 1),
    ("1. FC Heidenheim", "Bayern Munich", "2026-03-16", 0, 4),
    ("Borussia Mönchengladbach", "SC Freiburg", "2026-03-16", 2, 0),
    # Matchday 26 — Mar 2026
    ("Bayern Munich", "Borussia Mönchengladbach", "2026-03-21", 4, 0),
    ("Bayer Leverkusen", "Mainz 05", "2026-03-21", 3, 0),
    ("Werder Bremen", "SC Freiburg", "2026-03-22", 1, 1),
    ("Eintracht Frankfurt", "Borussia Dortmund", "2026-03-22", 0, 2),
    ("VfL Wolfsburg", "1. FC Heidenheim", "2026-03-22", 4, 0),
    ("SC Paderborn", "Union Berlin", "2026-03-23", 0, 1),
    ("FC Augsburg", "RB Leipzig", "2026-03-23", 1, 4),
    ("TSG Hoffenheim", "VfB Stuttgart", "2026-03-23", 2, 3),
    # Matchday 27 — Mar/Apr 2026
    ("Borussia Dortmund", "VfB Stuttgart", "2026-03-29", 3, 1),
    ("RB Leipzig", "TSG Hoffenheim", "2026-03-29", 4, 0),
    ("Union Berlin", "1. FC Heidenheim", "2026-03-30", 2, 0),
    ("SC Freiburg", "Bayer Leverkusen", "2026-03-30", 1, 3),
    ("Mainz 05", "FC Augsburg", "2026-03-30", 2, 1),
    ("VfL Wolfsburg", "Bayern Munich", "2026-03-31", 1, 3),
    ("Borussia Mönchengladbach", "Eintracht Frankfurt", "2026-03-31", 1, 2),
    ("Werder Bremen", "SC Paderborn", "2026-03-31", 3, 0),
    # Matchday 28 — Apr 2026
    ("Bayern Munich", "Union Berlin", "2026-04-04", 4, 0),
    ("Bayer Leverkusen", "Borussia Dortmund", "2026-04-04", 2, 1),
    ("VfB Stuttgart", "RB Leipzig", "2026-04-05", 2, 3),
    ("Eintracht Frankfurt", "VfL Wolfsburg", "2026-04-05", 3, 0),
    ("SC Paderborn", "Borussia Mönchengladbach", "2026-04-05", 0, 2),
    ("FC Augsburg", "SC Freiburg", "2026-04-06", 1, 2),
    ("1. FC Heidenheim", "Werder Bremen", "2026-04-06", 2, 1),
    ("TSG Hoffenheim", "Mainz 05", "2026-04-06", 1, 1),
    # Matchday 29 — Apr 2026
    ("Borussia Dortmund", "Union Berlin", "2026-04-11", 4, 0),
    ("RB Leipzig", "1. FC Heidenheim", "2026-04-11", 3, 0),
    ("Werder Bremen", "Bayer Leverkusen", "2026-04-12", 0, 4),
    ("SC Freiburg", "Bayern Munich", "2026-04-12", 0, 4),
    ("Borussia Mönchengladbach", "TSG Hoffenheim", "2026-04-12", 2, 2),
    ("Mainz 05", "SC Paderborn", "2026-04-13", 3, 0),
    ("VfL Wolfsburg", "FC Augsburg", "2026-04-13", 2, 0),
    ("Eintracht Frankfurt", "VfB Stuttgart", "2026-04-13", 2, 1),
    # Matchday 30 — Apr 2026
    ("Bayern Munich", "Mainz 05", "2026-04-18", 4, 0),
    ("Bayer Leverkusen", "SC Freiburg", "2026-04-18", 3, 1),
    ("Union Berlin", "Borussia Dortmund", "2026-04-19", 0, 2),
    ("VfB Stuttgart", "VfL Wolfsburg", "2026-04-19", 3, 1),
    ("TSG Hoffenheim", "RB Leipzig", "2026-04-19", 1, 3),
    ("SC Paderborn", "Eintracht Frankfurt", "2026-04-20", 0, 4),
    ("FC Augsburg", "Borussia Mönchengladbach", "2026-04-20", 0, 1),
    ("1. FC Heidenheim", "Werder Bremen", "2026-04-20", 2, 2),
    # Matchday 31 — Apr 2026
    ("Borussia Dortmund", "Borussia Mönchengladbach", "2026-04-25", 5, 1),
    ("RB Leipzig", "Union Berlin", "2026-04-25", 3, 0),
    ("Bayer Leverkusen", "Bayern Munich", "2026-04-26", 0, 2),
    ("Werder Bremen", "TSG Hoffenheim", "2026-04-26", 1, 1),
    ("SC Freiburg", "Mainz 05", "2026-04-26", 2, 1),
    ("VfL Wolfsburg", "SC Paderborn", "2026-04-27", 4, 0),
    ("Eintracht Frankfurt", "FC Augsburg", "2026-04-27", 3, 0),
    ("1. FC Heidenheim", "VfB Stuttgart", "2026-04-27", 1, 3),
    # Matchday 32 — May 2026
    ("Bayern Munich", "RB Leipzig", "2026-05-02", 3, 1),
    ("Union Berlin", "SC Freiburg", "2026-05-02", 1, 2),
    ("VfB Stuttgart", "Borussia Dortmund", "2026-05-03", 1, 3),
    ("TSG Hoffenheim", "Bayer Leverkusen", "2026-05-03", 0, 4),
    ("Borussia Mönchengladbach", "VfL Wolfsburg", "2026-05-03", 2, 1),
    ("Mainz 05", "1. FC Heidenheim", "2026-05-04", 3, 0),
    ("SC Paderborn", "FC Augsburg", "2026-05-04", 1, 2),
    ("Eintracht Frankfurt", "Werder Bremen", "2026-05-04", 4, 0),
    # Matchday 33 — May 2026
    ("Borussia Dortmund", "Werder Bremen", "2026-05-09", 4, 0),
    ("RB Leipzig", "Mainz 05", "2026-05-09", 3, 1),
    ("Bayer Leverkusen", "Borussia Mönchengladbach", "2026-05-10", 4, 0),
    ("Union Berlin", "Eintracht Frankfurt", "2026-05-10", 1, 2),
    ("SC Freiburg", "TSG Hoffenheim", "2026-05-10", 3, 0),
    ("VfL Wolfsburg", "Bayern Munich", "2026-05-11", 0, 4),
    ("FC Augsburg", "VfB Stuttgart", "2026-05-11", 1, 3),
    ("1. FC Heidenheim", "SC Paderborn", "2026-05-11", 2, 0),
    # Matchday 34 — May 2026
    ("Bayern Munich", "1. FC Heidenheim", "2026-05-16", 5, 0),
    ("Werder Bremen", "Bayer Leverkusen", "2026-05-16", 0, 3),
    ("VfB Stuttgart", "SC Freiburg", "2026-05-17", 2, 0),
    ("Eintracht Frankfurt", "SC Paderborn", "2026-05-17", 4, 0),
    ("Borussia Mönchengladbach", "Mainz 05", "2026-05-17", 1, 2),
    ("TSG Hoffenheim", "Borussia Dortmund", "2026-05-18", 0, 4),
    ("VfL Wolfsburg", "Union Berlin", "2026-05-18", 2, 1),
    ("FC Augsburg", "RB Leipzig", "2026-05-18", 0, 3),
]


async def seed() -> int:
    async with async_session() as db:
        result = await db.execute(select(func.count(Game.id)))
        existing = result.scalar() or 0

        if existing > 0:
            print(f"Game table already has {existing} rows. Skipping seed.")
            return existing

        games = [
            Game(
                home_team=home,
                away_team=away,
                date=datetime.fromisoformat(date).replace(tzinfo=timezone.utc),
                goals_home=gh,
                goals_away=ga,
            )
            for home, away, date, gh, ga in MATCHES
        ]

        for g in games:
            db.add(g)

        await db.commit()
        print(f"Inserted {len(games)} historical match results")
        return len(games)


def main():
    count = asyncio.run(seed())
    print(f"Done — {count} games created")


if __name__ == "__main__":
    main()
