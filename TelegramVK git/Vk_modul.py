import requests
from config import VK_SERVIS_KEY
class Post:
    def __init__(self, owner, text, photo):
        self.owner = owner
        self.text = text
        self.photo = photo

def get_post_vk(domain_group):
    #Отправка запроса постов
    version = 5.199
    count = 5
    offset = 0
    respronce = requests.get('https://api.vk.com/method/wall.get',
                                 params={
                                     'access_token': VK_SERVIS_KEY,
                                     'v': version,
                                     'domain': domain_group,
                                     'count': count,
                                     'offset': offset
                                 }
                             )
    data = respronce.json()

    #Получаем посты из вк
    posts = data['response']['items']

    try:
        return posts
    except Exception as e:
        print(type(e).__name__)
