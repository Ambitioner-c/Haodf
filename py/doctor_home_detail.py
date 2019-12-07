"""
author: cfl
    获取医生主页信息
"""
import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import threading
import os
from random import randint

Headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/78.0.3904.108 Safari/537.36'}
Cookies = {'Cookie': ''}


def get_doctor_home(pathname, doctor_href, doctor_home):
    url = 'https://%s.haodf.com/' % doctor_home

    # 获取页面内容
    res = requests.get(url, headers=Headers, cookies=Cookies)
    html = res.text
    html = BeautifulSoup(html, 'lxml')

    #
    # 上方模块
    div_up = html.findAll('div', attrs={'class': 'space_b_picright'})[0]

    # 职称
    h3_title = div_up.findAll('h3', attrs={'class': re.compile(r'doc_name')})[0]
    title = re.findall(r'>(.+?)</h3>', str(h3_title))[0]
    title = title.replace(' ', '|').strip('|').replace('  ', '||')

    # 科室
    div_office = div_up.findAll('div', attrs={'class': re.compile(r'doc_hospital')})[0]
    p_office_list = div_office.findAll('p')
    office = ''
    for j in p_office_list:
        office = office + re.findall(r'>(.+?)</a>', str(j))[0] + '|' + re.findall(r'>(.+?)</a>', str(j))[1] + '||'
    office = office.strip('|')

    #
    # 左边模块
    div_left = html.findAll('div', attrs={'class': 'mr_line1'})[0]

    # 诊后服务星和推荐热度
    ul_star_recommend = div_left.findAll('ul', attrs={'class': 'doc_info_ul1'})[0]
    # 诊后服务星
    li_star = ul_star_recommend.findAll('li')[0]
    star = str(5 - len(re.findall(r'zero', str(li_star))))
    # 推荐热度
    li_recommend = ul_star_recommend.findAll('li')[1]
    i_recommend = li_recommend.findAll('i', attrs={'class': 'bigredinfo'})[0]
    recommend = re.findall(r'>(.+?)</i>', str(i_recommend))[0]

    # 擅长
    div_skill = div_left.findAll('div', attrs={'class': 'hh'})[1]
    skill = div_skill.text.replace(' ', '').replace('、', '|').strip('等').replace('"', '|')

    # 简介
    url_intro = url + '/api/index/ajaxdoctorintro?uname=%s' % doctor_home
    # 获取页面内容
    res_intro = requests.get(url_intro, headers=Headers, cookies=Cookies)
    html_intro = res_intro.text
    html_intro = BeautifulSoup(html_intro, 'lxml')
    p_intro = html_intro.findAll('p', attrs={'class': 'hh'})[1]
    introduction = p_intro.text.replace(' ', '').replace('"', '|')

    # 医生id
    a_doctor_id = div_left.findAll('a', attrs={'id': 'thankLetter'})[0]
    doctor_id = re.findall(r'doctor_id=(.+?)&', str(a_doctor_id))[0]

    #
    # 中间模块
    div_center = html.findAll('div', attrs={'class': 'left_content'})[0]

    # 开场白
    span_abstract = div_center.findAll('span', attrs={'id': 'span_announce_title'})[0]
    p_abstract = div_center.findAll('p', attrs={'id': 'p_announce'})[0]
    abstract = span_abstract.text + '|' + p_abstract.text
    abstract = abstract.replace(' ', '').replace('\n', '')

    # 在线、预约、团队、私人
    div_online_appointment_team_private = div_center.findAll('div', attrs={'class': 'd-s-items'})[0]
    # 在线
    try:
        online = str(len(re.findall(r'zixun', str(div_online_appointment_team_private))))
    except:
        online = '0'
    # 预约
    try:
        appointment = str(len(re.findall(r'guahao', str(div_online_appointment_team_private))))
    except:
        appointment = '0'
    # 团队
    try:
        team = str(len(re.findall(r'teamdoc', str(div_online_appointment_team_private))))
    except:
        team = '0'
    # 私人
    try:
        private = str(len(re.findall(r'familydoc', str(div_online_appointment_team_private))))
    except:
        private = '0'

    # 患友会小组数
    div_group = html.findAll('div', attrs={'class': 'mr_line1'})[4]
    span_group = div_group.findAll('span', attrs={'class': 'orange1'})[0]
    group = span_group.text

    #
    # 下面模块
    ul_down = html.findAll('ul', attrs={'class': 'space_statistics'})[0]
    li_down_list = ul_down.findAll('li')

    li_list = []
    for j in li_down_list:
        li_list.append(str(re.findall(r'">(.+?)</span>', str(j))[0]).replace(',', ''))

    # 总访问
    interviews = li_list[0]
    # 昨日访问
    interview = li_list[1]
    # 总文章
    article = li_list[2]
    # 总患者
    patients = li_list[3]
    # 昨日诊后报到患者
    patient = li_list[4]
    # 微信诊后报到患者
    wechat = li_list[5]
    # 总诊后报到患者
    total = li_list[6]
    # 患者投票
    vote = li_list[7]
    # 感谢信
    thanks = li_list[8]
    # 心意礼物
    gift = li_list[9]
    # 上次在线
    last = li_list[10]
    # 开通时间
    dredge = li_list[11]

    write_doc(pathname,
              doctor_href, doctor_id,
              title, office,
              star, recommend, skill, introduction,
              abstract, online, team, appointment, private,
              group, interviews, interview, article, patients, patient, wechat, total, vote, thanks, gift, last, dredge)


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
        doctor_home_finish_reader_list = csv.reader(open(pathname + 'doctor_home_detail_finish.csv', 'r'))
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
        if doctor_home_all_list[j] not in doctor_home_finish_set:
            doctor_href_list.append(doctor_href_all_list[j])
            doctor_home_list.append(doctor_home_all_list[j])

    return doctor_href_list, doctor_home_list


def write_table(pathname):

    # 判断是否已经写入表头
    try:
        with open(pathname + 'doctor_home_detail.csv', 'r') as doctor_home_detail_reader:
            if doctor_home_detail_reader.readline() != '':
                return
            else:
                # 写入表头
                with open(pathname + 'doctor_home_detail.csv', 'a') as doctor_home_detail:
                    doctor_home_detail_writer = csv.writer(doctor_home_detail)

                    # 写入字段
                    fields = ['doctor_href', 'doctor_id',
                              'title', 'office',
                              'star', 'recommend', 'skill', 'introduction',
                              'abstract', 'online', 'team', 'appointment', 'private',
                              'group', 'interviews', 'interview', 'article', 'patients', 'patient', 'wechat', 'total', 'vote', 'thanks', 'gift', 'last', 'dredge']
                    doctor_home_detail_writer.writerow(fields)
    except:
        # 写入表头
        with open(pathname + 'doctor_home_detail.csv', 'a') as doctor_home_detail:
            doctor_home_detail_writer = csv.writer(doctor_home_detail)

            # 写入字段
            fields = ['doctor_href', 'doctor_id',
                      'title', 'office',
                      'star', 'recommend', 'skill', 'introduction',
                      'abstract', 'online', 'team', 'appointment', 'private',
                      'group', 'interviews', 'interview', 'article', 'patients', 'patient', 'wechat', 'total', 'vote', 'thanks', 'gift', 'last', 'dredge']
            doctor_home_detail_writer.writerow(fields)


# 'doctor_href', 'doctor_id',
# 'title', 'office',
# 'star', 'recommend', 'skill', 'introduction',
# 'abstract', 'online', 'team', 'appointment', 'private',
# 'group', interviews', 'interview', 'article', 'patients', 'patient', 'wechat', 'total', 'vote', 'thanks', 'gift', 'last', 'dredge'
def write_doc(pathname,
              doctor_href, doctor_id,
              title, office,
              star, recommend, skill, introduction,
              abstract, online, team, appointment, private,
              group, interviews, interview, article, patients, patient, wechat, total, vote, thanks, gift, last, dredge):
    # 医生主页
    with open(pathname + 'doctor_home_detail.csv', 'a') as doctor_home_detail:
        doctor_home_detail_writer = csv.writer(doctor_home_detail)

        # 写入行数据
        doctor_home_detail_writer.writerow([doctor_href, doctor_id,
                                            title, office,
                                            star, recommend, skill, introduction,
                                            abstract, online, team, appointment, private,
                                            group, interviews, interview, article, patients, patient, wechat, total, vote, thanks, gift, last, dredge])


def write_finish(pathname, doctor_href):
    with open(pathname + 'doctor_home_detail_finish.csv', 'a') as doctor_home_detail_finish:
        doctor_home_detail_finish_writer = csv.writer(doctor_home_detail_finish)

        # 写入行数据
        doctor_home_detail_finish_writer.writerow([doctor_href])


def write_error(pathname, doctor_href):
    with open(pathname + 'doctor_home_detail_error.csv', 'a') as doctor_home_detail_error:
        doctor_home_detail_error_writer = csv.writer(doctor_home_detail_error)

        # 写入行数据
        doctor_home_detail_error_writer.writerow([doctor_href])


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
            time.sleep(randint(2, 5))
            try:
                # 获取医院细节信息
                get_doctor_home(self.pathname, self.doctor_href_list[j], self.doctor_home_list[j])

                # 写入成功
                write_finish(self.pathname, self.doctor_href_list[j])

                finish = finish + 1
                print('线程(%s):已完成%s个医院!' % (thread_name, finish))
            except:
                os.system('spd-say "error"')
                print('\033[5;30;47m【错误：%s】\033[0m获取数据出现异常！' % j)

                # 写入错误
                write_error(self.pathname, self.doctor_href_list[j])

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
    my_doctor_href_list, my_doctor_home_list = read_doc(my_pathname)

    get_doctor_home(my_pathname, my_doctor_href_list[0], my_doctor_home_list[0])
    # # 将医生分成5等份
    # my_doctor_href_list1 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*0:int(len(my_doctor_href_list)/5)*1]
    # my_doctor_href_list2 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*1:int(len(my_doctor_href_list)/5)*2]
    # my_doctor_href_list3 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*2:int(len(my_doctor_href_list)/5)*3]
    # my_doctor_href_list4 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*3:int(len(my_doctor_href_list)/5)*4]
    # my_doctor_href_list5 = my_doctor_href_list[int(len(my_doctor_href_list)/5)*4:len(my_doctor_href_list)]
    #
    # # 将医生分成5等份
    # my_doctor_home_list1 = my_doctor_home_list[int(len(my_doctor_home_list)/5)*0:int(len(my_doctor_home_list)/5)*1]
    # my_doctor_home_list2 = my_doctor_home_list[int(len(my_doctor_home_list)/5)*1:int(len(my_doctor_home_list)/5)*2]
    # my_doctor_home_list3 = my_doctor_home_list[int(len(my_doctor_home_list)/5)*2:int(len(my_doctor_home_list)/5)*3]
    # my_doctor_home_list4 = my_doctor_home_list[int(len(my_doctor_home_list)/5)*3:int(len(my_doctor_home_list)/5)*4]
    # my_doctor_home_list5 = my_doctor_home_list[int(len(my_doctor_home_list)/5)*4:len(my_doctor_home_list)]
    #
    # # 执行多线程
    # t1 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list1, doctor_home_list=my_doctor_home_list1)
    # t2 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list2, doctor_home_list=my_doctor_home_list2)
    # t3 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list3, doctor_home_list=my_doctor_home_list3)
    # t4 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list4, doctor_home_list=my_doctor_home_list4)
    # t5 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list5, doctor_home_list=my_doctor_home_list5)
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