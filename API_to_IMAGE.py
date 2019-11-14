import os, os.path
from os import path
import sys
import urllib.request, json  # Read url, decode json

# NOTES
# This program assumes you have placed a folder with images named with lowercase set letters and card number Eg. sb41 or ll41
# Cards with alternative sides must have a "b" at the end of their name Eg. sb1b or ll1b
# This folder must be in the same folder as this py file for this to work
# In the future, I might add a feature to retrieve images directly from Ponyhead instead or make a o8c file directly

# SETTINGS
set = "ad"  # Case sensitive
imageExtension = ".jpg"  # Must be same for every image in the folder
folderName = "test_folder"  # Name of the folder with images

GUID = []
cardNumber = []
maneCount = 0
count = 0
dirPath = os.path.join(sys.path[0], folderName)  # Get full path

with urllib.request.urlopen(
    "http://www.ferrictorus.com/mlpapi1/cards?query=set:" + set + "&oguids=true"
) as url:
    data = json.loads(url.read().decode())

    # If JSON is empty, exit immediately to save time
    if data["data"] == []:
        print("No cards found in API, please check your settings!")
        sys.exit

    # Get GUID and card number
    for card in data["data"]:
        GUID.append(card["octgn_guid"])
        cardNumber.append(card["number"])

        # Add an additional count for manes to tally with the supposed amount of card images
        if card["type"] == "Mane":
            maneCount += 1

    # Loop through every image file
    for filename in os.listdir(dirPath):
        # Find if image name matches a set number
        for number in cardNumber:
            # Rename any alternate image file first
            if filename == set + number + "b" + imageExtension:
                src = dirPath + "\\" + filename
                index = cardNumber.index(number)
                newFilename = src.replace(filename, GUID[index])
                newFilename = (
                    newFilename + ".Mane Character Boosted" + imageExtension
                )
                os.rename(src, newFilename)
            elif filename == set + number + imageExtension:
                src = dirPath + "\\" + filename
                index = cardNumber.index(number)
                newFilename = src.replace(filename, GUID[index])
                newFilename = newFilename + imageExtension
                os.rename(src, newFilename)
