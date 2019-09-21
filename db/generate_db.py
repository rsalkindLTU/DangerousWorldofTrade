"""
This file contains tools and functionality to create the
database file needed for the E:D trading tool thing. It
relies on only one outside dependency (requests) for fetching
files from URLs. The function gen() begins the entire process.

Dependencies: requests (tested on 2.22.0) [Found in fetch.py]
Author: Rhys Salkind
License: (TODO)

"""
from json import load
from csv import reader
from shutil import rmtree
import os
import re
import pickle
import requests
#import fetch as f
import sqlite3 as sql

db_name = os.path.join('..', 'universe.db')
db_schema_location = 'db_tables.sql'
download_path = os.path.join('.', 'temp')

def download_file(url):
    '''
    Downloads a file into the temp directory. May take a LONG time.
    '''

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

def batch_dl(files):
    # Start by making the directories to hold the files
    # temporarily.
    try:
        os.mkdir(download_path)
    except:
        pass

    dl_url = "https://eddb.io/archive/v6/"
    for name in files:
        download_file(dl_url + name)

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
    with open(os.path.join('temp', filename), 'r') as f:
        header = f.readline()
        del header # We don't need it at all.
        lines = f.readlines()

    systems_schema = load_schema('db_tables.sql')[2].split('\n')
    update_string = "UPDATE systems SET "
    for s in systems_schema[2:-2]:
        string = s.split(' ')
        for elm in string:
            if elm != '':
                string = elm
                break

        update_string += string + '=?,'

    update_string = update_string[:-1] # Drop the last comma
    update_string += " WHERE id=?;"

    # For each of the lines, change None into 0
    iteration = 0
    insert_list = []
    for l in lines:
        temp = reader([l])
        temp = list(temp)

        bin_form = list(convert_to_bin(temp[0]))
        bin_form.append(bin_form.pop(0))
        insert_list.append(bin_form)

        #insert_list.append(convert_to_bin(temp[0]))
        if iteration > len(lines) // 16:
            print(len(insert_list))
            cursor.executemany(update_string, insert_list)
            conn.commit()
            insert_list = []
            iteration = 0
            print('Done!')

        iteration += 1

    cursor.executemany(update_string, insert_list)

def import_from_json(filename, cursor):
    '''
    This function treats just the values for each dictionary
    as the items that need to be inserted.

    INPUTS:
        - filename: filename or path to the file to work on.
        - cursor: a database cursor to execute commands on

    OUTPUT: Nothing returned. Database content is changed.
    '''

    print("Importing from " + filename)
    # Load all the json from the file into memory
    js = load(open(os.path.join('temp', filename), 'r'))
    load_string = "INSERT INTO "
    load_string += filename[:-5] + ' VALUES ('
    load_string += '?,' * len(js[0].values())
    load_string = load_string[:-1] + ');'

    iteration = 0
    to_fill = []
    for item in js:
        temp = convert_to_bin(item.values())
        to_fill.append(temp)
        iteration += 1
        if iteration > 10000:
            cursor.executemany(load_string, to_fill)
            to_fill = []
            iteration = 0

    cursor.executemany(load_string, to_fill)

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

    print("Importing from " + filename)
    # Load the lines from the csv into memory
    with open(os.path.join('temp', filename), 'r') as f:
        headers = f.readline() # Grab the headers and the file content
        lines = f.readlines()

    headers = headers.split(',')
    load_string = "INSERT INTO "
    load_string += filename[:-4] + ' VALUES ('
    load_string += '?,' * len(headers)
    load_string = load_string[:-1] + ');'

    # For each of the lines, change None into 0
    iteration = 0
    insert_list = []
    for l in lines:
        #print(l)
        temp = reader([l])
        temp = list(temp)
        #print(temp[0])
        #input()
        #temp = tuple([x.strip() for x in temp])
        insert_list.append(convert_to_bin(temp[0]))
        if iteration > len(lines) // 16:
            cursor.executemany(load_string, insert_list)
            conn.commit()
            insert_list = []
            iteration = 0

        iteration += 1

    cursor.executemany(load_string, insert_list)

def load_schema(schema_file):
    '''
    This function takes in a filename as a string and
    loads all the database scehmas from the file into
    a list of strings.
    '''
    print(os.path.abspath('.'))
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

    # Fill.
    cursor = conn.cursor()

    tables = load_schema(db_schema_location)

    for table in tables:
        cursor.execute(table)

    # Save and close.
    cursor.close()
    conn.commit()
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

    for f in files:
        if f == "systems_recently.csv": # For this case, we want to alter specific rows.
            update_systems(f, cursor, connection)
        elif re.match(r"\w*.json", f):
            import_from_json(f, cursor)
        elif re.match(r"\w*.csv", f):
            import_from_csv(f, cursor, connection)

        connection.commit()

    cursor.close()
    connection.commit()
    connection.close()

def gen():
    '''
    This function will first check if the database file already exists
    Then, it will check if it needs to download anything as the files are
    updated once a day. Then, it will clean the database, format the 
    incoming data, and place it into the database.

    All formats will come from the db_tables.sql file.

    INPUTS: None
    OUTPUTS: Nothing. Database file is updated or created.
    '''

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
        batch_dl(files[:-1]) # EXCLUDE 'systems.csv' because it's massive.
        populate_db(files[:-1])
    else:
        create_new(db_name)
        batch_dl(files) # We have to include the large file unfortunately.
        populate_db(files)

    # Once everything is done, clean up the temp folder
    clean_up()
    os.chdir(current_path)
