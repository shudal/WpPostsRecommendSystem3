# -*- coding: utf-8 -*-

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

#从配置文件中获取数据信息
db_host             = conf.get('database', 'host')
db_port             = int(conf.get('database', 'port'))
db_user             = conf.get('database', 'user')
db_password         = conf.get('database', 'password')
db_database_name    = conf.get('database','database')
db_table_prefix     = conf.get('database', 'table_prefix')
db_config = {'host' : db_host, 'port' : db_port, 'user' : db_user, 'password' : db_password, 'db' : db_database_name, 'prefix' : db_table_prefix}

print("Connecting database...")
#连接数据库
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

post_ids = []
id2index = {}
post_contents = []
for i in range(0, len(posts)):
	id2index[str(posts[i][0])] = i
	post_ids.append(posts[i][0])
	post_contents.append(posts[i][1])

print("The number of posts:" + str(len(post_contents)))

tfidf_matrix = tf.fit_transform(post_contents)

print(tfidf_matrix)
from sklearn.metrics.pairwise import linear_kernel
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

def get_recos(postid, cosine_sim = cosine_sim):
	idx = id2index[str(postid)]
	sim_scores = list(enumerate(cosine_sim[idx]))
	sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
	return sim_scores

sql_query_users = "select user_id from " + db_config['prefix'] + "_ulike";
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

print("The number of users :" + str(len(userids)));

for i in range(0, len(userids)):
	
	sql_query_likes = "select post_id from " + db_config['prefix'] + "_ulike where user_id='" + str(userids[i])  +"' and status='like'"
	cursor.execute(sql_query_likes)
	likePostsIds2 = cursor.fetchall()
	likePosts  = {}
	for k in range(0, len(likePostsIds2)):
		a = get_recos(likePostsIds2[k][0])

		for l in range(0, len(a)):
			likePosts[a[l][0]] = likePosts.get(a[l][0], 0) + a[l][1]

	#print(likePosts)			
	sql_query_likes = "select post_id from " + db_config['prefix'] + "_ulike where user_id='" + str(userids[i])  +"' and status='unlike'"
	cursor.execute(sql_query_likes)
	unlikePostsIds2 = cursor.fetchall()
	for k in range(0, len(unlikePostsIds2)):
		a = get_recos(unlikePostsIds2[k][0])

		for l in range(0, len(a)):
			likePosts[a[l][0]] = likePosts.get(a[l][0], 0) - a[l][1]

	#print(likePosts)
	likePosts = sorted(likePosts.items(), key=lambda item: item[1], reverse=True)
	
	recoPostsIds = []
	for k in range(0, len(likePosts)):
		recoPostsIds.append(likePosts[k][0])
	#print(likePosts)
	str_reco_posts = ""
	for k in range(0, len(recoPostsIds)):
		str_reco_posts += ("|" + str(recoPostsIds[k]))

	sql_get_cbreco = "select meta_value from " + db_config['prefix'] + "_usermeta where user_id='" + str(userids[i]) + "' and meta_key='_perci_haku_cbreco'"
	cursor.execute(sql_get_cbreco)
	data = cursor.fetchone()

	if data is None:
		sql_set_cbreco = "insert into " + db_config['prefix'] + "_usermeta(`user_id`,`meta_key`,`meta_value`) values('" + str(userids[i])  + "', '_perci_haku_cbreco','" + str_reco_posts + "')"
	else :
		sql_set_cbreco = "update " + db_config['prefix'] + "_usermeta set meta_value='" + str_reco_posts + "' where user_id='" + str(userids[i])  +  "' and meta_key='_perci_haku_cbreco'"

	print(str_reco_posts)
	try :
		cursor.execute(sql_set_cbreco)
		db.commit()
	except Exception as e:
		print(str(e))
		db.rollback()

