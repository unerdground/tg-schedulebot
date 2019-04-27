# SCRIPT PARSES DATA FROM .ics FILE
# PARSES DATE, CLASSES NAME, START TIME, END TIME, LOCATION
# PARSED DATA STORED IN DATABASE "schedule" IN TABLES WITH NAMES IN FORMAT "d"+YYYYMMDD

import mysql.connector
import re


# SQL OPERATIONS
class SQLHandler:

	# CONNECTION TO DATABASE
	def __init__(self):
		self.database = mysql.connector.connect(
			host="localhost",
			user="root",
			passwd="root",
			database="schedule"
		)

		self.mycursor = self.database.cursor()

	# CREATE TABLE WITH NAME 'name' AND DEFINED COLUMNS
	def create_table(self, name):
		sql = "CREATE TABLE IF NOT EXISTS " + name + " (name VARCHAR(50), dtstart VARCHAR(2), dtend VARCHAR(2), location VARCHAR(50))"
		self.mycursor.execute(sql, name)

	# WRITE DATA 'data' INTO TABLE 'name'
	def write_record(self, name, data):
		sql = "INSERT INTO " + name + " VALUES (%s, %s, %s, %s)"
		self.mycursor.execute(sql, data)

		self.database.commit()


class Parser:

	# OPEN FILE 'file'
	def __init__(self, file):
		self.file = open(file)
		self.lines = self.file.readlines()

	# CLOSE FILE
	def close_file(self):
		self.file.close()

	# RETURNS EXACT LINE OF FILE
	def read_line(self, line):
		return self.lines[line]

	# SEARCHES IN LINE PREDEFINED REGEX TEMPLATES
	def find_in_line(self, line, search_type):
		if search_type == "date":
			return re.search("20[0-9]{6}", line).group()  # SEARCH DATE IN FORMAT YYYYMMDD
		elif search_type == "dt":
			find = re.search("[0-9]{4}00", line).group()  # SEARCH TIMESTAMP IN FORMAT HHMM00
			return find.replace("0000", "")
		elif search_type == "loc":
			find = re.search(", .*", line).group()  # SEARCH STRING
			return find.replace(", ", "")
		elif search_type == "name":
			find = re.search(":.[^,]*,", line).group()  # SEARCH STRING
			return find.replace(":", "")


def start_parse():

	# SQL AND PARSE OBJECTS
	database = SQLHandler()
	parse = Parser("calendar.ics")

	# STRING WITH FIRST LOCATION
	# AT STRING i+1 STORED DATE AND START TIME
	# AT STRING i+2 STORED END TIME
	# AT STRING i+1 STORED NAME AND LOCATION
	# AT STRING i+6 STORED INFO ABOUT NEXT OBJECT
	i = 6
	while i < len(parse.lines):
		# PARSE DATE AND START TIME
		date = "D" + parse.find_in_line(parse.read_line(i), "date")
		dtstart = parse.find_in_line(parse.read_line(i), "dt")

		# GO TO NEXT LINE
		i += 2
		dtend = parse.find_in_line(parse.read_line(i), "dt")  # PARSE END TIME

		# GO TO NEXT LINE
		i += 1
		loc = parse.find_in_line(parse.read_line(i), "loc")  # PARSE LOCATION
		name = parse.find_in_line(parse.read_line(i), "name")  # PARSE NAME

		#CREATE TABLE FOR DATE 'date'
		database.create_table(date)

		# FILL ARRAY WITH PARSED DATA
		data = (name, dtstart, dtend, loc)

		# WRITE DATA TO DATABASE
		database.write_record(date, data)

		# GO TO NEXT RECORD
		i += 6

	parse.close_file()

start_parse()
