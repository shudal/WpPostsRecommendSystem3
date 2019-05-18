# -*- coding: utf-8 -*-
import jieba

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

other_config = {
    'readOnePictureTime': eval(conf.get('other', 'readOnePictureTime')),
    'oneMinuteReadChars': eval(conf.get('other',  'oneMinuteReadChars')),
    'readTimeWeight'    : eval(conf.get('other',  'readTimeWeight'))
}

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
numberOfAllPosts = len(post_contents)
print("文章总数：" + str(numberOfAllPosts))

from bs4 import BeautifulSoup
getPostPredictReadTimeFromId = {}
def posts2time():
    for i in range(0, len(post_contents)):
        # print(post_contents[i])
        soup = BeautifulSoup(post_contents[i])
        numberOfImgTags = len(soup.find_all("img"))
        # print(numberOfImgTags)

        # 浩渺为单位
        readThePostTime = numberOfImgTags * other_config['readOnePictureTime'] * 1000

        pContent2 = soup.get_text().strip()
        pContent  = ""
        for c in pContent2:
            # 得到汉字
            if '\u4e00' <= c <= '\u9fa5':
                pContent += c

        # print(pContent)

        readThePostTime += (60 * 1000 * len(pContent) / other_config['oneMinuteReadChars'])

        getPostPredictReadTimeFromId[str(index2id[str(i)])] = readThePostTime
        #print(readThePostTime)
posts2time()
print("成功获取所有文章的预计阅读时间")
from jieba import posseg as pseg
jieba.load_userdict('data/jiebaAstroDicts.txt')

# 过滤关键词列表的函数
def tagsFilter(tags):
    invalid_tags = ['wp', 'image', 'paragraph', 'nbsp', 'class', 'figure', 'figcaption', 'strong', 'www', 'id', 'img', 'src', 'http', 'h1astro', 'cn', 'blog', 'content', 'png', 'alt', 'div', 'center', 'aligncenter', 'align', 'width', 'height', '点击', '选择',  'Time', 'block', 'uploads', 'li', '插件', '勾选', 'quote', 'blockquote', 'quote', '原微博', 'href', 'https', 'm', 'weibo', 'detail', 'https', 'wx3', 'sinaimg', 'orj360', 'b293gy1g30otv0e9ej20of0dh4bz', 'jpg', 'hr', 'h4', 'style', 'text', '评论', '情感', '分析', '可视化', 'h4', 'style', 'display', 'flex', 'justify', 'containerEcharts', 'px', 'px', 'containerEcharts2', 'px', 'px', 'script', 'type', 'javascript', 'echarts', 'echarts', 'min', 'js', 'script', 'script', 'type', 'javascript', 'var', 'dom', 'document', 'getElementById', 'var', 'myChart', 'echarts', 'init', 'dom', 'var', 'app', 'option', 'null', 'option', 'title', '值', 'subtext', 'right', 'top', 'tooltip', 'trigger', 'item', 'formatter', 'trigger', 'axis', 'axisPointer','line', 'shadow', 'dataset', 'source', 'amount', 'score', 'grid', 'containLabel', 'true', 'xAxis', 'name', 'amount', 'yAxis', 'type', 'category', 'visualMap', 'orient', 'horizontal', 'left', 'left', 'min', 'max', 'High', 'Score', 'Low', 'Score', 'Map', 'the', 'score', 'column', 'to', 'color', 'dimension', 'inRange', 'color', 'D7DA8B', 'E15457', 'series', 'type', 'bar', 'encode', 'Map', 'the', 'amount', 'column', 'to', 'axis', 'amount', 'Map', 'the', 'product', 'column', 'to', 'axis', 'score', 'itemStyle', 'normal', 'color', 'function', 'params', 'var', 'colorList', 'e7e54', 'e7e54', 'e7e54', 'e7e54', 'b6b2', 'b6b2', 'e44f2f', 'e44f2f', 'e44f2f', 'e44f2f', 'return', 'colorList', 'params', 'dataIndex', 'if', 'option', 'typeof', 'option', 'object', 'myChart', 'setOption', 'option', 'true', 'script', 'script', 'type', 'javascript', 'var', 'dom', 'document', 'getElementById', 'containerEcharts2', 'var', 'myChart', 'echarts', 'init', 'dom', 'var', 'app', 'option', 'null', 'option', 'title', '倾向', '占', 'subtext', 'right', 'top', 'tooltip', 'trigger', 'item', 'formatter', 'legend', 'orient', 'horizontal', 'bottom', 'data', 'containerEchartsTitle', 'font', 'size', 'black', '词', '云图', 'br', 'EchartsWordcloud', 'cdn', 'bootcss', 'com', 'simple', 'wordcloud', 'chart', 'EchartsWordcloud', 'wordCloud', 'gridSize', 'sizeRange', 'rotationRange', 'shape', 'pentagon', 'drawOutOfBound', 'textStyle', 'rgb', 'Math', 'round', 'Math', 'random', 'Math', 'round', 'Math', 'random', 'Math', 'round', 'Math', 'random', 'join', 'emphasis', 'shadowBlur', 'shadowColor', 'value','window', 'onresize', 'resize', 'Again']
    filteredTags = []

    for i in range(0, len(tags)):
        if tags[i] not in invalid_tags:
            for c in tags[i]:
                # 关键词必须含有中文字符
                if '\u4e00' <= c <= '\u9fa5':
                    filteredTags.append(tags[i])
                    break
    return filteredTags

# 生成字符串关键词
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
    words = [word for word, flag in words if flag not in stop_flags and word not in stop_words]

    words = tagsFilter(words)

    return words

# print(tokenization(post_contents[3]))
print("开始训练模型......")
posts_words = [tokenization(content) for content in post_contents]
print("     训练模型完成!")

from gensim import corpora, models, similarities
dictionary = corpora.Dictionary(posts_words)
corpus = [dictionary.doc2bow(text) for text in posts_words]
lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=500)
index = similarities.MatrixSimilarity(lsi[corpus])

posts_vecs = []
for i in range(0, len(posts_words)):
    posts_vecs.append(dictionary.doc2bow(posts_words[i]))
print("size of postsVecs: " + str(len(posts_vecs)))

sql_query_users = "select userid from " + "perci_haku_readhistory";
cursor.execute(sql_query_users)
users3 = cursor.fetchall()
users2 = []
for i in range(0, len(users3)):
    userid = int(users3[i][0])
    if userid>100000000:
        continue
    users2.append(userid);

userids = list(set(users2))
userids.sort(key=users2.index)
print("用户总数 :" + str(len(userids)));
print(userids)
for i in range(0, len(userids)):
    print("开始处理id为" + str(userids[i]) + "的用户......")
    sql_query_history = "select * from " + "perci_haku_readhistory"  + " where userid='" + str(userids[i]) + "'"
    cursor.execute(sql_query_history)
    history = cursor.fetchall()

    print(history)

    postids = []
    getPostReadTimeFromId = {}
    for k in range(0, len(history)):
        postids.append(history[k][2])
        getPostReadTimeFromId[str(history[k][2])] = history[k][4]

    selectedIds = []
    postIndexes = []
    print(postids)
    # 选最多二十篇近期游览的文章
    for k in range(len(postids)-1, -1, -1):
        # 已经有了20个则退出
        if len(postIndexes) >= 20:
            break

        if postids[k] not in selectedIds:
            try:
                selectedIds.append(postids[k])
            except:
                continue
            try:
                postIndexes.append(id2index[str(postids[k])])
            except:
                pass

    # print("postIndexes:")
    print(postIndexes)
    allRes = []
    for k in range(0, len(postIndexes)):
        sims = index[lsi[posts_vecs[k]]]
        res = list(enumerate(sims))
        res = sorted(res, key=lambda x: x[1])

        # 选两篇
        for l in range(len(res)-2, len(res)-4, -1):
            if l < 0:
                break
            nowPostIndex = postIndexes[k]
            nowPostId    = index2id[str(nowPostIndex)]
            finalL = res[l][1] * (1 - other_config['readTimeWeight']) + res[l][1] * other_config['readTimeWeight'] * getPostReadTimeFromId[str(nowPostId)] / getPostPredictReadTimeFromId[str(nowPostId)] ;

            # print("L=" + str(res[l][1]))
            # print(" finalL=" + str(finalL))
            allRes.append([res[l][0], finalL])

    allRes = sorted(allRes, key=lambda  x: x[1])
    allRes = list(reversed(allRes))

    print(allRes)
    post_recoIds = []
    for k in range(0, len(allRes)):
        if len(post_recoIds) >= 10:
            break
        post_recoIds.append(index2id[str(allRes[k][0])])


    #print(post_recodIds)
    #print(post_recoIds)
    #print(post_recoIds)
    #print(postids)
    #print(selectedIds)
    #print(postIndexes)
    #print(userids[i])


    # 保存
    userid = userids[i]
    top_items = []
    for k in range(0, len(post_recoIds)):
        top_items.append(str(post_recoIds[k]))

    sql_get_perreco = "select meta_value from " + db_config['prefix'] + "_usermeta where user_id='" + str(userid) + "' and meta_key='_perci_haku_cbreco'"
    cursor.execute(sql_get_perreco)
    data = cursor.fetchone()

    if data is None:
        sql_set_perreco = "insert into " + db_config['prefix'] + "_usermeta (`user_id`, `meta_key`, `meta_value`) values ('" + str(userid) + "', '_perci_haku_cbreco','"
    else :
        sql_set_perreco = "update " + db_config['prefix'] + "_usermeta set meta_value='"


    for k in range(0, len(top_items)):
        sql_set_perreco = sql_set_perreco + "|" + top_items[k]

    if data is None:
        sql_set_perreco = sql_set_perreco + "')"
    else:
        sql_set_perreco = sql_set_perreco  + "' where user_id='" + str(userid) + "' and meta_key='_perci_haku_cbreco'"

    try :
        cursor.execute(sql_set_perreco)
        db.commit()
        print("     写入推荐文章id成功!")
    except Exception as e:
        print(str(e))
        db.rollback()
        print("     写入推荐文章id失败!")
        
    
print("全部完成!")


