import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def get_cdli_proveniences(geodata):
    # Finished - get cdli ID for proveniences
    # extract provenience equivalents
    url = 'https://cdli.mpiwg-berlin.mpg.de/proveniences'
    # Get the content from the webpage
    request = requests.get(url)
    # Use BeautifulSoup to parse the source code from the webpage.
    soup = BeautifulSoup(request.text, 'html.parser')
    # Locate the text that contains the link relevant for data download.
    link_text = soup.find_all("div", class_="paginator d-none d-lg-block")
    page_number = re.search('Page 1 of [1-9]+',link_text[0].text)
    pages_total = str.split(page_number.group(),' ')[-1]
    pages_total = int(pages_total)
    proveniences_cdli_keys = {'provenience':[]}
    proveniences_cdli_keys = pd.DataFrame(proveniences_cdli_keys)
    for x in range(pages_total):
        new_file = pd.read_csv(f'https://cdli.mpiwg-berlin.mpg.de/proveniences?page={x+1}&format=csv',index_col=0,usecols=['id','provenience'])
        proveniences_cdli_keys = pd.concat([proveniences_cdli_keys,new_file])

    for y in proveniences_cdli_keys.index.values:
        try:
            proveniences_cdli_keys.loc[y,'glow'] = geodata.loc[geodata['cdli_provenience_id']==str(y),'site_id'].values[0]
        except:
            continue

    return proveniences_cdli_keys

def get_cdli_cat(geodata):
    proveniences_cdli_keys = get_cdli_proveniences(geodata)
    catalogue = pd.read_csv('https://media.githubusercontent.com/media/cdli-gh/data/master/cdli_cat.csv',usecols=['id_text','period','genre','provenience','object_type'],keep_default_na=False)
    catalogue['id_text'] = catalogue['id_text'].map(lambda n: 'P'+str(n).zfill(6))
    catalogue.set_index('id_text')
    catalogue['uncertain_prov'] = False

    for x in range(len(catalogue)):
        prov_split = catalogue.loc[x,'provenience'].split(' ?')
        if len(prov_split) > 1:
            catalogue.loc[x,'uncertain_prov'] = True
            catalogue.loc[x,'provenience'] = prov_split[0]
        else: catalogue.loc[x,'provenience'] = prov_split[0]
        try:
            catalogue.loc[x,'prov_id'] = int(proveniences_cdli_keys.loc[proveniences_cdli_keys['provenience']==catalogue.loc[x,'provenience'],].index.values[0])
        except:
            continue

    return catalogue