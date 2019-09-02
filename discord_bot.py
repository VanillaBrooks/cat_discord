# outside libraries
import discord
import requests
import parse_json
import pandas as pd

# std lib
import os
import time
import asyncio
import logging
import datetime

# local files
from api import dis_id, dis_secret, dis_token, permission_int 
# from api import reddit_secret, reddit_client_id

cats_url = 'https://oauth.reddit.com/r/cats/hot/'
class MyClient(discord.Client):

    async def on_ready(self):
        self.file = 'discord_file.png'

        print('Logged on as {0}!'.format(self.user))

        while True:
            # load a cache of the previous files
            csv = CsvData("old_data.csv")

            r = await parse_json.get_api(logging) # equal to headers from the get api

            logging.info('Starting main while loop')
            # submissions = [i.url for i in r.subreddit('cats').top('hour')]
            

            while True:
                try:
                    page_json = await parse_json.get_page_json(r, cats_url, logging)
                except Exception as e:
                    logging.exception('got an error handing page_json: %s ' % e)

                if page_json != False:
                    break
                logging.warning('bad response code from get page json')
                time.sleep(5)

            
            logging.info('Submissions fetched')
            try:
                submissions = await parse_json.parse_posts(25, page_json, logging)
            except Exception as e:
                logging.exception('There was an error fetching submissions from parse_posts: %s' % e)
            
            num_posts_checked = 0
            for link in submissions['url']:
                num_posts_checked += 1
                
                if csv.contains_url(link) == False:
                    # break out of loop if we successfully downloaded the image
                    if await download_image(link) == True:
                        break
                else:
                    continue

            logging.info('Trying to call send_the_file()')
            await self.send_the_file()
            logging.info('Exited send_the_file()')
            os.remove(self.file)
            logging.info('deleted the file')

            for _ in range(num_posts_checked):
                id = submissions['id'].pop(0)
                url = submissions['url'].pop(0)

                csv.add_new_entry(id, url)            

            csv.save_csv()

            logging.info('Sleeping...')
            await asyncio.sleep(10) # hourly

    async def send_the_file(self):
        for channel in client.get_all_channels():
            if 'cat-stuff' in channel.name:
            # if 'cat-worship' in channel.name:
                logging.info(f'Sending file to channel: {channel}')
                await client.send_file(channel, self.file)
                # send_message

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
            print("appending")
            print(new_df)
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


if __name__ == '__main__':
    logger_config()
    client = MyClient()
    client.run(dis_token)
