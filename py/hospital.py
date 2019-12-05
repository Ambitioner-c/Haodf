"""
author:cfl
    获取医院列表.
"""
import requests
from bs4 import BeautifulSoup
import re
import csv


headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/78.0.3904.108 Safari/537.36'}


# 获取全部省
def get_all_province(url):
    # 获取页面内容
    res = requests.get(url, headers=headers)
    html = res.text
    html = BeautifulSoup(html, 'lxml')

    # 获取全部省
    div_province = html.findAll('div', attrs={'class': 'ct'})[0]
    div_province_list = div_province.findAll('div', attrs={'class': re.compile(r'kstl')})
    province_name_list = []
    province_href_list = []
    for j in div_province_list:
        name = re.findall(r'>(.+?)<', str(j))[0]
        href = re.findall(r'yiyuan/(.+?)/', str(j))[0]
        province_name_list.append(name)
        province_href_list.append(href)

    return province_name_list, province_href_list


# 获取医院
def get_hospital_id(pathname,
                    province_name, province_href):
    url = 'https://www.haodf.com/yiyuan/%s/list.htm' % province_href

    # 获取页面内容
    res = requests.get(url, headers=headers)
    html = res.text
    html = BeautifulSoup(html, 'lxml')

    # 当前省的全部城市
    div_city = html.findAll('div', attrs={'class': 'ct'})[1]

    # 全部城市名
    div_city_name_list = div_city.findAll('div', attrs={'class': 'm_title_green'})
    city_name_list = []
    for j in div_city_name_list:
        city_name = re.findall(r'>(.+?)<', str(j))[0]
        city_name_list.append(city_name)

    # 按区域获取医院
    for j in range(len(city_name_list)):
        # 区域
        div_district = div_city.findAll('div', attrs={'class': 'm_ctt_green'})[j]
        a_list = div_district.findAll('a', attrs={'href': re.compile(r'hospital')})

        hospital_address_list = []
        hospital_name_list = []
        hospital_href_list = []
        for k in a_list:
            name = re.findall(r'>(.+?)<', str(k))[0]
            href = re.findall(r'hospital/(.+?)\.htm', str(k))[0]
            hospital_address_list.append(province_name + city_name_list[j])
            hospital_name_list.append(name)
            hospital_href_list.append(href)
        # 写入医院数据
        write_doc(pathname,
                  hospital_address_list, hospital_href_list, hospital_name_list)


def write_table(pathname):

    # 判断是否已经写入表头
    try:
        with open(pathname + 'hospital.csv', 'r') as hospital_reader:
            if hospital_reader.readline() != '':
                return
            else:
                # 写入表头
                with open(pathname + 'hospital.csv', 'a') as hospital:
                    hospital_writer = csv.writer(hospital)

                    # 写入字段
                    fields = ['hospital_address', 'hospital_href', 'hospital_name']
                    hospital_writer.writerow(fields)
    except:
        # 写入表头
        with open(pathname + 'hospital.csv', 'a') as hospital:
            hospital_writer = csv.writer(hospital)

            # 写入字段
            fields = ['hospital_address', 'hospital_href', 'hospital_name']
            hospital_writer.writerow(fields)


# 'hospital_address', 'hospital_href', 'hospital_name'
def write_doc(pathname,
              hospital_address_list, hospital_href_list, hospital_name_list):
    # 医院
    with open(pathname + 'hospital.csv', 'a') as hospital:
        hospital_writer = csv.writer(hospital)

        # 写入行数据
        for j in range(len(hospital_name_list)):
            hospital_writer.writerow([hospital_address_list[j], hospital_href_list[j], hospital_name_list[j]])


if __name__ == '__main__':
    my_pathname = '../data/'

    # 全部医院列表
    my_url = 'https://www.haodf.com/yiyuan/all/list.htm'

    # 写入表头
    write_table(my_pathname)

    # 省名称、链接
    my_province_name_list, my_province_href_list = get_all_province(my_url)

    for i in range(len(my_province_name_list)):
        get_hospital_id(my_pathname, my_province_name_list[i], my_province_href_list[i])
