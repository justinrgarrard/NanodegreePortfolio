"""
OSM_csv_to_sql.py

Converts the CSV files created by OSM_xml_to_csv.py into a sql database.
"""

import sqlite3
import psycopg2
import csv
import re
# import config

OSM_PATH = "idaho_sw.xml"
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

letter = re.compile(r'[a-z]', re.IGNORECASE)
string = re.compile(r'[^0-9\.\-]')
apo = re.compile(r"'")
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
problemchars_x = re.compile(r'[=\+/&<>;\'"\?%#$@\,\.\t\r\n]') # Excludes spaces
double_space = re.compile(r'  ')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_dir_re = re.compile(r'\b[a-z]\b', re.IGNORECASE)

# SQL Table Creation Commands
nodes_cmd = """
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT
);
"""

nodes_tags_cmd = """
CREATE TABLE nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
);
"""

ways_cmd = """
CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT
);
"""

ways_tags_cmd = """
CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
);
"""

ways_nodes_cmd = """
CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);
"""


def establish_connection(db_name="osm_idaho.db"):
    # SQLite Implemenation
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    return con, cur


def initialize_tables(cur):
    # Drop any pre-existing tables
    cur.execute("DROP TABLE IF EXISTS Nodes")
    cur.execute("DROP TABLE IF EXISTS Nodes_Tags")
    cur.execute("DROP TABLE IF EXISTS Ways")
    cur.execute("DROP TABLE IF EXISTS Ways_Tags")
    cur.execute("DROP TABLE IF EXISTS Ways_Nodes")

    # Add fresh tables
    cur.execute(nodes_cmd)
    cur.execute(nodes_tags_cmd)
    cur.execute(ways_cmd)
    cur.execute(ways_tags_cmd)
    cur.execute(ways_nodes_cmd)


def fill_table(source, table_name, cur):
    first = True
    col_id = ''
    err = []
    for row in source:
        if first:
            # Record header
            first = False
            col_id = '(' + ','.join(row) + ')'
            print(col_id)
        else:
            # Handle text elements
            for i in range(0, len(row)):
                row[i] = re.sub(problemchars_x, '', row[i])
                row[i] = re.sub(double_space, ' ', row[i])
                if re.search(string, row[i]):
                    row[i] = "'" + row[i] + "'"
            # Insert element into table
            cmd = "INSERT INTO " + table_name + col_id + " VALUES(" + ','.join(row) + ");"
            try:
                cur.execute(cmd)
            except:
                err.append(cmd)


if __name__ == "__main__":
    print('Beginning CSV -> SQL Conversion...')

    cur, conn = establish_connection()
    with open(NODES_PATH, 'r') as nodes_file, \
            open(NODE_TAGS_PATH, 'r') as node_tags_file, \
            open(WAYS_PATH, 'r') as ways_file, \
            open(WAY_TAGS_PATH, 'r') as way_tags_file, \
            open(WAY_NODES_PATH, 'r') as way_nodes_file:
        node_f = csv.reader(nodes_file)
        node_tags_f = csv.reader(node_tags_file)
        ways_f = csv.reader(ways_file)
        way_tag_f = csv.reader(way_tags_file)
        way_nodes_f = csv.reader(way_nodes_file)

        fill_table(node_f, "Nodes", cur)
        fill_table(node_tags_f, "Nodes_Tags", cur)
        fill_table(ways_f, "Ways", cur)
        fill_table(way_tag_f, "Ways_Tags", cur)
        fill_table(way_nodes_f, "Ways_Nodes", cur)

    print('Finished!')
