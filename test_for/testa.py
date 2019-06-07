from selenium import webdriver

from pyquery import PyQuery as pq
import requests
import pymongo
import pymysql
from time import sleep

browser = webdriver.Chrome()

URL_TO_CRAWL = 'https://www.dianping.com/'
KEYWORD = '火锅'

ALL_IN_ONE = []
MAX_PAGE = 50

MONGO_URL = 'localhost'
MONGO_DB = 'dzdp'
MONGO_COLLECTION = 'items'
client = pymongo.MongoClient(MONGO_URL)
db_for_mongo = client[MONGO_DB]

db_for_mysql = pymysql.connect(host='localhost', user='root', password='123456')
cursor = db_for_mysql.cursor()


def get_stores():
    store_info = {}

    html = browser.page_source
    doc = pq(html)
    items_pic = doc('.shop-all-list .pic').items()
    for item in items_pic:
        img_urll = str(item.find('img').attr('data-src'))
        print(img_urll)
        print(item)
        print('aaaaaaaaaaaaa')

    # print(items_pic)
    # for item_pic in items_pic:
    #     print(item_pic)
    #     t = item_pic.find('img').text()
    #     print(t,'tttttttttttttt')


    # print(div_for_crawl)
    # doc = pq(div_for_crawl)
    # items = doc('.pic').items()
    # for pic in items:
    #     print(pic)
        # url = pic.find('img')
        # print(url)


    # a=0
    # for item in items:
    #     a = a+1
    #     print(type(item))
    #
    #     print(' a is ', a)
    #     product = {
    #         'store': str(item.find('.shop_text').text().strip()),
    #         'image_url': 'http:' + str(item.find('#searchProImg').find('img').attr('src')),
    #     }
    #     print('product is ')
    #     print(product)
    #     save_to_mongo(product)
        # save_to_mysql(product)
        # save_image_to_folder(product['image_url'], product['name'][:20].strip())


def save_image_to_folder(img_url, img_name):
    print('begin to save to folder')
    if img_url[6:]:
        r = requests.get(img_url)
        with open('./image_yhd/'+ img_name+ '.jpg','wb') as f:
            f.write(r.content)
    print('success to save to folder')


def save_to_mongo(product):
    try:
        if db_for_mongo[MONGO_COLLECTION].insert(product):
            print('存储到MongoDB成功')
    except Exception:
        print('存储到MongoDB失败')




def init_mysql_for_item():
    print(' begin to init mysql')
    sql_drop_db = 'drop database if exists exam;'
    sql_create_db = 'create database if not exists exam;'
    sql_drop_table = 'drop table if exists exam.dzdpitem;'
    sql_create_table = 'create table if not exists exam.dzdpitem(name varchar(300));'
    cursor.execute(sql_drop_db)
    cursor.execute(sql_create_db)
    cursor.execute(sql_drop_table)
    cursor.execute(sql_create_table)
    print(' init success')


def save_item_to_mysql(product):
    print(' begin to save to mysql')
    sql = 'INSERT INTO exam.dzdpitem values(%s);'
    print(sql,(product))
    try:
        cursor.execute(sql,(product))
        db_for_mysql.commit()
        print(' success save to mysql')
    except:
        db_for_mysql.rollback()
        print(' failed to save to mysql ')


def get_all_items():

    init_mysql_for_item()
    browser.get(URL_TO_CRAWL)
    html = browser.page_source


    doc = pq(html)

    items = doc('.first-item').items()

    for item in items:

        doc_item = pq(item)
        TITLE_EVERYTHING = []

        items_show = doc_item('.primary-container').text()
        TITLE_EVERY = items_show.split('\n')
        aa = ''.join(TITLE_EVERY)
        save_item_to_mysql(aa)
        TITLE_EVERYTHING.append(TITLE_EVERY)

        items_hide = doc_item('.groups').items()

        for item_hide in items_hide:

            doc_a = pq(item_hide)
            littles_item = doc_a('.group').items()
            for little in littles_item:
                each_group = []
                each_item_title_for_append = little.find('.channel-title').text()
                each_group.append(each_item_title_for_append)

                doc_item_each = pq(little)
                item_little_contents = doc_item_each('.second-item').items()
                for item_little_content in item_little_contents:
                    item_content_lit = item_little_content.text()
                    each_group.append(item_content_lit)
                bb = ''.join(each_group)
                save_item_to_mysql(bb)
                TITLE_EVERYTHING.append(each_group)
        ALL_IN_ONE.append(TITLE_EVERYTHING)


def main():
    # get_all_items()
    # print(ALL_IN_ONE)
    browser.get(URL_TO_CRAWL)
    jump_to_hotpot = browser.find_element_by_link_text(KEYWORD)
    changed_url = jump_to_hotpot.get_attribute('href')
    browser.get(changed_url)
    sleep(1)
    for i in range(1, 2):
        print('到 ', i)
        get_stores()
        print(' di ',i,' page is done')


if __name__ == '__main__':
    main()