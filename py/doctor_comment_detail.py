# _*_ coding : UTF-8 _*_
# author : cfl
# time   : 2019/12/12 下午13:51
"""
author: cfl
    获取医生的评论信息、投票信息
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


def get_doctor_comment_vote(pathname, doctor_href):
    """
    获取医生评论和投票信息
    :param pathname:
    :param doctor_href:
    :return:
    """
    url = 'https://www.haodf.com/doctor/%s/jingyan/%s.htm' % (doctor_href, '1')

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

    # 请求评论需要的名字
    meta_experience_name = html.findAll('meta', attrs={'name': 'mobile-agent'})[0]
    experience_name = re.findall(r'/jingyan/all-(.+?)\.htm', str(meta_experience_name))[0]

    #
    # 投票情况

    # 近两年
    vote_now = get_vote(html)

    # 两年前
    url_past = 'https://www.haodf.com/jingyan/all-%s.htm?type-old&votecnt2YearTab=1' % experience_name
    # 获取页面内容
    html_past = requests.get(url_past, headers=Headers).text
    html_past = BeautifulSoup(html_past, 'lxml')

    # 通过请求医生姓名，检验页面是否正常加载
    try:
        h1_past = html_past.findAll('h1', attrs={'class': re.compile('doctor-name')})[0]
    except:
        sleep(30)

        # 获取页面内容
        html_past = requests.get(url_past, headers=Headers).text
        html_past = BeautifulSoup(html_past, 'lxml')
    vote_past = get_vote(html_past)

    now = time.asctime(time.localtime(time.time()))
    # 写入投票
    write_vote_doc(pathname,
                   doctor_href,
                   vote_now, vote_past,
                   now)

    #
    # 评价
    get_comment(pathname, doctor_href, html)

    #
    # 页数
    try:
        div_page = html.findAll('div', attrs={'class': 'p_bar'})[0]
        a_page = div_page.findAll('a', attrs={'class': 'p_text'})[0]
        page = re.findall(r'(\d+)', str(a_page))[0]
        for j in range(2, int(page)+1):
            url = 'https://www.haodf.com/jingyan/all-%s/%s.htm' % (experience_name, str(j))

            sleep(randint(3, 5))

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

            # 评价
            get_comment(pathname, doctor_href, html)
    except:
        return


def get_vote(html):
    """
    获取投票信息
    :param html:
    :return: vote
    """
    # 投票情况
    try:
        # 无投票
        div_vote = html.findAll('div', attrs={'class': 'vote-type-con'})[0]
    except:
        return

    #
    # 最近两年
    try:
        a_now_list = re.findall(r'>(.+?)</a>', str(div_vote))
        vote = ''
        for j in a_now_list:
            vote = vote + str(j).replace(' ', '') + '|'
        vote = vote.strip('|')
    except:
        vote = '无'

    return vote


def get_comment(pathname, doctor_href, html):
    """
    获取评论信息，并写入文件
    :param pathname:
    :param doctor_href:
    :param html:
    :return:
    """
    # 患者评价
    try:
        div_comment_list = html.findAll('div', attrs={'class': 'patient-eva'})
    except:
        return

    for j in div_comment_list:
        #
        # 患者信息
        div_patient = j.findAll('div', attrs={'class': 'patient-eva-header'})[0]

        # 评价时间
        try:
            span_time_ = str(div_patient.findAll('span')[-1]).replace('\n', '').replace(' ', '')
            time_ = re.findall(r'>(.+?)</span>', str(span_time_))[0]
        except:
            time_ = '未填'

        # 所患疾病
        try:
            span_illness = div_patient.findAll('span', attrs={'class': 'disease-tag'})[0]
            illness = re.findall(r'>(.+?)<', str(span_illness))[0].replace(',', '，')
        except:
            illness = '未填'

        #
        # 细节信息
        div_info = j.findAll('div', attrs={'class': 'clearfix'})[0]

        # 看病目的
        try:
            purpose = re.findall(r'>看病目的：(.+?)</span>', str(div_info))[0].replace(',', '，')
        except:
            purpose = '未填'

        # 治疗方式
        try:
            way = re.findall(r'>治疗方式：(.+?)</span>', str(div_info))[0].replace(',', '，')
        except:
            way = '未填'

        # 患者主观疗效、态度满意度
        try:
            subjective = re.findall(r'>疗效满意度：(.+?)</span>', str(div_info))[0].replace(',', '，')
        except:
            subjective = '未填'
        try:
            attitude = re.findall(r'>态度满意度：(.+?)</span>', str(div_info))[0].replace(',', '，')
        except:
            attitude = '未填'

        # 选择该医生的理由
        try:
            reason = re.findall(r'>选择该医生的理由：(.+?)</span>', str(div_info))[0].replace(',', '，')
        except:
            reason = '未填'

        # 本次挂号途径
        try:
            approach = re.findall(r'>本次挂号途径：(.+?)</span>', str(div_info))[0].replace(',', '，')
        except:
            approach = '未填'

        # 目前病情状态
        try:
            state = re.findall(r'>目前病情状态：(.+?)</span>', str(div_info))[0].replace(',', '，')
        except:
            state = '未填'

        # 住院花费或者本次看病费用总计或者门诊花费
        try:
            cost = re.findall(r'(\d+)元', str(div_info))[0].replace(',', '，')
        except:
            cost = '未填'

        #
        # 评价信息
        div_comment = str(j.findAll('div')[-1]).replace('\n', '').replace(' ', '')

        # 评价id
        comment_id = '无'

        # 类型、评价
        try:
            type_ = re.findall(r'">(.+?)：', str(div_comment))[0]
            experience = re.findall(r'：(.+?)<', str(div_comment))[0].strip('	').strip(' ').replace(',', '，')
        except:
            type_ = '未填'
            experience = '未填'

        now = time.asctime(time.localtime(time.time()))
        write_comment_doc(pathname,
                          doctor_href, comment_id,
                          illness, purpose, way, subjective, attitude,
                          type_, experience, reason, approach, state, cost, time_,
                          now)


def read_doc(pathname):
    """
    读取带爬列表
    :param pathname:
    :return: doctor_href_list
    """
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
        doctor_href_finish_reader_list = csv.reader(open(pathname + 'doctor_comment_detail_finish.csv', 'r'))
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


def write_vote_table(pathname):
    """
    写入投票表头
    :param pathname:
    :return:
    """
    # 判断是否已经写入表头
    try:
        with open(pathname + 'doctor_vote_detail.csv', 'r') as doctor_vote_detail_reader:
            if doctor_vote_detail_reader.readline() != '':
                return
            else:
                # 写入表头
                with open(pathname + 'doctor_vote_detail.csv', 'a') as doctor_vote_detail:
                    doctor_vote_detail_writer = csv.writer(doctor_vote_detail)

                    # 写入字段
                    fields = ['doctor_href',
                              'vote_now', 'vote_past',
                              'now']
                    doctor_vote_detail_writer.writerow(fields)
    except:
        # 写入表头
        with open(pathname + 'doctor_vote_detail.csv', 'a') as doctor_vote_detail:
            doctor_vote_detail_writer = csv.writer(doctor_vote_detail)

            # 写入字段
            fields = ['doctor_href',
                      'vote_now', 'vote_past',
                      'now']
            doctor_vote_detail_writer.writerow(fields)


def write_comment_table(pathname):
    """
    写入评论表头
    :param pathname:
    :return:
    """
    # 判断是否已经写入表头
    try:
        with open(pathname + 'doctor_comment_detail.csv', 'r') as doctor_comment_detail_reader:
            if doctor_comment_detail_reader.readline() != '':
                return
            else:
                # 写入表头
                with open(pathname + 'doctor_comment_detail.csv', 'a') as doctor_comment_detail:
                    doctor_comment_detail_writer = csv.writer(doctor_comment_detail)

                    # 写入字段
                    fields = ['doctor_href', 'comment_id',
                              'illness', 'purpose', 'way', 'subjective', 'attitude',
                              'type', 'experience', 'reason', 'approach', 'state', 'cost', 'time',
                              'now']
                    doctor_comment_detail_writer.writerow(fields)
    except:
        # 写入表头
        with open(pathname + 'doctor_comment_detail.csv', 'a') as doctor_comment_detail:
            doctor_comment_detail_writer = csv.writer(doctor_comment_detail)

            # 写入字段
            fields = ['doctor_href', 'comment_id',
                      'illness', 'purpose', 'way', 'subjective', 'attitude',
                      'type', 'experience', 'reason', 'approach', 'state', 'cost', 'time',
                      'now']
            doctor_comment_detail_writer.writerow(fields)


# 'doctor_href',
# 'vote_now', 'vote_past',
# 'now'
def write_vote_doc(pathname,
                   doctor_href,
                   vote_now, vote_past,
                   now):
    """
    写入投票信息
    :param pathname:
    :param doctor_href:
    :param vote_now:
    :param vote_past:
    :param now:
    :return:
    """
    # 医生主页
    with open(pathname + 'doctor_vote_detail.csv', 'a') as doctor_vote_detail:
        doctor_vote_detail_writer = csv.writer(doctor_vote_detail)

        # 写入行数据
        doctor_vote_detail_writer.writerow([doctor_href,
                                            vote_now, vote_past,
                                            now])


# 'doctor_href', 'comment_id',
# 'illness', 'purpose', 'way', 'subjective', 'attitude',
# 'type', 'experience', 'reason', 'approach', 'state', 'cost', 'time',
# 'now'
def write_comment_doc(pathname,
                      doctor_href, comment_id,
                      illness, purpose, way, subjective, attitude,
                      type_, experience, reason, approach, state, cost, time_,
                      now):
    """
    写入评论信息
    :param pathname:
    :param doctor_href:
    :param comment_id:
    :param illness:
    :param purpose:
    :param way:
    :param subjective:
    :param attitude:
    :param type_:
    :param experience:
    :param reason:
    :param approach:
    :param state:
    :param cost:
    :param time_:
    :param now:
    :return:
    """
    # 医生主页
    with open(pathname + 'doctor_comment_detail.csv', 'a') as doctor_comment_detail:
        doctor_comment_detail_writer = csv.writer(doctor_comment_detail)

        # 写入行数据
        doctor_comment_detail_writer.writerow([doctor_href, comment_id,
                                               illness, purpose, way, subjective, attitude,
                                               type_, experience, reason, approach, state, cost, time_,
                                               now])


def write_finish(pathname, doctor_href):
    """
    写入成功
    :param pathname:
    :param doctor_href:
    :return:
    """
    with open(pathname + 'doctor_comment_detail_finish.csv', 'a') as doctor_home_detail_finish:
        doctor_home_detail_finish_writer = csv.writer(doctor_home_detail_finish)

        # 写入行数据
        doctor_home_detail_finish_writer.writerow([doctor_href])


def write_error(pathname, doctor_href):
    """
    写入失败
    :param pathname:
    :param doctor_href:
    :return:
    """
    with open(pathname + 'doctor_comment_detail_error.csv', 'a') as doctor_home_detail_error:
        doctor_home_detail_error_writer = csv.writer(doctor_home_detail_error)

        # 写入行数据
        doctor_home_detail_error_writer.writerow([doctor_href])


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
                get_doctor_comment_vote(self.pathname, self.doctor_href_list[j])

                # 写入成功
                write_finish(self.pathname, self.doctor_href_list[j])

                finish = finish + 1
                print('线程(%s):已完成%s个comment、vote!' % (thread_name, finish))
            except:
                os.system('spd-say "error"')
                print('\033[5;30;47m【错误：%s】\033[0m获取数据出现异常！' % self.doctor_href_list[j])

                # 写入错误
                write_error(self.pathname, self.doctor_href_list[j])

                error = error + 1
                print('线程(%s):已错误%s个comment、vote!' % (thread_name, error))

                continue
            end = time.time()
            print('time:%s' % str(end - start))


if __name__ == '__main__':
    my_pathname = '../data/'

    # 写入表头
    write_vote_table(my_pathname)
    write_comment_table(my_pathname)

    # 获取待爬取列表
    my_doctor_href_list = read_doc(my_pathname)

    # get_doctor_comment_vote(my_pathname, my_doctor_href_list[1])
    get_doctor_comment_vote(my_pathname, 'DE4r0Fy0C9LuwlwRKORH3rVxD-uCU22Ut')
    write_finish(my_pathname, 'DE4r0Fy0C9LuwlwRKORH3rVxD-uCU22Ut')

    # # 将医生分成5等份
    # my_doctor_href_list1 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*0:int(len(my_doctor_href_list)/5)*1]
    # my_doctor_href_list2 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*1:int(len(my_doctor_href_list)/5)*2]
    # my_doctor_href_list3 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*2:int(len(my_doctor_href_list)/5)*3]
    # my_doctor_href_list4 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*3:int(len(my_doctor_href_list)/5)*4]
    # my_doctor_href_list5 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*4:len(my_doctor_href_list)]
    #
    # # 执行多线程
    # t1 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list1)
    # t2 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list2)
    # t3 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list3)
    # t4 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list4)
    # t5 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list5)
    #
    # t1.start()
    # t2.start()
    # t3.start()
    # t4.start()
    # t5.start()
    #
    # t1.join()
    # t2.join()
    # t3.join()
    # t4.join()
    # t5.join()
