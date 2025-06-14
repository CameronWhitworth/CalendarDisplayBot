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

            # Organize events by full date string (YYYY-MM-DD)
            day_event_map = {}
            for event in events:
                if not event.start_time:
                    continue
                date = event.start_time.date()
                date_str = date.strftime('%Y-%m-%d')
                if date_str not in day_event_map:
                    day_event_map[date_str] = []
                event_time = event.start_time.strftime('%H:%M') if event.start_time else ""
                event_title = event.name[:15]
                day_event_map[date_str].append((event_time, event_title))

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
                        if week_idx == 0:
                            # Days from previous month (fill from the end of previous month)
                            first_nonzero_idx = next((i for i, d in enumerate(week) if d != 0), 7)
                            prev_day = prev_month_days - (first_nonzero_idx - col_idx - 1)
                            # Build the correct date for previous month
                            prev_date = datetime(prev_year, prev_month, prev_day).date()
                            prev_date_str = prev_date.strftime('%Y-%m-%d')
                            events = day_event_map.get(prev_date_str, [])
                            row.append({"day": str(prev_day), "inout": "out", "events": events})
                        else:
                            # Days from next month (fill from 1 upwards)
                            first_zero_idx = next((i for i, d in enumerate(week) if d == 0), 7)
                            next_day = col_idx - first_zero_idx + 1
                            # Build the correct date for next month
                            next_date = datetime(next_year, next_month, next_day).date()
                            next_date_str = next_date.strftime('%Y-%m-%d')
                            events = day_event_map.get(next_date_str, [])
                            row.append({"day": str(next_day), "inout": "out", "events": events})
                    else:
                        # In-month day
                        this_date = datetime(year, month, day).date()
                        this_date_str = this_date.strftime('%Y-%m-%d')
                        events = day_event_map.get(this_date_str, [])
                        row.append({"day": str(day), "inout": "in", "events": events})
                table_data.append(row)

            # Style calendar using external class
            fig = CalendarStyler().style(table_data, month, year)

            # Save and send image
            temp_path = os.path.join(tempfile.gettempdir(), "calendar.png")
            fig.savefig(temp_path, bbox_inches='tight', transparent=False)
            plt.close(fig)

            await interaction.followup.send(file=discord.File(temp_path))
