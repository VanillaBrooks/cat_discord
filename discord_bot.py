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
            old_csv_data = await get_older_data()

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
                
                #check that the dataframe exists
                if type(old_csv_data) != bool:

                    # if the link is in the csv file we continue to the next iteration
                    if link in old_csv_data['url'].values:
                        continue
                # break out of loop if we successfully downloaded the image
                if await download_image(link) == True:
                    break

                     
            logging.info('Trying to call send_the_file()')
            # await self.send_the_file()
            logging.info('Exited send_the_file()')
            os.remove(self.file)
            logging.info('deleted the file')

            # remove checked posts from list and store them in csv
            old_data = {}
            old_data['id'] = []
            old_data['url'] = []

            for _ in range(num_posts_checked):
                old_data['id'].append(submissions['id'].pop(0))
                old_data['url'].append(submissions['url'].pop(0))

            # write to csv
            df = pd.DataFrame(old_data)

            df.to_csv('old_data.csv', header=True, index=False)


            logging.info('Sleeping...')
            await asyncio.sleep(60*60) # hourly

    async def send_the_file(self):
        for channel in client.get_all_channels():
            if 'cat' in channel.name:
                logging.info(f'Sending file to channel: {channel}')
                await client.send_file(channel, self.file)
                # send_message


async def get_older_data():
    if not os.path.exists('old_data.csv'):
        return False
    else:
        return pd.read_csv('old_data.csv')

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
