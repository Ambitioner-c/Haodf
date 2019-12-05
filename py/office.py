"""
author: cfl
    获取科室列表。
"""
import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import threading
import os
from random import randint


headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/78.0.3904.108 Safari/537.36'}


def read_doc(pathname):
    # 全列表
    hospital_all_href_list = []
    hospital_all_reader_list = csv.reader(open(pathname + 'hospital.csv', 'r'))
    # 删掉第一行
    n = 0
    for j in hospital_all_reader_list:
        if n != 0:
            hospital_all_href_list.append(j[1])
        n += 1

    # 已完成列表
    try:
        office_finish_href_list = []
        office_finish_reader_list = csv.reader(open(pathname + 'office_finish.csv', 'r'))
        for j in office_finish_reader_list:
            office_finish_href_list.append(j[0])
        office_finish_href_set = set(office_finish_href_list)
    except:
        office_finish_href_list = []
        office_finish_href_set = set(office_finish_href_list)

    # 待爬取列表
    office_href_list = []
    for j in hospital_all_href_list:
        if j not in office_finish_href_set:
            office_href_list.append(j)

    return office_href_list


def get_office(pathname, href):
    url = 'https://www.haodf.com/hospital/%s/daifu.htm' % href

    # 获取页面内容
    res = requests.get(url, headers=headers)
    html = res.text
    html = BeautifulSoup(html, 'lxml')

    # 科室类型
    div_office_type = html.findAll('div', attrs={'class': 'intro_doc-nav-mod'})[0]

    # 全部科室类型名
    div_office_type_name_list = div_office_type.findAll('div', attrs={'class': 'de_title-mod'})
    office_type_name_list = []
    for j in div_office_type_name_list:
        office_type_name = re.findall(r'>(.+?)<', str(j))[0]
        office_type_name_list.append(office_type_name)

    # 按科室类型获取科室
    for j in range(len(office_type_name_list)):
        # 科室
        ul_office = div_office_type.findAll('ul', attrs={'class': 'de_content-mod'})[j]
        a_list = ul_office.findAll('a', attrs={'href': re.compile(r'daifu')})

        office_href_list = []
        office_name_list = []
        for k in a_list:
            office_href = re.findall(r'hospital/.+?/(.+?)/daifu\.htm', str(k))[0]
            name = re.findall(r'>(.+?)<', str(k))[0]
            office_href_list.append(office_href)
            office_name_list.append(office_type_name_list[j] + '|' + name)
        # 写入医院数据
        write_doc(pathname,
                  href, office_href_list, office_name_list)


def write_table(pathname):

    # 判断是否已经写入表头
    try:
        with open(pathname + 'office.csv', 'r') as office_reader:
            if office_reader.readline() != '':
                return
            else:
                # 写入表头
                with open(pathname + 'office.csv', 'a') as office:
                    office_writer = csv.writer(office)

                    # 写入字段
                    fields = ['href', 'office_href', 'office_name']
                    office_writer.writerow(fields)
    except:
        # 写入表头
        with open(pathname + 'office.csv', 'a') as office:
            office_writer = csv.writer(office)

            # 写入字段
            fields = ['href', 'office_href', 'office_name']
            office_writer.writerow(fields)


# 'href', 'office'
def write_doc(pathname,
              href, office_href_list, office_name_list):
    # 医院细节信息
    with open(pathname + 'office.csv', 'a') as office:
        office_writer = csv.writer(office)

        # 写入行数据
        for j in range(len(office_href_list)):
            office_writer.writerow([href, office_href_list[j], office_name_list[j]])


def write_finish(pathname, href):
    with open(pathname + 'office_finish.csv', 'a') as office_finish:
        office_finish_writer = csv.writer(office_finish)

        # 写入行数据
        office_finish_writer.writerow([href])


def write_error(pathname, href):
    with open(pathname + 'office_error.csv', 'a') as office_error:
        office_error_writer = csv.writer(office_error)

        # 写入行数据
        office_error_writer.writerow([href])


class MyThread(threading.Thread):
    def __init__(self, pathname, office_href_list):
        threading.Thread.__init__(self)
        self.pathname = pathname
        self.office_href_list = office_href_list

    def run(self):
        # 线程名
        thread_name = threading.current_thread().name

        finish = 0
        error = 0

        for j in self.office_href_list:
            start = time.time()

            print('--------------------------------------------------------------------')
            time.sleep(randint(2, 5))
            try:
                # 获取医院细节信息
                get_office(self.pathname, j)

                # 写入成功
                write_finish(self.pathname, j)

                finish = finish + 1
                print('线程(%s):已完成%s个医院!' % (thread_name, finish))
            except:
                os.system('spd-say "error"')
                print('\033[5;30;47m【错误：%s】\033[0m获取数据出现异常！' % j)

                # 写入错误
                write_error(self.pathname, j)

                error = error + 1
                print('线程(%s):已错误%s个医院!' % (thread_name, error))

                continue
            end = time.time()
            print('time:%s' % str(end - start))


if __name__ == '__main__':
    my_pathname = '../data/'

    # 写入表头
    write_table(my_pathname)

    # 获取待爬取列表
    my_office_href_list = read_doc(my_pathname)

    # 将医院分成5等份
    my_office_href_list_1 = my_office_href_list[
                              int(len(my_office_href_list) / 5) * 0: int(len(my_office_href_list) / 5) * 1]
    my_office_href_list_2 = my_office_href_list[
                              int(len(my_office_href_list) / 5) * 1: int(len(my_office_href_list) / 5) * 2]
    my_office_href_list_3 = my_office_href_list[
                              int(len(my_office_href_list) / 5) * 2: int(len(my_office_href_list) / 5) * 3]
    my_office_href_list_4 = my_office_href_list[
                              int(len(my_office_href_list) / 5) * 3: int(len(my_office_href_list) / 5) * 4]
    my_office_href_list_5 = my_office_href_list[int(len(my_office_href_list) / 5) * 4: len(my_office_href_list)]

    # 执行多线程
    t1 = MyThread(pathname=my_pathname, office_href_list=my_office_href_list_1)
    t2 = MyThread(pathname=my_pathname, office_href_list=my_office_href_list_2)
    t3 = MyThread(pathname=my_pathname, office_href_list=my_office_href_list_3)
    t4 = MyThread(pathname=my_pathname, office_href_list=my_office_href_list_4)
    t5 = MyThread(pathname=my_pathname, office_href_list=my_office_href_list_5)

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
