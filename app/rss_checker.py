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
        author_profile_id = None
        db = SQLighter(database_name)
        subscriptions_data = db.select_all('subscriptions')
        if subscriptions_data:
            rss_feeds_dict = self.generate_dict_of_rss_feeds(subscriptions_data)
            topics_data = db.select_all('topics')
            for topic in topics_data:
                db_topic_url = topic[0]
                db_topic_last_update = topic[1]
                log.info("Checking topic {} with last update date {}".format(db_topic_url, db_topic_last_update))
                # get author_profile_id for this db_topic_url
                for subscriptions_raw in subscriptions_data:
                    if db_topic_url in subscriptions_raw:
                        author_profile_id = subscriptions_raw[2]
                # check if topic was updated since last check
                if author_profile_id:
                    rss_data_object = feedparser.parse(rss_feeds_dict[author_profile_id])
                    for rss_entry in rss_data_object['entries']:
                        db_topic_last_update_unified = datetime.strptime(
                            db_topic_last_update, '%Y-%m-%dT%H:%M:%S+00:00'
                        )
                        rss_topic_last_update_unified = datetime.strptime(
                            rss_entry['updated'], '%Y-%m-%dT%H:%M:%S+00:00'
                        )
                        if db_topic_url == rss_entry['link'] \
                                and db_topic_last_update_unified < rss_topic_last_update_unified:
                            log.info("{} was updated since last check: {} < {}".format(
                                db_topic_url, db_topic_last_update_unified, rss_topic_last_update_unified
                            ))
                            updated_topics_set.append(
                            [db_topic_url, rss_entry['updated']]
                        )
                else:
                    log.info("{} was not found in subscriptions. Updates check is skipped".format(db_topic_url))
        return updated_topics_set

    def generate_dict_of_rss_feeds(self, subscriptions_data):
        op_profile_id_set = set()
        for entry in subscriptions_data:
            op_profile_id_set.add(entry[2])
        rss_feeds_dict = {}
        for profile_id in op_profile_id_set:
            rss_feeds_dict[profile_id] = self.get_rss_feed(profile_id)
        return rss_feeds_dict

    @staticmethod
    def get_html_of_url(url):
        try:
            page_html = (requests.get(url)).text
            soup_page_html = BeautifulSoup(page_html, 'html.parser')
            return soup_page_html
        except requests.exceptions.RequestException as e:
            log.error(e)
            return None

    def get_profile_id(self, url):
        topic_page_soup = self.get_html_of_url(url)
        all_tbodies_tags = topic_page_soup.find_all('tbody', attrs={'class': 'row1'})
        tbody_post_ids = []
        for tbody_tag in all_tbodies_tags:
            tbody_post_ids.append(tbody_tag.get('id').replace('post_', ''))
        tbody_post_ids.sort()
        author_post_id = tbody_post_ids[0]
        author_tbody_tag = topic_page_soup.find(id="post_{}".format(author_post_id))
        links = author_tbody_tag.find_all('a', attrs={'class': 'txtb'}, href=True)
        relative_profile_link = links[0].get('href')
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
