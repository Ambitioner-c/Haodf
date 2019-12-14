# _*_ coding : UTF-8 _*_
# author : cfl
# time   : 2019/12/14 下午8:58
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


def get_doctor_href(pathname, doctor_href, doctor_id):
    url = 'https://www.haodf.com/doctor/%s-all-servicestar.htm' % doctor_id

    # 获取页面内容
    html = requests.get(url, headers=Headers).text
    html = BeautifulSoup(html, 'lxml')

    # 通过请求医生姓名，检验页面是否正常加载
    try:
        h1 = html.findAll('h1', attrs={'class': re.compile('doctor-name')})[0]
    except:
        sleep(30)

        # 获取页面内容
        html = requests.get(url, headers=Headers).text
        html = BeautifulSoup(html, 'lxml')

    #
    # 信息
    get_info(pathname, doctor_href, html)

    #
    # 临床
    get_clinic(pathname, doctor_href, html)


def get_info(pathname, doctor_href, html):
    # 右边模块
    div_right = html.findAll('div', attrs={'class': re.compile('container-r')})[0]
    # 诊治后的患者数
    span_diagnosis = div_right.findAll('span', attrs={'class': re.compile('experience-data')})[1]
    diagnosis = re.findall(r'>(\d+)例<', str(span_diagnosis))[0]

    # 随访中的患者数
    span_follow = div_right.findAll('span', attrs={'class': re.compile('experience-data')})[2]
    follow = re.findall(r'>(\d+)例<', str(span_follow))[0]

    treatment = ''
    attitude = ''
    helps = ''
    help_ = ''
    now = time.asctime(time.localtime(time.time()))
    write_href_doc(pathname,
                   doctor_href,
                   treatment, attitude, helps, help_,
                   diagnosis, follow,
                   now)


def get_clinic(pathname, doctor_href, html):
    # 左边模块
    try:
        div_left = html.findAll('div', attrs={'class': re.compile('vote-type-con')})[0]
        # 临床经验
        clinic_list = re.findall(r'>(.+?)</a>', str(div_left))

        clinic = ''
        for j in range(1, len(clinic_list)):
            clinic = clinic + clinic_list[j] + '|'
        clinic = clinic.strip("|")
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
    doctor_id_all_list = []
    doctor_href_id_all_reader_list = csv.reader(open(pathname + 'doctor_home_detail.csv', 'r'))
    # 删掉第一行
    n = 0
    for j in doctor_href_id_all_reader_list:
        if n != 0:
            doctor_href_all_list.append(j[0])
            doctor_id_all_list.append(j[1])
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
    doctor_id_list = []
    doctor_href_list = []
    for j in range(len(doctor_href_all_list)):
        if doctor_href_all_list[j] not in doctor_href_finish_set:
            doctor_href_list.append(doctor_href_all_list[j])
            doctor_id_list.append(doctor_id_all_list[j])

    return doctor_href_list, doctor_id_list


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
    def __init__(self, pathname, doctor_href_list, doctor_id_list):
        threading.Thread.__init__(self)
        self.pathname = pathname
        self.doctor_href_list = doctor_href_list
        self.doctor_id_list = doctor_id_list

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
                get_doctor_href(self.pathname, self.doctor_href_list[j], self.doctor_id_list[j])

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
    my_doctor_href_list, my_doctor_id_list = read_doc(my_pathname)

    # get_doctor_comment_vote(my_pathname, my_doctor_href_list[1])
    # get_doctor_href(my_pathname, 'DE4r0BCkuHzdei2EkeRwE-9BS0ak-', '294647')
    # write_finish(my_pathname, 'DE4r0Fy0C9Luhnz9uxO5EkJ1SHSYhq37w')

    # 将医生分成5等份
    my_doctor_href_list1 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*0:int(len(my_doctor_href_list)/5)*1]
    my_doctor_href_list2 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*1:int(len(my_doctor_href_list)/5)*2]
    my_doctor_href_list3 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*2:int(len(my_doctor_href_list)/5)*3]
    my_doctor_href_list4 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*3:int(len(my_doctor_href_list)/5)*4]
    my_doctor_href_list5 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*4:len(my_doctor_href_list)]

    my_doctor_id_list1 = my_doctor_id_list[int(len(my_doctor_id_list)/5)*0:int(len(my_doctor_id_list)/5)*1]
    my_doctor_id_list2 = my_doctor_id_list[int(len(my_doctor_id_list)/5)*1:int(len(my_doctor_id_list)/5)*2]
    my_doctor_id_list3 = my_doctor_id_list[int(len(my_doctor_id_list)/5)*2:int(len(my_doctor_id_list)/5)*3]
    my_doctor_id_list4 = my_doctor_id_list[int(len(my_doctor_id_list)/5)*3:int(len(my_doctor_id_list)/5)*4]
    my_doctor_id_list5 = my_doctor_id_list[int(len(my_doctor_id_list)/5)*4:len(my_doctor_id_list)]

    # 执行多线程
    t1 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list1, doctor_id_list=my_doctor_id_list1)
    t2 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list2, doctor_id_list=my_doctor_id_list2)
    t3 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list3, doctor_id_list=my_doctor_id_list3)
    t4 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list4, doctor_id_list=my_doctor_id_list4)
    t5 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list5, doctor_id_list=my_doctor_id_list5)

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
