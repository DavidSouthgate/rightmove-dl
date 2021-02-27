#!/usr/local/bin/python3
import json
from os import getcwd, listdir, remove
from os.path import isdir, join, exists
from CsvWriter import CsvWriter

def main():
    directory = getcwd()
    writer = CsvWriter("rightmove.csv")
    writer.write("Name", "Price Qualifier", "Price", "Status", "Bedrooms", "Bathrooms", "Size (sq. m)", "Link")

    for subdir in listdir(directory):
        path = join(directory, subdir)
        if isdir(path):
            process_directory(writer, path)
    
    writer.close()

def process_directory(writer, path):
    json_path = join(path, "data.json")

    with open(json_path) as f:
        data = json.load(f)

    name = data["propertyData"]["address"]["displayAddress"]
    priceQualifier = data["propertyData"]["prices"]["displayPriceQualifier"]
    
    rawPrice = data["propertyData"]["prices"]["primaryPrice"]
    if rawPrice[0] != "£":
        print("Warning: Unsuported currency symbol '{}' for price in {}".format(rawPrice[0], path))
        return
    price = int(rawPrice[1:].replace(",", ""))

    bedrooms = data["propertyData"]["bedrooms"]
    bathrooms = data["propertyData"]["bathrooms"]

    sizeSqM = None
    for sizing in data["propertyData"]["sizings"]:
        if sizing["unit"] == "sqm":
            sizeSqM = sizing["minimumSize"]
            break
    status = get_status(data)
    link = "https://www.rightmove.co.uk/properties/" + data["propertyData"]["id"] + "/"

    writer.write(name, priceQualifier, price, status, bedrooms, bathrooms, sizeSqM, link)

def get_status(data):
    tags = data["propertyData"]["tags"]
    if len(tags) == 0:
        return None
    remove = []
    for i in range(0, len(tags)):
        tag = tags[i]
        if tag == "ONLINE_VIEWING":
            remove.append(tag)
        else:
            tags[i] = tag_to_status(tags[i])
    for tag in remove:
        tags.remove(tag)
    return ",".join(tags)

def tag_to_status(tag):
    split = tag.split("_")
    split = map(tag_part_to_status_part, split)
    return " ".join(split)

def tag_part_to_status_part(part):
    if part == "STC":
        return part
    return part.title()

if __name__ == "__main__":
    main()
