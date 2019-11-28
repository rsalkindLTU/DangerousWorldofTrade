'''
This file serves database calculation requests.
It does this by wrapping the DB individual threads
that will each return eventually.
'''
import db
from db import DBHandler
from math import sqrt
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
pool = ThreadPoolExecutor(10)

class DBRequester():
    def __init__(self, statement, params=None):
        self.statement = statement
        self.params = params

    def setup(self):
        self.db_conn = db.DBHandler()
        self.add_function(self.distance, 3, 'DISTANCE')

    def execute(self):
        self.setup()
        if self.params is None:
            return self.db_conn.request(self.statement, ())
        else:
            return self.db_conn.request(self.statement, self.params)

    def add_function(self, function, len_params, db_internal_name):
        self.db_conn.connection.create_function(db_internal_name, len_params, function)

    def distance(self, x, y, z):
        ''' Simple distance calculation '''
        return sqrt(x*x + y*y + z*z)

    statement = '''
    SELECT listings.commodity_id, listings.buy_price, listings.sell_price, stations.name, system.name
    FROM listings
    INNER JOIN stations
    ON listings.station_id = stations.id
    WHERE listings.station_id IN (SELECT id FROM stations WHERE system_id IN (SELECT id FROM systems WHERE DISTANCE(x - ?, y - ?, z - ?) < ?))
    '''

def grab_station_listings(ids):
    '''
    Given a list of station ids, grab all the commodity prices and ids
    '''
    out = []
    db_conn = DBHandler()
    for i in ids:
        out.append((i, db_conn.request("SELECT commodity_id, buy_price, sell_price FROM listings WHERE station_id = ? AND buy_price != 0 AND sell_price != 0", i)))

    return out

def determine_buy_order(pricing_list, current_station_listings, cargo_size, price_limit):
    '''
    Takes in a list of potential prices and ids. Determines what gets bought,
    how much gets bought, and where it gets bought.
    '''
    current_selection = (0, 0, 0, 0) # In the format (station_id, commodity_id, #toBuy, GPM)

    # First, build up a comparison table for profit calculations
    local_station_prices = {}
    for item in current_station_listings[0][1]:
        # Insert form = (commodity_id, (buy, sell))
        local_station_prices[item[0]] = item[1]

    for item in pricing_list:
        curr_id = item[0]
        listings = item[1]
        #curr_id, listings = item
        max_profit = (0, 0, 0) # (GPR, commodity_id, station_id)

        for l in listings:
            # Each l is in the shape (commodity_id, buy_price, sell_price)
            # We have to determine what the best profit is

            # The try/except here is to catch items that our current station is not selling.
            try:
                buy_here_cost = cargo_size * local_station_prices[l[0]]
            except KeyError:
                continue

            sell_price = cargo_size * l[2]
            if sell_price == 0:
                continue

            if buy_here_cost > price_limit:
                # We can't use this, so continue
                continue

            gross_profit_margin = (sell_price - buy_here_cost) / sell_price

            # If the calculated GPD is good, assign it to the max profit.
            if gross_profit_margin > max_profit[0]:
                max_profit = (gross_profit_margin, l[0], curr_id)

        # Once we are done looping, we can check if our max_profit is better than our current selction
        # current_selection: (station_id, commodity_id, #toBuy, GPM)
        if max_profit[0] > current_selection[3]:
            current_selection = (curr_id, max_profit[1], cargo_size, max_profit[0])

    # Now we have a selection, do the db reqeusts to get:
    # (system name, station name, commodity name, count)

    db_conn = DBHandler()
    station_name_id = db_conn.request("SELECT name, system_id FROM stations WHERE id = ?", current_selection[0])[0]
    station_name = station_name_id[0]
    system_name = db_conn.request("SELECT name FROM systems WHERE id = ?", (station_name_id[1], ))[0][0]
    commodity_name = db_conn.request("SELECT name FROM commodities WHERE id = ?", (current_selection[1],))[0][0]

    return (system_name, station_name, commodity_name, cargo_size)



def planets_in_range(ship_range, current_location, cargo_size, station_name, spend_limit):
    '''
    This function takes in what range the ship has and where 
    the ship is located. It will return any star systems in
    range. Maybe more?
    '''
    # Start by getting the stations in range
    station_ids_in_range = """SELECT id FROM stations WHERE system_id IN (SELECT id FROM distances WHERE distance < ? AND distance != 0)"""
    stat_req = DBRequester(station_ids_in_range, params=(ship_range,))
    stat_fut = pool.submit(stat_req.execute)

    # Now for each station ID, grab some info from the listings
    next_stat_listings_fut = pool.submit(grab_station_listings, stat_fut.result())

    # Grab the current stations listings
    current_station_id = DBHandler().request("SELECT id FROM stations WHERE name = ?", (station_name,))
    current_station_listings = grab_station_listings(current_station_id)

    # Now, we need to determine which listing and station is the final answer
    return determine_buy_order(next_stat_listings_fut.result(), current_station_listings, cargo_size, spend_limit)

    '''
    params = [current_location[0], current_location[1], current_location[2], ship_range]
    res = DBRequester(statement, params=params)
    return res.execute()
    '''

def build_distances(current_location):
    # Start by removing the previous distances table
    conn = db.DBHandler()
    conn.request("DROP TABLE IF EXISTS distances")
    conn.request("CREATE TABLE distances (id integer PRIMARY KEY, distance real)")

    param = [current_location[0], current_location[1], current_location[2]]
    req = DBRequester(
        """INSERT INTO distances (id, distance) SELECT id, DISTANCE(x - ?, y - ?, z - ?) FROM systems""", 
        params=current_location
    )

    req.execute()


    # Populate the table based on the current location.
    #conn.request("""INSERT INTO distances (id, distance)
    #SELECT id, DISTANCE(x - ?, y - ?, z - ?) FROM systems""", current_location)
