"""
OSM_xml_to_csv.py

Converts an OpenStreetMap XML file into multiple CSV's.
"""

# Imported Libraries
import xml.etree.cElementTree as ET   # XML Processing
import re                             # Regular Expressions
import csv                            # CSV Handler
import codecs                         # File Opener
import street_cleaning as cl


# Set path names
OSM_PATH = "idaho_sw.xml"
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

# Regex
lower_colon = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

"""
Clean and shape node or way XML element to Python dict

element: XML element.
node_attr: Schema of fields for node element.
way_attr_fields: Schema of fields for way element.
problem_chars: A regex for finding problem characters.
returns: A dictionary with formatted data relevant to the element type.
"""
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=problemchars):
    node_attribs = dict()
    way_attribs = dict()
    way_nodes = []

    if element.tag == 'node':
        for field in node_attr_fields:
            node_attribs[field] = element.attrib[field]

        node_id = node_attribs['id']
        tag_iterator = element.iter("tag")
        tags = process_tags(tag_iterator, node_id)
        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        for field in way_attr_fields:
            way_attribs[field] = element.attrib[field]

        way_id = way_attribs['id']
        position = 0
        for node_element in element.iter("nd"):
            node_dict = dict()
            node_dict['id'] = way_id
            node_dict['node_id'] = node_element.attrib['ref']
            node_dict['position'] = position
            position += 1
            way_nodes.append(node_dict)

        tag_iterator = element.iter("tag")
        tags = process_tags(tag_iterator, way_id)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
"""
Yield element if it is the right type of tag.

osm_file: The filename for the XML data.
tags: List of tags.
"""
def get_element(osm_file, tags=('node', 'way', 'relation')):
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


"""
Process tag elements, cleaning and organizing them into a dict.

tag_iterator: An iterator for the tag elements.
default_tag_type: The default value for tags without a declared type.
returns: A dictionary with tag attributes.
"""
def process_tags(tag_iterator, node_id, default_tag_type='regular'):
    tags = []
    for tag_element in tag_iterator:
        if not re.match(problemchars, tag_element.attrib['k']):
            tag_dict = dict()
            tag_dict['id'] = node_id
            if re.match(lower_colon, tag_element.attrib['k']):
                index = tag_element.attrib['k'].find(':')
                tag_dict['key'] = tag_element.attrib['k'][index + 1:]
                tag_dict['type'] = tag_element.attrib['k'][:index]
                if cl.is_street_name(tag_element):
                    tag_dict['value'] = cl.update_street_name(tag_element.attrib['v'])
                elif cl.is_post_code(tag_element):
                    tag_dict['value'] = cl.update_post_code(tag_element.attrib['v'])
                else:
                    tag_dict['value'] = tag_element.attrib['v']
            else:
                tag_dict['key'] = tag_element.attrib['k']
                tag_dict['type'] = default_tag_type
                tag_dict['value'] = tag_element.attrib['v']
            tags.append(tag_dict)
    return tags


# ================================================== #
#               Main Function                        #
# ================================================== #
"""
Iteratively process each XML element and write to csv(s).

file_in: The input filename.
"""
def process_map(file_in):
    with codecs.open(NODES_PATH, 'w') as nodes_file, \
            codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
            codecs.open(WAYS_PATH, 'w') as ways_file, \
            codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
            codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = csv.DictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = csv.DictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = csv.DictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = csv.DictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = csv.DictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == "__main__":
    print('Beginning XML -> CSV Conversion...')
    process_map(OSM_PATH)
    print('Finished!')


