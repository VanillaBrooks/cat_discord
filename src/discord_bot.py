# outside libraries
import discord
import helpers
import praw

# std lib
import os
import asyncio
import logging

# local files
import api

r = praw.Reddit(client_id=api.reddit_client_id, client_secret=api.reddit_secret,
                user_agent='cat bot')

# how long between posts [seconds]
delay_timer = 60 * 60

class MyClient(discord.Client):

    async def on_ready(self):
        self.file = 'discord_file.png'

        print('Logged on as {0}!'.format(self.user))
        csv = helpers.CsvData("old_data.csv")

        while True:
            # load a cache of the previous files

            logging.info('Starting main while loop')
            new_posts = [[i.url, i.id] for i in r.subreddit("cats").hot(limit=25)]
            hot_urls, hot_ids = list(zip(*new_posts))
            logging.info('Submissions fetched')

            num_posts_checked = 0
            for link in hot_urls:
                num_posts_checked += 1
                
                # if we have not posted this before...
                if csv.contains_url(link) == False:
                    
                    # if the link is not an image skip downloading it
                    if await helpers.check_link(link, logging) == False:
                        continue
                    # break out of loop if we successfully downloaded the image
                    if await helpers.download_image(link) == True:
                        break
                else:
                    continue

            logging.info('Trying to call send_the_file()')
            await self.send_the_file()
            logging.info('Exited send_the_file()')
            # try to remove the file
            try:os.remove(self.file)
            except Exception: pass
            logging.info('deleted the file')

            # this could probably just do hot_ids[num_posts_checked]
            for j in range(num_posts_checked):
                id_  = hot_ids[j]
                url = hot_urls[j]

                csv.add_new_entry(id_, url)            

            csv.save_csv()

            logging.info('Sleeping...')
            await asyncio.sleep(delay_timer) # hourly

    async def send_the_file(self):
        for channel in client.get_all_channels():
            # if 'cat-stuff' in channel.name:
            if 'cat-worship' in channel.name:
                logging.info(f'Sending file to channel: {channel}')
                try:
                    # send_message
                    await client.send_file(channel, self.file)
                except Exception as e:
                    # message was too big
                    logging.exception(f"encountered error: {e}")

if __name__ == '__main__':
    helpers.logger_config()
    client = MyClient()
    client.run(api.dis_token)
