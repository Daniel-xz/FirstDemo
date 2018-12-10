import json
import requests
from requests.exceptions import RequestException

import time
from bs4 import BeautifulSoup
import sqlite3

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/51.0.2704.63 Safari/537.36'}

#获取页面源码
def get_onepage(url):
    try:
        html = requests.get(url, headers=headers)
        if html.status_code == 200:
            return html.text
    except RequestException as e:
        print('except happended')

#解析网页源码，封装到一个dict中
def parse_onepage(html):
    soup = BeautifulSoup(html, 'lxml')
    # print(soup.find_all(name='dd'))
    # list=['url','name','time','score','star','intro']
    dict = {}
    for message in soup.find_all(name='dd'):
        dict['url'] = 'https://maoyan.com' + message.a['href']
        dict['name'] = message.a['title']
        dict['time'] = message.find(attrs={'class': 'releasetime'}).string[5:]
        dict['star'] = message.find(attrs={'class': 'star'}).string.strip()[3:]
        dict['score'] = message.find(
            attrs={'class': 'integer'}).string + message.find(attrs={'class': 'fraction'}).string
        # dict['intro'] = BeautifulSoup(get_onepage(dict['url']),'lxml').find(attrs={'class':'mod-content'})
        yield dict

#将网页信息存入到sqlite中
def intoDB(dict):
    # bool=True
    conn = sqlite3.connect('moviesinfo.db')
    cursor = conn.cursor()
    cursor.execute(
        '''create table if not exists user2 (name varchar(20) primary key,
    url varchar(50),
    star varchar(100),
    time varchar(20),
    score varchar(20))
    ''')
    # sqlQuery='select name from user1'
    # cursor.execute(sqlQuery)
    # results=cursor.fetchall()
    # for result in results:
    #     if result[0]==dict['name']:
    #         bool=False

    # args=(dict['name'],dict['url'],dict['star'],dict['time'],dict['score'])
    # while(bool):
    sql = "REPLACE  INTO user2(name, url, star, time, score) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(
        sql,
        (dict['name'],
         dict['url'],
         dict['star'],
         dict['time'],
         dict['score'])
    )
    cursor.close()
    conn.commit()
    conn.close()


def main(offset):
    url = 'https://maoyan.com/board/4?offset='+str(offset)
    html = get_onepage(url)
    for demo in parse_onepage(html):
        intoDB(demo)


if __name__ == '__main__':
    for offset in range(0,6):
        main(offset*10)
        time.sleep(1)
