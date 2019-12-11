import csv


# 把问文件去重，并重写到2中
# doctor_href_set = set([])
#
# doctor_home_detail = csv.reader(open('../data/doctor_home_detail_finish.csv', 'r'))
# for i in doctor_home_detail:
#     if i[0] not in doctor_href_set:
#         doctor_href_set.add(i[0])
#         with open('../data/doctor_home_detail_finish2.csv', 'a') as f:
#             writer = csv.writer(f)
#             writer.writerow(i)


# 判断文件是否存在重复
# doctor_detail = csv.reader(open('../data/doctor_article_detail_finish.csv', 'r'))
#
# doctor_list = []
# for i in doctor_detail:
#     doctor_list.append(i[0])
# doctor_set = set(doctor_list)
# print(len(doctor_list))
# print(len(doctor_set))


# 检测是否存在逗号
# doctor_home_detail = csv.reader(open('/home/cfl/Downloads/qq-files/656359504/file_recv/doctor_home_detail3.csv', 'r'))
# for i in doctor_home_detail:
#     length = len(i)
#     if length != 27:
#         print(i[0])
