import requests
from bs4 import BeautifulSoup
import json, os
from lib import get_driver, get_item_info, item_list_crawler, login
import time, asyncio
from selenium.webdriver.common.by import By
from tqdm import tqdm


def bs4_getter_temp(dic, login_session, login_info):
    
    response = login_session.get(dic['href'], headers={ "User-Agent": "Mozilla/5.0" })
    # response = login_session.get(dic['href'])


    # except
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # title_detail_xpath = '.item_name'
    detail_name_xpath = '#contents > div.xans-element-.xans-product.xans-product-detail > div.detailArea > div.buy-wrapper > div.buy-scroll-box > div.infoArea > div.xans-element-.xans-product.xans-product-detaildesign > table > tbody > tr:nth-child(6) > td > span'
    detail_img_xpath = 'div.keyImg.item > div.thumbnail > a > img'
    detail_info_img_xpath = '#prdDetail > div.cont > div > img'
    option_xpath = '#product_option_id1 > option'
    # title_detail = soup.select(title_detail_xpath)

    detail_name = soup.select(detail_name_xpath)
    detail_img = soup.select_one(detail_img_xpath)
    detail_info_img = soup.select(detail_info_img_xpath)
    options_info = soup.select(option_xpath)

    options = []
    for i in options_info:
        option_text = i.text
        options.append(option_text)

    dic['img'] = detail_img['src']
    info_img = []
    for i in detail_info_img:
        try:
            info_img.append(str(i['src']))
            info_img.append(str(i['ec-data-src']))
        except:
            # print(dic)
            pass
            

    dic['detail_name'] = str(detail_name)
    dic['detail_info_img'] = str(info_img)
    dic['options'] = str(options)

    return dic

def bs4_getter_temp_sele(dic, driver, tct):
    driver.get(dic['href'])

    detail_img_xpath = '//*[@id="mainImage"]/img'
    detail_info_img_class = 'detail_explain_box'
    detail_title_xpath = '/html/body/div[2]/div[2]/div/div/div[1]/div[2]/form/div/div/div[2]/dl/dt'
    detail_text_xpath = '/html/body/div[2]/div[2]/div/div/div[1]/div[2]/form/div/div/div[2]/dl/dd'

    detail_img = driver.find_elements(By.XPATH,detail_img_xpath)
    detail_info_img = driver.find_elements(By.CLASS_NAME, detail_info_img_class)
    detail_title = driver.find_elements(By.XPATH, detail_title_xpath)
    detail_text = driver.find_elements(By.XPATH, detail_text_xpath)

    dic['qty'] = 'need to check'
    dic['model_name'] = 'need to check'

    for n, i in enumerate(detail_title):
        if i.text == '상품재고':
            dic['qty'] = detail_text[n].text

        if i.text == '자체상품코드':
            dic['model_name'] = detail_text[n].text

    dic['img'] = []
    for i in detail_img:
        dic['img'].append(i.get_attribute('src'))
    
    dic['detail_info_img'] = []
    for i in detail_info_img:
        img_tags = i.find_elements(By.TAG_NAME, 'img')
        for i in img_tags:
            dic['detail_info_img'].append(i.get_attribute('src'))

    tct.write(f"{dic['title']}\t{dic['model_name']}\t{dic['img']}\t{dic['href']}\t{dic['detail_info_img']}\t{dic['qty']}\n")


def get_detail_info(web_name, result_processed, driver):
    with open(f'../result/{web_name}/target_result.tsv', 'a') as tct:
        for i in tqdm(result_processed):
            print(i)
            bs4_getter_temp_sele(i, driver, tct)


def temp_save(web_name, result):
    with open(f'../result/{web_name}/main_result.json', 'w') as k:
        json.dump(result, k, ensure_ascii=False)


def get_login_session(login_info):
    """
    get response
    """

    login_url = login_info['LOGIN_URL']
    login_info = {
        login_info["ID_NAME"] : login_info['USER'],
        login_info["PASS_NAME"] : login_info['PASS']
        }
    session = requests.Session()
    res = session.post(login_url, data=login_info)

    return res
    



if __name__ == "__main__":
    start = time.time()  # 시작 시간 저장
    web_name = 'unionpet'

    USER = "facebridge20"
    PASS = "tmakxm12!@"
    LOGIN_URL = 'https://unionpet.co.kr/member/login.php'
    ID_NAME = 'loginId'
    PASS_NAME = 'loginPwd'
    LOGIN_BTN = '//*[@id="formLogin"]/div[1]/div[1]/button'
    MAIN_TITLE_TAG = 'title'
    MAIN_HREF_TAG = 'href'

    login_info = {

        "USER": USER,
        "PASS": PASS,
        "ID_NAME" : ID_NAME,
        "PASS_NAME" : PASS_NAME,
        "LOGIN_URL" : LOGIN_URL,
        "LOGIN_BTN" : LOGIN_BTN
    }
    tag_info = {
        "href" : MAIN_HREF_TAG,
        "title" : MAIN_TITLE_TAG

    }

    if os.path.exists(f'../result/{web_name}/main_result.json'):
        print('already exist')
        with open(f'../result/{web_name}/main_result.json', 'r') as k:
            main_result = json.load(k)

        driver = get_driver()
        driver = login(driver, login_info)

    else:
        print('main result not exist')
        driver = get_driver()
        driver = login(driver, login_info)

        urls = ['https://www.unionpet.co.kr/goods/goods_list.php?cateCd=105','https://www.unionpet.co.kr/goods/goods_list.php?cateCd=104']

        main_result = []
        url = urls[0]

        item_xpath = {
            "item_href_xpath" : '//*[@id="contents"]/div/div/div[2]/div[4]/div/div[1]/ul/li/div/div[1]/a',
            "item_title_xpath" : '//*[@id="contents"]/div/div/div[2]/div[4]/div/div[1]/ul/li/div/div[2]/div[1]/a/strong'
        }
        for url in urls:
            main_result.extend(item_list_crawler(driver, item_xpath, url, tag_info))

        print("get main_result")
        os.makedirs(f'../result/{web_name}', exist_ok=True)

        temp_save(web_name, main_result)
        print("temp_save done")

    print("checking_url")
    _ = []
    result_processed = []
    for i in main_result:
        url = i['href']
        if url not in _:
            result_processed.append(i)
    with open(f'../result/{web_name}/target_result.tsv', 'w') as _:
        _.write("title\tmodel_name\timg\thref\tdetail_info_img\tqty\n")
    _.close

    print("start get detail_info")
    get_detail_info(web_name, result_processed, driver)

    print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
