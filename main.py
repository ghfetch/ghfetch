import os
import sys
import json
import requests
from pathlib import Path

# requirements
import asyncio
import aiohttp
from PIL import Image
from termcolor import colored

THIS_PATH = Path(__file__).parent.resolve()

async def api_call(is_repo, name):
    BASE_URL = 'https://api.github.com/'
    ENDPOINT_URL = 'repos/' if is_repo else 'users/'

    URL = f'{BASE_URL}{ENDPOINT_URL}{name}'

    async with aiohttp.request('GET', URL) as res:
        http_status = res.status

        if http_status != 200:
            content = await res.json()
            return content
            # return http_status

        content = await res.json()
        return content

def image_to_ascii(url):
    ASCII_CHARS = ['B','S','#','&','@','$','%','*','!',':','.']
    img_data = requests.get(url).content
    file_name = url.split('/')[-1].split('?')[0]
    user_img_location = Path(f'{THIS_PATH}/images/{file_name}.png')

    with open(user_img_location, 'wb') as file:
        file.write(img_data)

    with Image.open(user_img_location) as image:
        width, height = image.size
        CORRECT_WIDTH = 0.5 # Fixes aspect ratio and ascii width issues because characters are always taller than wider

        aspect_ratio = height / width
        new_width = 75
        new_height = aspect_ratio * new_width * CORRECT_WIDTH

        pixels = image.resize((new_width, int(new_height))).convert('L').getdata()

        framed_pixels = ''.join([ASCII_CHARS[pixel//25] for pixel in pixels])

        # Gets all the pixels and creates a new array in which
        # each position of the array is all the pixels needed
        # to fill each column of the ascii art
        ascii_text = [framed_pixels[index:index + new_width] for index in range(0, len(framed_pixels), new_width)]

    user_img_location.unlink(missing_ok=True)

    return ascii_text

def fetch_repo(info):
    return {
        'image': info['owner']['avatar_url'],
        'description': info['description'],
        'repo_website': info['homepage'],
        'owner': info['owner'],
        'size': info['size'],
        'stars': info['stargazers_count'],
        'watchers': info['watchers_count'],
        'issues': info['open_issues_count'],
        'forks': info['forks_count'],
        **({'license': info['license']['name']} if info['license'] is not None else {}),
        **({'forked_parent': info['parent']['owner']['html_url']} if info['fork'] else {}),
        # TODO: Languages: like colors in neofetch, with colors and icons
    }

def fetch_user(info):
    return {
        'image': info['avatar_url'],
        'personal_website': info['blog'],
        'username': info['login'],
        'company': info['company'],
        'email': info['email'],
        'location': info['c'],
        'description': info['bio'],
        'public_repos': info['public_repos'],
        'public_gists': info['public_gists'],
        'followers': info['followers'],
        'following': info['following'],
    }

def fetch_organization(info):
    return {
        'image': info['avatar_url'],
        'company_website': info['blog'],
        'username': info['login'],
        'email': info['email'],
        'location': info['location'],
        'description': info['bio'],
        'public_repos': info['public_repos'],
        'public_gists': info['public_gists'],
        'followers': info['followers'],
        'following': info['following'],
    }


def fetch_main(name):
    is_repo = '/' in name

    info = asyncio.run(api_call(is_repo, name))

    generic_info = {
        'name': info['name'],
        **({'type': info['type']} if not is_repo else {'type': 'repo'}),
        'github_url': info['html_url'],
        'created_at': info['created_at'],
        'updated_at': info['updated_at'],
    }

    if is_repo:
        return generic_info | fetch_repo(info)
    elif info['type'] == 'User':
        return generic_info | fetch_user(info)
    elif info['type'] == 'Organization':
        return generic_info | fetch_organization(info)


if __name__ == '__main__':
    # Api call
    name = sys.argv[1]

    print(fetch_main(name))


    # Image ascii convert

    # for line in image_to_ascii('https://avatars.githubusercontent.com/u/110683019?v=4'):
    #     print(colored(line, 'red'))
