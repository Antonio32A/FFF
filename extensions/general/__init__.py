from .general import General
from .profile import Profile

def setup(fff):
    fff.add_cog(General(fff))
    fff.add_cog(Profile(fff))
