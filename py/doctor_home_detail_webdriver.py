"""
author: cfl
    获取医生主页信息，成功，
    先解析js，但是失败了，
    后使用chrome的webdriver。
"""
from bs4 import BeautifulSoup
import re
import csv
import time
import threading
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep


Headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;'
                     'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'zh-CN,zh;q=0.9',
           'Cache-Control': 'max-age=0',
           'Connection': 'keep-alive',
           'Sec-Fetch-Mode': 'navigate',
           'Sec-Fetch-Site': 'same-origin',
           'Sec-Fetch-User': '?1',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/78.0.3904.108 Safari/537.36',
           'Host': '',
           'Referer': ''}
Cookies = {'Cookie': ''}


def get_driver(executable_path):
    chrome_opt = Options()  # 创建参数设置对象.
    chrome_opt.add_argument('--headless')  # 无界面化.
    chrome_opt.add_argument('--disable-gpu')  # 配合上面的无界面化.
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_opt.add_experimental_option("prefs", prefs)  # 不加载图片
    chrome_opt.add_argument('--window-size=1366,768')  # 设置窗口大小, 窗口大小会有影响.
    chrome_opt.add_argument("--no-sandbox")  # 使用沙盒模式运行

    # 创建Chrome对象并传入设置信息.
    driver = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_opt)

    return driver


def get_doctor_home(driver, pathname, doctor_href, doctor_home):
    url = 'https://%s.haodf.com/' % doctor_home

    # 获取页面内容
    driver.get(url)
    # cookies = driver.get_cookies()
    # __jsluid_s = cookies[1]['value']
    # __jsl_clearance = cookies[0]['value']
    # expiry = cookies[0]['expiry']
    # domain = cookies[0]['domain']
    #
    # cookie = 'UM_distinctid=16eb655dcbc2b-068f433501878-31760856-1fa400-16eb655dcbef2;' \
    #          ' _ga=GA1.2.924382091.1575017111;' \
    #          ' g=HDF.21.5de0e010c88f3;' \
    #          ' CNZZDATA-FE=CNZZDATA-FE;' \
    #          ' _gid=GA1.2.720435388.1575708911;' \
    #          ' Hm_lvt_dfa5478034171cc641b1639b2a5b717d=1575445054,1575452105,1575615451,1575708911;' \
    #          ' _gat=1;' \
    #          ' CNZZDATA1256706712=1752327309-1575544577-https%253A%252F%252F' + domain + '%252F%7C1575711992;' \
    #          ' __jsluid_s=' + __jsluid_s + ';' \
    #          ' __jsl_clearance=' + __jsl_clearance + ';' \
    #          ' Hm_lpvt_dfa5478034171cc641b1639b2a5b717d=' + str(expiry)
    # print(cookie)
    #
    # Headers['Host'] = domain
    # Headers['Referer'] = 'https://' + domain + '/'
    # Cookies['Cookie'] = cookie
    # html = requests.get(url, headers=Headers, cookies=Cookies).text

    while '<title>' not in driver.page_source:
        sleep(1)
    html = driver.page_source
    html = BeautifulSoup(html, 'lxml')

    #
    # 上方模块
    div_up = html.findAll('div', attrs={'class': 'space_b_picright'})[0]

    # 职称
    h3_title = div_up.findAll('h3', attrs={'class': re.compile(r'doc_name')})[0]
    title = re.findall(r'>(.+?)</h3>', str(h3_title))[0]
    title = title.replace(' ', '|').strip('|').replace('  ', '||')

    # 科室
    div_office = div_up.findAll('div', attrs={'class': re.compile(r'doc_hospital')})[0]
    p_office_list = div_office.findAll('p')
    office = ''
    for j in p_office_list:
        office = office + re.findall(r'>(.+?)</a>', str(j))[0] + '|' + re.findall(r'>(.+?)</a>', str(j))[1] + '||'
    office = office.strip('|')

    #
    # 左边模块
    # 有可能是停诊公告
    j = 0
    while 'doc_info' not in str(html.findAll('div', attrs={'class': 'mr_line1'})[j]):
        j = j + 1
    div_left = html.findAll('div', attrs={'class': 'mr_line1'})[j]

    # 诊后服务星和推荐热度
    ul_star_recommend = div_left.findAll('ul', attrs={'class': 'doc_info_ul1'})[0]
    # 诊后服务星
    try:
        li_star = ul_star_recommend.findAll('li', attrs={'class': 'first_li'})[0]
        star = str(5 - len(re.findall(r'zero', str(li_star))))
    except:
        star = ''
    # 推荐热度
    li_recommend = ul_star_recommend.findAll('li', attrs={'': ''})[-2]
    i_recommend = li_recommend.findAll('i', attrs={'class': 'bigredinfo'})[-1]
    recommend = re.findall(r'>(.+?)</i>', str(i_recommend))[0]

    # 擅长、简介
    url_intro = url + '/api/index/ajaxdoctorintro?uname=%s' % doctor_home
    # 获取页面内容
    driver.get(url_intro)
    html_intro = driver.page_source
    html_intro = BeautifulSoup(html_intro, 'lxml')
    try:
        # 擅长
        p_skill = html_intro.findAll('p', attrs={'class': 'hh'})[0]
        skill = ('' + p_skill.text).replace(' ', '').replace('"', '').replace('\\n', '')
    except:
        skill = ''
    try:
        # 简介
        p_intro = html_intro.findAll('p', attrs={'class': 'hh'})[1]
        introduction = ('' + p_intro.text).replace(' ', '').replace('"', '').replace('\\n', '')
    except:
        introduction = ''

    # 医生id
    a_doctor_id = div_left.findAll('a', attrs={'id': 'thankLetter'})[0]
    doctor_id = re.findall(r'doctor_id=(.+?)&', str(a_doctor_id))[0]

    #
    # 中间模块
    div_center = html.findAll('div', attrs={'class': 'left_content'})[0]

    # 开场白
    try:
        span_abstract = div_center.findAll('span', attrs={'id': 'span_announce_title'})[0]
        p_abstract = div_center.findAll('p', attrs={'id': 'p_announce'})[0]
        abstract = span_abstract.text + '|' + p_abstract.text
        abstract = abstract.replace(' ', '').replace('\n', '')
    except:
        abstract = ''

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
    div_group = html.findAll('div', attrs={'class': 'mr_line1'})[-2]
    try:
        span_group = div_group.findAll('span', attrs={'class': 'orange1'})[0]
        group = span_group.text
    except:
        group = '0'

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

    now = time.asctime(time.localtime(time.time()))
    write_doc(pathname,
              doctor_href, doctor_id,
              title, office,
              star, recommend, skill, introduction,
              abstract, online, team, appointment, private,
              group, interviews, interview, article, patients, patient, wechat, total, vote, thanks, gift, last, dredge,
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
                              'group', 'interviews', 'interview', 'article', 'patients', 'patient', 'wechat', 'total', 'vote', 'thanks', 'gift', 'last', 'dredge',
                              'now']
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
                      'group', 'interviews', 'interview', 'article', 'patients', 'patient', 'wechat', 'total', 'vote', 'thanks', 'gift', 'last', 'dredge',
                      'now']
            doctor_home_detail_writer.writerow(fields)


# 'doctor_href', 'doctor_id',
# 'title', 'office',
# 'star', 'recommend', 'skill', 'introduction',
# 'abstract', 'online', 'team', 'appointment', 'private',
# 'group', interviews', 'interview', 'article', 'patients', 'patient', 'wechat', 'total', 'vote', 'thanks', 'gift', 'last', 'dredge',
# 'now'
def write_doc(pathname,
              doctor_href, doctor_id,
              title, office,
              star, recommend, skill, introduction,
              abstract, online, team, appointment, private,
              group, interviews, interview, article, patients, patient, wechat, total, vote, thanks, gift, last, dredge,
              now):
    # 医生主页
    with open(pathname + 'doctor_home_detail.csv', 'a') as doctor_home_detail:
        doctor_home_detail_writer = csv.writer(doctor_home_detail)

        # 写入行数据
        doctor_home_detail_writer.writerow([doctor_href, doctor_id,
                                            title, office,
                                            star, recommend, skill, introduction,
                                            abstract, online, team, appointment, private,
                                            group, interviews, interview, article, patients, patient, wechat, total, vote, thanks, gift, last, dredge,
                                            now])


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

        driver = get_driver(my_executable_path)

        for j in range(len(self.doctor_href_list)):
            start = time.time()

            print('--------------------------------------------------------------------')
            try:
                # 获取医院细节信息
                get_doctor_home(driver, self.pathname, self.doctor_href_list[j], self.doctor_home_list[j])

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

    my_executable_path = '/usr/local/bin/chromedriver/chromedriver'

    my_driver = get_driver(my_executable_path)
    # 写入表头
    write_table(my_pathname)

    # 获取待爬取列表
    my_doctor_href_list, my_doctor_home_list = read_doc(my_pathname)

    # get_doctor_home(my_driver, my_pathname, my_doctor_href_list[0], my_doctor_home_list[0])
    # get_doctor_home(my_driver, my_pathname, 'DE4rO-XCoLUmy11ccTieBvzKOb', 'sunandr')
    # write_finish(my_pathname, 'DE4rO-XCoLUmy11ccTieBvzKOb')
    # 将医生分成5等份
    my_doctor_href_list1 = my_doctor_href_list[int(len(my_doctor_href_list)/3)*0:int(len(my_doctor_href_list)/3)*1]
    my_doctor_href_list2 = my_doctor_href_list[int(len(my_doctor_href_list)/3)*1:int(len(my_doctor_href_list)/3)*2]
    my_doctor_href_list3 = my_doctor_href_list[int(len(my_doctor_href_list)/3)*2:len(my_doctor_href_list)]

    # 将医生分成5等份
    my_doctor_home_list1 = my_doctor_home_list[int(len(my_doctor_home_list)/3)*0:int(len(my_doctor_home_list)/3)*1]
    my_doctor_home_list2 = my_doctor_home_list[int(len(my_doctor_home_list)/3)*1:int(len(my_doctor_home_list)/3)*2]
    my_doctor_home_list3 = my_doctor_home_list[int(len(my_doctor_home_list)/3)*4:len(my_doctor_home_list)]

    # 执行多线程
    t1 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list1, doctor_home_list=my_doctor_home_list1)
    t2 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list2, doctor_home_list=my_doctor_home_list2)
    t3 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list3, doctor_home_list=my_doctor_home_list3)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
