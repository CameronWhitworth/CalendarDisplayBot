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

        # Adjusted for a more square and taller look with extra space at the top
        fig, ax = plt.subplots(figsize=(3, 2.4), facecolor=background_color)
        ax.set_facecolor(background_color)
        ax.set_axis_off()

        # Prepare cellText for table (extract text from tuple)
        cell_text = []
        for row in table_data:
            cell_text.append([cell[0] if isinstance(cell, tuple) else cell for cell in row])

        table = ax.table(cellText=cell_text, cellLoc='left', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(13)

        # Adjust cell heights: header row half as tall as others
        for (row, col), cell in table.get_celld().items():
            if row == 0:  # Header row
                cell.set_height(0.5)
                cell.set_width(1.0)
            else:
                cell.set_height(1.0)
                cell.set_width(1.0)
            cell.set_linewidth(0.75)
            cell.set_text_props(va='top', ha='left', wrap=True, color=font_color)

            if row == 0:
                cell.set_facecolor(header_color)
                cell.set_text_props(weight='bold', ha='center', color=font_color)
            else:
                # Determine if this is an out-of-month cell
                cell_data = table_data[row][col]
                is_out = isinstance(cell_data, tuple) and cell_data[1] == 'out'
                if col >= 5:
                    cell.set_facecolor(weekend_color if not is_out else out_month_color)
                else:
                    cell.set_facecolor(cell_color if not is_out else out_month_color)

                if is_out:
                    cell.set_text_props(color=out_month_font_color)
                else:
                    if is_current_month:
                        cell_text = cell_data[0] if isinstance(cell_data, tuple) else cell_data
                        if cell_text.startswith(str(today.day)):
                            cell.set_facecolor(today_color)

                    if "\n" in (cell_data[0] if isinstance(cell_data, tuple) else cell_data):
                        cell.set_facecolor(event_color)

        # Month/year in the large padding area at the top
        plt.figtext(
            0.5, 0.95,  # X (centered), Y (very top)
            f"{calendar.month_name[month]} {year}",
            ha='center', va='top',
            fontsize=24, color=font_color, weight='bold'
        )

        # Set solid white background
        fig.patch.set_facecolor(background_color)
        fig.patch.set_alpha(1.0)

        return fig
