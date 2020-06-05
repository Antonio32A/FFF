from .spreadsheet import Spreadsheet


def setup(fff):
    fff.add_cog(Spreadsheet(fff))
