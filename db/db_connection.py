import os
import sqlite3 as sql

class DBHandler:
    '''
    This class wraps the database connection to make opening,
    requests, and clean up easier.
    '''
    def __init__(self):
        self.db_filepath = os.path.join('.', 'universe.db')
        self.connection = sql.connect(self.db_filepath)

    def request(self, string, items=()):
        cursor = self.connection.cursor()

        out = cursor.execute(string, items).fetchall()

        cursor.close()
        self.connection.commit()
        return out

    def close(self):
        self.connection.commit()
        self.connection.close()

