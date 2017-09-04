"""
cleaning.py

A collection of functions and regular expressions useful in cleaning
OpenStreetMap data.
"""

from collections import defaultdict   # Hashmap w/ Default Value
import re                             # Regular Expressions


# Useful Regular Expressions
letter = re.compile(r'[a-z]', re.IGNORECASE)
string = re.compile(r'[^0-9\.\-]')
apo = re.compile(r"'")
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
street_dir_re = re.compile(r'\b[a-z]\b', re.IGNORECASE)
double_space = re.compile(r'  ')

# Street prefix and suffix mappings
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court",
            "Place", "Square", "Lane", "Road", "Trail",
            "Parkway", "Commons"]

suffix_mapping = {"St": "Street",
                    "St.": "Street",
                    "Rd": "Road",
                    "Rd.": "Road",
                    "RD": "Road",
                    "Ave": "Avenue",
                    "Ave.": "Avenue",
                    "Blvd": "Boulevard",
                    "Blvd.": "Boulevard",
                    "Ln": "Lane",
                    "Ln.": "Lane",
                    "Dr": "Drive",
                  }

prefix_mapping = {"N.": "North",
                    "N": "North",
                    "S.": "South",
                    "S": "South",
                    "W.": "West",
                    "W": "West",
                    "E.": "East",
                    "E": "East",
                  }


"""
Determines if a provided node contains street name data.

elem: An ET node.
returns: Boolean.
"""
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

"""
Determines if a provided node contains postal code data.

elem: An ET node.
returns: Boolean.
"""
def is_post_code(elem):
    return ("post" in elem.attrib['k'])

"""
Scans the OpenStreetMap file for all recorded street suffixes.

street_list: A list of street names.
returns: A defaultdict containing all street suffixes as keys
and instances of streets using those suffixes as values.
"""
def audit_streets(street_list):
    street_types = defaultdict(set)
    for item in street_list:
        m = street_type_re.search(item)
        if m:
            street_type = m.group()
            street_types[street_type].add(item)
    return street_types


"""
Returns a cleaned version of the input street name.

name: A string representing a street name.
returns: String.
"""
def update_street_name(name):
    fix = name.split()
    first = True
    for word in fix:
        if first and 'Mc' not in word and 'ID' not in word:
            name = name.replace(word, word.capitalize())
            word = word.capitalize()
            first = False
        if word in suffix_mapping.keys():
            name = name.replace(word, suffix_mapping[word])
        elif word in prefix_mapping.keys() and len(word) <= 2:
            name = name.replace(word, prefix_mapping[word])
    name = name.replace('.', '')
    return name

"""
Returns a cleaned version of the input postal code.

name: A string representing a street name.
returns: String.
"""
def update_post_code(code):
    code = re.sub(letter, '', code)
    code = re.sub(problemchars, ' ', code)
    code = re.sub(double_space, '', code)
    code = code.strip()
    fix = code.split('-')
    return fix[0]

"""
Tests the effectiveness of update_street_name by printing changes.

street_types: A dictionary of street names by prefix.
"""
def test_clean(street_types):
    for st_type, ways in street_types.items():
        for name in ways:
            better_name = update_street_name(name)
            if better_name != name:
                print(name + ' -> ' + better_name)

"""
Tests the effectiveness of update_post_name by printing changes.

post_codes: A dictionary of postal codes.
"""
def test_post_clean(post_codes):
    clean = defaultdict(set)
    for code, count in post_codes.items():
        better_code = update_post_code(code)
        if better_code != code:
            print(code + ' -> ' + better_code)