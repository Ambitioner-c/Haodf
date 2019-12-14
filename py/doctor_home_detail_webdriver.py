# _*_ coding : UTF-8 _*_
# author : cfl
# time   : 2019/12/12 下午16:49
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


Headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/78.0.3904.108 Safari/537.36'}


def get_driver(executable_path):
    """
    获取webdriver
    :param executable_path:
    :return: driver
    """
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
    """
    获取医生主页信息，并写入文件
    :param driver:
    :param pathname:
    :param doctor_href:
    :param doctor_home:
    :return:
    """
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

    # 检验页面是否正常加载
    n = 0
    while '<title>' not in driver.page_source:
        n = n + 1
        if n != 30:
            sleep(1)
        else:
            # 强制退出
            break
    html = driver.page_source
    html = BeautifulSoup(html, 'lxml')

    #
    # 上方模块
    div_up = html.findAll('div', attrs={'class': re.compile('doctor-intro')})[0]

    # 职称
    h1_name = div_up.findAll('h1', attrs={'class': 'doctor-name'})[0]
    name = re.findall(r'>(.+?)<', str(h1_name))[0]
    span_title = div_up.findAll('span', attrs={'class': 'positon'})[0]
    title_list = re.findall(r'>(.+?)</span>', str(span_title))
    try:
        title = name + '||' + title_list[0] + '|' + title_list[1]
    except:
        try:
            title = name + '||' + title_list[0]
        except:
            title = name

    # 科室
    p_office_list = div_up.findAll('p', attrs={'class': re.compile(r'doctor-faculty')})
    office = ''
    for j in p_office_list:
        j = str(j).replace('\n', '')
        office = office + re.findall(r'>(.+?)</a>', str(j))[0] + '|' + re.findall(r'>(.+?)</a>', str(j))[1] + '||'
    office = office.strip('|')

    # 推荐热度
    div_recommend = div_up.findAll('div', attrs={'class': re.compile(r'profile-sta')})[0]
    p_recommend = div_recommend.findAll('p')[0]
    try:
        i_recommend = p_recommend.findAll('i')[0]
        recommend = re.findall(r'>(.+?)</i>', str(i_recommend))[0]
    except:
        recommend = '推荐数据核实中'

    #
    # 中间模块
    div_center = html.findAll('div', attrs={'class': re.compile('good-at-con')})[0]

    # 擅长
    try:
        div_skill = div_center.findAll('div', attrs={'class': 'good-at-text'})[0]
        skill = str(re.findall(r'>(.+?)</div>', str(div_skill))[0]).replace(',', '，')
    except:
        skill = ''

    # 简介
    try:
        div_intro = div_center.findAll('div', attrs={'class': 'good-at-text'})[1]
        introduction = div_intro.text.replace(',', '，')
    except:
        introduction = ''

    #
    # 在线、预约、团队、私人
    online_appointment_team_private = []
    div_online_appointment_team_private = html.findAll('div', attrs={'class': re.compile('entry-con')})[0]
    a_online_appointment_team_private_list = div_online_appointment_team_private.findAll('a')
    for j in a_online_appointment_team_private_list:
        if 'enable' in str(j):
            online_appointment_team_private.append('1')
        else:
            online_appointment_team_private.append('0')
    # 在线
    online = online_appointment_team_private[0]

    # 预约
    appointment = online_appointment_team_private[2]

    # 团队
    team = online_appointment_team_private[1]

    # 私人
    private = online_appointment_team_private[3]

    #
    # 开场白
    try:
        div_abstract = html.findAll('div', attrs={'class': re.compile('welcome-con')})[0]
        # 标题
        div_abstract1 = div_abstract.findAll('div', attrs={'class': re.compile('item-welcome-title')})[0]
        div_abstract1 = str(div_abstract1).replace('\n', '').replace(' ', '')
        abstract1 = re.findall(r'el">(.+?)<', div_abstract1)[0].replace(',', '，')

        # 内容
        div_abstract2 = div_abstract.findAll('div', attrs={'class': re.compile('main-item-welcome')})[0]
        div_abstract2 = str(div_abstract2).replace('\n', '').replace(' ', '')
        abstract2 = re.findall(r'>(.+?)<', div_abstract2)[0].replace(',', '，')
        abstract = abstract1 + '|' + abstract2
    except:
        abstract = ''

    #
    # 医生id
    div_doctor_id = html.findAll('div', attrs={'class': re.compile('patient-vote')})[0]
    doctor_id = re.findall(r'doctor_id=(.+?)&', str(div_doctor_id))[0]

    #
    # 患友会小组数
    try:
        div_group = html.findAll('div', attrs={'class': re.compile('patients-collect')})[0]
        group = re.findall(r'>(\d+)</span>个患者讨论小组', str(div_group))[0]
    except:
        group = '0'

    #
    # 诊后服务星
    try:
        div_star = html.findAll('div', attrs={'class': re.compile('doc-experience')})[0]
        span_star = div_star.findAll('span', attrs={'class': re.compile('experience-data')})[0]
        star = str(len(re.findall(r'star_yellow', str(span_star))))
    except:
        star = ''

    #
    # 最重要模块
    div_inpor = html.findAll('div', attrs={'class': re.compile('person-web')})[0]
    div_inpor_list = div_inpor.findAll('div', attrs={'class': 'per-sta-data'})

    li_list = []
    for j in div_inpor_list:
        li_list.append(str(re.findall(r'">(.+?)<', str(j))[0]).replace(',', ''))

    # 总访问
    interviews = li_list[0].replace('次', '')
    # 昨日访问
    interview = re.findall(r'(\d+)次', str(li_list[1]))[0]
    # 总文章
    article = li_list[2].replace('篇', '')
    # 总患者
    patients = li_list[3].replace('位', '')
    # 昨日诊后报到患者
    patient = li_list[4].replace('位', '')
    # 微信诊后报到患者
    wechat = li_list[5].replace('位', '')
    # 总诊后报到患者
    total = li_list[6].replace('位', '')
    # 患者投票
    vote = li_list[7].replace('票', '')
    # 感谢信
    thanks = li_list[8].replace('封', '')
    # 心意礼物
    gift = li_list[9].replace('个', '')
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
    """
    读取待爬列表
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
        if doctor_href_all_list[j] not in doctor_home_finish_set:
            doctor_href_list.append(doctor_href_all_list[j])
            doctor_home_list.append(doctor_home_all_list[j])

    return doctor_href_list, doctor_home_list


def write_table(pathname):
    """
    写入表头
    :param pathname:
    :return:
    """
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
    """
    写入文件
    :param pathname:
    :param doctor_href:
    :param doctor_id:
    :param title:
    :param office:
    :param star:
    :param recommend:
    :param skill:
    :param introduction:
    :param abstract:
    :param online:
    :param team:
    :param appointment:
    :param private:
    :param group:
    :param interviews:
    :param interview:
    :param article:
    :param patients:
    :param patient:
    :param wechat:
    :param total:
    :param vote:
    :param thanks:
    :param gift:
    :param last:
    :param dredge:
    :param now:
    :return:
    """
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
    """
    写入成功
    :param pathname:
    :param doctor_href:
    :return:
    """
    with open(pathname + 'doctor_home_detail_finish.csv', 'a') as doctor_home_detail_finish:
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
                print('线程(%s):已完成%s个home!' % (thread_name, finish))
            except:
                os.system('spd-say "error"')
                print('\033[5;30;47m【错误：%s】\033[0m获取数据出现异常！' % self.doctor_href_list[j])

                # 写入错误
                write_error(self.pathname, self.doctor_href_list[j])

                error = error + 1
                print('线程(%s):已错误%s个home!' % (thread_name, error))

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
    # my_doctor_href_list = my_doctor_href_list[2500:]
    # my_doctor_home_list = my_doctor_home_list[2500:]

    # get_doctor_home(my_driver, my_pathname, my_doctor_href_list[0], my_doctor_home_list[0])
    # get_doctor_home(my_driver, my_pathname, 'DE4r0BCkuHzdeGEHBSpOXKq2IWmiF', 'zjsdl')
    # write_finish(my_pathname, 'DE4r0BCkuHzdeGEHBSpOXKq2IWmiF')

    # 将医生分成3等份
    my_doctor_href_list1 = my_doctor_href_list[int(len(my_doctor_href_list)/3)*0:int(len(my_doctor_href_list)/3)*1]
    my_doctor_href_list2 = my_doctor_href_list[int(len(my_doctor_href_list)/3)*1:int(len(my_doctor_href_list)/3)*2]
    my_doctor_href_list3 = my_doctor_href_list[int(len(my_doctor_href_list)/3)*2:len(my_doctor_href_list)]

    # 将医生分成3等份
    my_doctor_home_list1 = my_doctor_home_list[int(len(my_doctor_home_list)/3)*0:int(len(my_doctor_home_list)/3)*1]
    my_doctor_home_list2 = my_doctor_home_list[int(len(my_doctor_home_list)/3)*1:int(len(my_doctor_home_list)/3)*2]
    my_doctor_home_list3 = my_doctor_home_list[int(len(my_doctor_home_list)/3)*2:len(my_doctor_home_list)]

    # 执行多线程
    t1 = MyThread(pathname=my_pathname, doctor_href_list=my_doctor_href_list, doctor_home_list=my_doctor_home_list)

    t1.start()
