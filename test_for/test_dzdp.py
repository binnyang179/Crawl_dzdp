from selenium import webdriver
from selenium.webdriver import ChromeOptions
import re
import shutil

from pyquery import PyQuery as pq
import requests
import pymongo
import pymysql
from time import sleep
from lxml import etree
import os
from io import StringIO
import random

option = ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])
browser = webdriver.Chrome(options=option)

URL_TO_CRAWL = 'https://www.dianping.com/'
KEYWORD = '火锅'
DB_MONGOS = ['judgeInfo', 'storeInfo', 'item_show']

ALL_IN_ONE = []
MAX_PAGE = 50

MONGO_URL = 'localhost'
MONGO_DB = 'dzdp'
client = pymongo.MongoClient(MONGO_URL)
db_for_mongo = client[MONGO_DB]


db_for_mysql = pymysql.connect(host='localhost', user='root', password='123456')
cursor = db_for_mysql.cursor()


def get_each_judge():
    print('init judge success')

    sql = 'select judgePage from exam.dzdpstore;'
    cursor.execute(sql)
    row_count = cursor.rowcount
    print('Count:', row_count)
    results = cursor.fetchall()
    for each_url in results:
        abc = str(each_url)[2:-3]
        print(abc)
        browser.get(abc)
        sleep(5)
        get_judge_and_image()


def get_judge_and_image():
    print('begin get judge and image')

    html = browser.page_source
    with open('as.html', 'w') as f:
        f.write(html)
    doc = pq(html)

    shop_name = doc.find('.shop-name').text()
    print('shop name is ', shop_name)

    judegs_items = doc('#reviewlist-wrapper').find('.content').items()
    count_store = 0
    # judge_img_num = 0
    for judegs_item in judegs_items:

        count_store += 1
        print('count store is ', count_store)
        judge = judegs_item.find('.desc').text()

        judge = str(judge).replace('\n','')
        rule = re.compile("[^\u4e00-\u9fa5^.^a-z^A-Z^0-9^,^.^?^!]")

        line_judge = rule.sub('', judge)

        print(line_judge)

        judge_images = judegs_item.find('.photos').find('.item').items()
        num = 0
        for judge_image in judge_images:
            num += 1
            print('judge image num ',num)
            image_judge_url = judge_image.find('img').attr('src')
            image_judge_name = judge_image.find('img').attr('alt')

            print('image judge url is ', image_judge_url)
            print(' image judge name is ', image_judge_name)

            judge_info = {
                'judge': line_judge,
                'judge_img_name': image_judge_name,
                'judge_img_url': image_judge_url
            }

            print(judge_info)

            save_to_mongo(DB_MONGOS[0], judge_info)

            name_for_judge_image = str(image_judge_name)
            print('name_for_judge_image is ', name_for_judge_image)

            name_for_judge_image = image_judge_name + str(random.randint(10000,20000))


            print("name_for_judge_image is ", name_for_judge_image)

            save_image_to_folder(image_judge_url, name_for_judge_image, 'judge')


def get_stores():
    html = browser.page_source
    doc = pq(html)
    items_pic = doc('.shop-all-list .pic').items()
    for item in items_pic:
        aa = ''.join(str(item))
        asd = etree.parse(StringIO(aa), etree.HTMLParser())
        img_url = str(asd.xpath('//img/@src'))[2:-2]
        store = str(asd.xpath('//img/@title'))[2:-2]
        store_judge_page_url = str(asd.xpath('//a/@href'))[2:-2]
        print('store judge page url is ', store_judge_page_url)
        store_info = {
            'store': store,
            'image_url': img_url,
            'judge_page_url': store_judge_page_url
        }
        save_to_mongo(DB_MONGOS[1], store_info)
        save_store_to_mysql(store_info)
        save_image_to_folder(str(store_info['image_url'])[:-1], str(store_info['store'])[1:6], 'store')


def save_image_to_folder(img_url, img_name, folder):
    print('begin to save to folder')
    # print(img_url, ',', img_name)
    if img_url[6:]:
        r = requests.get(img_url)
        with open('./images_dzdp/' + folder + '/' + img_name + '.jpg', 'wb') as f:
            f.write(r.content)
    print('success to save to folder')


def save_to_mongo(DBname,product):
    try:
        if db_for_mongo[DBname].insert(product):
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


def init_mysql_for_store():
    print(' begin store info')
    sql_create_db = 'create database if not exists exam;'
    sql_drop_table = 'drop table if exists exam.dzdpstore;'
    sql_create_table = 'create table if not exists exam.dzdpstore(name varchar(50), url varchar(400), judgePage varchar(400));'
    cursor.execute(sql_create_db)
    cursor.execute(sql_drop_table)
    cursor.execute(sql_create_table)
    print('init for store success')


def init_mysql_for_judge():
    print(' begin judge info')
    sql_create_db = 'create database if not exists exam;'
    sql_drop_table = 'drop table if exists exam.dzdpjudge;'
    sql_create_table = 'create table if not exists exam.dzdpjudge(judge varchar(500), judge_img_name varchar(300), judge_img_url varchar(300) );'
    cursor.execute(sql_create_db)
    cursor.execute(sql_drop_table)
    cursor.execute(sql_create_table)
    print('init for store success')


def save_judge_for_mysql(product):
    print('begin judge')
    sql = 'INSERT INTO exam.dzdpjudge values(%s, %s, %s);'
    a = str(product['judge'])
    b = str(product['judge_img_name'])
    c = str(product['judge_img_url'])
    try:
        cursor.execute(sql, (a, b, c))
        db_for_mysql.commit()
        print(' success save to mysql')
    except:
        db_for_mysql.rollback()
        print(' failed to save to mysql ')


def save_item_to_mysql(product):
    print(' begin to save to mysql')
    sql = 'INSERT INTO exam.dzdpitem values(%s);'
    try:
        cursor.execute(sql, (product))
        db_for_mysql.commit()
        print(' success save to mysql')
    except:
        db_for_mysql.rollback()
        print(' failed to save to mysql ')


def save_store_to_mysql(product):
    print('begin store mysql')
    sql = 'INSERT INTO exam.dzdpstore values(%s, %s, %s);'
    a = str(product['store'])
    b = str(product['image_url'])
    c = str(product['judge_page_url'])
    print(sql, (a, b, c))
    try:
        cursor.execute(sql, (a, b, c))
        db_for_mysql.commit()
        print(' success save to mysql')
    except:
        db_for_mysql.rollback()
        print(' failed to save to mysql ')


def get_all_items():
    browser.get(URL_TO_CRAWL)
    html = browser.page_source

    doc = pq(html)

    items = doc('.first-item').items()

    for item in items:

        doc_item = pq(item)
        TITLE_EVERYTHING = []

        items_show = doc_item('.primary-container').text()
        # TITLE_EVERY = items_show.split('\n')
        TITLE_EVERY= items_show.replace('\n', ',')
        aa = ''.join(TITLE_EVERY)

        save_item_to_mysql(aa)
        item_for_mongo = {
            'name': aa+', '
        }
        save_to_mongo(DB_MONGOS[2], item_for_mongo)

        TITLE_EVERYTHING.append(TITLE_EVERY)

        items_hide = doc_item('.groups').items()

        for item_hide in items_hide:

            doc_a = pq(item_hide)
            littles_item = doc_a('.group').items()
            for little in littles_item:
                each_group = []
                each_item_title_for_append = little.find('.channel-title').text()
                each_group.append(each_item_title_for_append+', ')

                doc_item_each = pq(little)
                item_little_contents = doc_item_each('.second-item').items()
                for item_little_content in item_little_contents:
                    item_content_lit = item_little_content.text()
                    each_group.append(item_content_lit + ', ')
                bb = ''.join(each_group)
                save_item_to_mysql(bb+',')
                item_for_mongo = {
                    'name': bb
                }
                save_to_mongo('item_show', item_for_mongo)

                TITLE_EVERYTHING.append(each_group)
        ALL_IN_ONE.append(TITLE_EVERYTHING)


def main():
    shutil.rmtree('images_dzdp')
    if os.path.exists('images_dzdp') is False:
        os.mkdir('images_dzdp')
    if os.path.exists('images_dzdp/store') is False:
        os.mkdir('images_dzdp/store')
    if os.path.exists('images_dzdp/judge') is False:
        os.mkdir('images_dzdp/judge')
    init_mysql_for_item()
    init_mysql_for_store()
    init_mysql_for_judge()
    for v in range(3):
        db_for_mongo[DB_MONGOS[v]].drop()

    get_all_items()
    print(ALL_IN_ONE)

    browser.get(URL_TO_CRAWL)
    jump_to_hotpot = browser.find_element_by_link_text(KEYWORD)
    changed_url = jump_to_hotpot.get_attribute('href')
    browser.get(changed_url)
    start_url = browser.current_url
    print('current url is ', start_url)

    for i in range(1, 2):
        print('di ', i)
        get_stores()
        print(' di ', i, ' page is done')
        # html = browser.page_source
        jump_to_next = browser.find_element_by_class_name('next')
        js = "window.scrollTo(0, document.body.scrollHeight-1500)"
        browser.execute_script(js)
        # sleep(2)
        if i < 1:
            print('jump to next')
            jump_to_next.click()

    print('begin to judge')
    get_each_judge()


if __name__ == '__main__':
    main()
