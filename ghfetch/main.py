#!/bin/python

import sys
import requests
from math import floor
from pathlib import Path

# requirements
import asyncio
import aiohttp
from rich import print
from PIL import Image

HOME_PATH = Path().home()
THIS_PATH = Path(__file__).parent.resolve()

def startup():
    tmp_folder = Path(f'{HOME_PATH}/.ghfetch/tmp')

    Path(tmp_folder).mkdir(parents=True, exist_ok=True)

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

async def create_languages_stat(url):
    async with aiohttp.request('GET', url) as res:
        http_status = res.status

        if http_status != 200:
            return http_status

        languages = await res.json()

    if len(languages) > 4:
        # Get the first three values and add a fourth one that sums the rest
        languages = dict(list(languages.items())[:3]) | {'Other': sum(list(languages.values())[3:])}

    TOTAL = sum(languages.values())

    return {k:f'{floor((v/TOTAL)*1000)/10}%' for k,v in languages.items()}

def fetch_repo(info):
    return {
        'owner': info['owner']['login'],
        'stars': info['stargazers_count'],
        'watchers': info['watchers_count'],
        'forks': info['forks_count'],
        'archived': info['archived'],
        **({'license': info['license']['name']} if info['license'] is not None else {'license': None}),
        **({'forked_parent': info['parent']['html_url']} if info['fork'] else {}),
        'languages': asyncio.run(create_languages_stat(info['languages_url'])),
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
        'created_at': info['created_at'][:10],
    }

    def correct_formatting(dict):
        return {k:v if v != '' else None for k, v in dict.items()}

    if is_repo:
        return correct_formatting(generic_info | fetch_repo(info))
    elif info['type'] == 'User':
        return correct_formatting(generic_info | fetch_user(info))
    elif info['type'] == 'Organization':
        return correct_formatting(generic_info)

def rgb_to_hex(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

def image_to_unicode(url):
    IMAGE_WIDTH = 35
    COLORED_CHAR_LENGTH = 20 # Number of characters needed in raw to print a colored unicode character [#012345]█[/#012345]
    UNICODE_BLOCK_CHAR = '\u2588'

    file_name = url.split('/')[-1].split('?')[0]
    user_img_location = Path(f'{HOME_PATH}/.ghfetch/tmp/{file_name}.png')

    img_data = requests.get(url).content

    with open(user_img_location, 'wb') as file:
        file.write(img_data)

    with Image.open(user_img_location) as image:
        MULTIPLIER = 0.45 # Used to fix the image height because the characters are taller

        # Get initial width and height
        width, height = image.size
        aspect_ratio = height / width

        # Fix the new height according to the aspect ratio (1:1)
        IMAGE_HEIGHT = int(aspect_ratio * IMAGE_WIDTH * MULTIPLIER)

        pixel_values = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT)).getdata()

        line = ''
        unicode_per_rows = []

        for char in pixel_values:
            # Retrieve all RGB values and discard alpha channel (rich doesn't support alpha channel)
            r, g, b = char if len(char) == 3 else char[:-1]
            hex = rgb_to_hex(r, g, b)

            line += f'[{hex}]{UNICODE_BLOCK_CHAR}[/{hex}]'

            if len(line) == COLORED_CHAR_LENGTH * IMAGE_WIDTH:
                unicode_per_rows.append(f'{line}\t')
                line = ''

        Path.unlink(user_img_location, missing_ok=True)

        return unicode_per_rows

def print_output(fetched_info):
    COLOR_TITLE = '#068FFF'
    COLOR_TEXT = '#EEEEEE'
    COLOR_ARCHIVED = '#F48024'

    def title(text):
        return f'[{COLOR_TITLE}]{text}[/{COLOR_TITLE}]'

    def text(text):
        return f'[{COLOR_TEXT}]{text}[/{COLOR_TEXT}]'

    def archived(text):
        return f'[{COLOR_ARCHIVED}]{text}[/{COLOR_ARCHIVED}]'

    n = 0 # Where n is the row where to start

    output = image_to_unicode(fetched_info['image'])

    if fetched_info['type'] == 'User':
        output[n]      += title(fetched_info["username"])
        output[n + 1]  += text('-' * (len(fetched_info['username'])))
        output[n + 2]  += f'{title("Name")}: {text(fetched_info["name"])}'
        output[n + 3]  += f'{title("Description")}: {text(fetched_info["description"][:50] + "..." if (fetched_info["description"] is not None) and (len(fetched_info["description"]) > 50) else fetched_info["description"])}'
        output[n + 4]  += f'{title("Location")}: {text(fetched_info["location"])}'
        output[n + 5]  += f'{title("Email")}: {text(fetched_info["email"])}'
        output[n + 6]  += f'{title("Company")}: {text(fetched_info["company"])}'
        output[n + 7]  += f'{title("Personal Website")}: {text(fetched_info["website"])}'
        output[n + 8]  += f'{title("Following")}: {text(fetched_info["following"])}'
        output[n + 9]  += f'{title("Followers")}: {text(fetched_info["followers"])}'
        output[n + 10] += f'{title("Public repos")}: {text(fetched_info["public_repos"])}'
        output[n + 11] += f'{title("Public gists")}: {text(fetched_info["public_gists"])}'
        output[n + 12] += f'{title("Joined at")}: {text(fetched_info["created_at"])}'
        output[n + 13] += f'{title("Github URL")}: {text(fetched_info["github_url"])}'

    elif fetched_info['type'] == 'Organization':
        output[n + 1]  += title(fetched_info["username"])
        output[n + 2]  += text('-' * (len(fetched_info['username'])))
        output[n + 3]  += f'{title("Name")}: {text(fetched_info["name"])}'
        output[n + 4]  += f'{title("Description")}: {text(fetched_info["description"][:50] + "..." if (fetched_info["description"] is not None) and (len(fetched_info["description"]) > 50) else fetched_info["description"])}'
        output[n + 5]  += f'{title("Location")}: {text(fetched_info["location"])}'
        output[n + 6]  += f'{title("E-mail")}: {text(fetched_info["email"])}'
        output[n + 7]  += f'{title("Personal Website")}: {text(fetched_info["website"])}'
        output[n + 8]  += f'{title("Following")}: {text(fetched_info["following"])}'
        output[n + 9]  += f'{title("Followers")}: {text(fetched_info["followers"])}'
        output[n + 10] += f'{title("Public repos")}:{text(fetched_info["public_repos"])}'
        output[n + 11] += f'{title("Public gists")}:{text(fetched_info["public_gists"])}'
        output[n + 12] += f'{title("Joined at")}: {text(fetched_info["created_at"])}'
        output[n + 13] += f'{title("Github URL")}: {text(fetched_info["github_url"])}'

    elif fetched_info['type'] == 'Repo':
        output[n + 1] += archived('[Archived] ') if fetched_info['archived'] else ''
        output[n + 1] += title(f'{fetched_info["owner"]}/{fetched_info["name"]}')
        output[n + 2] += text('-' * (len(f'{fetched_info["owner"]}/{fetched_info["name"]}') if not fetched_info['archived'] else len(f'{fetched_info["owner"]}/{fetched_info["name"]}') + len('[Archived] ')))

        if 'forked_parent' in fetched_info:
            output[n + 3] += f'{title("Forked from")}: {text(fetched_info["forked_parent"])}'
            n += 1

        output[n + 3] += f'{title("Owner")}: {text(fetched_info["owner"])}'
        output[n + 4] += f'{title("Description")}: {text(fetched_info["description"][:50] + "..." if (fetched_info["description"] is not None) and (len(fetched_info["description"]) > 50) else fetched_info["description"])}'
        output[n + 5] += f'{title("License")}: {text(fetched_info["license"])}'
        output[n + 6] += f'{title("Stars")}: {text(fetched_info["stars"])}'
        output[n + 7] += f'{title("Watchers")}: {text(fetched_info["watchers"])}'
        output[n + 8] += f'{title("Forks")}: {text(fetched_info["forks"])}'
        output[n + 9] += f'{title("Joined at")}: {text(fetched_info["created_at"])}'
        output[n + 10] += f'{title("Github URL")}: {text(fetched_info["github_url"])}'
        output[n + 11] += f'{title("Langs")}: ' if len(fetched_info['languages'].items()) > 0 else ''

        if len(fetched_info["languages"].items()) > 2:
            output[n + 12] += f'{", ".join([(f"{title(k)}: {text(v)}") for k, v in fetched_info["languages"].items()][:2])}, '
            output[n + 13] += ', '.join([(f"{title(k)}: {text(v)}") for k, v in fetched_info["languages"].items()][2:])
        else:
            output[n + 12] += ', '.join([(f"{title(k)}: {text(v)}") for k, v in fetched_info["languages"].items()])

    for line in output:
        print(line)


def main():
    startup()

    if len(sys.argv) != 2:
        return print('Only one argument must be provided')

    name = sys.argv[1]

    # API call
    fetched_info = fetch_main(name)
    if fetched_info == 401:
        return print("You don't have access to this")
    if fetched_info == 404:
        return print("The passed parameter it's not an existing User / Company / repo")
    if fetched_info == 429:
        return print("This works through the Github API and looks like you've reached the hourly limit.\nTake advantage of this and go to make yourself a cup of coffee\u2615")

    print_output(fetched_info)

if __name__ == '__main__':
    main()