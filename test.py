import requests
from bs4 import BeautifulSoup


def bs4_getter(url):

    response = requests.get(url, headers={ "User-Agent": "Mozilla/5.0" })
    dic = {}
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        detail_name_xpath = '.infoArea > div > table > tbody > tr > td > span'
        detail_img_xpath = '#big_img_box'

        detail_name = soup.select(detail_name_xpath)[4].text
        img = soup.select_one(detail_img_xpath)
        dic['detail_name'] = detail_name
        dic['img'] = img

    else : 
        print(url)


bs4_getter(url)