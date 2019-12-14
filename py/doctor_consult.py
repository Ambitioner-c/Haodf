# _*_ coding : UTF-8 _*_
# author : cfl
# time   : 2019/12/14 下午21:02
"""
author: cfl
    获取医生咨询信息
"""
import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import threading
import os
from random import randint
from time import sleep


Headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/78.0.3904.108 Safari/537.36'}


def get_doctor_consult(pathname, hospital_href, office_href):
    """
    获取医生咨询信息
    :param pathname:
    :param hospital_href:
    :param office_href:
    :return:
    """
    # 遍历，如果获取不到数据，则说明该页无医生信息
    page = 0
    while True:
        page = page + 1
        url = 'https://www.haodf.com/hospital/%s/%s/daifu.htm?p=%s' % (hospital_href, office_href, str(page))

        # 获取页面内容
        sleep(randint(2, 5))
        html = requests.get(url, headers=Headers).text
        html = BeautifulSoup(html, 'lxml')

        # 通过请求医院名，检验页面是否正常加载
        try:
            div = html.findAll('div', attrs={'id': re.compile('headpA_blue')})[0]
        except:
            sleep(30)

            # 获取页面内容
            html = requests.get(url, headers=Headers).text
            html = BeautifulSoup(html, 'lxml')

        # 医生列表
        try:
            table_doctor = html.findAll('table', attrs={'id': 'doc_list_index'})[0]

            doctor_room_list = []
            consult_list = []
            consults_list = []

            tr_doctor_list = table_doctor.findAll('tr')[1:]
            for j in tr_doctor_list:
                # 主页id
                doctor_room = re.findall(r'//(.+?)\.haodf\.com', str(j))[0]

                # 咨询情况
                td_consult = j.findAll('td', attrs={'class': re.compile('td_hf')})[0]
                consult = re.findall(r'>(\d+)</span>', str(td_consult))[0]
                consults = re.findall(r'>(\d+)</span>', str(td_consult))[1]

                doctor_room_list.append(doctor_room)
                consult_list.append(consult)
                consults_list.append(consults)

            now = time.asctime(time.localtime(time.time()))
            write_doc(pathname,
                      doctor_room_list,
                      consult_list, consults_list, now)
        except:
            break


def read_doc(pathname):
    """
    读取待爬列表
    :param pathname:
    :return: hospital_href_list, office_href_list
    """
    # 全列表
    hospital_all_href_list = []
    office_all_href_list = []
    hospital_office_all_reader_list = csv.reader(open(pathname + 'office.csv', 'r'))
    # 删掉第一行
    n = 0
    for j in hospital_office_all_reader_list:
        if n != 0:
            hospital_all_href_list.append(j[0])
            office_all_href_list.append(j[1])
        n += 1

    # 已完成列表
    try:
        office_finish_href_list = []
        office_finish_reader_list = csv.reader(open(pathname + 'doctor_consult_finish.csv', 'r'))
        for j in office_finish_reader_list:
            office_finish_href_list.append(j[0])
        office_finish_href_set = set(office_finish_href_list)
    except:
        office_finish_href_list = []
        office_finish_href_set = set(office_finish_href_list)

    # 待爬取列表
    hospital_href_list = []
    office_href_list = []
    for j in range(len(office_all_href_list)):
        if office_all_href_list[j] not in office_finish_href_set:
            hospital_href_list.append(hospital_all_href_list[j])
            office_href_list.append(office_all_href_list[j])

    return hospital_href_list, office_href_list


def write_table(pathname):
    """
    写入表头
    :param pathname:
    :return
    """
    # 判断是否已经写入表头
    try:
        with open(pathname + 'doctor_consult.csv', 'r') as doctor_reader:
            if doctor_reader.readline() != '':
                return
            else:
                # 写入表头
                with open(pathname + 'doctor_consult.csv', 'a') as doctor:
                    doctor_writer = csv.writer(doctor)

                    # 写入字段
                    fields = ['doctor_room',
                              'consult', 'consults', 'now']
                    doctor_writer.writerow(fields)
    except:
        # 写入表头
        with open(pathname + 'doctor_consult.csv', 'a') as doctor:
            doctor_writer = csv.writer(doctor)

            # 写入字段
            fields = ['doctor_room',
                      'consult', 'consults', 'now']
            doctor_writer.writerow(fields)


# 'doctor_room_list',
# 'consult_list', 'consults_list', 'now'
def write_doc(pathname,
              doctor_room_list,
              consult_list, consults_list, now):
    """
    写入文件
    :param pathname:
    :param doctor_room_list:
    :param consult_list:
    :param consults_list:
    :param now:
    :return
    """
    # 医生
    with open(pathname + 'doctor_consult.csv', 'a') as doctor:
        doctor_writer = csv.writer(doctor)

        # 写入行数据
        for j in range(len(doctor_room_list)):
            doctor_writer.writerow([doctor_room_list[j],
                                    consult_list[j], consults_list[j], now])


def write_finish(pathname, office_href):
    """
    写入成功
    :param pathname:
    :param office_href:
    :return:
    """
    with open(pathname + 'doctor_consult_finish.csv', 'a') as doctor_consult_finish:
        doctor_consult_finish_writer = csv.writer(doctor_consult_finish)

        # 写入行数据
        doctor_consult_finish_writer.writerow([office_href])


def write_error(pathname, office_href):
    """
    写入成功
    :param pathname:
    :param office_href:
    :return:
    """
    with open(pathname + 'doctor_consult_error.csv', 'a') as doctor_consult_error:
        doctor_consult_error_writer = csv.writer(doctor_consult_error)

        # 写入行数据
        doctor_consult_error_writer.writerow([office_href])


class MyThread(threading.Thread):
    def __init__(self, pathname, hospital_href_list, office_href_list):
        threading.Thread.__init__(self)
        self.pathname = pathname
        self.hospital_href_list = hospital_href_list
        self.office_href_list = office_href_list

    def run(self):
        # 线程名
        thread_name = threading.current_thread().name

        finish = 0
        error = 0

        for j in range(len(self.office_href_list)):
            start = time.time()

            print('--------------------------------------------------------------------')
            time.sleep(randint(2, 5))
            try:
                # 获取医院细节信息
                get_doctor_consult(self.pathname, self.hospital_href_list[j], self.office_href_list[j])

                # 写入成功
                write_finish(self.pathname, self.office_href_list[j])

                finish = finish + 1
                print('线程(%s):已完成%s个office!' % (thread_name, finish))
            except:
                os.system('spd-say "error"')
                print('\033[5;30;47m【错误：%s】\033[0m获取数据出现异常！' % self.office_href_list[j])

                # 写入错误
                write_error(self.pathname, self.office_href_list[j])

                error = error + 1
                print('线程(%s):已错误%s个office!' % (thread_name, error))

                continue
            end = time.time()
            print('time:%s' % str(end - start))


if __name__ == '__main__':
    my_pathname = '../data/'

    # 写入表头
    write_table(my_pathname)

    # 获取待爬取列表
    my_hospital_href_list, my_office_href_list = read_doc(my_pathname)

    # 将医院分成5等份
    my_hospital_href_list_1 = my_hospital_href_list[int(len(my_hospital_href_list)/5)*0:int(len(my_hospital_href_list)/5)*1]
    my_hospital_href_list_2 = my_hospital_href_list[int(len(my_hospital_href_list)/5)*1:int(len(my_hospital_href_list)/5)*2]
    my_hospital_href_list_3 = my_hospital_href_list[int(len(my_hospital_href_list)/5)*2:int(len(my_hospital_href_list)/5)*3]
    my_hospital_href_list_4 = my_hospital_href_list[int(len(my_hospital_href_list)/5)*3:int(len(my_hospital_href_list)/5)*4]
    my_hospital_href_list_5 = my_hospital_href_list[int(len(my_hospital_href_list)/5)*4:len(my_hospital_href_list)]

    # 将科室分成5等份
    my_office_href_list_1 = my_office_href_list[int(len(my_office_href_list)/5)*0:int(len(my_office_href_list)/5)*1]
    my_office_href_list_2 = my_office_href_list[int(len(my_office_href_list)/5)*1:int(len(my_office_href_list)/5)*2]
    my_office_href_list_3 = my_office_href_list[int(len(my_office_href_list)/5)*2:int(len(my_office_href_list)/5)*3]
    my_office_href_list_4 = my_office_href_list[int(len(my_office_href_list)/5)*3:int(len(my_office_href_list)/5)*4]
    my_office_href_list_5 = my_office_href_list[int(len(my_office_href_list)/5)*4:len(my_office_href_list)]

    # 执行多线程
    t1 = MyThread(pathname=my_pathname, hospital_href_list=my_hospital_href_list_1, office_href_list=my_office_href_list_1)
    t2 = MyThread(pathname=my_pathname, hospital_href_list=my_hospital_href_list_2, office_href_list=my_office_href_list_2)
    t3 = MyThread(pathname=my_pathname, hospital_href_list=my_hospital_href_list_3, office_href_list=my_office_href_list_3)
    t4 = MyThread(pathname=my_pathname, hospital_href_list=my_hospital_href_list_4, office_href_list=my_office_href_list_4)
    t5 = MyThread(pathname=my_pathname, hospital_href_list=my_hospital_href_list_5, office_href_list=my_office_href_list_5)

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
