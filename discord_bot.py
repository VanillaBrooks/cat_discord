# outside libraries
import discord
import requests
import praw

# std lib
import os
import time
import asyncio
import logging
import datetime

# local files
from api import dis_id, dis_secret, dis_token, permission_int 
from api import reddit_secret, reddit_client_id

class MyClient(discord.Client):

    async def on_ready(self):
        self.file = 'discord_file.png'

        print('Logged on as {0}!'.format(self.user))
        r = praw.Reddit(client_id=reddit_client_id, client_secret=reddit_secret, user_agent='discord cat pictures by u/dehnextentaclesuprise')

        while True:
            logging.info('Starting main while loop')
            submissions = [i.url for i in r.subreddit('cats').top('hour')]
            logging.info('Submissions fetched')
            
            links = await check_link(submissions)

            if not await download_image(links):
                continue
                
            logging.info('Trying to call send_the_file()')
            await self.send_the_file()
            logging.info('Exited send_the_file()')
            os.remove(self.file)
            logging.info('deleted the file')

            logging.info('Sleeping...')
            await asyncio.sleep(60*60) # hourly

    async def send_the_file(self):
        for channel in client.get_all_channels():
            if 'cat' in channel.name:
                logging.info(f'Sending file to channel: {channel}')
                await client.send_file(channel, self.file)


# filter function to find the links we can use 
async def check_link(link_list):
    good_links = []
    for link in link_list:
        bad_link = True
        if "tumblr" not in link and 'imgur' not in link and 'gfycat' not in link and 'redd' \
                not in link:
            pass

        # disregard if its an imgur .gif or .gifv
        elif '.gif' in link or '.gifv' in link or 'v.redd' in link:
            pass

        # dont download if its an imgur album or comments section
        elif '/a/' in link or '/r/' in link:
            pass

        elif link == True:
            pass

        # download gfycat posts
        elif 'gfycat' in link:
            pass

        # downlaod direct links to imgur and reddit
        elif 'i.i' in link or 'i.r' in link:
            logging.info(f'found good link: {link}')
            good_links.append(link)
            bad = False
        if bad:
            logging.info(f'BAD LINK : {link}')

    return good_links

# iterates through list of good image links and tries to download one
async def download_image(link_list):
    for link in link_list:
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
