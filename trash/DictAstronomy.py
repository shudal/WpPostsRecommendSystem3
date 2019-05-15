# -*- coding: utf-8 -*
import csv
from jieba import analyse

class DictAstronomy:
    def __init__(self):
        self.dictPath='./file_data/astronomy_dict.csv'

    def dict_read(self):
        f = open(self.dictPath, 'r', encoding='utf-8')
        csvreader = csv.reader(f)
        key_list = list(csvreader)
        values = list(3 for i in range(len(key_list)))
        lists = []
        for i in key_list:
            lists.append(i[0])
        # print(list)
        dict_data = dict(zip(lists, values))
        return dict_data

    def is_get_astronomy(self,dict_data,string,top_num):
        #提取前十个关键词
        keywords = analyse.extract_tags(string, topK=top_num, withWeight=True, allowPOS=('n', 'nr', 'ns'))
        astro_flag = 0
        count = 0
        keywords_astronomy=[]
        # 循环top10关键词  判断是否存在
        for item in keywords:
            print(item[0], item[1])
            try:
                if dict_data[item[0]]:
                    print(count, ' : ')
                    keywords_astronomy.append(item[0])
                    astro_flag = 1
                    count += 1
            except:
                print('Not find!')

        if astro_flag == 1 and count >= 2:
            return True, keywords_astronomy
        else:
            return False, keywords_astronomy
