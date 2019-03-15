# @author :Jiaqi Ding
# @time   :2019/3/15 23:37
# @file   :pear_video_downloader.py
# @IDE    :PyCharm
import requests
from bs4 import BeautifulSoup
import time
import os
import re
import random


def get_random_ip():
    """
    获得随机ip
    """
    a = random.randint(1, 255)
    b = random.randint(1, 255)
    c = random.randint(1, 255)
    d = random.randint(1, 255)
    random_ip = (str(a)+'.'+str(b)+'.'+str(c)+'.'+str(d))
    return random_ip


def fetch_hot_page_content(hot_page_url):
    """
    获取指定网站内容
    """
    request_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        'X-Forwarded-For': get_random_ip()
    }
    while True:
        try:
            req = requests.get(url=hot_page_url, headers=request_headers, timeout=2)
            break
        except:
            print('Error Happened in fetch_hot_page_content, Please wait 1 second')
            time.sleep(1)
    content = req.content
    return content


def get_video_ids(hot_page_content):
    """
        提取网页中所有视频页id
        <a href="video_1529607" class="actplay" target="_blank">

    """
    ids = []
    soup = BeautifulSoup(hot_page_content, features='html.parser', from_encoding="utf-8")
    for link in soup.findAll('a', class_='actplay'):
        if link['href'].find('video') > -1:
            ids.append(link['href'])
    ids = list(set(ids))
    return ids


def fetch_video_page_content(video_id):
    """
        获得视频页的内容
    """
    request_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        'X-Forwarded-For': get_random_ip()
    }
    video_url = 'https://www.pearvideo.com/'+video_id
    while True:
        try:
            req = requests.get(url=video_url, headers=request_headers, timeout=2)
            break
        except:
            print('Error Happened in fetch_video_page_content, Please wait 1 second')
            time.sleep(1)
    content = req.content
    return content


def get_video_name_and_link(video_page_content):
    """
        获取页面中srcUrl,即视频链接
    """
    purl = str(video_page_content)
    req = 'srcUrl="(.*?)"'
    purl_1 = re.findall(req, purl)
    video_link = purl_1[0]
    """
    获取指定id标签的内容
          <title>奇葩！业主收楼发现洗手盆仅巴掌大_詹姆斯-梨视频官网-Pear Video</title>
    """
    title_tag = BeautifulSoup(video_page_content, features='html.parser', from_encoding="utf-8").find('title')
    if not title_tag:
        print('unable to target title!')
        return False
    else:
        title = title_tag.text
    """
       去除文件名中的特殊字符
    """
    file_name = title
    file_name = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", file_name)
    full_file_name = '%s.mp4' % file_name
    name_and_link = (full_file_name, video_link)
    return name_and_link


def download_video(video_name, video_link):
    """
        下载视频
    """
    if os.path.exists(video_name):
        print("File Has Already Downloaded! Skip!")
    else:
        print("%s Downloading!" % video_name)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36Name',
            'X-Forwarded-For': get_random_ip()
        }
        f = open(video_name, 'wb')
        count = 0
        count_tmp = 0
        time1 = time.time()
        try:
            req = requests.get(url=video_link, stream=True, headers=headers, timeout=2)
            length = float(req.headers['content-length'])
            print("file size: %f M" % (length / 1024 / 1024))
            for chunk in req.iter_content(chunk_size=2048):
                if chunk:
                    f.write(chunk)
                    count += len(chunk)
                    if time.time() - time1 > 2:
                        p = count / length * 100
                        speed = (count - count_tmp) / 1024 / 1024 / 2
                        count_tmp = count
                        print(video_name + ': ' + '{:.2f}'.format(p) + '%' + ' Speed: ' + '{:.2f}'.format(speed) + 'M/S')
                        time1 = time.time()
            f.close()
            print("Download Success!")
            return True
        except:
            print('Error Happened in downloading')
            f.close()
            time.sleep(2)
            os.remove(video_name)
            print(video_name + " deleted.")

            return False


if __name__ == '__main__':
    # hot page content
    hot_page_content = fetch_hot_page_content('https://www.pearvideo.com/popular')
    # get all video ids
    video_ids = []
    video_ids += get_video_ids(hot_page_content)
    print(video_ids)
    for id in video_ids:
        # get video page content
        video_page_content = fetch_video_page_content(id)
        # print(video_page_content)
        # get video link
        video_name_and_link = get_video_name_and_link(video_page_content)
        print(video_name_and_link)
        if video_name_and_link is False:
            continue
        else:
            attempt = 0
            while not download_video(video_name_and_link[0], video_name_and_link[1]):
                attempt = attempt + 1
                if attempt >= 5:
                    break