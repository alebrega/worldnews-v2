from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import taxonomies

from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts
import uuid
import requests


# wp = Client('https://www.thestartupfounder.com/xmlrpc.php',
#           'alebrega', 'JSoWLaPm*b*MZm9qG$')


class Wordpress:
    client = None

    def __init__(self, url='https://www.thestartupfounder.com/xmlrpc.php', user='alebrega', password='JSoWLaPm*b*MZm9qG$'):
        self.client = Client(url, user, password)

    def publish(self, title, content, image_url, keywords):

        try:
            post = WordPressPost()
            post.title = title
            post.comment_status = 'approve'
            post.content = content
            post.status = 'draft'
            attachment_id = self.upload_pic(image_url)
            post.thumbnail = attachment_id
            post.terms_names = {
                'post_tag': keywords,
                'category': ['To review']
            }
            self.client.call(NewPost(post))
        except Exception as e:
            print('Some errors trying to publish to Wordpress (Wordpress.py): ' + str(e))
            return False
        return True

    def get_tags(self):
        categories = self.client.call(taxonomies.GetTerms('category'))
        post_tags = self.client.call(taxonomies.GetTerms('post_tag'))
        tag_list = [tag.name
                    for tag in post_tags]
        categories_list = [category.name
                           for category in categories]
        tag_list.extend(categories_list)
        return tag_list

    def upload_pic(self, img_url):
        try:
            img_data = requests.get(img_url).content
            img_name = './uploads/'+str(uuid.uuid4())+'.jpg'
            with open(img_name, 'wb') as handler:
                handler.write(img_data)

            filename = img_name

            # prepare metadata
            data = {
                'name': img_name,
                'type': 'image/jpeg',  # mimetype
            }

            # read the binary file and let the XMLRPC library encode it into base64
            with open(filename, 'rb') as img:
                data['bits'] = xmlrpc_client.Binary(img.read())

            response = self.client.call(media.UploadFile(data))
            attachment_id = response['id']
        except Exception as e:
            print(
                'Some errors trying to save the image from remote host: ' + str(img_url))
            attachment_id = ""

        return attachment_id
