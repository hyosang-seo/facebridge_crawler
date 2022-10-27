# crawler for udong corp.

# 상품명
# 공급가 - not yet
# 상세페이지 들어가면 나오는 모델명
# 상세페이지의 이미지 url
import requests
from bs4 import BeautifulSoup

import json, os
from json.tool import main
from tqdm import tqdm
from lib import get_driver, get_item_info, item_list_crawler
import time, asyncio

# def item_list_crawler(driver, item_xpath):
#     """
#     item text, href crawrling until len(items) == 0
#     """
#     result =[]
#     item_count = 1
#     page_num = 1

#     while item_count != 0:
#     # while page_num < 2:
#         url = 'https://beseller.net/product/list.html?cate_no=160&page={}'.format(page_num)
#         result_dic = get_item_info(driver, url, item_xpath)
#         print(f"page : {page_num} item count : {len(result_dic)} EA")
#         page_num +=1
#         item_count = len(result_dic)
        
#         result.extend(result_dic)

    # return result

async def bs4_getter_temp(dic):
    response = requests.get(dic['href'], headers={ "User-Agent": "Mozilla/5.0" })
    # dic = {}

    # except
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    title_detail_xpath = '.infoArea > div > table > tbody > tr > th'
    detail_name_xpath = '.infoArea > div > table > tbody > tr > td > span'
    detail_img_xpath = '#big_img_box'
    detail_info_img_xpath = '#prdDetail > div > center > img'


    title_detail = soup.select(title_detail_xpath)
    detail_name = soup.select(detail_name_xpath)
    detail_img = soup.select_one(detail_img_xpath)['data-one_big_img']
    detail_info_img = soup.select(detail_info_img_xpath)
    for n, i in enumerate(title_detail):
        n +=1
        if i.text == '모델':
            dic['detail_name'] = detail_name[n-1].text

    if 'detail_name' not in dic.keys():
        dic['detail_name'] = 'pass'

    dic['img'] = detail_img
    info_img = []
    for i in detail_info_img:
        info_img.append(i['ec-data-src'])

    dic['detail_info_img'] = info_img

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
    web_name = 'beseller'
    if os.path.exists(f'./{web_name}/main_result.json'):
        print('already exist')
        with open(f'./{web_name}/main_result.json', 'r') as k:
            main_result = json.load(k)
    else:
        print('main result not exist')

        driver = get_driver()
        print("got driver")
        item_xpath = '/html/body/div[1]/div[4]/div[2]/div[3]/div[3]/ul/li/div[2]/p[2]/a' 
        url = 'https://beseller.net/product/list.html?cate_no=160&page='
        main_result = item_list_crawler(driver, item_xpath, url)
        print("get main_result")
        driver.close()
        temp_save(web_name, main_result)
        print("temp_save done")
    
    get_detail_info(web_name, main_result)
    print("time :", time.time() - start)  # 현재시각 - 시작시간 = 실행 시간
