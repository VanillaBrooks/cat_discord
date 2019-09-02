import pandas as pd
import os
import logging
import datetime
import requests
import time


# Handler for CSV operations        
class CsvData():
    def __init__(self, path):
        self.path = path

        self.append_ids = []
        self.append_urls = []

        if os.path.exists(path):
            self.check_csv = True

            self.csv_data = pd.read_csv(path)
        else: 
            self.check_csv = False

    # Aff new ids to be merged without checking if they are already in the DF
    def add_new_entry_unchecked(self, id, url):
        self.append_ids.append(id)
        self.append_urls.append(url)
    
    # add new ids to be merged to the main DF while checking they dont already exist
    def add_new_entry(self, id, url):
        # data does not already exist
        if self.contains_id(id) == False and self.contains_url(url) == False:
            self.add_new_entry_unchecked(id, url)
        # data exists
        else:
            pass

    # id / url pair is BOTH not in the main dataframe
    def contains_older(self, id, url):
        
        # csv contains the id or the url
        if  self.contains_id(id) or self.contains_url(url):
            return True
        # the picture has not been posted before
        else:
            return False

    # a given id is in the main dataframe
    def contains_id(self, id):
        if self.check_csv == True:
            return self.csv_data['id'].isin([id]).any()
        else: 
            return False
    # a given url is in the main dataframe
    def contains_url(self, url):
        if self.check_csv == True:
            return self.csv_data['url'].isin([url]).any()
        else: 
            return False

    # append current data to the CSV, merge the new ids and urls into the main dataframe
    def save_csv(self):
        new_df = pd.DataFrame({
            "id": self.append_ids,
            "url": self.append_urls
            })
        
        if self.check_csv == False:
            # this is the creation of the CSV, write the headers
            new_df.to_csv(self.path, header=True, index=False)
            self.check_csv = True
            self.csv_data = new_df

        elif self.check_csv == True:
            # Append to existing data, no headers
            new_df.to_csv(self.path, mode='a', header=False, index=False)
            self.csv_data = pd.concat([self.csv_data, new_df])

        self.append_ids  = []
        self.append_urls = []
        
    def __repr__(self):
        if self.check_csv:
            return str(self.csv_data)
        else:
            return ""


# filter function to find the links we can use
async def check_link(link, logging):
    good_link = False

    # downlaod direct links to imgur and reddit
    if 'i.i' in link or 'i.r' in link:
        logging.info(f'found good link: {link}')
        good_link = True

    if good_link == False:
        logging.info(f'BAD LINK : {link}')

    return good_link


# setup logging
def logger_config():
    logging_folder = 'logging/'
    try: os.mkdir(logging_folder)
    except Exception:
        pass

    # month - day __ hour - minute - second
    LOG_FILENAME = logging_folder + datetime.datetime.now().strftime('%m-%d__%H-%M-%S') + '.txt'

    logging.basicConfig(filename=LOG_FILENAME, 
        level=logging.INFO, 
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')



# iterates through list of good image links and tries to download one
async def download_image(link):
    logging.info(f'downloading image link {link}')
    response = requests.get(link)

    try:
        with open('discord_file.png', 'wb') as fo:
            for chunk in response.iter_content(4096):
                fo.write(chunk)

        return True

    # oh fuck what went wrong better log that bitch
    except Exception:
        logging.exception('Got an exception downloading')

    return False