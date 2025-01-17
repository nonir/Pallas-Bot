import os
import traceback
import urllib.parse
import requests
from requests_html import HTMLSession, HTML

nudge = ['任命助理', '问候', '闲置', '交谈1', '交谈2', '交谈3', '晋升后交谈1',
         '晋升后交谈2', '信赖提升后交谈1', '信赖提升后交谈2', '信赖提升后交谈3', '戳一下', '信赖触摸']

voices_source = 'resource/voices'


def make_folder(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except FileExistsError:
            pass


class DownloadTools:
    @staticmethod
    def request_file(url, stringify=True):
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) '
                          'AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'
        }
        # noinspection PyBroadException
        try:
            stream = requests.get(url, headers=headers, stream=True)
            if stream.status_code == 200:
                if stringify:
                    return str(stream.content, encoding='utf-8')
                else:
                    return stream.content
        except Exception:
            print(traceback.format_exc())
        return False


class Wiki(DownloadTools):
    def __init__(self):
        self.wiki_url = 'http://prts.wiki'
        self.wiki_session = HTMLSession()

    def get_page(self, url) -> HTML:
        req = self.wiki_session.get(url)
        return getattr(req, 'html')

    def get_voice_urls(self, name):
        html = self.get_page(f'http://prts.wiki/w/{name}/语音记录')
        files = {}
        for item in html.find('a[download]'):
            url = urllib.parse.unquote(item.attrs['href'])
            if not 'http:' in url:
                url = 'http:' + url
            file_name = url.split('/')[-1]
            files[file_name] = url
        return files

    def request_pic_from_wiki(self, name):
        # noinspection PyBroadException
        try:
            html = self.get_page(f'{self.wiki_url}/w/文件:{name}.png')
            file = html.find('#file > a', first=True)
            furl = self.wiki_url + file.attrs['href']
            return self.request_file(furl, stringify=False)
        except Exception:
            print(traceback.format_exc())
        return False

    def request_voice_from_wiki(self, operator, url, filename):
        file = f'{voices_source}/{operator}/{filename}'
        if os.path.exists(file):
            return file

        res = self.request_file(url, stringify=False)
        if res:
            make_folder(f'{voices_source}/{operator}')
            with open(file, mode='wb+') as src:
                src.write(res)
            return file

    def download_operator_voices(self, operator, name):
        try:
            urls = self.get_voice_urls(operator)
            filename = f'{operator}_{name}.wav'
            if filename in urls:
                return self.request_voice_from_wiki(operator, urls[filename], filename)
        except Exception as e:
            print(repr(e))
        return False

    def download_pallas_voices(self):
        try:
            voices = {
                'Pallas': '帕拉斯',
            }
            for en, name in voices.items():
                urls = self.get_voice_urls(name)
                talks = [f'{name}_{item}.wav' for item in nudge]

                for filename in urls:
                    print('Downing', filename)
                    if filename in talks:
                        res = self.request_voice_from_wiki(
                            name, urls[filename], filename)

        except Exception as e:
            print(repr(e))

    @staticmethod
    def voice_exists(operator, name):
        folder = f'{voices_source}/{operator}'
        file = f'{folder}/{operator}_{name}.wav'
        if not os.path.exists(file):
            make_folder(folder)
            return False
        return file
