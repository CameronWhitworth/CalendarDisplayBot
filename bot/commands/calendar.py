import discord
from discord import app_commands
import calendar
from datetime import datetime
import os
import tempfile
import matplotlib.pyplot as plt
from .calendar_styler import CalendarStyler  # <-- Import the styling class

class CalendarCommand:
    def __init__(self, client: discord.Client):
        self.client = client

    def register(self, tree: app_commands.CommandTree):
        @tree.command(name="calendar", description="View this month's events in a calendar view")
        @app_commands.describe(
            month="Month (1-12)",
            year="Year (e.g. 2025)"
        )
        async def calendar_view(
            interaction: discord.Interaction,
            month: int = datetime.now().month,
            year: int = datetime.now().year
        ):
            await interaction.response.defer()

            # Fetch guild events
            events = await interaction.guild.fetch_scheduled_events()

            # Organize events by day
            day_event_map = {}
            for event in events:
                if not event.start_time:
                    continue
                date = event.start_time.date()
                if date.month == month and date.year == year:
                    day = str(date.day)
                    if day not in day_event_map:
                        day_event_map[day] = []
                    event_time = event.start_time.strftime('%H:%M') if event.start_time else ""
                    event_title = event.name[:15]
                    day_event_map[day].append((event_time, event_title))

            # Generate calendar with out-of-month days
            cal = calendar.monthcalendar(year, month)
            headers = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            table_data = [headers]

            # Determine previous and next month
            prev_month = month - 1 if month > 1 else 12
            prev_year = year if month > 1 else year - 1
            next_month = month + 1 if month < 12 else 1
            next_year = year if month < 12 else year + 1
            prev_month_days = calendar.monthrange(prev_year, prev_month)[1]

            for week_idx, week in enumerate(cal):
                row = []
                for col_idx, day in enumerate(week):
                    if day == 0:
                        # Fill in previous or next month days
                        if week_idx == 0:
                            # Days from previous month
                            prev_day = prev_month_days - week[:col_idx][::-1].count(0) + col_idx + 1
                            row.append({"day": str(prev_day), "inout": "out", "events": []})
                        else:
                            # Days from next month
                            next_day = col_idx - week[:col_idx].count(0) + 1
                            row.append({"day": str(next_day), "inout": "out", "events": []})
                    else:
                        events = day_event_map.get(str(day), [])
                        row.append({"day": str(day), "inout": "in", "events": events})
                table_data.append(row)

            # Style calendar using external class
            fig = CalendarStyler().style(table_data, month, year)

            # Save and send image
            temp_path = os.path.join(tempfile.gettempdir(), "calendar.png")
            fig.savefig(temp_path, bbox_inches='tight', transparent=False)
            plt.close(fig)

            await interaction.followup.send(file=discord.File(temp_path))
