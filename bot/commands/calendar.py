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
                    day_event_map[day].append(event.name[:15])

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
                            row.append((str(prev_day), 'out'))
                        else:
                            # Days from next month
                            next_day = week[:col_idx].count(0) + sum(1 for d in week[:col_idx] if d != 0) + 1
                            # Count how many next month days already filled in this row
                            next_day = col_idx - week[:col_idx].count(0) + 1
                            row.append((str(next_day), 'out'))
                    else:
                        row.append((str(day), 'in'))
                table_data.append(row)

            # Fill in events into calendar cells
            for row_idx in range(1, len(table_data)):
                for col_idx in range(7):
                    day, inout = table_data[row_idx][col_idx]
                    if inout == 'in' and day in day_event_map:
                        table_data[row_idx][col_idx] = (day + "\n" + "\n".join(day_event_map[day]), 'in')

            # Style calendar using external class
            fig = CalendarStyler().style(table_data, month, year)

            # Save and send image
            temp_path = os.path.join(tempfile.gettempdir(), "calendar.png")
            fig.savefig(temp_path, bbox_inches='tight', transparent=False)
            plt.close(fig)

            await interaction.followup.send(file=discord.File(temp_path))
