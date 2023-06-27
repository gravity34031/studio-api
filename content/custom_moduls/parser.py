import requests
from io import BytesIO
from django.core.files.images import ImageFile



def parse(url):
    response = requests.get(url)
    if response.status_code != requests.codes.ok:
        return None
    return response

def get_img_from_url(url):
    image_response = parse(url)
    # if there's response error
    if image_response is None:
        return None
    fp = BytesIO()
    fp.write(image_response.content) # byte image
    file_name = url.split("/")[-2]
    file = ImageFile(fp, file_name)
    return file


def get_oembed_data(link):
    oembed_raw_url = 'https://www.youtube.com/oembed?url='
    video_url = link
    # full oembed url
    url = oembed_raw_url + video_url
    
    oembed_response = parse(url)
    # if there's response error
    if oembed_response is None:
        return {}

    oembed_json = oembed_response.json()
    title = oembed_json.get('title')

    # get image
    image_url = oembed_json.get('thumbnail_url')
    image = get_img_from_url(image_url)

    return {'title': title, 'image': image}