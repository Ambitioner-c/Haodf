# _*_ coding : UTF-8 _*_
# author : cfl
# time   : 2019/12/12 下午12:32
"""
author: cfl
    获取医生的文章信息
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


def get_doctor_article(pathname, doctor_href, doctor_home):
    """
    获取医生文章信息，并写入文件
    :param pathname:
    :param doctor_href:
    :param doctor_home:
    :return:
    """
    page = 0
    while True:
        # 一直循环遍历，直到无内容
        page = page + 1
        url = 'https://%s.haodf.com/lanmu_%s' % (doctor_home, str(page))

        # 获取页面内容
        html = requests.get(url, headers=Headers).text
        # 这里去掉</html>，是因为返回结果中只有一个<html>，却有两个</html>，导致BeautifulSoup无法解析
        html = html.replace('</html>', '')
        html = BeautifulSoup(html, 'lxml')

        # 通过请求医生姓名，检验页面是否正常加载
        try:
            h1 = html.findAll('h1', attrs={'class': re.compile('doctor-name')})[0]
        except:
            sleep(30)

            # 获取页面内容
            html = requests.get(url, headers=Headers).text
            html = html.replace('</html>', '')
            html = BeautifulSoup(html, 'lxml')

        try:
            # 无文章，则跳出循环
            span_hint = html.findAll('span', attrs={'class': re.compile(r's_hint')})[0]
            return
        except:
            # 文章列表
            ul_article = html.findAll('ul', attrs={'class': 'article_ul'})[0]
            li_article_list = ul_article.findAll('li')
            for j in li_article_list:
                #
                # 文章名部分
                p_title = j.findAll('p', attrs={'class': 'art_title'})[0]

                # 文章类型
                type_ = re.findall(r'\[(....)', str(p_title))[0]

                # 文章id、标题
                a_article_id_title = p_title.findAll('a', attrs={'class': 'art_t'})[0]
                # 文章id
                article_id = re.findall(r'id="(.+?)"', str(a_article_id_title))[0]
                # 标题
                title = re.findall(r'>(.+?)</a>', str(a_article_id_title))[0].replace(',', '，')

                # 转载
                span_reprint = j.findAll('span', attrs={'class': 'pl5'})[0]
                if '转载' in str(span_reprint):
                    reprint = '1'
                else:
                    reprint = '0'

                # 置顶
                try:
                    span_stick = j.findAll('span', attrs={'class': 'article_recommend'})[0]
                    stick = '1'
                except:
                    stick = '0'

                #
                # 阅读部分
                p_read = j.findAll('p', attrs={'class': 'read_article'})[0]

                # 已读人数
                try:
                    read = re.findall(r'(\d+)人已', str(p_read))[0]
                except:
                    read = '0'

                # 评价数
                try:
                    evaluate = re.findall(r'(\d+)条评价', str(p_read))[0]
                except:
                    evaluate = '0'

                # 好评率
                try:
                    good = re.findall(r'(\d+%)好评率', str(p_read))[0]
                except:
                    good = '0'

                # 付费
                try:
                    buy = re.findall(r'付费', str(p_read))[0]
                    buy = '1'
                except:
                    buy = '0'

                # 发表时间
                time_ = re.findall(r'于(.+?)</span>', str(p_read))[0].replace(' ', '')

                now = time.asctime(time.localtime(time.time()))
                write_article_doc(pathname,
                                  doctor_href, article_id,
                                  type_, reprint, stick, title,
                                  read, evaluate, good, buy, time_,
                                  now)


def read_doc(pathname):
    """
    读取带爬列表
    :param pathname:
    :return: doctor_href_list, doctor_home_list
    """
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
        doctor_home_finish_reader_list = csv.reader(open(pathname + 'doctor_article_detail_finish.csv', 'r'))
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


def write_article_table(pathname):
    """
    写入文章表头
    :param pathname:
    :return:
    """
    # 判断是否已经写入表头
    try:
        with open(pathname + 'doctor_article_detail.csv', 'r') as doctor_article_detail_reader:
            if doctor_article_detail_reader.readline() != '':
                return
            else:
                # 写入表头
                with open(pathname + 'doctor_article_detail.csv', 'a') as doctor_article_detail:
                    doctor_article_detail_writer = csv.writer(doctor_article_detail)

                    # 写入字段
                    fields = ['doctor_href', 'article_id',
                              'type', 'reprint', 'stick', 'title',
                              'read', 'evaluate', 'good', 'buy', 'time',
                              'now']
                    doctor_article_detail_writer.writerow(fields)
    except:
        # 写入表头
        with open(pathname + 'doctor_article_detail.csv', 'a') as doctor_article_detail:
            doctor_article_detail_writer = csv.writer(doctor_article_detail)

            # 写入字段
            fields = ['doctor_href', 'article_id',
                      'type', 'reprint', 'stick', 'title',
                      'read', 'evaluate', 'good', 'buy', 'time',
                      'now']
            doctor_article_detail_writer.writerow(fields)


# 'doctor_href', 'article_id',
# 'type_', 'reprint', 'stick', 'title',
# 'read', 'evaluate', 'good', 'buy', 'num', 'time_',
# 'now'
def write_article_doc(pathname,
                      doctor_href, article_id,
                      type_, reprint, stick, title,
                      read, evaluate, good, buy, time_,
                      now):
    """
    写入文章文件
    :param pathname:
    :param doctor_href:
    :param article_id:
    :param type_:
    :param reprint:
    :param stick:
    :param title:
    :param read:
    :param evaluate:
    :param good:
    :param buy:
    :param time_:
    :param now:
    :return:
    """
    # 文章页
    with open(pathname + 'doctor_article_detail.csv', 'a') as doctor_article_detail:
        doctor_article_detail_writer = csv.writer(doctor_article_detail)

        # 写入行数据
        doctor_article_detail_writer.writerow([doctor_href, article_id,
                                               type_, reprint, stick, title,
                                               read, evaluate, good, buy, time_,
                                               now])


def write_finish(pathname, doctor_href):
    """
    写入成功
    :param pathname:
    :param doctor_href:
    :return:
    """
    with open(pathname + 'doctor_article_detail_finish.csv', 'a') as doctor_article_detail_finish:
        doctor_article_detail_finish_writer = csv.writer(doctor_article_detail_finish)

        # 写入行数据
        doctor_article_detail_finish_writer.writerow([doctor_href])


def write_error(pathname, doctor_href):
    """
    写入失败
    :param pathname:
    :param doctor_href:
    :return:
    """
    with open(pathname + 'doctor_article_detail_error.csv', 'a') as doctor_article_detail_error:
        doctor_article_detail_error_writer = csv.writer(doctor_article_detail_error)

        # 写入行数据
        doctor_article_detail_error_writer.writerow([doctor_href])


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
                get_doctor_article(self.pathname, self.doctor_href_list[j], self.doctor_home_list[j])

                # 写入成功
                write_finish(self.pathname, self.doctor_href_list[j])

                finish = finish + 1
                print('线程(%s):已完成%s个article!' % (thread_name, finish))
            except:
                os.system('spd-say "error"')
                print('\033[5;30;47m【错误：%s】\033[0m获取数据出现异常！' % self.doctor_href_list[j])

                # 写入错误
                write_error(self.pathname, self.doctor_href_list[j])

                error = error + 1
                print('线程(%s):已错误%s个article!' % (thread_name, error))

                continue
            end = time.time()
            print('time:%s' % str(end - start))


if __name__ == '__main__':
    my_pathname = '../data/'

    # 写入表头
    write_article_table(my_pathname)

    # 获取待爬取列表
    my_doctor_href_list, my_doctor_home_list = read_doc(my_pathname)

    # get_doctor_article(my_pathname, my_doctor_href_list[0], my_doctor_home_list[0])
    # get_doctor_article(my_pathname, 'DE4r0BCkuHzduKp0KEpOXKq2IWmiF', 'drdaibixia')
    # write_finish(my_pathname, 'DE4r0BCkuHzduKp0KEpOXKq2IWmiF')

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
