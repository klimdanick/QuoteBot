import io
import svgwrite
from cairosvg import svg2png
import discord


class StatView(discord.ui.View):
    def __init__(self, quotebook):
        super().__init__(timeout=180)
        self.quotebook = quotebook
        buttons = [
            ("all", discord.ButtonStyle.primary),
            ("leaderboard", discord.ButtonStyle.secondary),
            ("authors", discord.ButtonStyle.secondary),
        ]
        
        for label, style in buttons:
            self.add_item(discord.ui.Button(label=label, style=style, custom_id=label))

    async def process_button_press(
        self, interaction: discord.Interaction
    ):
        if not interaction.data:
            return
        id = interaction.data.get('custom_id')
        response = self.quotebook.get_stats(id)
        if "files" in response:
            for file in response["files"]:
                await interaction.followup.send(file=file)
            return
        await interaction.followup.send(**response)

    async def interaction_check(self, interaction: discord.Interaction):
        if not isinstance(interaction, discord.Interaction):
            return False
        await interaction.response.defer()
        await self.process_button_press(interaction)
        


def dictToTable(leaderboard, column_names, include_index=True, discord_file=True):
    def add_line(dwg, start, end):
        dwg.add(dwg.line(start, end, stroke=svgwrite.rgb(255, 255, 255, "%")))

    def add_text(dwg, text, insert):
        dwg.add(
            dwg.text(
                text,
                insert=insert,
                style="font-family:sans",
                fill="white",
                text_anchor="middle",
                alignment_baseline="middle",
            )
        )

    num_columns = len(column_names)
    svg_width = 300
    margin = 5
    cell_width = (svg_width - 2 * margin) / num_columns
    cell_height = 30

    svg_height = (
        len(leaderboard) + 1
    ) * cell_height + margin * 2  # Plus one for the header row
    dwg = svgwrite.Drawing(filename="table.png", size=(svg_width, svg_height))

    # Draw border lines
    add_line(dwg, (margin, margin), (svg_width - margin, margin))
    add_line(
        dwg, (margin, svg_height - margin), (svg_width - margin, svg_height - margin)
    )
    add_line(dwg, (margin, margin), (margin, svg_height - margin))
    add_line(
        dwg, (svg_width - margin, margin), (svg_width - margin, svg_height - margin)
    )

    # Add column names as header row
    for i, column_name in enumerate(column_names):
        add_text(
            dwg,
            column_name,
            ((i + 0.5) * cell_width + margin, cell_height / 2 + margin),
        )

    for i, row in enumerate(leaderboard.items(), start=1):
        y = margin + i * cell_height

        # Horizontal lines
        add_line(dwg, (margin, y), (svg_width - margin, y))

        if include_index:
            add_text(dwg, str(i), (margin + 0.5 * cell_width, y + cell_height / 2))

        for j, value in enumerate(row, start=(1 if include_index else 0)):
            x = (j + 0.5) * cell_width + margin
            add_text(dwg, str(value), (x, y + cell_height / 2))

    buffer = io.BytesIO()

    svg2png(bytestring=dwg.tostring(), write_to=buffer)
    buffer.seek(0)

    return discord.File(fp=buffer, filename=dwg.filename) if discord_file else buffer
