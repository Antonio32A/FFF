from .bot import fff
from .handlers import Handlers

async def setup(fff):
    await fff.add_cog(Util(fff))
