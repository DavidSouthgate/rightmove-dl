#!/usr/local/bin/python3
import sys
import os
import shutil
import requests
import json
import youtube_dl

def main():
    if len(sys.argv) != 2:
        return invalid_argument_count()

    url = sys.argv[1]
    page = requests.get(url)
    content = page.content

    data = get_page_data(content)
    name = get_name(data)

    directory = os.getcwd() + "/" + name
    os.mkdir(directory)
    os.chdir(directory)

    print("Downloading data to " + directory)

    process_images(directory, data)
    process_floorplans(directory, data)
    process_virtual_tours(directory, data)
    process_json_dump(directory, data)

def process_images(directory, data):
    images_directory = directory + "/Images"
    os.mkdir(images_directory)
    os.chdir(images_directory)

    images = get_images(data)
    download_images(images)

    os.chdir(directory)
    delete_directory_if_empty(images_directory)

def process_floorplans(directory, data):
    floorplans_directory = directory + "/Floorplans"
    os.mkdir(floorplans_directory)
    os.chdir(floorplans_directory)

    floorplans = get_floorplans(data)
    download_images(floorplans)

    os.chdir(directory)
    delete_directory_if_empty(floorplans_directory)

def process_virtual_tours(directory, data):
    virtual_tours_directory = directory + "/Virtual Tours"
    os.mkdir(virtual_tours_directory)
    os.chdir(virtual_tours_directory)

    virtual_tours = get_virtual_tours(data)
    download_virtual_tours(virtual_tours)

    os.chdir(directory)
    delete_directory_if_empty(virtual_tours_directory)

def process_json_dump(directory, data):
    os.chdir(directory)
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)

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
    eprint("Unable to extract data from page")
    sys.exit(1)

def get_images(data):
    images = []
    for image in data["propertyData"]["images"]:
        images.append({
            "url": image["url"],
            "name": image["caption"]
        })
    return images

def get_image_filename(image):
    filename = image["url"].split("/")[-1]
    extension = filename.split(".")[-1]

    if image["name"] is not None:
        return image["name"] + "." + extension
    else:
        return filename

def get_floorplans(data):
    floorplans = []
    for floorplan in data["propertyData"]["floorplans"]:
        if floorplan["type"] != "IMAGE":
            print("Warning: found unsupported floorplan of type " + floorplan["type"] + ". This will be ignored.")
        else:
            floorplans.append({
                "url": floorplan["url"],
                "name": floorplan["caption"]
            })
    return floorplans

def download_images(images):
    for image in images:
        filename = get_image_filename(image)
        print("Downloading " + filename)

        request = requests.get(image["url"], stream = True)
        if request.status_code == 200:
            request.raw.decode_content = True
            with open(filename,'wb') as f:
                shutil.copyfileobj(request.raw, f)
        else:
            eprint("Could not download image " + filename + ". Status code was " + request.status_code)

def get_virtual_tours(data):
    virtual_tours = []
    for virtual_tour in data["propertyData"]["virtualTours"]:
        virtual_tours.append(virtual_tour["url"])
    return virtual_tours

def download_virtual_tours(virtual_tours):
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for url in virtual_tours:
            ydl.download([url])

def delete_directory_if_empty(directory):
    if len(os.listdir(directory)) == 0:
        os.rmdir(directory)

def invalid_argument_count():
    eprint("Expected exactly one command line argument")
    eprint("")
    eprint("Usage:")
    eprint("    python rightmove-downloader.py <Rightmove Property URL>")
    eprint("")

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":
    main()