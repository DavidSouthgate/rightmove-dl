#!/usr/local/bin/python3
import sys
import os
import shutil
import requests
import json
import youtube_dl
import re
from bcolors import warning, error

def main():
    if len(sys.argv) != 2:
        return invalid_argument_count()

    url = sys.argv[1]
    page = requests.get(url)
    content = page.content

    data = get_page_data(content)
    
    directory_name = get_directory_name(data)
    directory = os.getcwd() + "/" + directory_name
    os.mkdir(directory)
    os.chdir(directory)

    print("Downloading data to " + directory)

    process_images(directory, data)
    process_floorplans(directory, data)
    process_virtual_tours(directory, data)
    process_epc_graphs(directory, data)
    process_brochures(directory, data)
    process_json_dump(directory, data)

def process_json_dump(directory, data):
    os.chdir(directory)
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

def get_name(data):
    return data["propertyData"]["address"]["displayAddress"].strip()

def get_page_data(content):
    search = "    window.PAGE_MODEL = "
    for line in content.splitlines():
        line = line.decode('utf-8')
        start = line[0:len(search)]
        if search == start:
            json_str = line[len(search):] 
            return json.loads(json_str)
    error("Unable to extract data from page")
    sys.exit(1)

"""
Media Types
"""

def process_images(directory, data):
    process_medias(directory, data, "images", "Image")

def process_floorplans(directory, data):
    process_medias(directory, data, "floorplans", "Floorplan")

def process_brochures(directory, data):
    process_medias(directory, data, "brochures", "Brochure")

def process_epc_graphs(directory, data):
    process_medias(directory, data, "epcGraphs", "EPC Graph")

"""
Medias

Throughout this codebase we use the fake word "medias" to differentiate from the singular form "media". This isn't
correct English but makes naming things easier.
"""

def process_medias(directory, data, media_type, name_singular):
    name_plural = name_singular + "s"
    new_directory = directory + "/" + name_plural
    os.mkdir(new_directory)
    os.chdir(new_directory)

    media = get_medias(data, media_type, name_singular)
    download_medias(media)

    os.chdir(directory)
    delete_directory_if_empty(new_directory)

def get_medias(data, media_type, name_singular):
    assets = []
    for asset in data["propertyData"][media_type]:
        if media_type == "floorplans" and asset["type"] != "IMAGE":
            warning("Found unsupported floorplan of type " + floorplan["type"] + ". This will be ignored.")
        elif "https://media.rightmove.co.uk/" in asset["url"]:
            assets.append({
                "url": asset["url"],
                "name": asset["caption"]
            })
        else:
            warning("Unsupported {} at {}".format(name_singular, asset["url"]))
    return assets

def download_medias(medias):
    for media in medias:
        filename = get_media_filename(media)
        print("Downloading " + filename)

        request = requests.get(media["url"], stream = True)
        if request.status_code == 200:
            request.raw.decode_content = True
            with open(filename,'wb') as f:
                shutil.copyfileobj(request.raw, f)
        else:
            error("Could not download media " + filename + ". Status code was " + request.status_code)

def get_media_filename(media):
    filename = media["url"].split("/")[-1]
    extension = filename.split(".")[-1]

    if media["name"] is None:
        return get_safe_name(filename)
    
    i = 1
    filename = generate_media_filename(media["name"], extension, i)
    while os.path.isfile(filename):
        filename = generate_media_filename(media["name"], extension, i)
        i += 1
    return filename

def generate_media_filename(name, extension, i):
    filename = name + (" " + str(i) if i > 1 else "") + "." + extension
    return get_safe_name(filename)

"""
Virtual Tours
"""

def process_virtual_tours(directory, data):
    virtual_tours_directory = directory + "/Virtual Tours"
    os.mkdir(virtual_tours_directory)
    os.chdir(virtual_tours_directory)

    virtual_tours = get_virtual_tours(data)
    download_virtual_tours(virtual_tours)

    os.chdir(directory)
    delete_directory_if_empty(virtual_tours_directory)

def get_virtual_tours(data):
    virtual_tours = []
    for virtual_tour in data["propertyData"]["virtualTours"]:
        if virtual_tour["provider"] == "YOUTUBE" or virtual_tour["provider"] == "VIMEO":
            virtual_tours.append({
                "url": virtual_tour["url"],
                "name": virtual_tour["caption"]
            })
        else:
            warning("Ignoring unsupported virtual tour at {}".format(virtual_tour["url"]))
    return virtual_tours

def download_virtual_tours(virtual_tours):
    for virtual_tour in virtual_tours:
        name = get_safe_name(virtual_tour["name"])
        opts = {"outtmpl": name}
        with youtube_dl.YoutubeDL(opts) as ydl:
            try:
                ydl.download([virtual_tour["url"]])
            except youtube_dl.utils.DownloadError as e:
                pass

"""
Util
"""

def get_directory_name(data):
    name = get_name(data)
    name = name.replace("/", "-")
    name = name.replace(" ,", ",")
    return get_safe_name(name)

def get_safe_name(name):
    name = re.sub("[^A-Za-z0-9\- ,._]", "", name)
    while "  " in name:
        name.replace("  ", " ")
    return name

def delete_directory_if_empty(directory):
    if len(os.listdir(directory)) == 0:
        os.rmdir(directory)

def invalid_argument_count():
    error("Expected exactly one command line argument")
    print("")
    print("Usage:")
    print("    python rightmove-dl.py <Rightmove Property URL>")
    print("")

if __name__ == "__main__":
    main()
