"""
author:cfl
    获取医院信息.
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
        hospital_finish_href_list = []
        hospital_finish_reader_list = csv.reader(open(pathname + 'hospital_detail_finish.csv', 'r'))
        for j in hospital_finish_reader_list:
            hospital_finish_href_list.append(j[0])
        hospital_finish_href_set = set(hospital_finish_href_list)
    except:
        hospital_finish_href_list = []
        hospital_finish_href_set = set(hospital_finish_href_list)

    # 待爬取列表
    hospital_href_list = []
    for j in hospital_all_href_list:
        if j not in hospital_finish_href_set:
            hospital_href_list.append(j)

    return hospital_href_list


def get_hospital_detail(pathname, href):
    url = 'https://www.haodf.com/hospital/%s.htm' % href

    # 获取页面内容
    res = requests.get(url, headers=headers)
    html = res.text
    html = BeautifulSoup(html, 'lxml')

    # 标签
    span_label_list = html.findAll('span', attrs={'class': 'hospital-label-item'})
    label = ''
    for j in range(len(span_label_list)):
        label = label + '|' + span_label_list[j].text.replace('\n', '').replace(' ', '')
    label = label.strip('|')

    # 知名度
    p_popularity_list = html.findAll('p', attrs={'class': re.compile(r'hp?-i-item')})
    popularity = ''
    for j in range(len(p_popularity_list)):
        popularity = popularity + p_popularity_list[j].text.replace('\n', '').replace(' ', '')
    # 关注度排名
    attention = re.findall(r'关注度排名(.+?)累计访问量', popularity)[0]
    # 累计访问量
    visitor = re.findall(r'累计访问量(.+?)在线服务患者', popularity)[0]
    # 在线服务患者
    serve = re.findall(r'在线服务患者(.+?)两年内评价', popularity)[0]
    # 两年内评价
    evaluate = re.findall(r'好评(.+?)差评', popularity)[0]
    # 差评
    negative = re.findall(r'差评(.+?)患者满意度', popularity)[0]
    # 患者满意度
    satisfaction = re.findall(r'患者满意度(.+)', popularity)[0]

    # 影响力
    try:
        ul_influence_list = html.findAll('ul', attrs={'class': 'hospital-o-ul'})
        influence = ''
        for j in range(len(ul_influence_list)):
            influence = influence + ul_influence_list[j].text.replace('\n', '').replace(' ', '')

        influence = influence.replace('名', '名|').strip('|')
    except:
        influence = ''

    # 服务
    p_service_list = html.findAll('p', attrs={'class': re.compile(r'service-data')})
    span_service_list = html.findAll('span', attrs={'class': re.compile(r'service-data-num')})
    p_service = ''
    span_service = ''
    for j in p_service_list:
        p_service = p_service + j.text
    for j in span_service_list:
        span_service = span_service + j.text
    service = (p_service + span_service).replace('\n', '').replace(' ', '')
    # 在线
    try:
        online = re.findall(r'(\d+)位大夫在线', service)[0]
    except:
        online = ''
    try:
        online_num = re.findall(r'在线服务患者(\d+)位', service)[0]
    except:
        online_num = ''
    # 挂号
    try:
        registration = re.findall(r'(\d+)位大夫可挂号', service)[0]
    except:
        registration = ''
    try:
        registration_num = re.findall(r'可挂号服务患者(\d+)位', service)[0]
    except:
        registration_num = ''
    # 通话
    try:
        communicate = re.findall(r'(\d+)名大夫可通话', service)[0]
    except:
        communicate = ''
    try:
        communicate_num = re.findall(r'可通话服务患者(\d+)位', service)[0]
    except:
        communicate_num = ''

    # 科室、大夫
    span_office_doctor = html.findAll('span', attrs={'class': 'm-h-title-grey'})[0]
    office_doctor = span_office_doctor.text.replace('\n', '').replace(' ', '')
    try:
        office_num = re.findall(r'科室(\d+)个', office_doctor)[0]
    except:
        office_num = ''
    try:
        doctor_num = re.findall(r'大夫(\d+)人', office_doctor)[0]
    except:
        doctor_num = ''

    # 感谢信
    try:
        span_thanks = html.findAll('span', attrs={'class': 'm-h-t-num'})[0]
        thanks_num = span_thanks.text.replace('\n', '').replace(' ', '')
    except:
        thanks_num = ''

    # # 简介
    # url = 'https://www.haodf.com/hospital/%s/jieshao.htm' % href
    # res_introduce = requests.get(url, headers=headers)
    # html_introduce = res_introduce.text
    # html_introduce = BeautifulSoup(html_introduce, 'lxml')
    #
    # table_introduce = html_introduce.findAll('table', attrs={'class': 'czsj'})[0]
    #
    # table_introduce = table_introduce.text.replace(' ', '')
    write_doc(pathname,
              href, label,
              attention, visitor, serve, evaluate, negative, satisfaction, influence,
              online, online_num, registration, registration_num, communicate, communicate_num,
              office_num, doctor_num, thanks_num)


def write_table(pathname):

    # 判断是否已经写入表头
    try:
        with open(pathname + 'hospital_detail.csv', 'r') as hospital_detail_reader:
            if hospital_detail_reader.readline() != '':
                return
            else:
                # 写入表头
                with open(pathname + 'hospital_detail.csv', 'a') as hospital_detail:
                    hospital_detail_writer = csv.writer(hospital_detail)

                    # 写入字段
                    fields = ['href', 'label',
                              'attention', 'visitor', 'serve', 'evaluate', 'negative', 'satisfaction', 'influence',
                              'online', 'online_num', 'registration', 'registration_num', 'communicate', 'communicate_num',
                              'office_num', 'doctor_num', 'thanks_num',
                              'time']
                    hospital_detail_writer.writerow(fields)
    except:
        # 写入表头
        with open(pathname + 'hospital_detail.csv', 'a') as hospital_detail:
            hospital_detail_writer = csv.writer(hospital_detail)

            # 写入字段
            fields = ['href', 'label',
                      'attention', 'visitor', 'serve', 'evaluate', 'negative', 'satisfaction', 'influence',
                      'online', 'online_num', 'registration', 'registration_num', 'communicate', 'communicate_num',
                      'office_num', 'doctor_num', 'thanks_num',
                      'time']
            hospital_detail_writer.writerow(fields)


# 'href', 'label',
# 'attention', 'visitor', 'serve', 'evaluate', 'negative', 'satisfaction', 'influence',
# 'online', 'online_num', 'registration', 'registration_num', 'communicate', 'communicate_num',
# 'office_num', 'doctor_num', 'thanks_num',
# 'time'
def write_doc(pathname,
              href, label,
              attention, visitor, serve, evaluate, negative, satisfaction, influence,
              online, online_num, registration, registration_num, communicate, communicate_num,
              office_num, doctor_num, thanks_num):
    # 医院细节信息
    with open(pathname + 'hospital_detail.csv', 'a') as hospital_detail:
        hospital_detail_writer = csv.writer(hospital_detail)

        now = time.asctime(time.localtime(time.time()))
        # 写入行数据
        hospital_detail_writer.writerow([href, label,
                                         attention, visitor, serve, evaluate, negative, satisfaction, influence,
                                         online, online_num, registration, registration_num, communicate, communicate_num,
                                         office_num, doctor_num, thanks_num,
                                         now])
        print(now)


def write_finish(pathname, href):
    with open(pathname + 'hospital_detail_finish.csv', 'a') as hospital_detail_finish:
        hospital_detail_finish_writer = csv.writer(hospital_detail_finish)

        # 写入行数据
        hospital_detail_finish_writer.writerow([href])


def write_error(pathname, href):
    with open(pathname + 'hospital_detail_error.csv', 'a') as hospital_detail_error:
        hospital_detail_error_writer = csv.writer(hospital_detail_error)

        # 写入行数据
        hospital_detail_error_writer.writerow([href])


class MyThread(threading.Thread):
    def __init__(self, pathname, hospital_href_list):
        threading.Thread.__init__(self)
        self.pathname = pathname
        self.hospital_href_list = hospital_href_list

    def run(self):
        # 线程名
        thread_name = threading.current_thread().name

        finish = 0
        error = 0

        for j in self.hospital_href_list:
            start = time.time()

            print('--------------------------------------------------------------------')
            time.sleep(randint(2, 5))
            try:
                # 获取医院细节信息
                get_hospital_detail(self.pathname, j)

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
    my_hospital_href_list = read_doc(my_pathname)

    # 将医院分成5等份
    my_hospital_href_list_1 = my_hospital_href_list[
                              int(len(my_hospital_href_list) / 5) * 0: int(len(my_hospital_href_list) / 5) * 1]
    my_hospital_href_list_2 = my_hospital_href_list[
                              int(len(my_hospital_href_list) / 5) * 1: int(len(my_hospital_href_list) / 5) * 2]
    my_hospital_href_list_3 = my_hospital_href_list[
                              int(len(my_hospital_href_list) / 5) * 2: int(len(my_hospital_href_list) / 5) * 3]
    my_hospital_href_list_4 = my_hospital_href_list[
                              int(len(my_hospital_href_list) / 5) * 3: int(len(my_hospital_href_list) / 5) * 4]
    my_hospital_href_list_5 = my_hospital_href_list[int(len(my_hospital_href_list) / 5) * 4: len(my_hospital_href_list)]

    # 执行多线程
    t1 = MyThread(pathname=my_pathname, hospital_href_list=my_hospital_href_list_1)
    t2 = MyThread(pathname=my_pathname, hospital_href_list=my_hospital_href_list_2)
    t3 = MyThread(pathname=my_pathname, hospital_href_list=my_hospital_href_list_3)
    t4 = MyThread(pathname=my_pathname, hospital_href_list=my_hospital_href_list_4)
    t5 = MyThread(pathname=my_pathname, hospital_href_list=my_hospital_href_list_5)

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
