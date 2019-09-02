import requests.auth
import json
import requests
from pprint import pprint
import datetime
from api import secret, client_id, post_data

# secret = 'fCUqRDZ0VJw_pCKIoQ3SeyqNOXU'
# client_id = 's7MHnqAlzfGlSA'


async def get_api(logging):
    logging.info('starting to get fresh api creds')
    client_auth = requests.auth.HTTPBasicAuth(
        client_id, secret)
    # post_data = {"grant_type": "password",
    #              "username": "DehnexTentcleSuprise", "password": "FreightCar"}

    headers = {"User-Agent": "json/0.1 by DehneXtentclsuprise"}
    logging.info('sending post request for creds')
    response = requests.post(
        "https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)

    logging.info('returning to main func from get_api()')
    return {"Authorization": "bearer %s" % response.json()['access_token'],
            "User-Agent": "Json/0.1 by DehneXtentclsuprise"}


async def get_page_json(headers, url, logging):
    logging.info('sending get request for submissions')
    response = requests.get(
        url, headers=headers)

    logging.info('request recieved with response %s' % response)
    if '200' in str(response):
        return response.json()
    else:
        raise ValueError("JSON response code was not 200")


async def parse_posts(num_posts_to_parse, input_json, logging):
    if num_posts_to_parse > 25:
        raise ValueError('number of posts must be <=25')

    posts = input_json['data']['children'][:num_posts_to_parse]

    postdict = {}

    keys = ['url',  'title', 'subreddit',
            'upvotes', 'time', 'id', 'comment count']
    fields = 'url title subreddit ups created id num_comments'.split(' ')

    postdict = {i: [] for i in keys}

    # convert from unix time to UTC time

    async def to_utc(unix_time_str):
        int_time = int(unix_time_str)
        new_time = datetime.datetime.utcfromtimestamp(int_time)
        return new_time

    # make sure a string or a tuple is a string
    async def to_string(unknown_type):
        title_type = type(unknown_type)

        if title_type == tuple:
            unknown_type = ''.join(i for i in unknown_type)
        elif title_type != str:
            raise ValueError('type was not str or tuple %s ' % title_type)

        return unknown_type

    for post in posts:

        post_data = post['data']
        logging.info('working on post with id %s' % post_data['id'])
        for i in range(len(fields)):
            
            field = fields[i]
            current_key = keys[i]

            current_data = post_data[field]

            if i == 0:  # if we are dealing with url
                # if the link is bad we dont continue
                if await check_link(current_data, logging) == False:
                    break
            elif i == 1:  # convert a potential tuple title to strings
                current_data = await to_string(current_data)
            elif i == 4: # handles time conversion
                current_data = await to_utc(current_data)

            postdict[current_key].append(current_data)

    logging.info('exiting to main func')
    return postdict


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
