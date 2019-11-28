"""
This file contains tools and functionality to create the
database file needed for the E:D trading tool thing. It
relies on only one outside dependency (requests) for fetching
files from URLs. The function gen() begins the entire process.

External Dependencies: requests (<=2.22.0)
Author: Rhys Salkind
License: (TODO)

"""
from json import load               # For loading json fron a file into a structure
from csv import reader              # To help load csv into a list for processing
from shutil import rmtree           # To remove the temporary directory easily.
from operator import itemgetter     # To work with specific indices of database columns 
import os                           # Mostly for os.path stuff. Also os.remove to remove files.
import re                           # Regex to find markers in the db_tables file
import pickle                       # For storing blob data in the database.
import requests                     # For http requests
import sqlite3 as sql               # For the sqlite3 Database operations!

db_name = os.path.join('..', 'universe.db')
db_schema_location = 'db_tables.sql'
download_path = os.path.join('.', 'temp')

def download_file(url):
    '''
    Downloads a file into the temp directory. This function
    is no longer used for any csv files, as they are quite
    large.
    '''
    try:
        os.mkdir(download_path)
    except:
        pass

    cur_path = os.getcwd()
    os.chdir(download_path)
    local_filename = url.split('/')[-1]
    r = requests.get(url)

    open(local_filename, 'wb').write(r.content)

    os.chdir(cur_path)

def clean_up():
    '''
    Simple function wrapper that deletes the temp directory to save space
    on the user's hard drive.
    '''
    rmtree(download_path)

def convert_to_bin(items):
    '''
    A helper function to extract and convert any non-text, integer,
    or real numbers into a binary format for sqlite
    '''
    # Convert from a tuple to modify it
    items = list(items)
    index = 0

    for i in items:
        if isinstance(i, int):
            pass
        elif isinstance(i, float):
            pass
        elif isinstance(i, bool):
            if i is True:
                items[index] = 1
            elif i is False:
                items[index] = 0
        elif i is None:
            items[index] = ''
        elif isinstance(i, str):
            pass
        else:
            items[index] = pickle.dumps(i)

        index += 1

    return tuple(items)

def update_systems(filename, cursor, conn):
    '''
    This function will read the csv from the systems_recently.csv
    to update the systems table without completly obliterating it
    and attempting to reform it.

    INPUTS: 
        - filename: path or name to file
        - cursor: a database cursor object to execute commands on
    OUTPUTS: nothing.
    '''
    print("[Database Check] Importing from " + filename)
    dl_url = "https://eddb.io/archive/v6/"
    r = requests.get(dl_url + filename, stream=True)

    indicies = [0,1,2,3,4,5,7,19]

    systems_schema = load_schema('db_tables.sql')[2].split('\n')
    #sys_schemas = [s.split('\n') for s in systems_schema]
    #sys_schemas = [s.strip() for s in sys_schemas]
    update_string = "UPDATE systems SET "
    for s in systems_schema[2:-2]:
        string = s.split(' ')
        if string[4].find('--') != -1:
            continue
        for elm in string:
            #print("Elm find(--): {} for {}".format( elm.find('--'), elm))
            if elm != '':
                string = elm
                break

        update_string += string + '=?,'

    update_string = update_string[:-1] # Drop the last comma
    update_string += " WHERE id=?;"

    iteration = 0
    insert_list = []
    cursor.execute("BEGIN TRANSACTION")
    for l in r.iter_lines():
        temp = reader([l.decode('utf-8')])
        temp = list(temp)

        bin_form = list(convert_to_bin(temp[0]))
        bin_form = list(itemgetter(*indicies)(bin_form))
        bin_form.append(bin_form.pop(0))
        insert_list.append(bin_form)

        #if iteration > 31000000 // 16:
            #print(insert_list[:10])
            #cursor.executemany(load_string, insert_list)
            #insert_list = []
            #iteration = 0

        #iteration += 1

    print("[Database Check] Recent systems executing.")
    cursor.executemany(update_string, insert_list)
    cursor.execute("END TRANSACTION")

def import_from_json(filename, cursor):
    '''
    This function treats just the values for each dictionary
    as the items that need to be inserted.

    INPUTS:
        - filename: filename or path to the file to work on.
        - cursor: a database cursor to execute commands on

    OUTPUT: Nothing returned. Database content is changed.
    '''
    # Start by loading in all the indicies for each potential file
    indicies = []
    if filename.find('commodities') != -1:
        indicies = [0, 1, 3, 4] # id, name, avg_price, is_rare
    elif filename.find('stations') != -1:
        indicies = [0, 1, 2, 4] + list(range(13, 21 + 1))
        # id, name, system_id, landing_pad_size, has_*
    #print('Using indicies: {} for filename "{}"'.format(indicies, filename))

    print("[Database Check] Importing from " + filename)
    # Load all the json from the file into memory
    js = load(open(os.path.join('temp', filename), 'r'))
    load_string = "INSERT INTO "
    load_string += filename[:-5] + ' VALUES ('
    load_string += '?,' * len(indicies)
    load_string = load_string[:-1] + ');'
    #print("Load string: '{}'".format(load_string))

    iteration = 0
    to_fill = []
    cursor.execute("BEGIN TRANSACTION")
    for item in js:
        temp = convert_to_bin(item.values())
        temp = itemgetter(*indicies)(temp)
        to_fill.append(temp)
        iteration += 1
        if iteration > 10000:
            for i in to_fill:
                if len(i) > 13:
                    print(i)
            cursor.executemany(load_string, to_fill)
            to_fill = []
            iteration = 0

    cursor.executemany(load_string, to_fill)
    cursor.execute("END TRANSACTION")

def import_from_csv(filename, cursor, conn):
    '''
    This function will take the csv data and put all the data into the requisite
    tables in the database

    INPUTS: 
        - filename: filename or path to a file to import data from.
        - cursor: database cursor to execute commands on
        - conn: database connection to commit changes when working on large datasets.
    OUTPUT: Nothing. Database state is changed.
    '''
    indicies = []
    if filename == 'listings.csv':
        indicies = list(range(9 + 1))
    elif filename == 'systems.csv':
        indicies = list(range(0, 5 + 1)) + [7, 19]

    #print('Using indicies: {} for filename "{}"'.format(indicies, filename))

    print("[Database Check] Importing from " + filename)
    # Open a streaming connection rather than a file connection
    dl_url = "https://eddb.io/archive/v6/"
    r = requests.get(dl_url + filename, stream=True)

    # Load the lines from the csv into memory
    #with open(os.path.join('temp', filename), 'r') as f:
        #headers = f.readline() # Grab the headers and the file content
        #lines = f.readlines()

    headers = False
    load_string = "INSERT INTO "
    load_string += filename[:-4] + ' VALUES ('

    iteration = 0
    insert_list = []
    cursor.execute("BEGIN TRANSACTION")
    for l in r.iter_lines():
        temp = reader([l.decode('utf-8')])
        temp = list(temp)
        temp = itemgetter(*indicies)(temp[0])

        if headers is False:
            load_string += '?,' * len(temp)
            load_string = load_string[:-1] + ');'
            headers = True
            #print(load_string)
            continue

        #print(temp[0])
        #input()
        #temp = tuple([x.strip() for x in temp])
        insert_list.append(convert_to_bin(temp))
        if iteration > 31000000 // 16:
            cursor.executemany(load_string, insert_list)
            conn.commit()
            insert_list = []
            iteration = 0

        iteration += 1

    cursor.executemany(load_string, insert_list)
    cursor.execute("END TRANSACTION")

def load_schema(schema_file):
    '''
    This function takes in a filename as a string and
    loads all the database schemas from the file into
    a list of strings.
    '''
    #print(os.path.abspath('.'))
    with open(os.path.join(os.curdir, schema_file), 'r') as f:
        lines = f.readlines()

    ranges = []
    start = 0
    end = 0
    index = 0
    reg = re.compile(r"--\s\w*\s\w*\s(START|END)")

    # Get all the line ranges for the table schemas
    for l in lines:
        if re.match(reg, l):
            if start == 0:
                start = index
            elif start != 0 and end == 0:
                end = index
                ranges.append(range(start + 1, end))
                start, end = 0, 0

        index += 1

    # Combine each range into one long string
    #print(ranges)
    out = []
    for r in ranges:
        temp = ''
        for x in r:
            temp += lines[x]
        out.append(temp)

    return out

def clean_existing(filename):
    '''
    This function assumes that the file exists, and will only
    do marginal updates. All tables except for the systems table
    are completely dropped and rebuilt.
    '''
    # Start with clearing out the unneeded table information.
    conn = sql.connect(db_name)

    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS listings;")
    cursor.execute("DROP TABLE IF EXISTS stations;")
    cursor.execute("DROP TABLE IF EXISTS commodities;")
    conn.commit()

    # Now, get the schema strings
    next_schema = load_schema(db_schema_location)
    # Exclude the system schema
    tables = next_schema[:2]
    tables.append(next_schema[-1])

    for t in tables:
        cursor.execute(t)

    cursor.close()
    conn.commit()
    conn.close()

def create_new(filename):
    '''
    This function assumes that the database file does not exist
    and WILL NOT CHECK FOR IT. Instead, it creates the file with
    the schema's present.
    '''
    # We do not need to clear out the table, we only need to create
    # it and put the schemas in.

    # Create the table
    conn = sql.connect(db_name)

    # Cursor to fill
    cursor = conn.cursor()

    # Read the script into the cursor
    cursor.executescript(open(db_schema_location, 'r').read())

    # Save and close.
    conn.commit()
    cursor.close()
    conn.close()

def populate_db(files):
    '''
    This function will determine weather to use json
    parsing to populate the database or using csv methods.

    '''

    # Loop through each file, establish a db connection, and determine 
    # the parse type (json vs csv)
    connection = sql.connect(db_name)
    cursor = connection.cursor()
    dl_url = "https://eddb.io/archive/v6/"

    for f in files:
        if f == "systems_recently.csv": # For this case, we want to alter specific rows.
            update_systems(f, cursor, connection)
        elif re.match(r"\w*.json", f):
            download_file(dl_url + f)
            import_from_json(f, cursor)
        elif re.match(r"\w*.csv", f):
            import_from_csv(f, cursor, connection)

        connection.commit()

    # Ensure that the index tables are up and running
    # TODO
    #generate_index_tables(cursor)
    cursor.close()
    connection.commit()
    connection.close()

def post_gen():
    '''
    This function will do any operations on the database itself that need
    to get done after the generation process.
    '''
    print("[Database Check] Running database post-creation process. . .")
    conn = sql.connect(db_name)
    cursor = conn.cursor()

    # Clean the indexes
    cursor.execute("DROP INDEX IF EXISTS idx_system_names;")
    cursor.execute("DROP INDEX IF EXISTS idx_listings_stationids;")
    conn.commit()

    # Generate new indexes.
    cursor.execute("CREATE INDEX idx_system_names ON systems(name);")
    cursor.execute("CREATE INDEX idx_listings_stationids ON listings(station_id);")

    # Generate the distances table

    cursor.close()
    conn.commit()
    conn.close()


def gen(force_new=False):
    '''
    This function will first check if the database file already exists
    Then, it will check if it needs to download anything as the files are
    updated once a day. Then, it will clean the database, format the 
    incoming data, and place it into the database.

    All formats will come from the db_tables.sql file.

    INPUTS: None
    OUTPUTS: Nothing. Database file is updated or created.
    '''
    # If we are forcing a new database, delete the old one.
    if force_new:
        try:
            os.remove('universe.db')
        except FileNotFoundError:
            pass

    # Check for the database file before continuing.
    current_path = os.path.abspath('.')
    os.chdir(os.path.join('.', 'db'))
    files = [
        'stations.json',
        'listings.csv',
        'commodities.json',
        'systems_recently.csv',
        'systems.csv'
        ]
    if os.path.isfile(db_name):
        # If it exists
        clean_existing(db_name)
        populate_db(files[:-1])
        post_gen()
    else:
        create_new(db_name)
        populate_db(files)
        post_gen()

    # Once everything is done, clean up the temp folder
    clean_up()
    os.chdir(current_path)
