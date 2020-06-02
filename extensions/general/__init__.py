from .profile import Profile
from .test import Test
# from .contest import Contest


def setup(fff):
    fff.add_cog(Profile(fff))
    fff.add_cog(Test(fff))
    # fff.add_cog(Contest(fff))
