from .general import General
from .profile import Profile
from .contest import Contest

def setup(fff):
    fff.add_cog(General(fff))
    fff.add_cog(Profile(fff))
    fff.add_cog(Contest(fff))
