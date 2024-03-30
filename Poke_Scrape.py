
"""Poke_Scrape.py scraping serebii and bulbapedia"""
from urllib.request import urlopen
import requests
import os
import numpy as np
import pandas as pd
import json
import re
import csv
from bs4 import BeautifulSoup, NavigableString

# "https://www.serebii.net/pokemon/bulbasaur/"
#useful site to scrap 
class Pokemon_info: 
    names = {"swordshield": "Sword/Shield","ultrasunultramoon": "UltraSun/UltraMoon",
              "sunmoon": "Sun/Moon", "omegarubyalphasapphire": "Omega Ruby/Alpha Sapphire",
              "xy":"X/Y","black2white2":"Black2/White2",
              "blackwhite":"Black/White","platinum":"Platinum",
              "heartgoldsoulsilver":"Heartgold/Soulsilver","diamondpearl":"Diamond/Pearl",
              "rubysapphire":"Ruby/Sapphire","fireredleafgreen":"FireRed/LeafGreen",
              "brilliantdiamondshiningpearl":"Brilliant Diamond/Shining Pearl","legendsarceus":"Legends Arceus",
              "scarletviolet":"Scarlet/Violet","isleofarmordex": "Isle Of Armor",
              "thecrowntundradex":"Crown Tundra"}
    pokedex = {2: set(range(1,252)), 3:set(range(1,387)), 4: set(range(1,494)),
               5: set(range(1,650)) ,6:set(range(1,722)),7: set(range(1,808))}
    game_to_gen = {"Red/Blue/Green/Yellow": 1, "Gold/Silver": 2, "Crystal": 2, "Ruby/Sapphire": 3, "Emerald": 3,
                   "FireRed/LeafGreen": 3, "Diamond/Pearl": 4, "Platinum": 4, "Heartgold/Soulsilver": 4,
                   "Black/White": 5, "Black2/White2": 5, "X/Y": 6, "Omega Ruby/Alpha Sapphire" : 6, 
                   "Sun/Moon": 7 , "UltraSun/UltraMoon": 7, "Let's Go, Pikachu/Let's Go, Eevee" : 7,
                   "Sword/Shield":8, "Sword/Shield DLC":8, "Brilliant Diamond/Shining Pearl" : 8,
                   "Legends Arceus": 8, "Scarlet/Violet": 9, "Scarlet/Violet DLC": 9}
    

def run_serebi_Scrap():
    """serebii script scrapes all Pokemon information and uploads it as a CSV."""
    pokedex_list = []
    url = "https://www.serebii.net/pokemon/nationalpokedex.shtml"
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("iso-8859-1")
    soup = BeautifulSoup(html, "html.parser")
    national_dex = soup.find_all("tr")
    pkmn = national_dex[2]
    info = pkmn.find_all("td")
    fix_serebii_info(info)
    for pkmn in national_dex[2::2]:
        info = pkmn.find_all("td")
        pokedex_list.append(fix_serebii_info(info))
    return pokedex_list

def run_image_db_scrap():
    """db scrap returns all Pokemon Home Assets as JPEG."""
    url = "https://pokemondb.net/pokedex/shiny"
    page = requests.get(url)
    content =page.content
    soup = BeautifulSoup(content, "html.parser")
    normal_mon = soup.find_all("img",{"class":"img-fixed shinydex-sprite shinydex-sprite-normal"})
    shiny_mon = soup.find_all("img",{"class":"img-fixed shinydex-sprite shinydex-sprite-shiny"})
    os.mkdir("Pokemon_Home_JPEG")
    for mon in normal_mon: 
        r = requests.get(mon["src"])
        file_name = os.path.join("Pokemon_Home_JPEG",mon["src"].split("/")[-1])
        with open(file_name,"wb") as f:
            for chunk in r:
                f.write(chunk)
    for mon in shiny_mon:
        r = requests.get(mon["src"])
        file_name = os.path.join("Pokemon_Home_JPEG",mon["src"].split("/")[-1].replace(".jpg","-shiny.jpg"))
        with open(file_name, 'wb') as f:
            for chunk in r:
                f.write(chunk)

def run_image_bulb_scrap():
    """Bulbpedia scrap will return all the Pokemon Home Assets as PNG. """
    #"https://archives.bulbagarden.net/w/index.php?title=Category:HOME_artwork&filefrom=%2A058%0AHOME0058H+s.png#mw-category-media"
    url= "https://archives.bulbagarden.net/w/index.php?title=Category:HOME_artwork"
    os.mkdir("Pokemon_Home_PNG")
    while url !="": 
        page = requests.get(url)
        content =page.content
        soup = BeautifulSoup(content, "html.parser")
        images = soup.find_all("img")
        pages= soup.find_all("a", {"title": "Category:HOME artwork"})
        for image in images[:-1]:
            r = requests.get(image["src"])
            file_name = os.path.join("Pokemon_Home_PNG",image["src"].split("/")[-2])
            with open(file_name,"wb") as f:
                for chunk in r:
                    f.write(chunk)
        url=""
        for page in pages:
            if page.text == "next page":
                url="https://archives.bulbagarden.net"+page["href"]
                break


def run_bulb_scrap(names):
    """Bulb2 Scraps all possible Game locations of a Pokemon returns entire dex"""
    location_list = []
    for name in names:
        #name.replace(" ", "_")
        url ='https://bulbapedia.bulbagarden.net/wiki/'+name.replace(" ", "_")+"_(Pok%C3%A9mon)"
        page = requests.get(url)
        content =page.content
        soup = BeautifulSoup(content, "html.parser")
        gen_table = soup.find("h3",string="Game locations").find_next_sibling("table")
        gen_table = gen_table.tbody.tr
        Location_indexes = {}
        Location_indexes["Name"] = soup.find("big").get_text()
        while gen_table: 
            games =  gen_table.get_text().replace("\n\n\n\n", "  ").strip()
            games =  games.replace("\n\n", "/").replace("\n","")
            games =  games.split("  ")
            if '' in games:
                games.remove('')
            for key, value in zip(games[1::2],games[2::2]):
                if len(key.split("/")) == 2:
                    versions = key.split("/")
                    Location_indexes[versions[0]] = value
                    Location_indexes[versions[1]] = value
                else:
                    Location_indexes[key] = value
            gen_table = gen_table.find_next_sibling()
        location_list.append(Location_indexes)
    return location_list

# key words, Unobtainable, Event, Trade

def main(*args):
    Poke_info = Pokemon_info()
    df = pd.DataFrame(run_serebi_Scrap())
    #Image USES
    #run_image_db_scrap()
    #run_image_bulb_scrap()

    # Gets DATA
    #location_list = run_bulb_scrap(df["Name"])
    #df2 = pd.DataFrame(location_list,columns=location_list[0].keys())
    #df = pd.merge(df,df2, on="Name")
    #df.to_csv('Updated_pokemon.tsv',encoding='utf-8',index=False,sep="\t")
    #Gets region data (can be seperate from top)
    scrape_all_regional_Dex(df)




def fix_serebii_info(info):
    info_dict = {}
    info_dict["pokedex_number"]=info[0].text.strip()
    info_dict["Name"] = info[3].text.strip()
    types = info[4].find_all("a")
    if len(types) == 2:
        info_dict["type1"]= types[0]["href"][14:]
        info_dict["type2"]= types[1]["href"][14:]
    else:
        info_dict["type1"]= types[0]["href"][14:]
    abilities = info[5].find_all("a")
    info_dict["abilities"] = []
    for ability in abilities:
        info_dict["abilities"].append(ability.text)
    info_dict["hp"] = info[6].text.strip()
    info_dict["attack"] = info[7].text.strip()
    info_dict["defense"] = info[8].text.strip()
    info_dict["sp_attack"] = info[9].text.strip()
    info_dict["sp_defense"] = info[10].text.strip()
    info_dict["speed"] = info[11].text.strip()
    return info_dict


def scrape_all_regional_Dex(df):
    """Scraps all OBTAINABLE pokemon in that specific game/ region"""
    json_dex = {}
    json_dex["Red/Blue/Green/Yellow"] = json_dex ["Let's Go, Pikachu/Let's Go, Eevee"] = list(range(1,151))
    json_dex["Gold/Silver"] = list(Pokemon_info.pokedex[2].difference({1,2,3,4,5,6,7,8,9,138,139,140,141,144,145,146,150,151,251}))
    json_dex["Crystal"] = list(Pokemon_info.pokedex[2].difference({1,2,3,4,5,6,7,8,9,37,38,56,57,138,139,140,141,144,145,146,150,151,179,180,181,203,223,224}))
    json_dex["Ruby/Sapphire"]= json_dex["FireRed/LeafGreen"] = Pokemon_info.pokedex[3]
    json_dex["Emerald"] = list(Pokemon_info.pokedex[3].difference({283,284,307,308,315,335,337}))
    json_dex["Diamond/Pearl"]= json_dex["Heartgold/Soulsilver"] = json_dex["Platinum"]  = Pokemon_info.pokedex[4]
    json_dex["Black/White"]= json_dex["Black2/White2"] = Pokemon_info.pokedex[5]
    json_dex["X/Y"] = json_dex["Omega Ruby/Alpha Sapphire"]  = Pokemon_info.pokedex[6]
    json_dex["UltraSun/UltraMoon"] = json_dex["Sun/Moon"] = Pokemon_info.pokedex[7]
    json_dex["Sword/Shield DLC"] = set()
    json_dex["Scarlet/Violet DLC"] = set()
    #Gen8 and above due to limited pokemon
    json_dex = Dex_region_Scrape(df=df,json_dex=json_dex,names=Pokemon_info.names)
    #gen 7 and below
    json_dex = unavailable_scrape(df=df,json_dex=json_dex,names=Pokemon_info.names)
    json_arr = []
    for key in json_dex:
        json_arr.append({"Name" : key, "Dex": sorted(list(json_dex[key])), "Gen": Pokemon_info.game_to_gen[key]})
    dex_file = open("RegionalDex.json", "w") 
    json.dump(json_arr,dex_file,indent=4)
    dex_file.close()

def Dex_region_Scrape(df,json_dex,names):
    """Scraps all OBTAINABLE pokemon that are post gen 7"""
    number_set = set()
    Dex_regions = ["https://www.serebii.net/swordshield/galarpokedex.shtml", 
               "https://www.serebii.net/swordshield/isleofarmordex.shtml",
               "https://www.serebii.net/swordshield/thecrowntundradex.shtml",
               "https://serebii.net/swordshield/pokemonnotindex.shtml",
               "https://www.serebii.net/scarletviolet/paldeapokedex.shtml",
               "https://www.serebii.net/scarletviolet/kitakamipokedex.shtml",
               "https://www.serebii.net/scarletviolet/blueberrypokedex.shtml",
               "https://www.serebii.net/brilliantdiamondshiningpearl/sinnohpokedex.shtml",
               "https://www.serebii.net/brilliantdiamondshiningpearl/otherpokemon.shtml",
               "https://www.serebii.net/legendsarceus/hisuipokedex.shtml"]
    for url in Dex_regions:
        number_set.clear()
        page = urlopen(url)
        split_url = url.split("/")
        game = split_url[3]
        dlc = split_url[4].split(".")[0]
        html_bytes = page.read()
        html = html_bytes.decode("iso-8859-1")
        soup = BeautifulSoup(html, "html.parser")
        dex = soup.find_all("td",{"class": "fooinfo"})
        if game == "swordshield":
            for pkmn in dex[2::11]:
                name = pkmn.findChildren("br")[0].previous
                number_set.add(int(df.loc[df["Name"] == name]["pokedex_number"].values[0][1:]))
            if dlc == "pokemonnotindex" or dlc == "isleofarmordex" or dlc == "thecrowntundradex":
                json_dex["Sword/Shield DLC"] = json_dex["Sword/Shield DLC"] | number_set.copy()
            else: 
                json_dex[names[game]]= number_set.copy()
        elif game == "brilliantdiamondshiningpearl" or game == "legendsarceus":
            for pkmn in dex[2::4]:
                name = pkmn.findChildren("br")[0].previous
                number_set.add(int(df.loc[df["Name"] == name]["pokedex_number"].values[0][1:]))
            if dlc == "otherpokemon":
                json_dex[names[game]] =  json_dex[names[game]] | number_set.copy()
            else: 
                json_dex[names[game]]= number_set.copy()
        elif game == "scarletviolet":
            for pkmn in dex[2::4]:
                name = pkmn.text.strip()
                number_set.add(int(df.loc[df["Name"] == name]["pokedex_number"].values[0][1:]))
            if dlc =="kitakamipokedex" or dlc=="blueberrypokedex":
                json_dex["Scarlet/Violet DLC"] = json_dex["Scarlet/Violet DLC"] | number_set.copy()
            else: 
                json_dex[names[game]]= number_set.copy()
    return json_dex

def unavailable_scrape(df,json_dex, names):
    """Scraps all OBTAINABLE pokemon that are gen 7 or previous"""
    unavailable_mons = ["https://www.serebii.net/ultrasunultramoon/unobtainable.shtml",
                        "https://www.serebii.net/sunmoon/unobtainable.shtml",
                        "https://www.serebii.net/omegarubyalphasapphire/unobtainable.shtml",
                        "https://www.serebii.net/xy/unobtainable.shtml",
                        "https://www.serebii.net/black2white2/unobtainable.shtml",
                        "https://www.serebii.net/blackwhite/unobtainable.shtml",
                        "https://www.serebii.net/platinum/missing.shtml",
                        "https://www.serebii.net/heartgoldsoulsilver/unobtainable.shtml",
                        "https://www.serebii.net/diamondpearl/unobtainables.shtml",
                        "https://www.serebii.net/rubysapphire/unobtainable.shtml",
                        "https://www.serebii.net/fireredleafgreen/unobtainable.shtml",
                        ]
    number_set = set()
    for url in unavailable_mons:
        number_set.clear()
        page = urlopen(url)
        split_url = url.split("/")
        game = split_url[3]
        html_bytes = page.read()
        html = html_bytes.decode("iso-8859-1")
        soup = BeautifulSoup(html, "html.parser")
        dex = soup.find_all("td", string=re.compile("#"))
        for pkmn in dex:
            number = int(pkmn.text.strip()[1:])
            number_set.add(number)
        json_dex[names[game]] = json_dex[names[game]].difference(number_set)
    return json_dex




if __name__ == "__main__":
    main()