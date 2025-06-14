import matplotlib.pyplot as plt
from datetime import datetime
import calendar

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
        out_month_color = '#36393f'  # Slightly greyed out for out-of-month days
        out_month_font_color = '#b9bbbe'  # Lighter grey font

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
            cell.set_linewidth(1)
            cell.set_edgecolor('#23272a')
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
            is_out = is_out_of_month(cell_data)
            cell_text_val = get_cell_text(cell_data)

            # Determine cell color
            if is_out:
                cell.set_facecolor(out_month_color)
                cell.set_text_props(color=out_month_font_color, va='top')
            else:
                base_color = weekend_color if col >= 5 else cell_color
                cell.set_facecolor(base_color)

                # Check for today's date
                if is_current_month and cell_text_val.startswith(str(today.day)):
                    cell.set_facecolor(today_color)

                # Check for events
                if "\n" in cell_text_val:
                    cell.set_facecolor(event_color)

        # Manual text placement for day cells
        fig.canvas.draw()
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                continue

            cell_data = table_data[row][col]
            text_val = get_cell_text(cell_data)
            if not text_val:
                continue

            # Hide original text
            cell.get_text().set_text("")

            # Calculate text position
            bbox = cell.get_window_extent(ax_cal.figure.canvas.get_renderer())
            inv = ax_cal.transData.inverted()
            bbox_data = bbox.transformed(inv)
            x = bbox_data.x0 + 0.06 * (bbox_data.x1 - bbox_data.x0)
            y = bbox_data.y1 - 0.06 * (bbox_data.y1 - bbox_data.y0)

            # Place text
            ax_cal.text(
                x, y, text_val,
                ha='left', va='top',
                fontsize=13,
                color=cell.get_text().get_color(),
                weight=cell.get_text().get_weight(),
                wrap=True
            )

        # Set solid white background
        fig.patch.set_facecolor(background_color)
        fig.patch.set_alpha(0.0)

        return fig
