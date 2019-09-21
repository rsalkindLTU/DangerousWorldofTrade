import sqlite3 as sql
import pickle
import db_connection as dbc
from math import sqrt

test = dbc.DBHandler()

statement = """
SELECT listings.commodity_id, listings.buy_price, listings.sell_price, stations.name
FROM listings
INNER JOIN stations
ON listings.station_id = stations.id
WHERE listings.station_id IN (SELECT id FROM stations WHERE system_id IN (SELECT id FROM systems WHERE DISTANCE(x - ?, y - ?, z - ?) < ?))
"""
def distance(x, y, z):
    return sqrt(x*x + y*y + z*z)
test.connection.create_function("DISTANCE", 3, distance)

ret = test.request(statement, (53.5, -4.625, 67.000, 30))

print(len(ret))
