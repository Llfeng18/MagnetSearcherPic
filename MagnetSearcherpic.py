import os
import re
import time
import random
import psutil
import requests
import threading
from urllib import parse
from urllib import request
from bs4 import BeautifulSoup
from urllib.parse import quote
from multiprocessing import Pool, cpu_count

urlPart_row = "https://bbs.188sex.com/"
delay_mult = 0

my_headers = [
    {'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"},
    {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"},
    {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"},
    {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14"},
    {'User-Agent': "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"},
    {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'},
    {'User-Agent': 'Opera/9.25 (Windows NT 5.1; U; en)'},
    {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)'},
    {'User-Agent': 'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)'},
    {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12'},
    {'User-Agent': 'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'},
    {'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7"},
    {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0"},
    {'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6"},
]


def get_now_time():
    """
    获取当前日期时间
    :return:当前日期时间
    """
    now = time.localtime()
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", now)
    return now_time


def strDecode(uriCode):
    a = re.sub('[+"]', '', uriCode)
    b = parse.unquote(a)
    c = re.compile(r'<[^>]+>', re.S)
    str = c.sub('', b)
    return str


def save_pic(pic_src, pic_cnt):
    """
    保存图片到本地
    :param pic_src: 图片地址
    :param pic_cnt: 图片数用于给图片命令
    :return: NA
    """
    for i in range(3):
        try:
            time.sleep(0.10)
            img = requests.get(pic_src, headers=random.choice(my_headers), timeout=10)
            img_name = "pic_cnt_{}.jpg".format(pic_cnt + 1)
            with open(img_name, 'ab') as f:
                f.write(img.content)
                print(img_name)
            break
        except Exception as e:
            print(e)

    return


def make_dir(folder_name, dir_path):
    """
    新建文件夹并切换到该目录下
    :param folder_name: 文件夹名称
    :param dir_path: 保存图片的根路径
    :return: True or Flase
    """
    folder_name.replace('\\', '')
    folder_name.replace('/', '')
    folder_name.replace(':', '')
    folder_name.replace('*', '')
    folder_name.replace('?', '')
    folder_name.replace('"', '')
    folder_name.replace('<', '')
    folder_name.replace('>', '')
    folder_name.replace('|', '')
    try:
        path = os.path.join(dir_path, folder_name)
        # 如果目录已经存在就不用再次爬取了，去重，提高效率。存在返回 False，否则反之
        if not os.path.exists(path):
            os.makedirs(path)
            print(path)
            os.chdir(path)
            return True
    except Exception as e:
        print(e)
    print("Folder has existed!")
    return False


def delete_empty_dir(save_dir):
    """
    如果程序半路中断的话，可能存在已经新建好文件夹但是仍没有下载的图片的
    情况但此时文件夹已经存在所以会忽略该套图的下载，此时要删除空文件夹
    :param save_dir: 保存图片的根路径
    :return: NA
    """
    if os.path.exists(save_dir):
        if os.path.isdir(save_dir):
            for d in os.listdir(save_dir):
                path = os.path.join(save_dir, d)     # 组装下一级地址
                if os.path.isdir(path):
                    delete_empty_dir(path)      # 递归删除空文件夹
        if not os.listdir(save_dir):
            os.rmdir(save_dir)
            print("remove the empty dir: {}".format(save_dir))
    else:
        print("Please start your performance!")     # 请开始你的表演

    return


def search_picurl(row_url, dir_path):
    """
    获得页面上每个图片对应的url
    :param row_url: 页面url
    :param dir_path: 保存图片的根路径
    :return: NA
    """
    if ("onclick" not in row_url) | ("title" not in row_url) | ("thread-" not in row_url):
        return

    row_test = re.findall(r'" title="(.*?)"', row_url, re.S)
    if len(row_test) != 1:
        return

    url_row = urlPart_row + (re.findall(r'"(.*?)" onclick="', row_url, re.S))[0]
    print(url_row)
    for i in range(3):
        req_row = request.Request(url=url_row, headers=random.choice(my_headers))
        time.sleep(random.random() * delay_mult + random.randint(0, pow(i, 2)) * 10)
        # print(req_row)
        try:
            res_row = request.urlopen(req_row)
            ret_row = res_row.read().decode("utf-8")
        except Exception as e:
            print(e)
        else:
            img_url = re.findall(r'" file="(.*?)" onmouseover="', ret_row, re.S)
            if (len(img_url) > 0) & ("http" not in img_url[0]):
                img_url = re.findall(r'" zoomfile="(.*?)" file="', ret_row, re.S)
                for index in range(len(img_url)):
                    img_url[index] = "https://bbs.188sex.com/" + img_url[index]
            print(len(img_url))
            print(img_url)
            if make_dir(row_test[0], dir_path):
                for k in range(len(img_url)):
                    save_pic(img_url[k], k)
            break

    return


def search_url(urlPart, page_num, dir_path):
    """
    根据主url获取每个子页面的url
    :param urlPart: 主url的部分路径(用于组url)
    :param page_num: 页面数(用于组url)
    :param dir_path: 保存图片的根路径
    :return: NA
    """
    url = urlPart + str(page_num) + ".html"
    print(url)
    for i in range(5):
        req = request.Request(url=url, headers=random.choice(my_headers))
        time.sleep(random.random() * delay_mult + random.randint(0, pow(i, 2)) * 10)
        try:
            res = request.urlopen(req)
            ret = res.read().decode("utf-8")
        except Exception as e:
            print(e)
        else:
            break

    row_url = re.findall(r'<a href=(.*?)">', ret, re.S)
    for i in range(len(row_url)):
        search_picurl(row_url[i], dir_path)


def get_sex_pic(page_num):
    """
    获取https://bbs.188sex.com/forum-125-1.html上的所有图片,1为page_num
    :param page_num:页面数
    :return: NA
    """
    url_part_1 = "https://bbs.188sex.com/forum-125-"
    dir_path = r"C:\download\pic\bbs.188sex.com\sex"

    search_url(url_part_1, page_num, dir_path)

    return


def get_selfie_pic(page_num):
    """
    获取https://bbs.188sex.com/forum-98-1.html上的所有图片,1为page_num
    :param page_num:页面数
    :return: NA
    """
    url_part_1 = "https://bbs.188sex.com/forum-98-"
    dir_path = r"C:\download\pic\bbs.188sex.com\selfie"

    search_url(url_part_1, page_num, dir_path)

    return


def get_western_pic(page_num):
    """
    获取https://bbs.188sex.com/forum-126-1.html上的所有图片,1为page_num
    :param page_num:页面数
    :return: NA
    """

    url_part_1 = "https://bbs.188sex.com/forum-126-"
    dir_path = r"C:\download\pic\bbs.188sex.com\western"

    search_url(url_part_1, page_num, dir_path)

    return


def get_fahrenheit_pic(page_num):
    """
    获取https://bbs.188sex.com/forum-128-1.html上的所有图片,1为page_num
    :param page_num:页面数
    :return: NA
    """

    url_part_1 = "https://bbs.188sex.com/forum-128-"
    dir_path = r"C:\download\pic\bbs.188sex.com\fahrenheit"

    search_url(url_part_1, page_num, dir_path)

    return


def get_pure_pic(page_num):
    """
    获取https://bbs.188sex.com/forum-124-1.html上的所有图片,1为page_num
    :param page_num:页面数
    :return: NA
    """

    url_part_1 = "https://bbs.188sex.com/forum-124-"
    dir_path = r"C:\download\pic\bbs.188sex.com\pure"

    search_url(url_part_1, page_num, dir_path)

    return


def get_art_pic(page_num):
    """
    获取https://bbs.188sex.com/forum-96-1.html上的所有图片,1为page_num
    :param page_num:页面数
    :return: NA
    """

    url_part_1 = "https://bbs.188sex.com/forum-96-"
    dir_path = r"C:\download\pic\bbs.188sex.com\art"

    search_url(url_part_1, page_num, dir_path)

    return


if __name__ == "__main__":
    sex_page_num_list = list(range(1, 408))
    selfie_page_num_list = list(range(1, 435))
    western_page_num_list = list(range(1, 438))
    fahrenheit_page_num_list = list(range(1, 201))
    pure_page_num_list = list(range(1, 146))
    art_page_num_list = list(range(1, 72))

    pool = Pool(processes=cpu_count())
    try:
        # delete_empty_dir(dir_path)
        # pool.map(get_selfie_pic, selfie_page_num_list)
        # pool.map(get_western_pic, western_page_num_list)
        pool.map(get_pure_pic, pure_page_num_list)
        # pool.map(get_sex_pic, sex_page_num_list)
        # pool.map(get_fahrenheit_pic, fahrenheit_page_num_list)
        # pool.map(get_art_pic, art_page_num_list)
    except Exception:
        time.sleep(30)
        # delete_empty_dir(dir_path)
        # pool.map(get_selfie_pic, selfie_page_num_list)
        # pool.map(get_western_pic, western_page_num_list)
        pool.map(get_pure_pic, pure_page_num_list)
        # pool.map(get_sex_pic, sex_page_num_list)
        # pool.map(get_fahrenheit_pic, fahrenheit_page_num_list)
        # pool.map(get_art_pic, art_page_num_list)
