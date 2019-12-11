# _*_ coding : UTF-8 _*_
# author : cfl
# time   : 2019/12/10 下午8:58
"""
    获取医生信息中心页、临床经验
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


Headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'
                         ' AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/78.0.3904.108 Safari/537.36'}


def get_doctor_href(pathname, doctor_href):
    url = 'https://www.haodf.com/doctor/%s.htm' % doctor_href

    # 获取页面内容
    html = requests.get(url, headers=Headers).text
    html = BeautifulSoup(html, 'lxml')

    # 检验页面是否正常加载
    try:
        div_doctor_header = html.findAll('div', attrs={'id': 'bp_doctor_about'})[0]
    except:
        sleep(30)

        # 获取页面内容
        html = requests.get(url, headers=Headers).text
        html = BeautifulSoup(html, 'lxml')

    # 获取script代码
    scripts = html.findAll('script')

    bp_doctor_about = ''
    for i in scripts:
        if 'bp_doctor_about' in str(i):
            on_pagelet_arrive = re.findall(r'onPageletArrive\((.+?)\);</script>', str(i))[0].strip('{').strip('}')
            id_ = re.findall(r'"id":"(.+?)"', str(on_pagelet_arrive))[0]
            content = re.findall(r'"content":(.+?),"cssList"', str(on_pagelet_arrive))[0].strip('"').strip('\\n')
            bp_doctor_about = content

    bp_doctor_servicestar = ''
    for i in scripts:
        if 'bp_doctor_servicestar' in str(i):
            on_pagelet_arrive = re.findall(r'onPageletArrive\((.+?)\);</script>', str(i))[0].strip('{').strip('}')
            id_ = re.findall(r'"id":"(.+?)"', str(on_pagelet_arrive))[0]
            content = re.findall(r'"content":(.+?),"cssList"', str(on_pagelet_arrive))[0].strip('"').strip('\\n')
            bp_doctor_servicestar = content

    #
    # 信息
    get_info(pathname, doctor_href, bp_doctor_about, bp_doctor_servicestar)

    #
    # 临床
    get_clinic(pathname, doctor_href, bp_doctor_servicestar)


def get_info(pathname, doctor_href, bp_doctor_about, bp_doctor_servicestar):
    #
    # 推荐热度部分

    # 疗效满意度
    treatment = re.findall(r'\\u7597\\u6548\\u6ee1\\u610f\\u5ea6\\uff1a(.+?)<', str(bp_doctor_about))[0]
    if '暂无' == treatment.encode('utf-8').decode('unicode_escape'):
        treatment = ''
    # 态度满意度
    attitude = re.findall(r'\\u6001\\u5ea6\\u6ee1\\u610f\\u5ea6\\uff1a(.+?)<', str(bp_doctor_about))[0]
    if '暂无' == attitude.encode('utf-8').decode('unicode_escape'):
        attitude = ''
    # 累计帮助患者数
    helps = re.findall(r'\\u7d2f\\u8ba1\\u5e2e\\u52a9\\u60a3\\u8005\\u6570\\uff1a(.+?)<', str(bp_doctor_about))[0]
    if '暂无' == helps.encode('utf-8').decode('unicode_escape'):
        helps = ''
    # 近两周帮助患者数
    help_ = re.findall(r'\\u8fd1\\u4e24\\u5468\\u5e2e\\u52a9\\u60a3\\u8005\\u6570\\uff1a(.+?)<', str(bp_doctor_about))[0]
    if '暂无' == help_.encode('utf-8').decode('unicode_escape'):
        help_ = ''

    #
    # 临床经验部分
    try:
        # 诊治过的患者数
        diagnosis = re.findall(r'\\u8bca\\u6cbb\\u8fc7\\u7684\\u60a3\\u8005\\u6570\\uff1a(.+?)\\u4f8b<', str(bp_doctor_servicestar))[0]
        # 随访中的患者数
        follow = re.findall(r'\\u968f\\u8bbf\\u4e2d\\u7684\\u60a3\\u8005\\u6570\\uff1a(.+?)\\u4f8b<', str(bp_doctor_servicestar))[0]
    except:
        diagnosis = ''
        follow = ''

    now = time.asctime(time.localtime(time.time()))
    write_href_doc(pathname,
                   doctor_href,
                   treatment, attitude, helps, help_,
                   diagnosis, follow,
                   now)


def get_clinic(pathname, doctor_href, bp_doctor_servicestar):
    # 临床经验部分
    try:
        # 临床经验
        name_list = re.findall(r']\);\\">(.+?)<\\/a>', str(bp_doctor_servicestar))
        num_list = re.findall(r'\((\d+)\\u4f8b', str(bp_doctor_servicestar))

        clinic = ''
        for j in range(len(num_list)):
            clinic = clinic + name_list[j].encode('utf-8').decode('unicode_escape') \
                     + '(' + str(num_list[j]).replace('例', '') + ')' + '|'
        clinic = clinic.strip(")").strip("|")
    except:
        clinic = ''

    now = time.asctime(time.localtime(time.time()))
    write_clinic_doc(pathname,
                     doctor_href,
                     clinic,
                     now)


def read_doc(pathname):
    # 全列表
    doctor_href_all_list = []
    doctor_href_all_reader_list = csv.reader(open(pathname + 'doctor.csv', 'r'))
    # 删掉第一行
    n = 0
    for j in doctor_href_all_reader_list:
        if n != 0:
            doctor_href_all_list.append(j[1])
        n += 1

    # 已完成列表
    try:
        doctor_href_finish_list = []
        doctor_href_finish_reader_list = csv.reader(open(pathname + 'doctor_href_detail_finish.csv', 'r'))
        for j in doctor_href_finish_reader_list:
            doctor_href_finish_list.append(j[0])
        doctor_href_finish_set = set(doctor_href_finish_list)
    except:
        doctor_href_finish_list = []
        doctor_href_finish_set = set(doctor_href_finish_list)

    # 待爬取列表
    doctor_href_list = []
    for j in range(len(doctor_href_all_list)):
        if doctor_href_all_list[j] not in doctor_href_finish_set:
            doctor_href_list.append(doctor_href_all_list[j])

    return doctor_href_list


def write_href_table(pathname):
    # 判断是否已经写入表头
    try:
        with open(pathname + 'doctor_href_detail.csv', 'r') as doctor_href_detail_reader:
            if doctor_href_detail_reader.readline() != '':
                return
            else:
                # 写入表头
                with open(pathname + 'doctor_href_detail.csv', 'a') as doctor_href_detail:
                    doctor_href_detail_writer = csv.writer(doctor_href_detail)

                    # 写入字段
                    fields = ['doctor_href',
                              'treatment', 'attitude', 'helps', 'help',
                              'diagnosis', 'follow',
                              'now']
                    doctor_href_detail_writer.writerow(fields)
    except:
        # 写入表头
        with open(pathname + 'doctor_href_detail.csv', 'a') as doctor_href_detail:
            doctor_href_detail_writer = csv.writer(doctor_href_detail)

            # 写入字段
            fields = ['doctor_href',
                      'treatment', 'attitude', 'helps', 'help',
                      'diagnosis', 'follow',
                      'now']
            doctor_href_detail_writer.writerow(fields)


def write_clinic_table(pathname):
    # 判断是否已经写入表头
    try:
        with open(pathname + 'doctor_clinic_detail.csv', 'r') as doctor_clinic_detail_reader:
            if doctor_clinic_detail_reader.readline() != '':
                return
            else:
                # 写入表头
                with open(pathname + 'doctor_clinic_detail.csv', 'a') as doctor_clinic_detail:
                    doctor_clinic_detail_writer = csv.writer(doctor_clinic_detail)

                    # 写入字段
                    fields = ['doctor_href',
                              'clinic',
                              'now']
                    doctor_clinic_detail_writer.writerow(fields)
    except:
        # 写入表头
        with open(pathname + 'doctor_clinic_detail.csv', 'a') as doctor_clinic_detail:
            doctor_clinic_detail_writer = csv.writer(doctor_clinic_detail)

            # 写入字段
            fields = ['doctor_href',
                      'clinic',
                      'now']
            doctor_clinic_detail_writer.writerow(fields)


# 'doctor_href',
# 'treatment', 'attitude', 'helps', 'help',
# 'diagnosis', 'follow',
# 'now'
def write_href_doc(pathname,
                   doctor_href,
                   treatment, attitude, helps, help,
                   diagnosis, follow,
                   now):
    # 医生信息页
    with open(pathname + 'doctor_href_detail.csv', 'a') as doctor_href_detail:
        doctor_href_detail_writer = csv.writer(doctor_href_detail)

        # 写入行数据
        doctor_href_detail_writer.writerow([doctor_href,
                                            treatment, attitude, helps, help,
                                            diagnosis, follow,
                                            now])


# 'doctor_href',
# 'clinic',
# 'now'
def write_clinic_doc(pathname,
                     doctor_href,
                     clinic,
                     now):
    # 医生主页
    with open(pathname + 'doctor_clinic_detail.csv', 'a') as doctor_clinic_detail:
        doctor_clinic_detail_writer = csv.writer(doctor_clinic_detail)

        # 写入行数据
        doctor_clinic_detail_writer.writerow([doctor_href,
                                              clinic,
                                              now])


def write_finish(pathname, doctor_href):
    with open(pathname + 'doctor_href_detail_finish.csv', 'a') as doctor_href_detail_finish:
        doctor_href_detail_finish_writer = csv.writer(doctor_href_detail_finish)

        # 写入行数据
        doctor_href_detail_finish_writer.writerow([doctor_href])


def write_error(pathname, doctor_href):
    with open(pathname + 'doctor_href_detail_error.csv', 'a') as doctor_href_detail_error:
        doctor_href_detail_error_writer = csv.writer(doctor_href_detail_error)

        # 写入行数据
        doctor_href_detail_error_writer.writerow([doctor_href])


class MyThread(threading.Thread):
    def __init__(self, pathname, doctor_href_list):
        threading.Thread.__init__(self)
        self.pathname = pathname
        self.doctor_href_list = doctor_href_list

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
                get_doctor_href(self.pathname, self.doctor_href_list[j])

                # 写入成功
                write_finish(self.pathname, self.doctor_href_list[j])

                finish = finish + 1
                print('线程(%s):已完成%s个href、clinic!' % (thread_name, finish))
            except:
                os.system('spd-say "error"')
                print('\033[5;30;47m【错误：%s】\033[0m获取数据出现异常！' % self.doctor_href_list[j])

                # 写入错误
                write_error(self.pathname, self.doctor_href_list[j])

                error = error + 1
                print('线程(%s):已错误%s个href、clinic!' % (thread_name, error))

                continue
            end = time.time()
            print('time:%s' % str(end - start))


if __name__ == '__main__':
    my_pathname = '../data/'

    # 写入表头
    write_href_table(my_pathname)
    write_clinic_table(my_pathname)

    # 获取待爬取列表
    my_doctor_href_list = read_doc(my_pathname)

    # get_doctor_comment_vote(my_pathname, my_doctor_href_list[1])
    # get_doctor_href(my_pathname, 'DE4r0Fy0C9Luhnz9uxO5EkJ1SHSYhq37w')
    # write_finish(my_pathname, 'DE4r0Fy0C9Luhnz9uxO5EkJ1SHSYhq37w')

    # 将医生分成5等份
    my_doctor_href_list1 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*0:int(len(my_doctor_href_list)/5)*1]
    my_doctor_href_list2 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*1:int(len(my_doctor_href_list)/5)*2]
    my_doctor_href_list3 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*2:int(len(my_doctor_href_list)/5)*3]
    my_doctor_href_list4 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*3:int(len(my_doctor_href_list)/5)*4]
    my_doctor_href_list5 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*4:len(my_doctor_href_list)]

    # 执行多线程
    t1 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list1)
    t2 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list2)
    t3 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list3)
    t4 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list4)
    t5 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list5)

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
