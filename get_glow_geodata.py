import requests
import geopandas
from bs4 import BeautifulSoup
import pandas as pd

# Download Geographical data from Zenodo repository by the Geomapping Landscapes of Writing project, please remember to cite the resource when used.
# We also add a column with individual cdli_provenience_id, in this way it gets easier to find the site_id from the cdli proveniences
def get_glow_geodata(url='https://doi.org/10.5281/zenodo.4960710'):
    # Get the content from the Zenodo webpage
    request = requests.get(url)
    # Use BeautifulSoup to parse the source code from the Zenodo webpage.
    soup = BeautifulSoup(request.text, 'html.parser')
    # Locate the text that contains the link relevant for data download.
    link_text = soup.find_all(type="application/octet-stream")
    # Get the link containing the GEOJSON data.
    link = link_text[1].get('href')
    # Read the geojson data with Geopandas from the link.
    geodata = geopandas.read_file(link)
    # Reduce the geojson data to only necesary data, that is 'site_id', 'cdli_id' and 'geometry'.
    geodata = geodata.filter(items=['site_id','cdli_provenience_id','geometry'])
    #geodata['number_texts'] = 0
    for x in range(len(geodata)):
        multiple_values = str(geodata.loc[x,'cdli_provenience_id']).split(' : ')
        if len(multiple_values) > 1:
            for value in multiple_values:
                    new_row = {'site_id':geodata.loc[x,'site_id'],'cdli_provenience_id':value,'geometry':geodata.loc[x,'geometry'],'number_texts':0}
                    new_row = pd.DataFrame(new_row,index=[len(geodata)])
                    geodata = pd.concat([geodata,new_row])
        else: continue
        geodata = geodata.drop(index=x)
        geodata = geodata.reset_index(drop=True)
    return geodata