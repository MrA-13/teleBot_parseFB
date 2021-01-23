import requests
from bs4 import BeautifulSoup
from time import time
from db import DB
import os


class FaceBookBot():
    def __init__(self):
        self.session = requests.Session()
        self.db = DB()

    def __parse_html(self, request_url):
        parsed_html = self.session.get(request_url)
        return parsed_html

    def __serialized_text_from_post(self, text):
        text = text.split('<div>')[1].split('</div>')[0]
        text = text.replace('</span><wbr/><span class="word_break"></span>', '')
        text = text.replace('<span>', '')
        return text



    def __post_content(self, id_):
        REQUEST_URL = f'https://mbasic.facebook.com/story.php?story_fbid={id_}&id=102843171685721'
        REQUEST_URL_FOR_PHOTO = ''
        PATH_TO_SRC_DIR = os.path.join('src', id_)

        content_from_page = self.__parse_html(REQUEST_URL).content.decode('utf-8').split('kBSvm2-_9bR.png')[0].encode()

        soup = BeautifulSoup(content_from_page, "html.parser")

        post_content_raw_text = str(soup.find_all('div', {"class": "bx"})[0])
        post_content_text = self.__serialized_text_from_post(post_content_raw_text)

        post_content_photo = []

        # Download media from post
        try:
            # Get all links with photo from current post
            temp =set()
            photo = soup.find_all('a')
            for i in photo:
                if 'photo' in i['href']:
                    temp.add(i['href'])

            temp = list(temp)

            if os.path.isdir(PATH_TO_SRC_DIR) is not True:
                os.mkdir(PATH_TO_SRC_DIR)
            # Download photo from post    
            for url in temp:
                REQUEST_URL_FOR_PHOTO = "https://mbasic.facebook.com/"+url
                NAME_PHOTO = os.path.join(PATH_TO_SRC_DIR, ''.join(str(time()).split('.')) + '.png')
                soup = BeautifulSoup(self.session.get(REQUEST_URL_FOR_PHOTO).content, "html.parser")

                post_content_photo.append(NAME_PHOTO)
                r = requests.get(soup.find_all('meta')[4].get('content'), stream=True)
                if r.status_code == 200:
                    with open(NAME_PHOTO, 'wb') as f:
                        for chunk in r.iter_content(1024):
                            f.write(chunk)    

        except Exception as exept:
            print(exept)


        return post_content_text, post_content_photo



    def __get_posts_ids(self):
        REQUEST_URL = "https://mbasic.facebook.com/Our.Donbass.Press"

        soup = BeautifulSoup(self.__parse_html(REQUEST_URL).content, "html.parser")
        content = soup.find_all('a')
        post_ids = []
        for lines in content:
            url = str(lines.get('href'))
            if "story.php?story_fbid=" in url:
                post_ids.append(url.split("story.php?story_fbid=")[1].split("&id=102843171685721")[0])
        return list(set(post_ids))


    def get_new_posts(self):
        posts_ids = self.db.check_new_post(self.__get_posts_ids())
        list_of_posts_content = []
        for id_ in posts_ids:
            text, photo = self.__post_content(id_)
            list_of_posts_content.append({'text': text, 'photo': photo})
        return list_of_posts_content
