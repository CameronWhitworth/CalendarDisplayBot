import matplotlib.pyplot as plt
from datetime import datetime
import calendar
import textwrap

class CalendarStyler:
    def style(self, table_data, month, year):
        today = datetime.today()
        is_current_month = today.month == month and today.year == year

        # Discord dark theme colors
        background_color = '#FFFFFF'  # Solid white
        header_color = '#2c2f33'
        cell_color = '#23272a'
        weekend_color = '#2e3338'
        today_color = '#7289da'
        event_color = '#99aab5'
        font_color = 'white'
        greyed_color = '#6c6f73'
        dimmed_font_color = '#b0b3b8'

        # Create two axes: one for the title, one for the calendar
        fig = plt.figure(figsize=(20, 15), facecolor=background_color)
        gs = fig.add_gridspec(2, 1, height_ratios=[0.10, 0.82], hspace=0)
        ax_title = fig.add_subplot(gs[0])
        ax_cal = fig.add_subplot(gs[1])
        ax_title.set_facecolor(background_color)
        ax_cal.set_facecolor(background_color)
        ax_title.set_axis_off()
        ax_cal.set_axis_off()

        # Draw the title in the top axes
        ax_title.text(
            0.5, 0.5, f"{calendar.month_name[month]} {year}",
            ha='center', va='center',
            fontsize=28, color=font_color, weight='bold',
            transform=ax_title.transAxes
        )

        # Prepare cellText for table (extract text from tuple)
        cell_text = [[cell[0] if isinstance(cell, tuple) else cell for cell in row] for row in table_data]

        # Draw the table in the lower axes
        table = ax_cal.table(cellText=cell_text, cellLoc='left', loc='center', bbox=[0, 0.05, 1, 0.95])
        table.auto_set_font_size(False)
        table.set_fontsize(13)

        def get_cell_text(cell_data):
            return cell_data[0] if isinstance(cell_data, tuple) else cell_data

        def is_out_of_month(cell_data):
            return isinstance(cell_data, tuple) and cell_data[1] == 'out'

        # Style cells
        for (row, col), cell in table.get_celld().items():
            # Set common properties
            cell.set_linewidth(0.2)
            cell.set_edgecolor('#4f545c')
            cell.set_text_props(va='top', ha='left', wrap=True, color=font_color)
            cell.PAD = 0

            if row == 0:  # Header row
                cell.set_height(0.5)
                cell.set_width(1.0)
                cell.set_facecolor(header_color)
                cell.set_text_props(weight='bold', ha='center', color=font_color)
                continue

            # Regular cell properties
            cell.set_height(1.1)
            cell.set_width(1.0)
            
            cell_data = table_data[row][col]

            # Determine cell color
            base_color = weekend_color if col >= 5 else cell_color
            cell.set_facecolor(base_color)

            # Check for today's date
            if (
                is_current_month
                and isinstance(cell_data, dict)
                and cell_data["inout"] == "in"
                and int(cell_data["day"]) == today.day
            ):
                cell.set_facecolor(today_color)
            # Grey out days before today in the current month
            elif (
                is_current_month
                and isinstance(cell_data, dict)
                and cell_data["inout"] == "in"
                and int(cell_data["day"]) < today.day
            ):
                cell.set_facecolor(greyed_color)
                cell.set_text_props(color=dimmed_font_color)
            # Grey out only previous month out-of-month days
            elif (
                isinstance(cell_data, dict)
                and cell_data["inout"] == "out"
                and row == 1  # first week after header
            ):
                cell.set_facecolor(greyed_color)
                cell.set_text_props(color=dimmed_font_color)

            # Check for events (Highlights dayw with events, disabled for now)
            # if isinstance(cell_data, dict) and cell_data["events"]:
            #     cell.set_facecolor(event_color)

        # Manual text placement for day cells
        fig.canvas.draw()
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                continue

            cell_data = table_data[row][col]
            if not cell_data:
                continue

            # Hide original text
            cell.get_text().set_text("")

            # Calculate text position
            bbox = cell.get_window_extent(ax_cal.figure.canvas.get_renderer())
            inv = ax_cal.transData.inverted()
            bbox_data = bbox.transformed(inv)
            x_center = (bbox_data.x0 + bbox_data.x1) / 2
            y_top = bbox_data.y1 - 0.08 * (bbox_data.y1 - bbox_data.y0)

            # Draw day number at top center
            day_num = cell_data["day"]
            ax_cal.text(
                x_center, y_top, str(day_num),
                ha='center', va='top',
                fontsize=12, weight='bold',
                color=cell.get_text().get_color()
            )

            # Draw events below day number
            line_spacing = 0.13 * (bbox_data.y1 - bbox_data.y0)  # Increased spacing
            y_event = y_top - (line_spacing * 1.1)  # Start a bit lower below the day number
            # Sort events by time (HH:MM)
            sorted_events = sorted(
                cell_data["events"],
                key=lambda e: e[0] if e[0] else "99:99"
            )
            for time, event in sorted_events:
                event_text = f"{time} {event}"
                max_lines = 2
                wrap_width = 25  # Adjust as needed

                wrapped_lines = textwrap.wrap(event_text, width=wrap_width)
                if len(wrapped_lines) > max_lines:
                    # Join all lines after the first into one string, then cut to fit
                    first_line = wrapped_lines[0]
                    # Combine the rest and cut to fit the second line
                    rest = ''.join(wrapped_lines[1:])
                    # Leave space for "..."
                    max_second_line_len = wrap_width - 3
                    second_line = rest[:max_second_line_len] + "..."
                    lines_to_draw = [first_line, second_line]
                else:
                    lines_to_draw = wrapped_lines

                for line in lines_to_draw:
                    ax_cal.text(
                        bbox_data.x0 + 0.06 * (bbox_data.x1 - bbox_data.x0), y_event,
                        line,
                        ha='left', va='top',
                        fontsize=11,
                        color=cell.get_text().get_color()
                    )
                    y_event -= line_spacing

        # Set solid white background
        fig.patch.set_facecolor(background_color)
        fig.patch.set_alpha(0.0)

        return fig
