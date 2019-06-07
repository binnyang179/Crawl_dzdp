from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import requests
import pymongo
import pymysql
from time import sleep

browser = webdriver.Chrome()
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# browser = webdriver.Chrome(chrome_options=chrome_options)
# wait = WebDriverWait(browser, 10)

URL_TO_CRAWL = 'http://www.dianping.com/tianjin/ch10/g110'
MAX_PAGE = 50

MONGO_URL = 'localhost'
MONGO_DB = 'dazhongdianpin'
MONGO_COLLECTION = 'products'
client = pymongo.MongoClient(MONGO_URL)
db_for_mongo = client[MONGO_DB]

db_for_mysql = pymysql.connect(host='localhost', user='root', password='123456')
cursor = db_for_mysql.cursor()


def each_page(page):
    print('正在爬取第', page, '页')
    get_products()


def get_products():
    html = browser.page_source
    doc = pq(html)
    items = doc('.mod_search_pro').items()
    a=0
    for item in items:
        a = a+1
        print(' a is ', a)
        product = {
            'name': str(item.find('.proName').text().strip())[114:],
            'price': str(item.find('.proPrice').find('.num').text().strip())[1:],
            'store': str(item.find('.shop_text').text().strip()),
            'judge': str(item.find('.positiveRatio').text().strip())[4:],
            'image_url': 'http:' + str(item.find('#searchProImg').find('img').attr('src')),
        }
        print('product is ')
        print(product)
        save_to_mongo(product)
        save_to_mysql(product)
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


def init_mysql():
    print(' begin to init mysql')
    sql_drop_db = 'drop database if exists exam;'
    sql_create_db = 'create database if not exists exam;'
    sql_drop_table = 'drop table if exists exam.yhd;'
    sql_create_table = 'create table if not exists exam.yhd(name varchar(250) ,price varchar(20), store varchar(100) , judge varchar(40), image_url varchar(250));'
    cursor.execute(sql_drop_db)
    cursor.execute(sql_create_db)
    cursor.execute(sql_drop_table)
    cursor.execute(sql_create_table)
    print(' init success')


def save_to_mysql(product):
    print(' begin to save to mysql')
    sql = 'INSERT INTO exam.yhd(name, price, store, judge, image_url) values(%s, %s, %s, %s, %s);'
    name = product['name']
    price = product['price']
    store = product['store']
    judge = product['judge']
    img = product['image_url']
    try:
        cursor.execute(sql, (name, price, store , judge, img))
        db_for_mysql.commit()
        print(' success save to mysql')
    except:
        db_for_mysql.rollback()
        print(' failed to save to mysql ')


def main():
    init_mysql()
    browser.get(URL_TO_CRAWL)
    sleep(2)
    for i in range(1, MAX_PAGE + 1):
        print(' 循环到', i, '页')
        each_page(i)
        print('读取第', i, '页成功, 跳转到下一页')
        sleep(1)
        if i < MAX_PAGE:
            pagenext_button = browser.find_element_by_xpath(".//a[@class='next']")
            pagenext_button.click()


if __name__ == '__main__':
    main()
