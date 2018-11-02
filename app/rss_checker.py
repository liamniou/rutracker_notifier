# -*- coding: utf-8 -*-
from sqliter import SQLighter
from config import database_name, rutracker_login, rutracker_password
from bs4 import BeautifulSoup
import requests
import urllib.request as urllib_request
import http
import chardet
import feedparser
import logging as log
from datetime import datetime


class RSSchecker:

    __opener = None

    def __login(self):
        cookies = http.cookiejar.FileCookieJar("cookies")
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cookies))
        opener.open("https://rutracker.org/forum/login.php",
                    "login_username={0}&login_password={1}&login=%C2%F5%EE%E4".format(rutracker_login, rutracker_password).encode("ascii"))
        self.__opener = opener

    def check_updates(self):
        updated_topics_set = []
        op_profile_id = None
        db = SQLighter(database_name)
        subscriptions_data = db.select_all('subscriptions')
        if subscriptions_data:
            rss_feeds_dict = self.generate_dict_of_rss_feeds(subscriptions_data)
            topics_data = db.select_all('topics')
            for topic in topics_data:
                topic_url = topic[0]
                topic_last_update = topic[1]
                # get op_profile_id for this topic_url
                for subscriptions_raw in subscriptions_data:
                    if topic_url in subscriptions_raw:
                        op_profile_id = subscriptions_raw[2]
                # check if topic was updated after last check
                if op_profile_id:
                    rss_data_object = feedparser.parse(rss_feeds_dict[op_profile_id])
                    for rss_entry in rss_data_object['entries']:
                        if topic_url == rss_entry['link'] \
                                and datetime.strptime(
                                    topic_last_update, '%Y-%m-%dT%H:%M:%S+00:00'
                                ) < datetime.strptime(
                                    rss_entry['updated'], '%Y-%m-%dT%H:%M:%S+00:00'):
                            updated_topics_set.append(
                            [topic_url, rss_entry['updated']]
                        )
                else:
                    log.info("{} was not found in subscriptions. Check of updates is skipped for this topic".format(topic_url))
        return updated_topics_set

    def generate_dict_of_rss_feeds(self, subscriptions_data):
        db = SQLighter(database_name)
        op_profile_id_set = set()
        for entry in subscriptions_data:
            op_profile_id_set.add(entry[2])
        rss_feeds_dict = {}
        for profile_id in op_profile_id_set:
            rss_feeds_dict[profile_id] = self.get_rss_feed(profile_id)
        return rss_feeds_dict

    @staticmethod
    def get_html_of_url(url):
        page_html = (requests.get(url)).text
        return BeautifulSoup(page_html, 'html.parser')

    def get_profile_id(self, url):
        topic_page_soup = self.get_html_of_url(url)
        all_a_links = topic_page_soup.find_all('a', attrs={'class': 'txtb'}, href=True)
        for a_link in all_a_links:
            if 'profile' in a_link['href']:
                relative_profile_link = a_link['href']
                profile_id = relative_profile_link.split('=')[-1]
        return profile_id

    def get_rss_feed(self, profile_id):
        if self.__opener is None:
            self.__login()
        data = 'mode=get_feed_url&type=u&id={0}'.format(profile_id)
        response = self.__opener.open('https://rutracker.org/forum/feed.php', data=data.encode("ascii")).read()
        detect_encoding_result = chardet.detect(response)
        return response.decode(detect_encoding_result['encoding'])

    def get_topic_title(self, url):
        topic_page_soup = self.get_html_of_url(url)
        return topic_page_soup.title.string
