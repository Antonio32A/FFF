from .tasks import Tasks


def setup(fff):
    fff.add_cog(Tasks(fff))
