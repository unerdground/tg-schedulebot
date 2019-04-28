"""This script parses data from .ics file and stores it in database
in tables with names 'dYYYYMMDD'
Data stored in format 'name, start time, end time'"""

# 'ics' LIBRARY NEEDED TO BE INSTALLED
from ics import Calendar
import SQLHandler


"""Parses data from .ics file"""
class Parser:

    """Constructor opens file with name 'filename'"""
    def __init__(self, filename):
        with open(filename, encoding='utf-8') as file:
            self.calendar = Calendar(file).events

    """Returns date of event in format 'dYYYYMMDD' as required to database"""
    def get_date(self, index):
        date = self.calendar[index].begin.datetime.strftime("%Y%m%d")
        return "d" + date

    """Returns tuple of data for database"""
    def get_data(self, index):
        dtstart = self.calendar[index].begin.datetime.strftime("%H:%M")
        dtend = self.calendar[index].end.datetime.strftime("%H:%M")
        name = self.calendar[index].name
        res = (name, dtstart, dtend)
        return res


"""Main function, handles parsing"""
def start_parse():
    parse = Parser("calendar.ics")
    database = SQLHandler.SQLHandler()

    for index in range(len(parse.calendar) - 1):
        database.create_table(parse.get_date(index))
        database.write_record(parse.get_date(index), parse.get_data(index))


start_parse()
