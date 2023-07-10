import sys
import requests
from pathlib import Path

# requirements
import asyncio
import aiohttp
from rich import print
from PIL import Image

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
    IMAGE_WIDTH = 35
    COLORED_CHAR_LENGTH = 20 # Number of characters needed in raw to print a colored unicode character [#012345]█[/#012345]
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

        return unicode_per_rows

def print_output(fetched_info):
    COLOR_TITLE = '#068FFF'
    COLOR_TEXT = '#EEEEEE'
    output = image_to_unicode(fetched_info['image'])

    if fetched_info['type'] == 'User':
        output[1] += f'[{COLOR_TITLE}]{fetched_info["type"]}: [/{COLOR_TITLE}][{COLOR_TEXT}]{fetched_info["username"]}[/{COLOR_TEXT}]'
        output[2] += f'[{COLOR_TEXT}]----------------------------------[/{COLOR_TEXT}]'
        output[3] += f'[{COLOR_TITLE}]Name: [/{COLOR_TITLE}][{COLOR_TEXT}]{fetched_info["name"]}[/{COLOR_TEXT}]'
        output[4] += f'[{COLOR_TITLE}]Description: [/{COLOR_TITLE}][{COLOR_TEXT}]{fetched_info["description"]}[/{COLOR_TEXT}]'
        output[5] += f'[{COLOR_TITLE}]Location: [/{COLOR_TITLE}][{COLOR_TEXT}]{fetched_info["location"]}[/{COLOR_TEXT}]'
        output[6] += f'[{COLOR_TITLE}]E-mail: [/{COLOR_TITLE}][{COLOR_TEXT}]{fetched_info["email"]}[/{COLOR_TEXT}]'
        output[7] += f'[{COLOR_TITLE}]Personal Website: [/{COLOR_TITLE}][{COLOR_TEXT}]{fetched_info["website"]}[/{COLOR_TEXT}]'
        output[8] += f'[{COLOR_TITLE}]Following: [/{COLOR_TITLE}][{COLOR_TEXT}]{fetched_info["following"]}[/{COLOR_TEXT}]'
        output[9] += f'[{COLOR_TITLE}]Followers: [/{COLOR_TITLE}][{COLOR_TEXT}]{fetched_info["followers"]}[/{COLOR_TEXT}]'
        output[10] += f'[{COLOR_TITLE}]Public repos: [/{COLOR_TITLE}][{COLOR_TEXT}]{fetched_info["public_repos"]}[/{COLOR_TEXT}]'
        output[11] += f'[{COLOR_TITLE}]Public gists: [/{COLOR_TITLE}][{COLOR_TEXT}]{fetched_info["public_gists"]}[/{COLOR_TEXT}]'
        output[12] += f'[{COLOR_TITLE}]Joined at: [/{COLOR_TITLE}][{COLOR_TEXT}]{fetched_info["created_at"]}[/{COLOR_TEXT}]'
        output[13] += f'[{COLOR_TITLE}]Github URL: [/{COLOR_TITLE}][{COLOR_TEXT}]{fetched_info["github_url"]}[/{COLOR_TEXT}]'

    elif fetched_info['type'] == 'Organization':
        pass

    elif fetched_info['type'] == 'Repo':
        pass


    for line in output:
        print(line)


def main():
    # API call
    if len(sys.argv) == 1:
        return print('One argument must be provided')

    name = sys.argv[1]

    fetched_info = fetch_main(name)

    print_output(fetched_info)

    # In case rate limit is exceeded:
    # https://avatars.githubusercontent.com/u/110683019?v=4
    # https://avatars.githubusercontent.com/u/1024025?v=4
    # https://avatars.githubusercontent.com/u/90156486?v=4


if __name__ == '__main__':
    main()