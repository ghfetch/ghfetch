#!/bin/python3
from json import load
from argparse import ArgumentParser
from requests import get
from math import floor, ceil
from pathlib import Path
from re import search, sub
from time import sleep

# requirements
from asyncio import run
from aiohttp import request
from rich.console import Console
from PIL import Image

HOME_PATH = Path().home()
THIS_PATH = Path(__file__).resolve().parent.resolve()
UNICODE_BLOCK_CHAR = '\u2588'
LANGUAGES_BLOCK_CHAR = '\u2580'
RESULTS_LIMIT = 5
PARSER_ERRORS = {
    'missing_target': 'At least one target must be provided',
}
HTTP_ERRORS = {
    401: "You don't have access to this resource",
    403: "This works through the Github API and looks like you've reached the hourly limit.\nTake advantage of this and go to make yourself a cup of coffee \u2615",
    404: "The passed parameter it's not an existing User / Company / repo",
    408: "Time out. Please try again later",
    409: "Conflict. This happends randomly with Github API, please try again later",
}
MESSAGES_TO_USER = {
    'over_results_limit': 'This command will print a total of {} repositories, this will consume a lot of your api credits and even may consume it all without being able to print everything. Do you want to execute it anyway? (y/N) '
}

def startup():
    tmp_folder = Path(f'{HOME_PATH}/.ghfetch/tmp')
    Path(tmp_folder).mkdir(parents=True, exist_ok=True)

def create_parser():
    parser = ArgumentParser(
        prog='ghfetch',
        description='A nice way to display CLI Github user / repo / organization info inspired in neofetch',
    )
    parser.add_argument('target', help='the name of the user/org/repo to fetch', type=str, nargs='*')
    parser.add_argument('-t', '--api-token', help='the GitHub API token', type=str)
    parser.add_argument('-x', '--execute', help='Automatically print every repo fetched', action='store_true')
    parser.add_argument('-y', '--skip', help='Automatically accept every confirmation', action='store_true')

    # TODO: add version parameter, recursive display of repos and rate limit info
    # parser.add_argument('-v', '--version', help='displays the current version of ghfetch', action='version', version='')
    # parser.add_argument('-r', '--reverse', help='reverse the output of multiple repos', action='store_true')
    # parser.add_argument('-l', '--limit', help='displays info about the rate limit', action='store_true')

    global ARGS
    ARGS = vars(parser.parse_args())

    return parser

async def api_call(is_repo, name):
    BASE_URL = 'https://api.github.com/'
    ENDPOINT_URL = 'repos/' if is_repo else 'users/'
    URL = f'{BASE_URL}{ENDPOINT_URL}{name}'
    API_TOKEN = ARGS['api_token']
    HEADERS = { 'Authorization': f'Bearer {API_TOKEN}', } if API_TOKEN else {}

    async with request(method='GET', url=URL, headers=HEADERS) as res:
        http_status = res.status

        if http_status != 200:
            return http_status

        content = await res.json()
        return content

def api_rate_exceeded(code):
    if not isinstance(code, int):
        return False

    print(HTTP_ERRORS[code])

    return True

async def get_commits_number(owner, repo):
    URL = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=1"
    API_TOKEN = ARGS['api_token']
    HEADERS = { 'Authorization': f'Bearer {API_TOKEN}', } if API_TOKEN else {}

    async with request('GET', url=URL, headers=HEADERS) as res:
        http_status = res.status

        if http_status != 200:
            return http_status

        commits = res.headers['Link'].split(';')[1].split(',')[1].split('=')[2][:-1]
        return {'commits': commits,}

async def get_repos_number(user):
    URL = f"https://api.github.com/users/{user}/repos?per_page=1"
    API_TOKEN = ARGS['api_token']
    HEADERS = { 'Authorization': f'Bearer {API_TOKEN}', } if API_TOKEN else {}

    async with request('GET', url=URL, headers=HEADERS) as res:
        http_status = res.status

        if http_status != 200:
            return http_status

        repos = res.headers['Link'].split(';')[1].split(',')[1].split('=')[2][:-1]
        return int(repos)

async def get_repos(user, url=None):
    repos = []

    if url == None:
        url = f"https://api.github.com/users/{user}/repos?type=public&per_page=100"

    API_TOKEN = ARGS['api_token']
    HEADERS = { 'Authorization': f'Bearer {API_TOKEN}', } if API_TOKEN else {}

    async with request('GET', url=url, headers=HEADERS) as res:
        http_status = res.status

        if http_status != 200:
            return http_status

        content = await res.json()
        # print(content)
        for repo in content:
            repos.append(repo["full_name"])

        if "Link" in res.headers and search(r'; rel="next"', res.headers['Link']):
            url = sub(r'.*<(.*)>; rel="next".*', r'\1', res.headers['Link'])

            repos_continuation = await get_repos(user, url=url)

            if isinstance(repos_continuation, int):
                return repos_continuation

            repos.extend(repos_continuation)

        return repos

async def create_languages_stat(url):
    API_TOKEN = ARGS['api_token']
    HEADERS = { 'Authorization': f'Bearer {API_TOKEN}', } if API_TOKEN else {}

    async with request('GET', url, headers=HEADERS) as res:
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
        'languages': run(create_languages_stat(info['languages_url'])),
    }

def fetch_user(info):
    return {'company': info['company'],}

def fetch_main(name):
    is_repo = '/' in name

    info = run(api_call(is_repo, name))

    if isinstance(info, int):
        if info == 409:
            sleep(2)
            return fetch_main(name)

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
        commits = run(get_commits_number(*name.split('/')))
        if isinstance(commits, int):
            return commits

        return correct_formatting(generic_info | fetch_repo(info)) | commits
    elif info['type'] == 'User':
        return correct_formatting(generic_info | fetch_user(info))
    elif info['type'] == 'Organization':
        return correct_formatting(generic_info)

def rgb_to_hex(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

def image_to_unicode(url):
    IMAGE_WIDTH = 35
    COLORED_CHAR_LENGTH = 20 # Number of characters needed in raw to print a colored unicode character [#012345]█[/#012345]

    file_name = url.split('/')[-1].split('?')[0]
    user_img_location = Path(f'{HOME_PATH}/.ghfetch/tmp/{file_name}.png')

    img_data = get(url).content

    with open(user_img_location, 'wb') as file:
        file.write(img_data)

    # Convert image to RGB in case the image is .gif
    Image.open(user_img_location).convert('RGB').save(user_img_location)

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

        unicode_per_rows.append(f"{' ' * IMAGE_WIDTH}\t")
        return unicode_per_rows

def print_output(fetched_info):
    COLOR_TITLE = '#068FFF'
    COLOR_TEXT = '#EDEDED'
    COLOR_ARCHIVED = '#F48024'

    def title(text, color = COLOR_TITLE):
        return f'[{color}]{text}[/{color}]'

    def text(text):
        return f'[{COLOR_TEXT}]{text}[/{COLOR_TEXT}]'

    def archived(text):
        return f'[{COLOR_ARCHIVED}]{text}[/{COLOR_ARCHIVED}]'

    def language(color):
        return f'[{color}]{LANGUAGES_BLOCK_CHAR}[/{color}]'

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
        output[n] += archived('[Archived] ') if fetched_info['archived'] else ''
        output[n] += title(f'{fetched_info["owner"]}/{fetched_info["name"]}')
        output[n + 1] += text('-' * (len(f'{fetched_info["owner"]}/{fetched_info["name"]}') if not fetched_info['archived'] else len(f'{fetched_info["owner"]}/{fetched_info["name"]}') + len('[Archived] ')))

        if 'forked_parent' in fetched_info:
            output[n + 2] += f'{title("Forked from")}: {text(fetched_info["forked_parent"])}'
            n += 1

        output[n + 2] += f'{title("Owner")}: {text(fetched_info["owner"])}'
        output[n + 3] += f'{title("Description")}: {text(fetched_info["description"][:50] + "..." if (fetched_info["description"] is not None) and (len(fetched_info["description"]) > 50) else fetched_info["description"])}'
        output[n + 4] += f'{title("License")}: {text(fetched_info["license"])}'
        output[n + 5] += f'{title("Commits")}: {text(fetched_info["commits"])}'
        output[n + 6] += f'{title("Stars")}: {text(fetched_info["stars"])}'
        output[n + 7] += f'{title("Watchers")}: {text(fetched_info["watchers"])}'
        output[n + 8] += f'{title("Forks")}: {text(fetched_info["forks"])}'
        output[n + 9] += f'{title("Joined at")}: {text(fetched_info["created_at"])}'
        output[n + 10] += f'{title("Github URL")}: {text(fetched_info["github_url"])}'

        def get_lang_color(dict, lang):
            try:
                return (
                    dict.get(lang)
                        .get('color') or COLOR_TEXT
                )
            except:
                return COLOR_TEXT

        with open(Path(f'{THIS_PATH}/data/language-colors.json'), 'r') as languages:
            languages = load(languages)

            if len(fetched_info["languages"].items()) > 2:
                output[n + 13] += ', '.join([(f"{title(k, get_lang_color(languages, k))}: {text(v)}") for k, v in fetched_info["languages"].items()][:2]) + ' '
                output[n + 14] += ', '.join([(f"{title(k, get_lang_color(languages, k))}: {text(v)}") for k, v in fetched_info["languages"].items()][2:])
            else:
                output[n + 13] += ', '.join([(f"{title(k, get_lang_color(languages, k))}: {text(v)}") for k, v in fetched_info["languages"].items()])


            LENGTH_BAR_DIVIDER = 3

            for lang, percentage in fetched_info['languages'].items():
                percentage = float(percentage[:-1])
                color = get_lang_color(languages, lang)


                cols = ceil(percentage / LENGTH_BAR_DIVIDER)
                for _ in range(cols):
                    output[n + 12] += f'{language(color)}'

    for line in output:
        Console().print(line, overflow='crop', soft_wrap=True)


def main():
    startup()
    parser = create_parser()

    target = ARGS['target']

    if len(target) < 1:
        parser.error(PARSER_ERRORS['missing_target'])

    # API call
    try:
        for t in target:
            if t.endswith("/*"):
                if ARGS['execute']:
                    if not ARGS['skip']:
                        repos_number =  run(get_repos_number(t.split("/")[0]))

                        if repos_number > RESULTS_LIMIT and input(MESSAGES_TO_USER["over_results_limit"].format(repos_number)).lower() != "y":
                            return

                    repos = run(get_repos(t.split("/")[0]))

                    if api_rate_exceeded(repos):
                        return repos

                    for repo in repos:
                        fetched_info = fetch_main(repo)
                        if api_rate_exceeded(fetched_info):
                            return

                        print_output(fetched_info)
                else:
                    repos = run(get_repos(t.split("/")[0]))

                    if api_rate_exceeded(repos):
                        return repos

                    for repo in repos:
                        Console().print(repo, overflow='crop', soft_wrap=True)

            else:
                fetched_info = fetch_main(t)
                if api_rate_exceeded(fetched_info):
                    return

                print_output(fetched_info)
    except TimeoutError:
        print(HTTP_ERRORS[408])

if __name__ == '__main__':
    main()