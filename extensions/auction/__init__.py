from .auction import Auction


def setup(fff):
    fff.add_cog(Auction(fff))
