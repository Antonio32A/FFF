import asyncpg


def format_member_data_to_sql(member: dict):
    """
    This formats and removes all the Nones and sets them to their types
    :param (dict) member: The member dict
    :returns (dict) member: The same member dict but with the data changed
    """
    if member['skill_level_xp'] is None:
        member['skill_level_xp'] = {
            "experience_skill_combat": -1,
            "experience_skill_mining": -1,
            "experience_skill_alchemy": -1,
            "experience_skill_farming": -1,
            "experience_skill_enchanting": -1,
            "experience_skill_fishing": -1,
            "experience_skill_foraging": -1,
            "experience_skill_taming": -1
        }

    if member['skill_average'] is None:
        member['skill_average'] = -1.0
    if member['slayer_xp'] is None:
        member['slayer_xp'] = -1
    if member['discord_connection'] is None:
        member['discord_connection'] = ""
    if member['paid_to'] is None:
        member['paid_to'] = ""
    if member['cute_name'] is None:
        member['cute_name'] = ""
    return member


def format_member_data_to_json(member: list):
    """
        This formats and removes all the -1 and "" and sets them to None
        :param (list) member: The member list, fetched from SQL
        :returns (dict) member: The same member dict but with the data changed
        """
    member = list(member)
    try:
        i = 0
        _ = member[18]
        # since we are formatting 2 different lists,
    except IndexError:
        i = 1

    skill_level_xp = {
        "experience_skill_combat": member[10-i],
        "experience_skill_mining": member[11-i],
        "experience_skill_alchemy": member[12-i],
        "experience_skill_farming": member[13-i],
        "experience_skill_enchanting": member[14-i],
        "experience_skill_fishing": member[15-i],
        "experience_skill_foraging": member[16-i],
        "experience_skill_taming": member[17-i]
    }
    if skill_level_xp["experience_skill_combat"] == -1:
        skill_level_xp = None

    counter = 0
    for _data in member:
        if _data == -1 or _data == "":
            member[counter] = None
        counter += 1

    new_member = {
        "uuid": member[1-i],
        "username": member[2-i],
        "discord_connection": member[3-i],
        "rank": member[4-i],
        "paid": member[5-i],
        "paid_to": member[6-i],
        "skill_average": member[7-i],
        "skill_level_xp": skill_level_xp,
        "slayer_xp": member[8-i],
        "passes_reqs": member[9-i],
        "cute_name": member[18-i]
    }

    try:
        _ = member[18]
        new_member["timestamp"] = member[0]
    except IndexError:
        pass
    return new_member


class Database:
    """
    PostgreSQL database utils
    """

    def __init__(self, credentials):
        self.credentials = credentials

    async def connect(self):
        """
        Connects to the database
        :returns (asyncpg.pool.Pool) pool: The database pool
        """
        return await asyncpg.create_pool(**self.credentials)

    @staticmethod
    async def set_guild_data(db: asyncpg.connection.Connection, data: dict):
        """
        Sets the database guild_data values and automatically converts a dict to SQL
        :param (asyncpg.connection.Connection) db: The database connection
        :param (dict) data: The guild_data
        """
        await db.execute("DELETE FROM guild_data")  # clear whole table
        for uuid in data.keys():
            member = data[uuid]
            member = format_member_data_to_sql(member)

            await db.execute(
                f"""
                INSERT INTO guild_data (
                    uuid, username, discord_connection, rank, paid, paid_to, skill_average, slayer_xp, passes_reqs, 
                    experience_skill_combat, experience_skill_mining, experience_skill_alchemy, 
                    experience_skill_farming, experience_skill_enchanting, experience_skill_fishing,
                    experience_skill_foraging, experience_skill_taming, cute_name
                )
                VALUES (
                    '{uuid}', '{member['username']}', '{member['discord_connection']}',
                    '{member['rank']}', {member['paid']}, '{member['paid_to']}', {member['skill_average']},
                    {member['slayer_xp']}, {member['passes_reqs']}, 
                    {member['skill_level_xp']['experience_skill_combat']},
                    {member['skill_level_xp']['experience_skill_mining']},
                    {member['skill_level_xp']['experience_skill_alchemy']},
                    {member['skill_level_xp']['experience_skill_farming']},
                    {member['skill_level_xp']['experience_skill_enchanting']},
                    {member['skill_level_xp']['experience_skill_fishing']}, 
                    {member['skill_level_xp']['experience_skill_foraging']},
                    {member['skill_level_xp']['experience_skill_taming']},
                    '{member['cute_name']}'
                )
                """
            )

    @staticmethod
    async def get_guild_data(db: asyncpg.connection.Connection):
        """
        Gets the guild_data as a dict
        :param (asyncpg.connection.Connection) db: The database connection
        :returns (dict) guild_data: The guild data dict
        """
        sql_data = await db.fetch("SELECT * FROM guild_data")
        data = {}
        for member in sql_data:
            member = list(member)
            member = format_member_data_to_json(member)
            data[member['uuid']] = member

        return data

    @staticmethod
    async def set_guild_data_history(db: asyncpg.connection.Connection, data: dict):
        """
        Sets the database guild_data_history values and automatically converts a dict to SQL
        :param (asyncpg.connection.Connection) db: The database connection
        :param (dict) data: The guild data history dict
        """
        await db.execute("DELETE FROM guild_data_history")  # clear whole table
        for timestamp, history_data in data.items():
            for uuid, member in history_data.items():
                member = format_member_data_to_sql(member)

                await db.execute(
                    f"""
                    INSERT INTO guild_data_history (
                        timestamp,
                        uuid, username, discord_connection, rank, paid, paid_to, skill_average, slayer_xp, passes_reqs, 
                        experience_skill_combat, experience_skill_mining, experience_skill_alchemy, 
                        experience_skill_farming, experience_skill_enchanting, experience_skill_fishing,
                        experience_skill_foraging, experience_skill_taming, cute_name
                    )
                    VALUES (
                        {member['timestamp']},
                        '{uuid}', '{member['username']}', '{member['discord_connection']}',
                        '{member['rank']}', {member['paid']}, '{member['paid_to']}', {member['skill_average']},
                        {member['slayer_xp']}, {member['passes_reqs']}, 
                        {member['skill_level_xp']['experience_skill_combat']},
                        {member['skill_level_xp']['experience_skill_mining']},
                        {member['skill_level_xp']['experience_skill_alchemy']},
                        {member['skill_level_xp']['experience_skill_farming']},
                        {member['skill_level_xp']['experience_skill_enchanting']},
                        {member['skill_level_xp']['experience_skill_fishing']}, 
                        {member['skill_level_xp']['experience_skill_foraging']},
                        {member['skill_level_xp']['experience_skill_taming']},
                        '{member['cute_name']}'
                    )
                    """
                )

    @staticmethod
    async def get_guild_data_history(db: asyncpg.connection.Connection):
        """
        Gets the guild_data_history as a dict
        :param (asyncpg.connection.Connection) db: The database connection
        :returns (list) guild_data_history: The guild_data_history list
        """
        members = {}
        data = await db.fetch("SELECT * FROM guild_data_history")

        for member in data:
            member = format_member_data_to_json(member)
            try:
                members[member['timestamp']][member['uuid']] = member
            except KeyError:
                members[member['timestamp']] = {member['uuid']: member}

        return members
