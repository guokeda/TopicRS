# encoding=utf-8
import jieba
import scipy.linalg as la
import matplotlib.pyplot as plt
from pylab import *
import sqlite3
import os

# option database

cur_dir = os.path.dirname(__file__)
db = os.path.join(cur_dir, 'TopicBank.sqlite')

# 画图时正常显示中文字体
mpl.rcParams['font.sans-serif'] = ['SimHei']
# stopchracters = ['这', '的','是','与','、', '：', '\n', ]
# stopchracters = ['这', '的', '、', '：', ]
# stopwords = open("stopwords.txt", encoding='UTF-8')
# stopchracters = ['\n', '考查']
# for w in stopwords:
#     stopchracters.append(w.rstrip('\n'))


# recommend the number of similarity document
recnumber = 3
# reducted dimension
dim = 2
# erro topic number
# erronum = 10


class CS:
    def __init__(self, stopchracters):
        self.stopchracters = stopchracters
        self.worddic = {}  # it includes all words appear in document
        self.doccount = 1  # express which document

    # read corpus and build word dictionary
    def buildworddictionary(self):
        conn = sqlite3.connect(db)
        cur = conn.cursor()

        query = "select analysis from topicbank"
        results = cur.execute(query).fetchall()
        for i in range(len(results)):
            self.wordsegmentation(results[i][0])
        cur.close()
        conn.close()
        # build word dictionary,it includes all words appear in document

    def wordsegmentation(self, line):
        wordlist = jieba.cut_for_search(line)
        # wordlist = jieba.cut(line)
        for word in wordlist:
            if word in self.stopchracters:
                continue
            elif word not in self.worddic:
                self.worddic[word] = [self.doccount]  # word bind that it appear document number
            else:
                self.worddic[word].append(self.doccount)
        self.doccount += 1

    # build term-document matrix
    def buidmatrxi(self):
        self.keylist = [key for key in self.worddic.keys() if
                        len(self.worddic[key]) >= 2]  # filter frequences of word in worddic too low or too high
        # self.keylist.sort()
        matrix = np.zeros([len(self.keylist), self.doccount])  # initial term-document matrix
        for i, key in enumerate(self.keylist):
            for d in self.worddic[key]:
                matrix[i, d] += 1
        return matrix

    # it use SVD factor term-document matrix
    def factormatrix(self):
        m = self.buidmatrxi()
        self.u, e, self.vt = la.svd(m)


    # calculate two documents similarity
    def calsimilarity(self, vec1, vec2):
        vec2 = vec2.T
        # decimal.getcontext().prec = 3
        # return decimal.Decimal(dot(vec1, vec2)) /decimal.Decimal((norm(vec1) * norm(vec2)))
        return round(dot(vec1, vec2) / (norm(vec1) * norm(vec2)), 3)

    # 在visualization函数中调用，这样可以节省因分解出来的矩阵造成的内存浪费问题。
    def recommend(self, docnumber, vt):
        v = vt
        # similarity as key,docnumber as value,in order to w
        w = {}
        for d in range(self.doccount):
            if d == docnumber:
                continue
            else:
                sim = self.calsimilarity(v[docnumber], v[d])
                w[d] = sim
        w_sort = sorted(w.items(), key=lambda x: x[1], reverse=True)
        return w_sort[:3]  # returm first three document as recommend

    def matrixRound(self, m):
        r, l = m.shape
        for i in range(r):
            for j in range(l):
                m[i, j] = round(m[i, j], 3)
        return m


    def mianfunction(self,id_recommend):
        vt_reduction = self.vt[:dim].T
        recommend_doc = self.recommend(id_recommend, vt_reduction)
        return [id[0] for id in recommend_doc]

