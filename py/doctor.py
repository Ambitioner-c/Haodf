"""
author: cfl
    获取医生列表。
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
        office_finish_reader_list = csv.reader(open(pathname + 'doctor_finish.csv', 'r'))
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


def get_doctor(pathname, hospital_href, office_href):
    # 遍历5页数，如果获取不到数据，则说明该页无医生信息
    for j in range(1, 6):
        url = 'https://www.haodf.com/hospital/%s/%s/daifu.htm?p=%s' % (hospital_href, office_href, str(j))

        # 获取页面内容
        res = requests.get(url, headers=headers)
        html = res.text
        html = BeautifulSoup(html, 'lxml')

        # 医生列表
        try:
            table_doctor = html.findAll('table', attrs={'id': 'doc_list_index'})[0]

            # 全部医生
            td_doctor_list = table_doctor.findAll('td', attrs={'class': 'tda'})
            doctor_href_list = []
            doctor_home_list = []
            doctor_name_list = []
            for k in td_doctor_list:
                doctor_href = re.findall(r'doctor/(.+?)\.htm', str(k))[0]
                doctor_home = re.findall(r'//(.+?)\.haodf\.com', str(k))[1]
                doctor_name = re.findall(r'">(.+?)</a>', str(k))[0]
                doctor_href_list.append(doctor_href)
                doctor_home_list.append(doctor_home)
                doctor_name_list.append(doctor_name)
            write_doc(pathname,
                      office_href, doctor_href_list, doctor_home_list, doctor_name_list)
        except:
            break


def write_table(pathname):

    # 判断是否已经写入表头
    try:
        with open(pathname + 'doctor.csv', 'r') as doctor_reader:
            if doctor_reader.readline() != '':
                return
            else:
                # 写入表头
                with open(pathname + 'doctor.csv', 'a') as doctor:
                    doctor_writer = csv.writer(doctor)

                    # 写入字段
                    fields = ['office_href', 'doctor_href', 'doctor_room', 'doctor_name']
                    doctor_writer.writerow(fields)
    except:
        # 写入表头
        with open(pathname + 'doctor.csv', 'a') as doctor:
            doctor_writer = csv.writer(doctor)

            # 写入字段
            fields = ['office_href', 'doctor_href', 'doctor_room', 'doctor_name']
            doctor_writer.writerow(fields)


# 'office_href', 'doctor_href', 'doctor_room'
def write_doc(pathname,
              office_href, doctor_href_list, doctor_room_list, doctor_name_list):
    # 医生
    with open(pathname + 'doctor.csv', 'a') as doctor:
        doctor_writer = csv.writer(doctor)

        # 写入行数据
        for j in range(len(doctor_href_list)):
            doctor_writer.writerow([office_href, doctor_href_list[j], doctor_room_list[j], doctor_name_list[j]])


def write_finish(pathname, office_href):
    with open(pathname + 'doctor_finish.csv', 'a') as doctor_finish:
        doctor_finish_writer = csv.writer(doctor_finish)

        # 写入行数据
        doctor_finish_writer.writerow([office_href])


def write_error(pathname, office_href):
    with open(pathname + 'doctor_error.csv', 'a') as doctor_error:
        doctor_error_writer = csv.writer(doctor_error)

        # 写入行数据
        doctor_error_writer.writerow([office_href])


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
                get_doctor(self.pathname, self.hospital_href_list[j], self.office_href_list[j])

                # 写入成功
                write_finish(self.pathname, self.office_href_list[j])

                finish = finish + 1
                print('线程(%s):已完成%s个医院!' % (thread_name, finish))
            except:
                os.system('spd-say "error"')
                print('\033[5;30;47m【错误：%s】\033[0m获取数据出现异常！' % j)

                # 写入错误
                write_error(self.pathname, self.office_href_list[j])

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
