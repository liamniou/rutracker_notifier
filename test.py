# -*- coding: utf-8 -*-
import feedparser
from rss_checker import RSSchecker

if __name__ == '__main__':
    # updates = RSSchecker.check_updates()
    # for element in updates:
    #     print(element[0])
    #     print(element[1])
    #     feed = feedparser.parse(element[0])
    #     print(feed)
    #     for feed in feed["entries"]:
    #         # Create array with all titles from RSS feed
    #         print(feed)
    #     print('---')

    RSSchecker = RSSchecker()
    rss_link = RSSchecker.find_rss_link('https://rutracker.org/forum/viewtopic.php?t=3102774')
    print(rss_link)