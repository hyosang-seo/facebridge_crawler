import requests
from bs4 import BeautifulSoup
import json, os
from lib import get_driver, get_item_info, item_list_crawler, login
import time, asyncio
from selenium.webdriver.common.by import By



async def bs4_getter_temp(dic, login_session, login_info):
    
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

    print(detail_img)
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

async def bs4_getter_temp_sele(dic, driver):
    driver.get(dic['href'])
    
    detail_name_xpath = '//*[@id="frmView"]/div/div/div[2]/dl[5]/dd'
    detail_img_xpath = '//*[@id="mainImage"]/img'
    detail_info_img_xpath = '//*[@id="detail"]/div[2]/div/div[2]/center/img'
    # option_selector = '#product_option_id1 > option'
    # title_detail = soup.select(title_detail_xpath)

    detail_name = driver.find_elements(By.XPATH, detail_name_xpath)
    detail_img = driver.find_elements(By.XPATH,detail_img_xpath)
    detail_info_img = driver.find_elements(By.XPATH, detail_info_img_xpath)

    dic['img'] = []
    for i in detail_img:
        dic['img'].append(i.get_attribute('src'))
    
    info_img = []
    for i in detail_info_img:
        info_img.append(i.get_attribute('src'))

    info_img = []
    for i in info_img:
        info_img.append(i.get_attribute('src'))


    dic['detail_name'] = detail_name[0].text
    dic['detail_info_img'] = info_img


    return dic

async def bs4_getter_async(main_result, login_info, login_session):
    # tasks = [asyncio.ensure_future(bs4_getter_temp_sele(i, login_session, login_info)) for i in main_result[:3]]
    tasks = [asyncio.ensure_future(bs4_getter_temp_sele(i, driver)) for i in main_result]

    target = await asyncio.gather(*tasks)

    return target

def temp_save(web_name, result):
    os.makedirs(web_name, exist_ok=True)
    with open(f'{web_name}/main_result.json', 'w') as k:
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
    
def get_detail_info(web_name, main_result, login_info):
    err_list = []
    loop = asyncio.get_event_loop()
    login_session = get_login_session(login_info)

    target_result =loop.run_until_complete(bs4_getter_async(main_result, login_info, login_session))
    loop.close

    with open(f'{web_name}/error.txt', 'w') as et:
        for i in err_list:
            # json.dump(err_list, et, ensure_ascii=False)
            et.write(json.dumps(i)+ '\n')

    with open(f'{web_name}/target_result.json', 'w') as tt:
        json.dump(target_result, tt, ensure_ascii=False)

    with open(f'{web_name}/target_result.tsv', 'w') as tct:
        tct.write('title\tdetail_name\timg\thref\detail_info_img\n')
        for i in target_result:
            tct.write(f"{i['title']}\t{i['detail_name']}\t{i['img']}\t{i['href']}\t{i['detail_info_img']}\n")
            

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

    if os.path.exists(f'./{web_name}/main_result.json'):
        print('already exist')
        with open(f'./{web_name}/main_result.json', 'r') as k:
            main_result = json.load(k)

        driver = get_driver()
        driver = login(driver, login_info)

    else:
        print('main result not exist')
        driver = get_driver()
        urls = ['https://www.unionpet.co.kr/goods/goods_list.php?cateCd=105','https://www.unionpet.co.kr/goods/goods_list.php?cateCd=104']

        main_result = []
        url = urls[0]
        item_xpath = {
            "item_href_xpath" : '//*[@id="contents"]/div/div/div[2]/div[4]/div/div[1]/ul/li/div/div[1]/a',
            "item_title_xpath" : '//*[@id="contents"]/div/div/div[2]/div[4]/div/div[1]/ul/li/div/div[2]/div[1]/a/strong'
        }
        main_result.extend(item_list_crawler(driver, item_xpath, url, tag_info, login_info))
        url = urls[1]
        main_result.extend(item_list_crawler(driver, item_xpath, url, tag_info))

        print("get main_result")
        # driver.close()
        temp_save(web_name, main_result)
        print("temp_save done")

    print("start get detail_info")
    get_detail_info(web_name, main_result, login_info)

    print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
