import urllib.request, json, re  # Read url, decode json, regex
from lxml import etree  # Using a custom XML library (Make sure you have installed lxml)
import sys

# NOTES: 
# If set number contains a letter, this will break the program due to the numerical sort Eg. RR
# Comment out the sort function if needed by the xml will be sorted by string

# SETTINGS
set = "LL"  # Enter set to convert (In uppercase)
setName = "Leaders and Legends"
setGUID = "e8928809-8c6a-40a7-a4f8-7c9718988fd4"
gameVersion = "2.4.0.0"
scriptVersion = "3.1"

# List of keywords to be placed in the Keywords property in the XML
keywordList = [
    "Agile",
    "Calming",
    "Caretaker",
    "Competitive",
    "Diligent",
    "Eccentric",
    "Experienced",
    "Hasty",
    "Inspired",
    "Meticulous",
    "Persistent",
    "Prepared",
    "Prismatic",
    "Pumped",
    "Random",
    "Showy",
    "Starting Problem",
    "Stubborn",
    "Studious",
    "Supportive",
    "Swift",
    "Teamwork",
    "Transform",
    "Traveler",
    "Vexing",
    "Villain",
    "Front: Home Limit",
    "Back: Home Limit",
]

# FUNCTIONS
# Converts color from API to elements for OCTGN
def findElement(color):
    if color == "Blue":
        return "Loyalty"
    elif color == "Orange":
        return "Honesty"
    elif color == "Pink":
        return "Laughter"
    elif color == "Purple":
        return "Magic"
    elif color == "White":
        return "Generosity"
    elif color == "Yellow":
        return "Kindness"
    elif color == "Wild":
        return "Wild"
    else:
        return "None"


# Converts gametext to proper keywords and gametext
def convertKeywordAndGametext(gametext):
    gametextModified = gametext  # Saves modified gametext from other checks
    gametextAltModified = ""

    # Check for keywords and put them in keywords section
    # This needs to run first since <P> is needed
    for i in range(0, len(keywordList)):
        regex1 = r"^" + keywordList[i] + " <P>"  # For Diligent <P>
        regex2 = r"^" + keywordList[i] + "\.$"  # For Diligent.
        regex3 = r"^" + keywordList[i] + " \d\.$"  # For Diligent 1.
        regex4 = r"^" + keywordList[i] + " \d <P>"  # For Diligent 1 <P> and Front:
        regex5 = r" " + keywordList[i] + " \d <P>"  # For Back: Home Limit
        regex6 = r"^" + keywordList[i] + "\."  # For Starting Problem.

        if re.search(regex1, gametext):
            keywords.append(keywordList[i])
            gametextModified = gametextModified.replace(keywordList[i] + " <P> ", "")
        if re.search(regex2, gametext):
            keywords.append(keywordList[i])
            gametextModified = gametextModified.replace(keywordList[i] + ".", "")
        if re.search(regex3, gametext):
            getNumber = re.search(regex3, gametext).group()
            getNumber = re.search(r"\d", getNumber).group()
            keywords.append(keywordList[i] + " " + getNumber)
            gametextModified = gametextModified.replace(
                keywordList[i] + " " + getNumber + ".", ""
            )
        if re.search(regex4, gametext):
            getKeyword = re.search(regex4, gametext).group()
            getNumber = re.search(r"\d", getKeyword).group()

            # Check if card is a mane and do some modifications
            if "Front" in getKeyword:
                modifiedKeyword = keywordList[i].replace("Front: ", "")
                keywords.append(modifiedKeyword + " " + getNumber)
            else:
                keywords.append(keywordList[i] + " " + getNumber)
            gametextModified = gametextModified.replace(
                keywordList[i] + " " + getNumber + " <P> ", ""
            )
        if re.search(regex5, gametext) and "Home Limit" in gametext:
            getNumber = re.search(regex5, gametext).group()
            getNumber = re.search(r"\d", getNumber).group()

            modifiedKeyword = keywordList[i].replace("Back: ", "")
            altKeywords.append(modifiedKeyword + " " + getNumber)
            # Some manes have no / and some do, split gametext for main and alt
            if "/" in gametextModified:
                gametextModified, gametextAltModified = gametextModified.split(
                    " / " + keywordList[i] + " " + getNumber + " <P> "
                )
            else:
                gametextModified, gametextAltModified = gametextModified.split(
                    " " + keywordList[i] + " " + getNumber + " <P> "
                )
        if re.search(regex6, gametext) and "Starting Problem" in gametext:
            keywords.append(keywordList[i])
            gametextModified = gametextModified.replace(keywordList[i] + ". ", "")

    # Check for color in gametext and make it to [element] Eg. Pink seashell token to [laughter] seashell token
    if "Blue" in gametextModified:
        gametextModified = gametextModified.replace("Blue", "[Loyalty]")
    elif "Orange" in gametextModified:
        gametextModified = gametextModified.replace("Orange", "[Honesty]")
    elif "Pink" in gametextModified:
        gametextModified = gametextModified.replace("Pink", "[Laughter]")
    elif "Purple" in gametextModified:
        gametextModified = gametextModified.replace("Purple", "[Magic]")
    elif "White" in gametextModified:
        gametextModified = gametextModified.replace("White", "[Generosity]")
    elif "Yellow" in gametextModified:
        gametextModified = gametextModified.replace("Yellow", "[Kindness]")

    # Check for <P>, [no text]. and replace them
    gametextModified = gametextModified.replace(" <P> ", "&#10;")
    gametextAltModified = gametextAltModified.replace(" <P> ", "&#10;")
    gametextModified = gametextModified.replace("[no text].", "")
    gametextAltModified = gametextAltModified.replace("[no text].", "")

    # Change [1] to 1AT (I might phase this out)

    return (gametextModified, gametextAltModified)


# Convert the rest of the lists if needed
def convertEverythingElse(toConvert, listName):
    toConvertModified = toConvert
    toConvertModifiedAlt = ""
    toConvertModifiedAlt2 = ""

    # Change null to empty string (Need to be placed at the start)
    if toConvertModified is None:
        toConvertModified = ""
    
    if listName == "cardType" and "Mane" in toConvertModified:
        toConvertModified = "Mane Character"
        toConvertModifiedAlt = "Mane Character Boosted"

    if listName == "power" and "/" in toConvertModified:
        toConvertModified, toConvertModifiedAlt = toConvertModified.split("/")

    # Get the number of the first req only
    if listName == "playReqPwr" and "/" in toConvertModified:
        # Check for tri color cards
        if len(re.findall(r"\/", toConvertModified)) == 2:
            toConvertModified = toConvertModified[:1]
            toConvertModifiedAlt = toConvertModified
            toConvertModifiedAlt2 = toConvertModified
        else:
            toConvertModified = toConvertModified[:1]
            toConvertModifiedAlt = toConvertModified
    
    if listName == "playReqPwr" and "0" in toConvertModified:
        toConvertModified = ""

    # Remove Starting Problem from traits since they would be in keywords
    if listName == "traits" and "Starting Problem" in toConvertModified:
        toConvertModified = ""

    if listName == "probPlayerElementPwr2" and toConvertModified is 0:
        toConvertModified = ""

    return (toConvertModified, toConvertModifiedAlt, toConvertModifiedAlt2)


# MAIN CODE (STORING DATA FROM API)
# Lists to store data from json
(
    GUID,
    name,
    setID,
    cardType,
    element,
    subname,
    power,
    cost,
    playReqPwr,
    playReqElement,
) = ([] for i in range(10))
(
    traits,
    keywords,
    text,
    probBonus,
    probOppPwr,
    probPlayerElement1,
    probPlayerElementPwr1,
    probPlayerElement2,
    probPlayerElementPwr2,
    rarity,
) = ([] for i in range(10))
(
    multiPriElement,
    multiSecElement,
    triPriElement,
    triSecElement,
    triElement,
    secPlayReqElement,
    secPlayReqElementPwr,
    triPlayReqElement,
    triPlayReqElementPwr,
    altCardType,
    altKeywords,
    altText,
    altPower,
) = ([] for i in range(13))

# List of every list (Need to append blanks to keep every list in the same length)
allList = [
    GUID,
    name,
    setID,
    cardType,
    element,
    subname,
    power,
    cost,
    playReqPwr,
    playReqElement,
    traits,
    keywords,
    text,
    probBonus,
    probOppPwr,
    probPlayerElement1,
    probPlayerElementPwr1,
    probPlayerElement2,
    probPlayerElementPwr2,
    rarity,
    multiPriElement,
    multiSecElement,
    triPriElement,
    triSecElement,
    triElement,
    secPlayReqElement,
    secPlayReqElementPwr,
    triPlayReqElement,
    triPlayReqElementPwr,
    altCardType,
    altKeywords,
    altText,
    altPower,
]

count = 0  # Used to check for any list that has nothing appended at the end of loop

with urllib.request.urlopen(
    "http://www.ferrictorus.com/mlpapi1/cards?query=set:" + set + "&oguids=true"
) as url:
    data = json.loads(url.read().decode())

    # If JSON is empty, exit immediately to save time
    if data["data"] == []:
        print("No cards found, please check your settings!")
        sys.exit

    # Sorts the returned JSON based on ascending card number (Note: if card number contains a letter, this will break the program Eg. RR)
    sorted_data = dict(data)
    sorted_data["data"] = sorted(data["data"], key=lambda item: int(item["number"]))

    # Append all necessary card data into their respective lists
    for card in sorted_data["data"]:
        # Any list that do not need any conversion
        GUID.append(card["octgn_guid"])
        name.append(card["title"])  # & will be auto changed to &amp; in XML
        subname.append(card["subtitle"])
        setID.append(card["set"] + card["number"])
        rarity.append(card["rarity"])

        # Convert gametext
        gametextToSave, altGametextToSave = convertKeywordAndGametext(card["gametext"])
        text.append(gametextToSave)
        altText.append(altGametextToSave)

        # Convert everything else
        converted, convertedAlt, convertedAlt2 = convertEverythingElse(
            card["type"], "cardType"
        )
        cardType.append(converted)
        altCardType.append(convertedAlt)
        converted, convertedAlt, convertedAlt2 = convertEverythingElse(
            card["power"], "power"
        )
        power.append(converted)
        altPower.append(convertedAlt)
        converted, convertedAlt, convertedAlt2 = convertEverythingElse(
            card["cost"], "cost"
        )
        cost.append(str(converted))
        converted, convertedAlt, convertedAlt2 = convertEverythingElse(
            card["req"], "playReqPwr"
        )
        playReqPwr.append(converted)
        secPlayReqElementPwr.append(convertedAlt)
        triPlayReqElementPwr.append(convertedAlt2)
        converted, convertedAlt, convertedAlt2 = convertEverythingElse(
            card["traits"], "traits"
        )
        traits.append(converted)
        converted, convertedAlt, convertedAlt2 = convertEverythingElse(
            card["bonus"], "probBonus"
        )
        probBonus.append(str(converted))
        converted, convertedAlt, convertedAlt2 = convertEverythingElse(
            card["prireq"], "probPlayerElementPwr1"
        )
        probPlayerElementPwr1.append(str(converted))
        converted, convertedAlt, convertedAlt2 = convertEverythingElse(
            card["secreq"], "probPlayerElementPwr2"
        )
        probPlayerElementPwr2.append(str(converted))
        converted, convertedAlt, convertedAlt2 = convertEverythingElse(
            card["wildreq"], "probOppPwr"
        )
        probOppPwr.append(str(converted))

        # Convert API color to OCTGN element
        if "/" in card["color"]:  # Check for multicolor and problem cards
            firstElement = ""
            secondElement = ""
            thirdElement = ""
            if card["type"] == "Problem":
                firstElement, secondElement = card["color"].split("/")
                convertedPriElement = findElement(firstElement)
                probPlayerElement1.append(convertedPriElement)
                convertedSecElement = findElement(secondElement)
                probPlayerElement2.append(convertedSecElement)
            else:
                element.append("Multicolor")

                # Split tricolor and duocolor cards
                if len(re.findall(r"\/", card["color"])) == 2:
                    firstElement, secondElement, thirdElement = card["color"].split("/")

                    convertedPriElement = findElement(firstElement)
                    triPriElement.append(convertedPriElement)
                    playReqElement.append(convertedPriElement)

                    convertedSecElement = findElement(secondElement)
                    triSecElement.append(convertedSecElement)
                    secPlayReqElement.append(convertedSecElement)

                    convertedTriElement = findElement(thirdElement)
                    triElement.append(convertedTriElement)
                    triPlayReqElement.append(convertedTriElement)
                else:
                    firstElement, secondElement = card["color"].split("/")

                    convertedPriElement = findElement(firstElement)
                    multiPriElement.append(convertedPriElement)
                    playReqElement.append(convertedPriElement)

                    convertedSecElement = findElement(secondElement)
                    multiSecElement.append(convertedSecElement)
                    secPlayReqElement.append(convertedSecElement)
        else:  # For normal cards and single element prob cards
            convertedElement = findElement(card["color"])

            if card["type"] == "Problem":
                probPlayerElement1.append(convertedElement)
            else:
                #Dilemmas needs a wild prob element
                if card["traits"] == "Dilemma":
                    probPlayerElement1.append("Wild")

                # Some cards like TM do not have elements, only friends have
                if card["type"] != "Friend" and "None" in convertedElement:
                    element.append("")
                else:
                    element.append(convertedElement)

                #Check if card has any color req
                if card["req"] != "0" and card["req"] is not None:
                    playReqElement.append(convertedElement)

        # Check if any list has not been appended (This should be the end of the loop)
        for i in range(0, len(allList)):
            if len(allList[i]) <= count:
                allList[i].append("")
        count += 1

# MAIN CODE (CONVERT STORED DATA TO XML)
# The root element
setRoot = etree.Element(
    "set",
    name=setName,
    id=setGUID,
    gameId="65656467-b709-43b2-a5c6-80c2f216adf9",
    gameVersion=gameVersion,
    version=scriptVersion,
)

# Sub elements
packaging = etree.SubElement(setRoot, "packaging")  # Will not be fleshed out
cards = etree.SubElement(setRoot, "cards")

for i in range(0, count):
    # Include size for problem cards
    if cardType[i] == "Problem":
        card = etree.SubElement(cards, "card", id=GUID[i], size="Problem", name=name[i])
    else:
        card = etree.SubElement(cards, "card", id=GUID[i], name=name[i])
    
    # Rest of the properties
    etree.SubElement(card, "property", name="Number", value=setID[i])
    etree.SubElement(card, "property", name="Type", value=cardType[i])
    etree.SubElement(card, "property", name="Element", value=element[i])
    etree.SubElement(
        card, "property", name="MultiPrimaryElement", value=multiPriElement[i]
    )
    etree.SubElement(
        card, "property", name="MultiSecondaryElement", value=multiSecElement[i]
    )
    etree.SubElement(card, "property", name="TriPrimaryElement", value=triPriElement[i])
    etree.SubElement(
        card, "property", name="TriSecondaryElement", value=triSecElement[i]
    )
    etree.SubElement(card, "property", name="TriElement", value=triElement[i])
    etree.SubElement(card, "property", name="Subname", value=subname[i])
    etree.SubElement(card, "property", name="Power", value=power[i])
    etree.SubElement(card, "property", name="Cost", value=cost[i])
    etree.SubElement(card, "property", name="PlayRequiredPower", value=playReqPwr[i])
    etree.SubElement(
        card, "property", name="PlayRequiredElement", value=playReqElement[i]
    )
    etree.SubElement(
        card,
        "property",
        name="SecondaryPlayRequiredPower",
        value=secPlayReqElementPwr[i],
    )
    etree.SubElement(
        card,
        "property",
        name="SecondaryPlayRequiredElement",
        value=secPlayReqElement[i],
    )
    etree.SubElement(
        card,
        "property",
        name="TertiaryPlayRequiredPower",
        value=triPlayReqElementPwr[i],
    )
    etree.SubElement(
        card, "property", name="TertiaryPlayRequiredElement", value=triPlayReqElement[i]
    )
    etree.SubElement(card, "property", name="Traits", value=traits[i])
    etree.SubElement(card, "property", name="Keywords", value=keywords[i])
    etree.SubElement(card, "property", name="Text", value=text[i])
    etree.SubElement(card, "property", name="ProblemBonus", value=probBonus[i])
    etree.SubElement(card, "property", name="ProblemOpponentPower", value=probOppPwr[i])
    etree.SubElement(
        card, "property", name="ProblemPlayerElement1", value=probPlayerElement1[i]
    )
    etree.SubElement(
        card,
        "property",
        name="ProblemPlayerElement1Power",
        value=probPlayerElementPwr1[i],
    )
    etree.SubElement(
        card, "property", name="ProblemPlayerElement2", value=probPlayerElement2[i]
    )
    etree.SubElement(
        card,
        "property",
        name="ProblemPlayerElement2Power",
        value=probPlayerElementPwr2[i],
    )
    etree.SubElement(card, "property", name="Rarity", value=rarity[i])

    # Alternate side for Mane Characters
    if cardType[i] == "Mane Character":
        alternate = etree.SubElement(card, "alternate", name=name[i], type="Mane Character Boosted")
        etree.SubElement(alternate, "property", name="Number", value=setID[i])
        etree.SubElement(alternate, "property", name="Type", value=altCardType[i])
        etree.SubElement(alternate, "property", name="Element", value=element[i])
        etree.SubElement(
            alternate, "property", name="MultiPrimaryElement", value=multiPriElement[i]
        )
        etree.SubElement(
            alternate, "property", name="MultiSecondaryElement", value=multiSecElement[i]
        )
        etree.SubElement(alternate, "property", name="TriPrimaryElement", value=triPriElement[i])
        etree.SubElement(
            alternate, "property", name="TriSecondaryElement", value=triSecElement[i]
        )
        etree.SubElement(alternate, "property", name="TriElement", value=triElement[i])
        etree.SubElement(alternate, "property", name="Subname", value=subname[i])
        etree.SubElement(alternate, "property", name="Power", value=altPower[i])
        etree.SubElement(alternate, "property", name="Cost", value=cost[i])
        etree.SubElement(alternate, "property", name="PlayRequiredPower", value=playReqPwr[i])
        etree.SubElement(
            alternate, "property", name="PlayRequiredElement", value=playReqElement[i]
        )
        etree.SubElement(
            alternate,
            "property",
            name="SecondaryPlayRequiredPower",
            value=secPlayReqElementPwr[i],
        )
        etree.SubElement(
            alternate,
            "property",
            name="SecondaryPlayRequiredElement",
            value=secPlayReqElement[i],
        )
        etree.SubElement(
            alternate,
            "property",
            name="TertiaryPlayRequiredPower",
            value=triPlayReqElementPwr[i],
        )
        etree.SubElement(
            alternate, "property", name="TertiaryPlayRequiredElement", value=triPlayReqElement[i]
        )
        etree.SubElement(alternate, "property", name="Traits", value=traits[i])
        etree.SubElement(alternate, "property", name="Keywords", value=altKeywords[i])
        etree.SubElement(alternate, "property", name="Text", value=altText[i])
        etree.SubElement(alternate, "property", name="ProblemBonus", value=probBonus[i])
        etree.SubElement(alternate, "property", name="ProblemOpponentPower", value=probOppPwr[i])
        etree.SubElement(
            alternate, "property", name="ProblemPlayerElement1", value=probPlayerElement1[i]
        )
        etree.SubElement(
            alternate,
            "property",
            name="ProblemPlayerElement1Power",
            value=probPlayerElementPwr1[i],
        )
        etree.SubElement(
            alternate, "property", name="ProblemPlayerElement2", value=probPlayerElement2[i]
        )
        etree.SubElement(
            alternate,
            "property",
            name="ProblemPlayerElement2Power",
            value=probPlayerElementPwr2[i],
        )
        etree.SubElement(alternate, "property", name="Rarity", value=rarity[i])

# Save to XML file (Note that &#10; becomes &amp;#10;)
etree.ElementTree(setRoot).write(
    "set.xml",
    encoding="utf-8",
    standalone="yes",
    xml_declaration=True,
    pretty_print=True,
)

# To fix the &amp;#10; issue
f = open("set.xml", "r")
filedata = f.read()
f.close()

newdata = filedata.replace("&amp;#10;", "&#10;")

f = open("set.xml", "w")
f.write(newdata)
f.close()

