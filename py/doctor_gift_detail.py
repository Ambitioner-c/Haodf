# _*_ coding : UTF-8 _*_
# author : cfl
# time   : 2019/12/11 下午20:45
"""
author: cfl
    获取医生的礼物信息。
"""
from bs4 import BeautifulSoup
import re
import csv
import time
import threading
import os
import requests
from time import sleep
from random import randint


Headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/78.0.3904.108 Safari/537.36'}


def get_doctor_gift(pathname, doctor_href, doctor_home):
    url = 'https://%s.haodf.com/present/presentnavigation' % doctor_home

    # 获取页面内容
    html = requests.get(url, headers=Headers).text
    html = BeautifulSoup(html, 'lxml')

    # 检验页面是否正常加载
    try:
        div = html.findAll('div', attrs={'class': re.compile('doc_title')})[0]
    except:
        sleep(30)

        # 获取页面内容
        html = requests.get(url, headers=Headers).text
        html = BeautifulSoup(html, 'lxml')

    try:
        # 无礼物
        div_gift = html.findAll('div', attrs={'class': re.compile(r'gift_none')})[0]
        return
    except:
        # 礼物列表
        li_gift_list = []
        ul_gift = html.findAll('ul', attrs={'class': re.compile(r'gift_wall_main')})[0]
        li_gift_list.extend(ul_gift.findAll('li'))
        try:
            ul_gift_hidden = html.findAll('ul', attrs={'id': re.compile(r'hasShowHidden')})[0]
            li_gift_list.extend(ul_gift_hidden.findAll('li'))
        except:
            li_gift_list.extend([])

        gifts = ''
        for j in li_gift_list:
            p_name_num = j.findAll('p', attrs={'class': 'gift_name'})[0]

            # 礼物名
            name = re.findall(r'>(.+?)\(', str(p_name_num))[0]

            # 礼物数量
            span_num = p_name_num.findAll('span')[0]
            num = re.findall(r'>(.+?)<', str(span_num))[0]

            gift = name + '(' + num + ')'
            gifts = gifts + gift + '|'
        gifts = gifts.strip('|')

        now = time.asctime(time.localtime(time.time()))
        write_gift_doc(pathname,
                       doctor_href,
                       gifts,
                       now)


def read_doc(pathname):
    # 全列表
    doctor_href_all_list = []
    doctor_home_all_list = []
    doctor_home_all_reader_list = csv.reader(open(pathname + 'doctor.csv', 'r'))
    # 删掉第一行
    n = 0
    for j in doctor_home_all_reader_list:
        if n != 0:
            doctor_href_all_list.append(j[1])
            doctor_home_all_list.append(j[2])
        n += 1

    # 已完成列表
    try:
        doctor_home_finish_list = []
        doctor_home_finish_reader_list = csv.reader(open(pathname + 'doctor_gift_detail_finish.csv', 'r'))
        for j in doctor_home_finish_reader_list:
            doctor_home_finish_list.append(j[0])
        doctor_home_finish_set = set(doctor_home_finish_list)
    except:
        doctor_home_finish_list = []
        doctor_home_finish_set = set(doctor_home_finish_list)

    # 待爬取列表
    doctor_href_list = []
    doctor_home_list = []
    for j in range(len(doctor_home_all_list)):
        if doctor_href_all_list[j] not in doctor_home_finish_set:
            doctor_href_list.append(doctor_href_all_list[j])
            doctor_home_list.append(doctor_home_all_list[j])

    return doctor_href_list, doctor_home_list


def write_gift_table(pathname):
    # 判断是否已经写入表头
    try:
        with open(pathname + 'doctor_gift_detail.csv', 'r') as doctor_gift_detail_reader:
            if doctor_gift_detail_reader.readline() != '':
                return
            else:
                # 写入表头
                with open(pathname + 'doctor_gift_detail.csv', 'a') as doctor_gift_detail:
                    doctor_gift_detail_writer = csv.writer(doctor_gift_detail)

                    # 写入字段
                    fields = ['doctor_href',
                              'gifts',
                              'now']
                    doctor_gift_detail_writer.writerow(fields)
    except:
        # 写入表头
        with open(pathname + 'doctor_gift_detail.csv', 'a') as doctor_gift_detail:
            doctor_gift_detail_writer = csv.writer(doctor_gift_detail)

            # 写入字段
            fields = ['doctor_href',
                      'gifts',
                      'now']
            doctor_gift_detail_writer.writerow(fields)


# 'doctor_href',
# 'gift',
# 'now'
def write_gift_doc(pathname,
                   doctor_href,
                   gifts,
                   now):
    # 文章页
    with open(pathname + 'doctor_gift_detail.csv', 'a') as doctor_gift_detail:
        doctor_gift_detail_writer = csv.writer(doctor_gift_detail)

        # 写入行数据
        doctor_gift_detail_writer.writerow([doctor_href,
                                            gifts,
                                            now])


def write_finish(pathname, doctor_href):
    with open(pathname + 'doctor_gift_detail_finish.csv', 'a') as doctor_gift_detail_finish:
        doctor_gift_detail_finish_writer = csv.writer(doctor_gift_detail_finish)

        # 写入行数据
        doctor_gift_detail_finish_writer.writerow([doctor_href])


def write_error(pathname, doctor_href):
    with open(pathname + 'doctor_gift_detail_error.csv', 'a') as doctor_gift_detail_error:
        doctor_gift_detail_error_writer = csv.writer(doctor_gift_detail_error)

        # 写入行数据
        doctor_gift_detail_error_writer.writerow([doctor_href])


class MyThread(threading.Thread):
    def __init__(self, pathname, doctor_href_list, doctor_home_list):
        threading.Thread.__init__(self)
        self.pathname = pathname
        self.doctor_href_list = doctor_href_list
        self.doctor_home_list = doctor_home_list

    def run(self):
        # 线程名
        thread_name = threading.current_thread().name

        finish = 0
        error = 0

        for j in range(len(self.doctor_href_list)):
            start = time.time()

            print('--------------------------------------------------------------------')
            sleep(randint(2, 5))
            try:
                # 获取医院细节信息
                get_doctor_gift(self.pathname, self.doctor_href_list[j], self.doctor_home_list[j])

                # 写入成功
                write_finish(self.pathname, self.doctor_href_list[j])

                finish = finish + 1
                print('线程(%s):已完成%s个医生!' % (thread_name, finish))
            except:
                os.system('spd-say "error"')
                print('\033[5;30;47m【错误：%s】\033[0m获取数据出现异常！' % j)

                # 写入错误
                write_error(self.pathname, self.doctor_href_list[j])

                error = error + 1
                print('线程(%s):已错误%s个医生!' % (thread_name, error))

                continue
            end = time.time()
            print('time:%s' % str(end - start))


if __name__ == '__main__':
    my_pathname = '../data/'

    # 写入表头
    write_gift_table(my_pathname)

    # 获取待爬取列表
    my_doctor_href_list, my_doctor_home_list = read_doc(my_pathname)

    # get_doctor_gift(my_pathname, my_doctor_href_list[0], my_doctor_home_list[0])
    # get_doctor_gift(my_pathname, 'DE4r0Fy0C9LuZMTNhlwc224tMuLDQvLT1', 'zhongjia217')
    # write_finish(my_pathname, 'DE4r0Fy0C9LuZMTNhlwc224tMuLDQvLT1')

    # 将医生分成5等份
    my_doctor_href_list1 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*0:int(len(my_doctor_href_list)/5)*1]
    my_doctor_href_list2 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*1:int(len(my_doctor_href_list)/5)*2]
    my_doctor_href_list3 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*2:int(len(my_doctor_href_list)/5)*3]
    my_doctor_href_list4 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*3:int(len(my_doctor_href_list)/5)*4]
    my_doctor_href_list5 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*4:len(my_doctor_href_list)]

    my_doctor_home_list1 = my_doctor_home_list[int(len(my_doctor_home_list)/5)*0:int(len(my_doctor_home_list)/5)*1]
    my_doctor_home_list2 = my_doctor_home_list[int(len(my_doctor_home_list)/5)*1:int(len(my_doctor_home_list)/5)*2]
    my_doctor_home_list3 = my_doctor_home_list[int(len(my_doctor_home_list)/5)*2:int(len(my_doctor_home_list)/5)*3]
    my_doctor_home_list4 = my_doctor_home_list[int(len(my_doctor_home_list)/5)*3:int(len(my_doctor_home_list)/5)*4]
    my_doctor_home_list5 = my_doctor_home_list[int(len(my_doctor_home_list)/5)*4:len(my_doctor_home_list)]

    # 执行多线程
    t1 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list1, doctor_home_list=my_doctor_home_list1)
    t2 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list2, doctor_home_list=my_doctor_home_list2)
    t3 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list3, doctor_home_list=my_doctor_home_list3)
    t4 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list4, doctor_home_list=my_doctor_home_list4)
    t5 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list5, doctor_home_list=my_doctor_home_list5)

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
