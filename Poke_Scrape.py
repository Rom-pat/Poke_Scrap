
"""Poke_Scrape.py scraping serebii and bulbapedia"""
from urllib.request import urlopen
import requests
import os
import numpy as np
#import json
import csv
from bs4 import BeautifulSoup

# "https://www.serebii.net/pokemon/bulbasaur/"
#useful site to scrap 

def run_serebi_Scrap():
    """serebii script scrapes all Pokemon information and uploads it as a CSV."""
    url = "https://www.serebii.net/pokemon/nationalpokedex.shtml"
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("iso-8859-1")
    soup = BeautifulSoup(html, "html.parser")
    national_dex = soup.find_all("tr")
    pkmn = national_dex[2]
    info = pkmn.find_all("td")
    info_dict = fix_serebii_info(info)
    with open('Updated_pokemon.csv', 'w',newline='') as csvfile:
        #open csv
        fieldnames = info_dict.keys()
        poke_Writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        poke_Writer.writeheader()
        poke_Writer.writerow(info_dict)
        #performs the csv writing/scraping
        for pkmn in national_dex[4::2]:
            info = pkmn.find_all("td")
            info_dict = fix_serebii_info(info)
            poke_Writer.writerow(info_dict)

def run_db_scrap():
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

def run_bulb_scrap():
    """Bulbpedia scrap will return all the Pokemon Home Assets as PNG. """
    #"https://archives.bulbagarden.net/w/index.php?title=Category:HOME_artwork&filefrom=%2A058%0AHOME0058H+s.png#mw-category-media"
    url= "https://archives.bulbagarden.net/w/index.php?title=Category:HOME_artwork"
    while url !="": 
        page = requests.get(url)
        content =page.content
        soup = BeautifulSoup(content, "html.parser")
        images = soup.find_all("img")
        pages= soup.find_all("a", {"title": "Category:HOME artwork"})
        os.mkdir("Pokemon_Home_PNG")
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


def main(*args):
    run_serebi_Scrap()
    run_db_scrap()
    run_bulb_scrap()



def fix_serebii_info(info):
    info_dict = {}
    info_dict["pokedex_number"]=info[0].text.strip()
    info_dict["name"] = info[3].text.strip()
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

if __name__ == "__main__":
    main()
