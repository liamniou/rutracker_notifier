# -*- coding: utf-8 -*-
from sqliter import SQLighter
from config import database_name
from bs4 import BeautifulSoup
import requests
import urllib.request as URLL
import http


class RSSchecker:

    __opener = None

    @staticmethod
    def check_updates():
        db = SQLighter(database_name)
        topics_data = db.get_all_data_from_topics()
        return topics_data

    @staticmethod
    def get_html_of_url(url):
        page_html = (requests.get(url)).text
        return BeautifulSoup(page_html, 'html.parser')

    def find_rss_link(self, topic_url):
        topic_page_soup = self.get_html_of_url(topic_url)
        relative_profile_link = topic_page_soup.find('a', attrs={'class': 'txtb'}, href=True)['href']
        profile_id = relative_profile_link.split('=')[-1]
        # auth = session.get('https://rutracker.org/forum/feed.php')
        if self.__opener is None:
            self.__login()

        data = 'mode=get_feed_url&type=u&id={0}'.format(profile_id)
        response = self.__opener.open('https://rutracker.org/forum/feed.php', data=data.encode("ascii")).read()

        return response

    def __login(self):
        cookies = http.cookiejar.FileCookieJar("cookies")
        opener = URLL.build_opener(URLL.HTTPCookieProcessor(cookies))
        opener.open("https://rutracker.org/forum/login.php",
                    "login_username={0}&login_password={1}&login=%C2%F5%EE%E4".format(login, password).encode("ascii"))
        self.__opener = opener
