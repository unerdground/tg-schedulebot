# 'mysql-connector' LIBRARY NEEDED TO BE INSTALLED
import mysql.connector


"""SQL Operations"""
class SQLHandler:

    """Initializes new connection to database"""
    def __init__(self):
        self.database = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="schedule"
        )
        self.mycursor = self.database.cursor()

    """Check if database with name 'name' alredy exists"""
    def check_if_exists(self, name):
        self.mycursor.execute("SHOW TABLES LIKE '" + name + "'")
        result = self.mycursor.fetchall()
        if len(result) == 0:
            return 0
        else:
            return 1

    """Returns data from database"""
    def read_from_base(self, name):
        self.mycursor.execute("SELECT * FROM " + name)
        result = self.mycursor.fetchall()
        return result

    """Creates table with predefined columns"""
    def create_table(self, name):
        sql = "CREATE TABLE IF NOT EXISTS " + name + " (name VARCHAR(100), dtstart VARCHAR(5), dtend VARCHAR(5))"
        self.mycursor.execute(sql)

    """Write data 'data' to database 'name'"""
    def write_record(self, name, data):
        sql = "INSERT INTO " + name + " VALUES (%s, %s, %s)"
        self.mycursor.execute(sql, data)

        self.database.commit()
