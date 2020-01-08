#!/usr/bin/env python
# coding: utf-8

from pymongo import MongoClient
import xml.etree.cElementTree as ET
import json


def shape_element(element):
    """
    Reshapes an XML element into a JSON object.
    
    Input:    cElementTree element
    Returns:  JSON object (dict)
    """
    
    if element.tag in ["node", "way", "relation"]:
        node = {}
        
        node["element_type"] = element.tag
        for key in element.attrib.keys():
            if key not in ["lat", "lon"]:
                node[key] = element.attrib[key]
                
        if element.tag == "node":
            # adds latitude and longitude values 
            # as coordinates to the node dict
            node["coordinates"] = [
                float(element.attrib["lat"]), 
                float(element.attrib["lon"])
            ]
        
        if element.tag == "way":
            # adds all node reference values as a 
            # list of node_refs to the node dict
            node_refs = []
            for nd in element.iter("nd"):
                node_refs.append(nd.attrib['ref'])
            if len(node_refs) != 0:
                node["node_refs"] = node_refs
        
        if element.tag == "relation":
            # adds each ref, role, and type attribute 
            # of each member as a member dict to a 
            # list of members to the node dict
            members = []
            for member in element.iter("member"):
                mem_dict = {
                    "ref" : member.attrib["ref"], 
                    "role" : member.attrib["role"], 
                    "type" : member.attrib["type"]
                }
                members.append(mem_dict)
            if len(members) != 0:
                node["members"] = members
        
        tags = element.iter("tag")
        
        if tags is not None:
            
            def build_nested_dict(keys, value, node_dict=None):
                # this function recursively builds a nested dict 
                # using keys and optionally node_dict and passing 
                # value through each recursion until the stop condition
                
                sub_dict = {}
                
                if len(keys) == 1:
                    sub_dict[keys[0]] = value
                elif node_dict is not None and keys[0] in node_dict.keys():
                    if isinstance(node_dict[keys[0]], dict):
                        sub_dict[keys[0]] = {
                            **node_dict[keys[0]], 
                            **build_nested_dict(keys[1:], value, node_dict[keys[0]])
                        }
                    else:
                        sub_dict[keys[0]] = [
                            node_dict[keys[0]], 
                            build_nested_dict(keys[1:], value)
                        ]
                else:
                    sub_dict[keys[0]] = build_nested_dict(keys[1:], value)
                
                return sub_dict
            
            for tag in tags:
                # if a tag key contains one or more 
                # colon (:) characters, then the build_nested_dict 
                # recursive function is called
                
                k = tag.attrib['k']
                keys = k.split(":")
                
                if len(keys) == 1:
                    node[tag.attrib['k']] = tag.attrib['v']
                elif keys[0] in node.keys():
                    if isinstance(node[keys[0]], dict):
                        node[keys[0]] = {
                            **node[keys[0]], 
                            **build_nested_dict(keys[1:], tag.attrib['v'], node[keys[0]])
                        }
                    else:
                        node[keys[0]] = [
                            node[keys[0]], 
                            build_nested_dict(keys[1:], tag.attrib['v'])
                        ]
                else:
                    node[keys[0]] = build_nested_dict(keys[1:], tag.attrib['v'])
        
        return node


def process_map(file_in, pretty = False):
    """
    Opens the XML file, iterates through each
    element, shapes each element into a JSON
    object, and outputs each shaped object into
    a JSON file.

    Input:    XML input file (string)
              optional pretty param for indents
    Returns:  (none)
    """
    file_out = "{0}.json".format(file_in)

    with codecs.open(file_out, "w") as fo:

        for _, element in ET.iterparse(file_in):
            el = shape_element(element)

            if el:
                if pretty:
                    fo.write(json.dumps(el, indent=4)+"\n")
                else:
                    fo.write(json.dumps(el)+"\n")


def upload_data_into_mongo(json_file):
    """
    Creates a MongoDB client, a database, and a 
    collection, then iterates through the elements 
    of the JSON data file and inserts each 
    document (element) into the collection.
    
    Input:    file name of the JSON data file (string)
    Returns:  Mongo database
    
    Note: A MongoDB instance must be running on local 
          host 27017 for this function to successfully 
          process.
          mapdb -> name of database
          map_docs -> name of collection
    """
    
    client = MongoClient("mongodb://localhost:27017")
    db = client.mapdb
    collection = db.map_docs
    
    with open(json_file) as f:
        file_data = json.load(f)
    
    collection.insert_many(file_data)
    
    return db

