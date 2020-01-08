#!/usr/bin/env python
# coding: utf-8

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint


def show_all_tags(osm_file):
    """
    Takes the osm_file as input, iterates through all tags, and 
    prints out all distinct values for all distinct keys to 
    the console.
    
    Input:    file name of the data file (string)
    Returns:  (none)
    
    This function is mostly helpful in the beginning stages 
    of auditing the OSM file data by giving the user a full 
    view of what tag elements are included in the data in 
    an easily readable format.
    """
    tag_types = defaultdict(set)
    
    for event, element in ET.iterparse(osm_file, events=('start',)):
        for tag in element.iter("tag"):
            tag_types[tag.attrib['k']].add(tag.attrib['v'])
            
    pprint.pprint(dict(tag_types))


def audit_streets(osm_file):
    """
    Iterates through the osm_file, finds all tags with the 
    'addr:street' key, and returns all tag values whose 
    street types are not expected.
    
    Input:    file name of the data file (string)
    Returns:  a dict of street values with unexpected 
                  street types
    
    By gathering the list of unexpected street types, 
    the user can build a mapping of proper street types 
    in order to replace the unexpected ones during 
    the data cleaning process.
    """
    street_types = defaultdict(set)
    
    # Valid street suffixes and abbreviation mappings sourced from:
    # USPS - C1 Street Suffix Abbreviations
    # https://pe.usps.com/text/pub28/28apc_002.htm
    
    USPS_expected = [
        "Alley", "Anex", "Arcade", "Avenue", "Bayou", "Beach", "Bend", "Bluff", "Bluffs", "Bottom", "Boulevard", "Branch", 
        "Bridge", "Brook", "Brooks", "Burg", "Burgs", "Bypass", "Camp", "Canyon", "Cape", "Causeway", "Center", "Centers", 
        "Circle", "Cliff", "Cliffs", "Club", "Common", "Commons", "Corner", "Corners", "Course", "Court", "Courts", 
        "Cove", "Coves", "Creek", "Crescent", "Crest", "Crossing", "Crossroad", "Crossroads", "Curve", "Dale", "Dam", 
        "Divide", "Drive", "Drives", "Estate", "Estates", "Expressway", "Extension", "Extensions", "Falls", "Ferry", 
        "Field", "Fields", "Flat", "Flats", "Ford", "Fords", "Forest", "Forge", "Forges", "Fork", "Forks", "Fort", 
        "Freeway", "Garden", "Gateway", "Glen", "Glens", "Green", "Greens", "Grove", "Groves", "Harbor", "Harbors", "Haven", 
        "Heights", "Highway", "Hill", "Hills", "Hollow", "Inlet", "Island", "Islands", "Isle", "Junction", "Junctions", 
        "Key", "Keys", "Knoll", "Knolls", "Lake", "Lakes", "Landing", "Lane", "Light", "Lights", "Loaf", "Lock", "Locks", 
        "Lodge", "Loop", "Manor", "Manors", "Meadows", "Mill", "Mills", "Mission", "Motorway", "Mount", "Mountain", 
        "Mountains", "Neck", "Orchard", "Oval", "Overpass", "Park", "Parks", "Parkway", "Parkways", "Passage", "Path", 
        "Pike", "Pine", "Pines", "Place", "Plain", "Plains", "Plaza", "Point", "Points", "Port", "Ports", "Prairie", 
        "Radial", "Ranch", "Rapid", "Rapids", "Rest", "Ridge", "Ridges", "River", "Road", "Roads", "Route", "Shoal", "Shoals", 
        "Shore", "Shores", "Skyway", "Spring", "Square", "Squares", "Station", "Stravenue", "Stream", "Street", "Streets", 
        "Summit", "Terrace", "Throughway", "Trace", "Track", "Trafficway", "Trail", "Trailer", "Tunnel", "Turnpike", 
        "Underpass", "Union", "Unions", "Valley", "Valleys", "Viaduct", "View", "Views", "Village", "Villages", "Ville", 
        "Vista", "Way", "Well", "Wells"
    ]
    
    # These additional expected street suffixes are assumed 
    # to be acceptable for data cleaning purposes
    
    addl_expected = [
        "Arsenal", "Cary", "Chase", "Cloisters", "Close", "Conn", "Concourse", 
        "Driveway", "Farm", "Greene", "James", "Level", "Mews", "Needle", 
        "Oaks", "Overlook", "Pass", "Pathway", "Ramon", "Row", "Run", 
        "Sage", "Slip", "Trek", "Turn", "Walk", "Waye"
    ]
    
    # The direction suffix allows the audit to look at the 
    # second to the last string in the addr:street value 
    # for any unexpected street types
    
    direction_suffix = [
        "N", "N.", "N*", "North", 
        "S", "S.", "S*", "South", 
        "E", "E.", "E*", "East", 
        "W", "W.", "W*", "West"
    ]
    
    def audit_street_type(street_types, street_name):
        words = street_name.split(" ")
        if words[-1] in direction_suffix:
            if words[-2] not in [*USPS_expected, *addl_expected]:
                street_types[words[-2]].add(street_name)
        else:
            if words[-1] not in [*USPS_expected, *addl_expected]:
                street_types[words[-1]].add(street_name)
                
    def is_street_name(elem):
        return (elem.attrib['k'] == "addr:street")
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag in ("node", "way", "relation"):
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    
    return street_types


def audit_street_direction(osm_file):
    """
    Iterates through the osm_file, finds all tags with the 
    'addr:street' key, and returns all tag values that 
    have direction abbreviation prefix or suffix.
    
    Input:    file name of the data file (string)
    Returns:  a dict of street values whose prefix or 
                  suffix is a direction abbreviation
    
    By gathering the list of street values whose prefix 
    or suffix is a direction abbreviation, the user can 
    build a mapping of proper direction strings in order 
    to replace the abbreviations during the data cleaning 
    process.
    """
    direction_types = defaultdict(set)
    
    direction_abbrvs = [
        "N", "N.", "N*", 
        "S", "S.", "S*", 
        "E", "E.", "E*", 
        "W", "W.", "W*"
    ]
    
    def audit_direction(direction_types, street_name):
        words = street_name.split(" ")
        if words[0] in direction_abbrvs:
            direction_types[words[0]].add(street_name)
        if words[-1] in direction_abbrvs and words[-2] not in ["Suite", "Ste", "Ste."]:
            # skips those where the second to the last word 
            # is an iteration of 'Suite', ex. 'Suite E'
            direction_types[words[-1]].add(street_name)
                
    def is_street_name(elem):
        return (elem.attrib['k'] == "addr:street")
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag in ("node", "way", "relation"):
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_direction(direction_types, tag.attrib['v'])
    
    return direction_types


def audit_cities(osm_file):
    """
    Iterates through the osm_file, finds all tags with the 
    'addr:city' key, and returns the count of each city.
    
    Input:    file name of the data file (string)
    Returns:  a dict of city names with total counts
    
    The user can hone in on the city names with the 
    lowest counts (such as ones and twos) and research 
    whether the lowest counts should be excluded from 
    the dataset.
    """
    cities = {}
    
    def audit_city(cities, city):
        if city in cities.keys():
            cities[city] += 1
        else:
            cities[city] = 1
    
    def is_city(elem):
        return (elem.attrib['k'] == "addr:city")
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag in ("node", "way", "relation"):
            for tag in elem.iter("tag"):
                if is_city(tag):
                    audit_city(cities, tag.attrib['v'])
    
    return cities


def audit_states(osm_file):
    """
    Iterates through the osm_file, finds all tags with the 
    'addr:state', 'gnis:ST_alpha', or 'is_in:state_code' key, 
    and returns the count of each value of the keys.
    
    Input:    file name of the data file (string)
    Returns:  a dict of state values with total counts
    
    This function shows all possible iterations of the 
    state values for two reasons in the cleaning process:
    1. Any states that should be excluded from the dataset
    2. The user can choose whether or not to make all 
       valid state values consistent, for example 
       'Virginia' vs 'VA'
    """
    states = {}
    
    def audit_state(states, state):
        if state in states.keys():
            states[state] += 1
        else:
            states[state] = 1
    
    def is_state(elem):
        return (elem.attrib['k'] in ["addr:state", "gnis:ST_alpha", "is_in:state_code"])
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag in ("node", "way", "relation"):
            for tag in elem.iter("tag"):
                if is_state(tag):
                    audit_state(states, tag.attrib['v'])
    
    return states


def audit_county_names(osm_file):
    """
    Iterates through the osm_file, finds all tags with the 
    'gnis:county_name' or 'gnis:County' key, and returns 
    each county name.
    
    Input:    file name of the data file (string)
    Returns:  a set of county names
    
    The user can hone in on the county names and research 
    whether any should be excluded from the dataset.
    """
    counties = set()
    
    def is_county_name(elem):
        return (elem.attrib['k'] in ["gnis:county_name", "gnis:County"])
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag in ("node", "way", "relation"):
            for tag in elem.iter("tag"):
                if is_county_name(tag):
                    counties.add(tag.attrib['v'])
    
    return counties


def audit_county_numbers(osm_file):
    """
    Iterates through the osm_file, finds all tags with the 
    'gnis:county_id' or 'gnis:County_num' key, and returns 
    each county number.
    
    Input:    file name of the data file (string)
    Returns:  a set of county numbers
    
    The user can hone in on the county numbers and research 
    whether any should be excluded from the dataset.
    """
    counties = set()
    
    def is_county_num(elem):
        return (elem.attrib['k'] in ["gnis:county_id", "gnis:County_num"])
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag in ("node", "way", "relation"):
            for tag in elem.iter("tag"):
                if is_county_num(tag):
                    counties.add(tag.attrib['v'])
    
    return counties


def audit_countries(osm_file):
    """
    Iterates through the osm_file, finds all tags with the 
    'addr:country' or 'is_in:country' key, and returns the 
    count of each value of the keys.
    
    Input:    file name of the data file (string)
    Returns:  a dict of country values with total counts
    
    This function shows all possible iterations of the 
    country values for two reasons in the cleaning process:
    1. Any countries that should be excluded from the dataset
    2. The user can choose whether or not to make all 
       valid country values consistent, for example 
       'United States' vs 'US'
    """
    countries = {}
    
    def audit_country(countries, country):
        if country in countries.keys():
            countries[country] += 1
        else:
            countries[country] = 1
    
    def is_country(elem):
        return (elem.attrib['k'] in ["is_in:country", "addr:country"])
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag in ("node", "way", "relation"):
            for tag in elem.iter("tag"):
                if is_country(tag):
                    audit_country(countries, tag.attrib['v'])
    
    return countries


def audit_postal_codes(osm_file):
    """
    Iterates through the osm_file, finds all tags within the 
    postal_code_keys, and returns the count of each value of 
    the keys.
    
    Input:    file name of the data file (string)
    Returns:  a dict of postal code values with total counts
    
    This function shows all postal code values for two reasons 
    in the cleaning process:
    1. Any postal codes that should be excluded from the dataset
    2. The user can choose whether or not to make all 
       valid postal code values consistent, for example 
       some values may consist of multiples like '23111;23112'
    """
    postal_codes = {}
    
    def audit_postal_code(postal_codes, postal_code):
        if postal_code in postal_codes.keys():
            postal_codes[postal_code] += 1
        else:
            postal_codes[postal_code] = 1
    
    def is_postal_code(elem):
        postal_code_keys = [
            "addr:postcode", "postal_code", "tiger:zip", 
            "tiger:zip_left", "tiger:zip_left_1", 
            "tiger:zip_left_2", "tiger:zip_left_3", 
            "tiger:zip_left_4", "tiger:zip_left_5", 
            "tiger:zip_right", "tiger:zip_right_1", 
            "tiger:zip_right_2", "tiger:zip_right_3"
        ]
        return (elem.attrib['k'] in postal_code_keys)
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag in ("node", "way", "relation"):
            for tag in elem.iter("tag"):
                if is_postal_code(tag):
                    audit_postal_code(postal_codes, tag.attrib['v'])
    
    return postal_codes


def audit_max_speeds(osm_file):
    """
    Iterates through the osm_file, finds all tags with the 
    'maxspeed' or 'maxspeed:advisory' key, and returns the 
    set of values of the keys.
    
    Input:    file name of the data file (string)
    Returns:  a set of max speed values
    
    Lists out all values of max speed within the dataset 
    for the purposes of consistency ('20 mph' vs '20').
    """
    max_speeds = set()
    
    def is_max_speed(elem):
        return (elem.attrib['k'] in ["maxspeed", "maxspeed:advisory"])
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag in ("node", "way", "relation"):
            for tag in elem.iter("tag"):
                if is_max_speed(tag):
                    max_speeds.add(tag.attrib['v'])
    
    return max_speeds


def audit_denominations(osm_file):
    """
    Iterates through the osm_file, finds all tags with the 
    'denomination' key, and returns the set of values of 
    the keys.
    
    Input:    file name of the data file (string)
    Returns:  a set of denomination values
    
    Lists out all values of denominations within the 
    dataset for the purposes of consistency 
    ('none' vs 'nondenominational').
    """
    denominations = set()
    
    def is_denomination(elem):
        return (elem.attrib['k'] == "denomination")
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag in ("node", "way", "relation"):
            for tag in elem.iter("tag"):
                if is_denomination(tag):
                    denominations.add(tag.attrib['v'])
    
    return denominations


def audit_religions(osm_file):
    """
    Iterates through the osm_file, finds all tags with the 
    'religion' key, and returns the set of values of the keys.
    
    Input:    file name of the data file (string)
    Returns:  a set of religion values
    
    Lists out all values of religions within the dataset 
    for the purposes of consistency ('Christian' vs 'christian').
    """
    religions = set()
    
    def is_religion(elem):
        return (elem.attrib['k'] == "religion")
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag in ("node", "way", "relation"):
            for tag in elem.iter("tag"):
                if is_religion(tag):
                    religions.add(tag.attrib['v'])
    
    return religions

