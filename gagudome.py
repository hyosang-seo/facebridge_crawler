import requests
from bs4 import BeautifulSoup
import json, os
from lib import get_driver, get_item_info, item_list_crawler
import time, asyncio


async def bs4_getter_temp(dic):
    response = requests.get(dic['href'], headers={ "User-Agent": "Mozilla/5.0" })
    
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
    print("detail_img : ",detail_img)
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

async def bs4_getter_async(main_result):
    tasks = [asyncio.ensure_future(bs4_getter_temp(i)) for i in main_result]
    target = await asyncio.gather(*tasks)

    return target

def temp_save(web_name, result):
    os.makedirs(web_name, exist_ok=True)
    with open(f'{web_name}/main_result.json', 'w') as k:
        json.dump(result, k, ensure_ascii=False)



def get_detail_info(web_name, main_result):
    err_list = []
    ss = []
    loop = asyncio.get_event_loop()
    target_result =loop.run_until_complete(bs4_getter_async(main_result))
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
    # print("start")
    web_name = 'gagudome'

    USER = "facebridge20"
    PASS = "tmakxm12!@"
    LOGIN_URL = 'https://gagudome.kr/member/login.html'
    ID_NAME = 'member_id'
    PASS_NAME = 'member_passwd'
    LOGIN_BTN = 'loginBtn'
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
    else:
        print('main result not exist')
        driver = get_driver()
        print("got driver")
        url = 'https://gagudome.kr/product/list.html?cate_no=113&sort_method=5&page='
        item_xpath = {
            "item_href_xpath" : '/html/body/div[4]/div/div[2]/div[4]/div[2]/ul/li/div[2]/p[2]/a',
            "item_title_xpath" : '/html/body/div[4]/div/div[2]/div[4]/div[2]/ul/li/div[2]/p[2]/a'
        }

        main_result = item_list_crawler(driver, item_xpath, url, tag_info, login_info)
        print("get main_result")
        driver.close()
        temp_save(web_name, main_result)
        print("temp_save done")

    main_result =[{
        "title": "[도매상품] 숲속귀족 높은 자작나무 책꽂이",
        "href": "https://gagudome.kr/product/%EB%8F%84%EB%A7%A4%EC%83%81%ED%92%88-%EC%88%B2%EC%86%8D%EA%B7%80%EC%A1%B1-%EB%86%92%EC%9D%80-%EC%9E%90%EC%9E%91%EB%82%98%EB%AC%B4-%EC%B1%85%EA%BD%82%EC%9D%B4/3277/category/113/display/1/"
    },
    {
        "title": "[도매상품] 숲속귀족 라운딩 잡지꽂이",
        "href": "https://gagudome.kr/product/%EB%8F%84%EB%A7%A4%EC%83%81%ED%92%88-%EC%88%B2%EC%86%8D%EA%B7%80%EC%A1%B1-%EB%9D%BC%EC%9A%B4%EB%94%A9-%EC%9E%A1%EC%A7%80%EA%BD%82%EC%9D%B4/3276/category/113/display/1/"
    },
    {
        "title": "[도매상품] 숲속귀족 낮은 자작나무 책꽂이",
        "href": "https://gagudome.kr/product/%EB%8F%84%EB%A7%A4%EC%83%81%ED%92%88-%EC%88%B2%EC%86%8D%EA%B7%80%EC%A1%B1-%EB%82%AE%EC%9D%80-%EC%9E%90%EC%9E%91%EB%82%98%EB%AC%B4-%EC%B1%85%EA%BD%82%EC%9D%B4/3275/category/113/display/1/"
    }]
    print("start get detail_info")
    get_detail_info(web_name, main_result)
    print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
