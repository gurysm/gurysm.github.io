import requests
from bs4 import BeautifulSoup
import re
from zipfile import ZipFile
from parse_ORACC_json import *
import os
from tqdm import tqdm
import pandas as pd
import json

def get_epsd2_project_urls():
    url_epsd2 = 'https://oracc.museum.upenn.edu/epsd2/json/index.html'
    request_epsd = requests.get(url_epsd2,verify=False)
    # Use BeautifulSoup to parse the source code from the epsd2 webpage.
    soup_epsd2 = BeautifulSoup(request_epsd.text, 'html.parser')
    # Currently, there is no proper systematisation of the corpora in epsd2, so we have to get the links based on the structure. Now we get all the table entries that will contain URLs.
    all_corpus_links = soup_epsd2.find_all('tr')
    # Dictionary for URLs that will be used to download corpora.
    urls = {}
    # Go through the entries of the table.
    for link_line in all_corpus_links:
        # Find the links in each table entries, also if there is none.
        link_in_line = link_line.find('a')
        # We here only look at table entries that contain links.
        if link_in_line != None:
            # Get the actual links.
            link_url = link_in_line.get('href')
            # We then count the number of hyphens, because that is the current defining factor of the corpora URLs.
            if link_url.count('-') > 0:
                # To get the names we find the first hyphen, which is immediately before the project name.
                project_name = re.search('\-',link_url)
                # We then redefine it as the project name only without the file format ending.
                project_name = link_url[project_name.start()+1:-4]
                # Append the subcorporar name and subcorpora link.
                urls[project_name.replace('/','-')] = 'https://oracc.museum.upenn.edu/json/epsd2-' + project_name.replace('/','-') + '.zip'
            else: continue
        else: continue
    return urls

def get_epsd2_files(dir):
    keys_2_pop = []
    # We run through each sub project in the urls dictionary.
    urls = get_epsd2_project_urls()
    for sub_project in urls:
        # We send ulr requests, based on the links given for each sub project in the urls dictionary.
        request_corpus = requests.get(urls[sub_project],verify=False)
        # We define the folder name for the ZIP folder we want to download.
        file_name = f'{dir}/{sub_project}.zip'
        # We open for the file name to be written based on the ZIP folder.
        with open(file_name, mode='wb') as file:
            # We write the ZIP folder with the content from the epsd2.
            file.write(request_corpus.content)
        try:
            # We try to make a ZIP object to extract the content.
            with ZipFile(file_name, 'r') as zip:
                # We extract to an espd2_data folder.
                zip.extractall(path=f'{dir}/epsd2_data/{sub_project}')
                os.remove(file_name)
        except:
            # In case the above didn't work we are told which folders couldn't be handled.
            print(f"{file_name} is downloaded, but the ZIP folder doesn't have content or doesn't work and it will be removed from the list of sub projects")
            keys_2_pop.append(sub_project)
            os.remove(f'{dir}/{sub_project}.zip')

    for keys in keys_2_pop:
        urls.pop(keys)
    return urls

def parse_epsd2_files(dir):
    text_files = []
    lemma = []
    meta_data = {'label': None}
    dollar_keys = ['extent', 'scope', 'state']
    urls = get_epsd2_files(dir)
    for sub_project in tqdm(urls):
        corpus_folder = f'{dir}/epsd2_data/{sub_project}/epsd2/{sub_project.replace("-","/")}/corpusjson'
        corpus_files = [x for x in os.listdir(corpus_folder) if x[0]=='P']
        for file in tqdm(corpus_files):
            text_files.append(f'{dir}/epsd2_data/{sub_project}/epsd2/{sub_project.replace("-","/")}/corpusjson/{file}')
            meta_data['id_text'] = file[0:7]
            with open(corpus_folder + '/' + file, 'r') as f:
                file_json = json.load(f)
            lemma.extend(parse_ORACC_json(file_json,meta_data,dollar_keys))

    # The resulting dataframe of all ORACC words from the JSON files we downloaded.
    lemma_df = pd.DataFrame(lemma)
    return lemma_df
