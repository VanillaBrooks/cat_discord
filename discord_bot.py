import discord, requests, os, time
import praw
import asyncio
from api import dis_id, dis_secret, dis_token, permission_int
from api import reddit_secret, reddit_client_id

class MyClient(discord.Client):

    async def on_ready(self):
        self.file = 'discord_file.png'

        print('Logged on as {0}!'.format(self.user))
        r = praw.Reddit(client_id=reddit_client_id, client_secret=reddit_secret, user_agent='discord cat pictures by u/dehnextentaclesuprise')

        while True:
            print(' in loop')
            submissions = [i.url for i in r.subreddit('cats').top('hour')]

            url = check_link(submissions)
            download_image(url)

            print('sending file')
            await self.send_the_file()
            print('file sent')
            os.remove(self.file)

            time.sleep(60*60) # hourly

    async def send_the_file(self):
        for channel in client.get_all_channels():
            if 'cat' in channel.name:
                print('sending a  file from loop')
                await client.send_file(channel, self.file)
                # await client.send_message(channel, 'this is a sample')


def check_link(link_list):
    for link in link_list:
        if "tumblr" not in link and 'imgur' not in link and 'gfycat' not in link and 'redd' \
                not in link:
            continue

        # disregard if its an imgur .gif or .gifv
        elif '.gif' in link or '.gifv' in link or 'v.redd' in link:
            continue

        # dont download if its an imgur album or comments section
        elif '/a/' in link or '/r/' in link:
            continue

        elif link == True:
            continue

        # download gfycat posts
        elif 'gfycat' in link:
            continue

        # downlaod direct links to imgur and reddit
        elif 'i.i' not in link and 'i.r' not in link and 'tumblr' not in link and \
                'v.redd' not in link:
            print('we found link')
            return link

def download_image(link):
    response = requests.get(link)
    try:
        with open('discord_file.png', 'wb') as fo:
            for chunk in response.iter_content(4096):
                fo.write(chunk)

    # oh fuck what went wrong better log that bitch
    except Exception as e:
        print('oh shit there was an exception with downloading')
        return False

    return True

if __name__ == '__main__':
    r = praw.Reddit(client_id=reddit_client_id, client_secret=reddit_secret, user_agent='discord cat pictures by u/dehnextentaclesuprise')

    client = MyClient()

    # print(list(client.servers))
    client.run(dis_token)


# https://discordapp.com/oauth2/authorize?&client_id=554126254429962242&scope=bot&permissions=8
