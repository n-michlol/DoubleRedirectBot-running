import os
import requests
import time
from urllib.parse import urlencode

class DoubleRedirectBot:
    def __init__(self, username, password):
        self.api_url = 'https://www.hamichlol.org.il/w/api.php'
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.login_token = None
        self.edit_token = None

    def login(self):
        params = {
            'action': 'query',
            'meta': 'tokens',
            'type': 'login',
            'format': 'json'
        }
        response = self.session.get(self.api_url, params=params)
        self.login_token = response.json()['query']['tokens']['logintoken']

        login_data = {
            'action': 'login',
            'lgname': self.username,
            'lgpassword': self.password,
            'lgtoken': self.login_token,
            'format': 'json'
        }
        response = self.session.post(self.api_url, data=login_data)
        if response.json()['login']['result'] != 'Success':
            raise Exception('Login failed')

        params = {
            'action': 'query',
            'meta': 'tokens',
            'format': 'json'
        }
        response = self.session.get(self.api_url, params=params)
        self.edit_token = response.json()['query']['tokens']['csrftoken']

    def get_double_redirects(self):
        params = {
            'action': 'query',
            'list': 'querypage',
            'qppage': 'DoubleRedirects',
            'qplimit': 'max',
            'format': 'json'
        }
        response = self.session.get(self.api_url, params=params)
        return response.json()['query']['querypage']['results']

    def get_redirect_target(self, title):
        params = {
            'action': 'query',
            'titles': title,
            'redirects': 'true',
            'format': 'json'
        }
        response = self.session.get(self.api_url, params=params)
        pages = response.json()['query']['pages']
        for page in pages.values():
            if 'missing' not in page:
                return page['title']
        return None

    def edit_page(self, title, new_target):
        params = {
            'action': 'edit',
            'title': title,
            'text': f'#הפניה [[{new_target}]]',
            'summary': 'בוט: תיקון הפניה כפולה',
            'bot': 'true',
            'token': self.edit_token,
            'format': 'json'
        }
        response = self.session.post(self.api_url, data=params)
        return response.json()

    def fix_double_redirects(self):
        self.login()
        double_redirects = self.get_double_redirects()
        
        for redirect in double_redirects:
            try:
                title = redirect['title']
                print(f'מטפל בדף: {title}')
                
                final_target = self.get_redirect_target(title)
                if final_target:
                    result = self.edit_page(title, final_target)
                    if 'error' in result:
                        print(f'שגיאה בעריכת {title}: {result["error"]}')
                    else:
                        print(f'תוקן בהצלחה: {title} -> {final_target}')
                
                time.sleep(0)
                
            except Exception as e:
                print(f'שגיאה בטיפול בדף {title}: {str(e)}')
                continue

if __name__ == '__main__':
    username = 'נריה בוט@הפניות-כפולות'
    password = os.getenv('BOT_PASSWORD')
    
    bot = DoubleRedirectBot(username, password)
    bot.fix_double_redirects()