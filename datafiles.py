#!/usr/bin/env python
# coding: utf-8

import overpy
import xml.etree.cElementTree as ET


def download_xml_data(min_lat=37.3729, min_lon=-77.5999, max_lat=37.7039, max_lon=-77.2689):
    """
    Queries the OpenStreetMap database using the Overpass API, 
    saves the results to a file (data.osm) in XML format, and 
    returns the saved file name.
    
    Parameters:
        min_lat : minimum latitude (float)
        min_lon : minimum longitude (float)
        max_lat : maximum latitude (float)
        max_lon : maximum longitude (float)
    
    The default parameters represent a bounding box in 
    Richmond, VA in the United States. Downloaded file 
    size is ~897 MB as of Jan 1, 2020.
    """
    OSM_FILE = "map"
    api = overpy.Overpass()
    bounding_box = ", ".join([str(min_lat), str(min_lon), str(max_lat), str(max_lon)])
    query_str = "".join(["[out:xml];node(", bounding_box, ");out meta;"])
    
    try:
        print("Querying Overpass...")
        result = api.query(query_str)
    except overpy.exception.OverPyException as e:
        print("Unable to return query results.")
        print("Try passing in different parameters for ")
        print("the bounding box into the function.")
        return
    
    print("Results retrieved from Overpass.")
    print("Writing results to map file...")
    
    with open(OSM_FILE, "wb") as output:
        output.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write(b'<osm>\n  ')
        for element in result:
            output.write(ET.tostring(element, encoding='utf-8'))
        output.write(b'</osm>')
    
    print("Download complete.")
    
    return OSM_FILE


def create_sample_file(input_file, output_file, k=1):
    """
    Writes every k-th top level element from input_file to a 
    new file (output_file) and returns the new file name.
    """
    
    def get_element(input_file, tags=('node', 'way', 'relation')):
        context = iter(ET.iterparse(input_file, events=('start', 'end')))
        _, root = next(context)
        for event, elem in context:
            if event == 'end' and elem.tag in tags:
                yield elem
                root.clear()
    
    print("Writing elements to sample file...")
    
    with open(output_file, "wb") as output:
        output.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write(b'<osm>\n  ')
        for i, element in enumerate(get_element(input_file)):
            if i % k == 0:
                output.write(ET.tostring(element, encoding='utf-8'))
        output.write(b'</osm>')
    
    print("Sample file created.")
    
    return output_file

