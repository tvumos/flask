import requests
import datetime
import model
from bs4 import BeautifulSoup
from lxml import html
import pprint
import json
from os import path


# def parsing_page_header(lxml_page):
#     result = {}
#     for i in range(1, 18):
#         numb = lxml_page.xpath(f'//html/body/table[3]/tr[4]/td/table[5]/tr[{i}]/td[1]/text()')
#         desk = lxml_page.xpath(f'//html/body/table[3]/tr[4]/td/table[5]/tr[{i}]/td[2]/text()')
#         if len(numb) == 1:
#             result[numb[0]] = desk[0]
#     return result
#
#
# def parsing_page_value(lxml_page):
#     result = []
#     for i in range(1, 18):
#         numb = lxml_page.xpath(f'//html/body/table[3]/tr[4]/td/table[5]/tr[{i}]/td[1]/text()')
#         desk = lxml_page.xpath(f'//html/body/table[3]/tr[4]/td/table[5]/tr[{i}]/td[2]/text()')
#         val = lxml_page.xpath(f'//html/body/table[3]/tr[4]/td/table[5]/tr[{i}]/td[3]/b/text()')
#         if len(val) == 1:
#             row = []
#             row.append(numb)
#             row.append(desk)
#             row.append(str(val[0]))
#             result.append(row)
#     return result


def get_result(url):
    # Запрос страницы выборов
    response = requests.get(url)
    # Создаем soup для разбора html
    soup = BeautifulSoup(response.text, 'html.parser')
    # Получаем страницу для выполнения запросов XPath
    page_body = html.fromstring(response.text, parser=html.HTMLParser(encoding='utf-8'))
    # Получаем расшифровку строк
    result = []
    for i in range(1, 18):
        numb = page_body.xpath(f'//html/body/table[3]/tr[4]/td/table[5]/tr[{i}]/td[1]/text()')
        desk = page_body.xpath(f'//html/body/table[3]/tr[4]/td/table[5]/tr[{i}]/td[2]/text()')
        val = page_body.xpath(f'//html/body/table[3]/tr[4]/td/table[5]/tr[{i}]/td[3]/b/text()')
        if len(numb) == 1:
            row = []
            row.append(str(numb[0]))
            row.append(str(desk[0]))
            row.append(str(val[0]))
            result.append(row)
    return result



def create_cash_files():
    # Запрос страницы выборов
    response = requests.get(model.URL_MSK)
    # Создаем soup для разбора html
    soup = BeautifulSoup(response.text, 'html.parser')

    dict_regions = {}
    dict_uik = {}
    regions_tag = soup.find_all('option')
    for region in regions_tag:      # [:11] ОТЛАДКА Удалить ограничение в 2 региона
        region_name = region.text
        region_ind = region_name.split()[0]
        region_name = region_name.replace(str(region_ind), '', 1).strip()
        url_region = region.get('value')
        if len(region_name) > 0:
            dict_regions[str(region_ind) + ' ' + region_name] = url_region

            # Получаем список УИКов по каждому региону
            uiks_list = []
            response_region = requests.get(url_region)
            region_soup = BeautifulSoup(response_region.text, 'html.parser')
            uiks_tag = region_soup.find_all('option')
            for uik_tag in uiks_tag:
                uik_name = uik_tag.text
                uik_ind = uik_name.split()[0]
                uik_name = uik_name.replace(str(uik_ind), '', 1).strip()
                url_uik = uik_tag.get('value')
                if len(uik_name) > 0:
                    uik_list = []
                    uik_list.append(uik_ind + ' ' + uik_name)
                    # uik_list.append(uik_name)
                    uik_list.append(url_uik)
                    uiks_list.append(uik_list)
            dict_uik[str(region_ind) + ' ' + region_name] = uiks_list
    # Сохранение файлов со списком регионов и списком УИК
    with open(model.FILE_NAME_REGION, "w") as f:
        json.dump(dict_regions, f)
    with open(model.FILE_NAME_UIK, "w") as f:
        json.dump(dict_uik, f)


if __name__ == "__main__":

    if not path.isfile(model.FILE_NAME_REGION) or not path.isfile(model.FILE_NAME_UIK):
        create_cash_files()

    with open(model.FILE_NAME_REGION, "r") as read_file:
        regions = json.load(read_file)
    # pprint.pprint(regions)
    with open(model.FILE_NAME_UIK, "r") as read_file:
        uiks = json.load(read_file)
    pprint.pprint(uiks)
