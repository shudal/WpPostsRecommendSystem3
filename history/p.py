# -*- coding: utf-8 -*-
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')

import os
import configparser
import pymysql
print("Reading config...")
cur_path=os.path.dirname(os.path.realpath(__file__))
config_path=os.path.join(cur_path,'config.ini')
conf=configparser.ConfigParser()
conf.read(config_path)

db_host             = conf.get('database', 'host')
db_port             = int(conf.get('database', 'port'))
db_user             = conf.get('database', 'user')
db_password         = conf.get('database', 'password')
db_database_name    = conf.get('database','database')
db_table_prefix     = conf.get('database', 'table_prefix')
db_config = {'host' : db_host, 'port' : db_port, 'user' : db_user, 'password' : db_password, 'db' : db_database_name, 'prefix' : db_table_prefix}

print("Connecting database...")
db = pymysql.connect(host = db_config['host'],port = db_config['port'], user = db_config['user'], password  = db_config['password'], db = db_config['db'], charset = 'utf8mb4')
cursor = db.cursor()


print("Query posts...")
import datetime
today = datetime.date.today()
preweek = today - datetime.timedelta(days=8)
#sql_query_posts = "select ID,post_content from " + db_config['prefix'] + "_posts p where p.post_date > '" + str(preweek)  + "' and post_status='publish' and post_type='post'"

sql_query_posts = "select ID,post_content from " + db_config['prefix'] + "_posts where post_status='publish' and post_type='post'"
cursor.execute(sql_query_posts)
posts = cursor.fetchall()

id2index = {}
index2id = {}
post_ids = []
post_contents = []
myPosts = {}
for i in range(0, len(posts)):
    id2index[str(posts[i][0])] = i
    index2id[str(i)] = posts[i][0]
    post_ids.append(posts[i][0])
    post_contents.append(posts[i][1])

import csv
def getAstroKeyWordsDict():
    f = open('./data/astronomy_dict.csv', 'r', encoding='utf-8')
    csvreader = csv.reader(f)
    key_list = list(csvreader)
    values = list(1 for i in range(len(key_list)))
    lists = []
    for i in key_list:
        lists.append(i[0])
    dict_data = dict(zip(lists, values))
    return dict_data
astroKeyWordsDict = getAstroKeyWordsDict()

from jieba import posseg as pseg

jieba.load_userdict('data/jiebaAstroDicts.txt')

def tokenization(content):
    '''
    {标点符号、连词、助词、副词、介词、时语素、‘的’、数词、方位词、代词}
    {'x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r'}
    去除文章中特定词性的词
    :content str
    :return list[str]
    '''
    stop_flags = {'x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r'}
    stop_words = {'nbsp', '\u3000', '\xa0'}
    words = pseg.cut(content)
    return [word for word, flag in words if flag not in stop_flags and word not in stop_words]

myStr = "你好阿，1你到底是是1谁？2名字是什么？"
print(tokenization(myStr))
del_words = {
	'原微博', '评论情感分析可视化', '评论情感分析值', '评论情感倾向占比', '情感分析词云图'
}

def filter_words(sentences):
    '''
    过滤文章中包含无用词的整条语句
    :sentences list[str]
    :return list[str]
    '''
    text = []
    for sentence in sentences:
        if sentence.strip() and not [word for word in del_words if word in sentence]:
            text.append(sentence.strip())
    return text


print("The number of posts:" + str(len(post_contents)))


def tagsFilter(tags, isList=True):
    invalid_tags = ['wp', 'image', 'paragraph', 'nbsp', 'class', 'figure', 'figcaption', 'strong', 'www', 'id', 'img', 'src', 'http', 'h1astro', 'cn', 'blog', 'content', 'png', 'alt', 'div', 'center', 'aligncenter', 'align', 'width', 'height', '点击', '选择',  'Time', 'block', 'uploads', 'li', '插件', '勾选']
    filteredTags = []

    if isList:
        for i in range(0, len(tags)):
            if (tags[i][0] not in invalid_tags):
                filteredTags.append(tags[i])
    else:
        for i in range(0, len(tags)):
            if tags[i] not in invalid_tags:
                filteredTags.appendtags[i]
    return filteredTags

postsTags = []
postsSims = []


maxTopK = 2000
from jieba import analyse

for i in range(0, len(post_contents)):
    tags = analyse.extract_tags(post_contents[i], topK=maxTopK, withWeight=False, allowPOS=('n'))
    tags = tagsFilter(tags)

print(postsTags)



