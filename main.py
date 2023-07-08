import os
import json
import requests
from pathlib import Path

# requirements
import asyncio
import aiohttp
from PIL import Image
from termcolor import colored

THIS_PATH = Path(__file__).parent.resolve()
ASCII_CHARS = ["B","S","#","&","@","$","%","*","!",":","."]

async def api_call():
    BASE_URL = 'https://api.github.com/'

    async with aiohttp.request('GET', BASE_URL) as res:
        http_status = res.status

        if http_status != 200:
            return http_status

        content = await res.json()
        return content

def image_to_ascii(url):
    img_data = requests.get(url).content
    file_name = url.split('/')[-1].split('?')[0]
    user_img_location = Path(f'{THIS_PATH}/images/{file_name}.png')

    # TODO: check if content is the same, don't download
    with open(user_img_location, 'wb') as file:
        file.write(img_data)

    with Image.open(user_img_location) as image:
        width, height = image.size
        CORRECT_WIDTH = 0.5 # Fixes aspect ratio and ascii width issues because characters are always taller than wider

        aspect_ratio = height / width
        new_width = 75
        new_height = aspect_ratio * new_width * CORRECT_WIDTH

        pixels = image.resize((new_width, int(new_height))).convert('L').getdata()

        # TODO: refactor
        new_pixels = [ASCII_CHARS[pixel//25] for pixel in pixels]
        new_pixels = ''.join(new_pixels)

        # Gets all the pixels and creates a new array in which
        # each position of the array is all the pixels needed
        # to fill each column of the ascii art
        ascii_text = [new_pixels[index:index + new_width] for index in range(0, len(new_pixels), new_width)]

    user_img_location.unlink(missing_ok=True)

    return ascii_text


def main():
    for line in image_to_ascii('https://avatars.githubusercontent.com/u/110683019?v=4'):
        print(colored(line, 'red'))

    print(asyncio.run(api_call()))


if __name__ == '__main__':
    main()