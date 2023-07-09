import os
import sys
import json
import requests
from pathlib import Path

# requirements
import asyncio
import aiohttp
from PIL import Image
from colr import Colr
# from termcolor import colored

THIS_PATH = Path(__file__).parent.resolve()

async def api_call(is_repo, name):
    BASE_URL = 'https://api.github.com/'
    ENDPOINT_URL = 'repos/' if is_repo else 'users/'

    URL = f'{BASE_URL}{ENDPOINT_URL}{name}'

    async with aiohttp.request('GET', URL) as res:
        http_status = res.status

        if http_status != 200:
            return http_status

        content = await res.json()
        return content

def image_to_ascii(url):
    img_data = requests.get(url).content
    file_name = url.split('/')[-1].split('?')[0]
    user_img_location = Path(f'{THIS_PATH}/images/{file_name}.png')

    with open(user_img_location, 'wb') as file:
        file.write(img_data)

    with Image.open(user_img_location) as image:
        IMAGE_WIDTH = 25
        MULTIPLIER = 0.45 # Used to fix the image height because the characters are taller

        # Get initial width and height
        width, height = image.size
        aspect_ratio = height / width

        # Fix the new height according to the aspect ratio (1:1)
        IMAGE_HEIGHT = int(aspect_ratio * IMAGE_WIDTH * MULTIPLIER)

        image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
        pixel_values = image.getdata()

        ascii_text = ''
        for index, character in enumerate(pixel_values):
            if not isinstance(character, (tuple, list)):
                continue

            r, g, b = character

            if (index != 0) and (index % IMAGE_WIDTH == 0):
                ascii_text += '\n'

            ascii_text += Colr().rgb(r, g, b, '\u2588')

    user_img_location.unlink(missing_ok=True)

    return ascii_text

def fetch_repo(info):
    return {
        'owner': info['owner'],
        # 'size': info['size'],
        'stars': info['stargazers_count'],
        'watchers': info['watchers_count'],
        # 'issues': info['open_issues_count'],
        'forks': info['forks_count'],
        'archived': info['archived'],
        'disabled': info['disabled'],
        **({'license': info['license']['name']} if info['license'] is not None else {}),
        **({'forked_parent': info['parent']['owner']['html_url']} if info['fork'] else {}),
        # TODO: Languages: like colors in neofetch, with colors and icons
    }

def fetch_user(info):
    return {'company': info['company'],}

def fetch_main(name):
    is_repo = '/' in name

    info = asyncio.run(api_call(is_repo, name))

    if info in (401, 404, 429):
        return info

    generic_info = {
        **({'image': info['avatar_url']} if not is_repo else {'image': info['owner']['avatar_url']}),
        **({'description': info['bio']} if not is_repo else {'description': info['description']}),
        **({'website': info['blog']} if not is_repo else {'website': info['homepage']}),
        **({'username': info['login']} if not is_repo else {}),
        **({'email': info['email']} if not is_repo else {}),
        **({'location': info['location']} if not is_repo else {}),
        **({'public_repos': info['public_repos']} if not is_repo else {}),
        **({'public_gists': info['public_gists']} if not is_repo else {}),
        **({'followers': info['followers']} if not is_repo else {}),
        **({'following': info['following']} if not is_repo else {}),
        **({'type': info['type']} if not is_repo else {'type': 'Repo'}),
        'name': info['name'],
        'github_url': info['html_url'],
        'created_at': info['created_at'],
        # 'updated_at': info['updated_at'],
    }

    if is_repo:
        return generic_info | fetch_repo(info)
    elif info['type'] == 'User':
        return generic_info | fetch_user(info)
    elif info['type'] == 'Organization':
        return generic_info

def output_generator(fetched_info):
    fetched_info['image'] = image_to_ascii(fetched_info['image'])

    # print(fetched_info)
    print(fetched_info['image'])
    print(fetched_info['followers'])
    print(fetched_info['github_url'])
    # print(json.decoder(fetched_info['image']))

if __name__ == '__main__':
    # Api call
    name = sys.argv[1]

    fetched_info = fetch_main(name)

    output_generator(fetched_info)

    # print(image_to_ascii('https://avatars.githubusercontent.com/u/110683019?v=4'))
    # print(image_to_ascii('https://avatars.githubusercontent.com/u/1024025?v=4'))
    # print(image_to_ascii('https://avatars.githubusercontent.com/u/90156486?v=4'))