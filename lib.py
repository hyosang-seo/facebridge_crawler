
from lib2to3.pgen2 import driver
from logging import raiseExceptions
from selenium import webdriver
import asyncio, time

def get_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    #       options.add_argument("--disable-extensions")
    #       options.add_argument("disable-infobars")
    #       options.add_argument("window-size=1920x1080")
    options.add_argument("no-sandbox")
    options.add_argument("disable-gpu")
    options.add_argument("--lang=ko_KR")
    options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
    driver = webdriver.Chrome('./chromedriver', chrome_options=options)

    return driver



def get_item_info(driver, item_xpath, tag_info):
    """
    get href and title form main page
    
    """
    href_list = []
    title_list = []

    item_href_xpath = item_xpath['item_href_xpath']
    item_title_xpath = item_xpath['item_title_xpath']

    # href
    item_href = driver.find_elements_by_xpath(item_href_xpath)
    for i in item_href:
        dic = {}
        href = i.get_attribute(tag_info['href'])
        dic["href"] = href
        href_list.append(dic)

    # title
    item_title = driver.find_elements_by_xpath(item_title_xpath)
    for i in item_title:
        dic = {}
        href = i.get_attribute(tag_info['title'])
        dic["title"] = i.text

        title_list.append(dic)

    dic_list = []

    if len(title_list) != len(href_list):
        raiseExceptions('count are diff')

    for i, n in enumerate(title_list):
        _ = {}
        _["title"] = title_list[i]['title']
        _["href"] = href_list[i]['href']
        dic_list.append(_)

    return dic_list

def login(driver, login_info):
    login_info = login_info[0]
    USER = login_info["USER"]
    PASS = login_info["PASS"]
    LOGIN_URL = login_info["LOGIN_URL"]
    ID_NAME = login_info['ID_NAME']
    PASS_NAME = login_info['PASS_NAME']
    LOGIN_BTN = login_info['LOGIN_BTN']

    driver.get(LOGIN_URL)
    driver.find_element_by_name(ID_NAME).send_keys(USER)
    driver.find_element_by_name(PASS_NAME).send_keys(PASS)
    driver.find_element_by_class_name(LOGIN_BTN).click()

    return driver

def item_list_crawler(driver, item_xpath, url, tag_info, *login_info):
    """
    item text, href crawrling until len(items) == 0
    """
    result =[]
    item_count = 1
    page_num = 1
    if login_info:
        driver = login(driver, login_info)
        time.sleep(1)
    while item_count != 0:
    # while page_num < 2:
        driver.get(url + str(page_num))
        result_dic = get_item_info(driver, item_xpath, tag_info)
        print(f"page : {page_num} item count : {len(result_dic)} EA")
        page_num +=1
        item_count = len(result_dic)
        result.extend(result_dic)

    return result



