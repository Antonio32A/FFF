import discord


class Embed(discord.Embed):
    """
    Custom Embed handler which adds Made by github.com/Antonio32A to embed footers
    """
    def __init__(self, **kwargs):
        super(Embed, self).__init__(**kwargs)
        self.set_footer(
            text="Made by github.com/Antonio32A",
            icon_url="https://cdn.discordapp.com/avatars/166630166825664512/1e08078e96777bebe928f66e3491edf5.png"
        )
