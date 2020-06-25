from .contest import Contest


def setup(fff):
    fff.add_cog(Contest(fff))
