# -*- coding: utf-8 -*-
# Time    : 2019/12/24 20:34
# Author  : 辛放
# Email   : 1374520110@qq.com
# ID      : SZ160110115
# File    : get_news.py
# Software: PyCharm

import time
import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
import jieba
import math
from svmutil import *

def Min_max_nor(x,min,max):
    # 归一化计算
    return (x - min)/(max - min)

def Tf_idf(n,N,A,a):
    # 文本特征表示
    return (n/N)*math.log(A/a + 0.01)

#构建请求头
head = """
Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Encoding:gzip, deflate, br
Accept-Language:zh-CN,zh;q=0.8
Cache-Control:max-age=0
Connection:keep-alive
Host:fund.10jqka.com.cn
Upgrade-Insecure-Requests:1
Content-Type:application/x-www-form-urlencoded; charset=UTF-8
User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36
"""

def str_to_dict(header):
    #构造请求头,可以在不同函数里构造不同的请求头
    header_dict = {}
    header = header.split('\n')
    for h in header:
        h = h.strip()
        if h:
            k, v = h.split(':', 1)
            header_dict[k] = v.strip()
    return header_dict

def stopwordslist():
    #按照拥有的文件进行分词
    stopwords = [line.strip() for line in open('hit_stop_word.txt', encoding='UTF-8').readlines()]
    return stopwords


"""
def train_model_SVM():
    X_train, X_test, y_train, y_test = get_train_test_data()
    tv = TfidfVectorizer()
    train_data = tv.fit_transform(X_train)
    test_data = tv.transform(X_test)

    clf = SVC(C=1000.0)
    clf.fit(train_data, y_train)
    print(clf.score(test_data, y_test))
"""

def get_url():
    """
    获取网页上的信息并进行数据处理
    """

    form = pd.DataFrame(columns=('titel', 'artitle', 'sort'))
    for url_num in range (0,10,1):
        time.sleep(random.random() * 3)
        host = 'Referer:https://fund.10jqka.com.cn/smxw_list/index_%d.shtml'%url_num
        url = 'http://fund.10jqka.com.cn/smxw_list/index.shtml'
        header = head + host
        headers = str_to_dict(header)
        try:
            response = requests.get(url=url, headers=headers)
        except:
            pass

        html = response.text

        #获取当前网页信息

        soup = BeautifulSoup(html, 'html.parser')
        data_1 = soup.find_all('div', {'class': 'l-line'})
        num = 0
        sw = stopwordslist()
        for item in data_1:
            num += 1
            time.sleep(random.random() * 3)
            url_1 = item.select('a')[0]['href']
            url_2 = url_1
            print(url_2)

            #对每一个分页的信息进行详细的提取

            host_2 = """refer: https://fund.10jqka.com.cn
            """
            header_2 = head + host_2
            headers_2 = str_to_dict(header_2)
            try:
                response = requests.get(url=url_2, headers=headers_2)
            except:
                pass

            u = response.text
            soup = BeautifulSoup(u, "html.parser")
            article = soup.find_all('div', {'class': 'nml_arti'})
            title = soup.find_all('h2', {'class': 'main-title'})
            sort = soup.find_all('div',{'class':  'info-fr fr'})

            #将获取的信息存储到本地结构中，并进行分词处理
            try:
                tit = title[0].get_text()
                art = article[0].get_text()
                art = art.strip('\n')
                sor = sort[0].get_text()
                sor = str(sor).strip('\n')

                seg_list = jieba.cut(art,cut_all=False)
                outstr = ''
                for word in seg_list:
                    if word not in sw:
                        if word != '\t':
                            outstr += word
                            outstr += ' '
                form = form.append(pd.DataFrame({'titel':[tit],'article':[outstr],'sort':[sor]}),ignore_index= True)
            except:
                pass
    return form

def data_mark():
    word_mark = pd.DataFrame(columns = ('word','mark'))
    word_mark_g = pd.DataFrame(columns=('word', 'mark','w_g','w_m','w_b'))
    word_mark_b = pd.DataFrame(columns=('word', 'mark','w_g','w_m','w_b'))
    word_mark_m = pd.DataFrame(columns=('word', 'mark','w_g','w_m','w_b'))
    data = get_url()
    for i in range(1, data.shape[0], 1):
        for word in str(data.iloc[i]['article']).split(' '):
            try:
                if data.iloc[i]['sort'] == '利好' :
                    word_mark = word_mark.append(pd.DataFrame({'word': [word], 'mark': [1.0]}),ignore_index=True)
                    word_mark_g = word_mark_g.append(pd.DataFrame({'word': [word], 'mark': [1.0],'w_g':[0.0],'w_m':[0.0],'w_b':[0.0]}), ignore_index=True)
                elif data.iloc[i]['sort'] == '利空':
                    word_mark = word_mark.append(pd.DataFrame({'word': [word], 'mark': [1.0]}),ignore_index=True)
                    word_mark_b = word_mark_b.append(pd.DataFrame({'word': [word], 'mark': [1.0],'w_g':[0.0],'w_m':[0.0],'w_b':[0.0]}), ignore_index=True)
                elif data.iloc[i]['sort'] == '中性':
                    word_mark = word_mark.append(pd.DataFrame({'word': [word], 'mark': [1.0]}), ignore_index=True)
                    word_mark_m = word_mark_m.append(pd.DataFrame({'word': [word], 'mark': [1.0],'w_g':[0.0],'w_m':[0.0],'w_b':[0.0]}), ignore_index=True)
                else:
                    pass
            except:
                pass
    word_mark = word_mark.groupby('word').sum().reset_index()
    word_mark_g = word_mark_g.groupby('word').sum().reset_index()
    word_mark_b = word_mark_b.groupby('word').sum().reset_index()
    word_mark_m = word_mark_m.groupby('word').sum().reset_index()
    i = 0
    for index,row in word_mark_g.iterrows():
        i = i+1
        try:
            row['w_g'] = Tf_idf(row['mark'],word_mark_g.shape[0],word_mark.shape[0],word_mark.loc[word_mark['word'] == row['word']]['mark'])
            word_mark_g.ix[i,'w_g'] = row['w_g']
        except:
            pass
    i = 0
    for index,row in word_mark_b.iterrows():
        i = i + 1
        try:
            row['w_b'] = Tf_idf(row['mark'],word_mark_b.shape[0],word_mark.shape[0],word_mark.loc[word_mark['word'] == row['word']]['mark'])
            word_mark_g.ix[i,'w_b'] = row['w_b']
        except:
            pass
    i = 0
    for index,row in word_mark_m.iterrows():
        i = i + 1
        try:
            row['w_m'] = Tf_idf(row['mark'],word_mark_m.shape[0],word_mark.shape[0],word_mark.loc[word_mark['word'] == row['word']]['mark'])
            word_mark_g.ix[i,'w_m'] = row['w_m']
        except:
            pass
    print(word_mark_g.dropna(axis = 0,how = 'any'))
    word_mark_g.dropna(axis=0, how='any').to_csv('特征值.txt')
    return word_mark_g.dropna(axis = 0,how = 'any')

def main():
    data_mark()

if __name__ == '__main__':
    main()