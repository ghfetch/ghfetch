import sys
import requests
from pathlib import Path

# requirements
import asyncio
import aiohttp
from rich import print
from PIL import Image

THIS_PATH = Path(__file__).parent.resolve()
IMAGE_WIDTH = 40

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

def fetch_repo(info):
    return {
        'owner': info['owner'],
        'stars': info['stargazers_count'],
        'watchers': info['watchers_count'],
        'forks': info['forks_count'],
        'archived': info['archived'],
        'disabled': info['disabled'],
        **({'license': info['license']['name']} if info['license'] is not None else {}),
        **({'forked_parent': info['parent']['owner']['html_url']} if info['fork'] else {}),
        # 'size': info['size'],
        # 'issues': info['open_issues_count'],

        # TODO: Languages: like colors in neofetch, with colors and icons, max 4 lines of height
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

def rgb_to_hex(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

def image_to_unicode(url):
    UNICODE_BLOCK_CHAR = '\u2588'

    file_name = url.split('/')[-1].split('?')[0]
    user_img_location = Path(f'{THIS_PATH}/images/{file_name}.png')

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

        unicode_text = ''
        for index, character in enumerate(pixel_values):
            # Retrieve all RGB values and discard alpha channel (rich doesn't support alpha channel)
            r, g, b = character if len(character) == 3 else character[:-1]

            # Adds new line when the index reaches the width limit
            if (index != 0) and (index % IMAGE_WIDTH == 0):
                unicode_text += '\n'

            hex = rgb_to_hex(r, g, b)

            unicode_text += f'[{hex}]{UNICODE_BLOCK_CHAR}[/{hex}]'

        user_img_location.unlink(missing_ok=True)

        return unicode_text

def output_generator(fetched_info):
    COLORED_CHAR_LENGTH = 20

    fetched_info['image'] = image_to_unicode(fetched_info['image'])

    formatted_output = ''
    for index, char in enumerate(fetched_info['image']):
        formatted_output += char

        # Checks if the width limit is reached to append text
        if index / COLORED_CHAR_LENGTH == IMAGE_WIDTH:
            formatted_output = formatted_output.rstrip() + '\t\tprueba\n'

    return formatted_output


def main():
    # API call
    if len(sys.argv) == 1:
        return print('One argument must be provided')

    name = sys.argv[1]

    fetched_info = fetch_main(name)

    print(output_generator(fetched_info))

    # In case rate limit is exceeded:
    # https://avatars.githubusercontent.com/u/110683019?v=4
    # https://avatars.githubusercontent.com/u/1024025?v=4
    # https://avatars.githubusercontent.com/u/90156486?v=4


if __name__ == '__main__':
    main()