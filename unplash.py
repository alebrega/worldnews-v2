from unsplash.api import Api
from unsplash.auth import Auth
import json

client_id = "2403a0faa985ce48bf64062b0a199f4a7a670378874ecfeee49c0fc22c44e38a"
client_secret = "64d29962a28580505209c54bebb116be7dac9918d9787556f4c18c7690ac817d"
redirect_uri = ""
code = ""

auth = Auth(client_id, client_secret, redirect_uri, code=code)

api = Api(auth)
# api.user.me()


import uuid
import requests


def get_pics(query, num_imgs):
    urls = []
    try:
        photos = api.search.photos(
            query=query, page=0, per_page=num_imgs)
        for photo in photos['results']:
            photo_get = api.photo.get(photo.id)
            urls.append(photo_get.urls.raw)
    except Exception as e:
        print('Some errors trying to save the image from remote host: ' + str(e))
    return urls
