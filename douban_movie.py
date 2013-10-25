#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mechanize,requests,sys,re,cPickle,socket
# from daili import get_daili
from bs4 import BeautifulSoup

reload(sys) 
sys.setdefaultencoding('utf-8')

FAV_CELEBRITIES_URL="http://movie.douban.com/people/"
MOVIE_URL_PRE="http://movie.douban.com/celebrity/"
MOVIE_URL_MIDDLE='/movies?start='
MOVIE_URL_SUFFIX="&format=text&sortby=vote&role=A"
MOVIE_URL_DIR_SUFFIX="&format=text&sortby=vote&role=D"

USER_MOVIE_PRE='http://movie.douban.com/people/'
USER_MOVIE_MIDDLE='/collect?mode=list&start='
USER_MOVIE_SUFFIX='&rating='

MOVIE_REAL='http://movie.douban.com/subject/'

MOVIE_ALL_PRE='http://movie.douban.com/people/'
MOVIE_ALL_MIDDLE='/collect?sort=time&amp;start='
MOVIE_ALL_SUFFIX='&amp;filter=all&amp;mode=list&amp;tags_sort=count'

# proxies_list=['http://%s'%ip for ip in get_daili()]
proxies_list=['http://%s'%ip for ip in cPickle.load(open("F:/ip.txt"))]
proxies_number=0
proxies = {
  "http": proxies_list[proxies_number],
}

def get_next_proxy():
    global proxies_number
    proxies_number+=1
    global proxies
    proxies['http']=proxies_list[proxies_number]
    print(u"已更换代理%s"%proxies)
    return proxies

#获得某个用户喜欢的名人的id号,以列表形式返回
def get_celebrities(user_id):
    #1.在如http://movie.douban.com/people/knight66/celebrities?start=0这种页面找到名人的id
    celebrities_list=[]
    def request_cele():
        global proxies
        try:
            r=requests.get('%s%s/celebrities?start=%s'%(FAV_CELEBRITIES_URL,user_id,start_number),proxies=proxies,timeout=8)
        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout,socket.timeout):
            proxies=get_next_proxy()
            r=request_cele()
        return r
    for start_number in xrange(0,75,15):

        while 1:
            r=request_cele()
            if r.status_code!=200:
                print(r.status_code)
                proxies=get_next_proxy()
                r=request_cele()
            else:
                break

        soup=BeautifulSoup(r.content)
        cele_ids=soup.findAll("a",href=re.compile("http://movie.douban.com/celebrity"))
        # print(cele_ids)
        celebrities_ids=set([re.search('\d{7}',cele_id["href"]).group() for cele_id in cele_ids])
        celebrities_list.extend(celebrities_ids)
        if(len(celebrities_ids)==0):
             break
    print(u"已经获取用户收藏的影人")
    return celebrities_list

#获得某个用户分别喜欢几星级影片的字典类型
def get_star_movies(user_id):

    star_movies={}
    #获取所有已经看到的电影
    movies_have_seen=[]
    #定义获得某个页面的函数
    def request_movie():
        global proxies
        try:
            r = requests.get("%s%s%s%s%s%s"%(USER_MOVIE_PRE,user_id,USER_MOVIE_MIDDLE,str(start_number),USER_MOVIE_SUFFIX,str(star)),proxies=proxies,timeout=8)
        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout,socket.timeout):
            proxies=get_next_proxy()
            r=request_movie()
        return r
    def request_movie_seen():
        global proxies
        try:
            r=requests.get('%s%s%s%s%s'%(MOVIE_ALL_PRE,user_id,MOVIE_ALL_MIDDLE,start_number,MOVIE_ALL_SUFFIX),proxies=proxies,timeout=8)
        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout,socket.timeout):
            proxies=get_next_proxy()
            r=request_movie_seen()
        return r
    #获得五,四,星的影片
    for star in xrange(5,3,-1):
        star_movie_ids=[]
        for start_number in xrange(0,9000,30):
            r=request_movie()
            while 1:
                if r.status_code!=200:
                    print(r.status_code)
                    proxies=get_next_proxy()
                    r=request_movie()
                else:
                    break
            soup=BeautifulSoup(r.content)
            href_list=soup.findAll("a",href=re.compile('http://movie.douban.com/subject'))
            part_id_list=[re.search('\d{7,8}',href['href']).group() for href in href_list]
            star_movie_ids.extend(part_id_list)
            if len(href_list)==0:
                break
        star_movies[star]=star_movie_ids
        print(u"%s星级电影已经抓取"%star)

    # 获取所有已看电影
    for start_number in xrange(0,9000,30):
        r=request_movie_seen()
        while 1:
            if r.status_code!=200:
                print(r.status_code)
                proxies=get_next_proxy()
                r=request_movie_seen()
            else:
                break


        soup=BeautifulSoup(r.content)
        href_list=soup.findAll("a",href=re.compile('http://movie.douban.com/subject'))
        part_id_list=[re.search('\d{7,8}',href['href']).group() for href in href_list]
        movies_have_seen.extend(part_id_list)
        if len(href_list)==0:
            break
    print(u"已经获取用户喜欢的影片了!")
    return star_movies,movies_have_seen



#几星级的影片对应获得几星级的名人,输入是星级和电影列表,输出是一个等级的电影人列表
def get_star_cele(star_movie_ids,loved_cele_mv_dict):

    celebrities_list=[]
    directors_list=[]
    def request_real():
        global proxies
        try:
            r = requests.get('%s%s'%(MOVIE_REAL,star_movie_id),proxies=proxies,timeout=8)
        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout,socket.timeout):
            proxies=get_next_proxy()
            r=request_real()
        return r
    for star_movie_id in star_movie_ids:
        print(star_movie_id)
        r=request_real()
        while 1:
            if (r.status_code==200) :
                break
            elif (r.status_code==404):
                break
            else :
                print(r.status_code)
                proxies=get_next_proxy()
                r=request_real()

        soup=BeautifulSoup(r.content)
        href_list=soup.find_all('a',{"rel":"v:starring"},href=re.compile('/celebrity/\d{7}'))
        part_id_list=[re.search('\d{7}',href['href']).group() for href in href_list]
        if len(part_id_list)>6:
            part_id_list=part_id_list[0:6]
        celebrities_list.extend(part_id_list)
        #处理导演
        part_directors_list=soup.find_all('a',{'rel':'v:directedBy'},href=re.compile('/celebrity/\d{7}'))
        part_directors_list=[re.search('\d{7}',href['href']).group() for href in part_directors_list]
        directors_list.extend(part_directors_list)

        #处理什么影人对应什么电影

        # for cele_id in part_id_list:
        #     try:
        #         loved_cele_mv_dict[cele_id].append(star_movie_id)
        #     except KeyError:
        #         mv_list=[]
        #         mv_list.append(star_movie_id)
        #         loved_cele_mv_dict[cele_id]=mv_list
    
        print(u'已经获取喜欢的电影%s所有的演员了 %s'%(star_movie_id,len(part_id_list)))

    return celebrities_list,directors_list

#输入star_movies输出几分对应的影星的字典
def cele_filter(star_movies,loved_cele_list):
    original_star_movies={}
    original_star_movies["directors"]=[]
    #生成用户喜欢的电影中什么电影有什么演员的字典类型
    loved_cele_mv_dict={}
    for star,movies in star_movies.iteritems():
        cele_list,directors_list=get_star_cele(movies,loved_cele_mv_dict)
        original_star_movies[star-2]=cele_list
        original_star_movies["directors"].extend(directors_list)

    #已经收藏的电影人给予六分
    original_star_movies[6]=loved_cele_list
    print(u"给影人的打分完成!")
    return (original_star_movies,loved_cele_mv_dict)



def get_final_rate_dic(original_star_movies):
    final_rate_dic={}
    print(original_star_movies)
    for rate,celebrities_list in original_star_movies.iteritems():
        if rate=='directors':
            dir_rate=5
            for celebrity in celebrities_list:
                one_cele_mv_list,one_cele_star_list=get_movie_dir(celebrity)
                for one_cele_movie,one_cele_star in zip(one_cele_mv_list,one_cele_star_list):
                    try:
                        if one_cele_star !='':
                            rate_and_cele=final_rate_dic[one_cele_movie]
                            past_rate=rate_and_cele["rate"]
                            final_rate_dic[one_cele_movie]["rate"]=past_rate+dir_rate
                            final_rate_dic[one_cele_movie]["celes"].append(celebrity)
                    except KeyError:
                        if one_cele_star !='':
                            rate_and_cele={"rate":0,"celes":[],'star':0}
                            rate_and_cele["rate"]=dir_rate
                            rate_and_cele['star']=float(one_cele_star)                    
                            rate_and_cele["celes"].append(celebrity)
                            final_rate_dic[one_cele_movie]=rate_and_cele
        else:
            for celebrity in celebrities_list:
                one_cele_mv_list,one_cele_star_list=get_movie(celebrity)
                for one_cele_movie,one_cele_star in zip(one_cele_mv_list,one_cele_star_list):
                    try:
                        if one_cele_star !='':
                            rate_and_cele=final_rate_dic[one_cele_movie]
                            past_rate=rate_and_cele["rate"]
                            final_rate_dic[one_cele_movie]["rate"]=past_rate+rate
                            final_rate_dic[one_cele_movie]["celes"].append(celebrity)
                    except KeyError:
                        if one_cele_star !='':
                            rate_and_cele={"rate":0,"celes":[],'star':0}
                            rate_and_cele["rate"]=rate
                            rate_and_cele['star']=float(one_cele_star)            
                            rate_and_cele["celes"].append(celebrity)
                            final_rate_dic[one_cele_movie]=rate_and_cele
    return final_rate_dic
#打分系统
def modify_final_rate(final_rate_dic,movies_have_seen):
    for movie_id,movie_item in final_rate_dic.iteritems():
        #增加改进后的评分
        original_rate=movie_item["rate"]
        original_star=(movie_item["star"])
        final_rate_dic[movie_id]["final_rate"]=original_rate*(1+original_star/10)


    #如果这部电影已经看过则删除
    for movie_id in movies_have_seen:
        try:
            del final_rate_dic[movie_id] 
        except KeyError:
            pass
        print(u'已经删除看过的电影%s'%(movie_id))
    #根据final_rate来评分
    final_rate_list=sorted(final_rate_dic.iteritems(),key=lambda x:x[1]['final_rate'],reverse=True)[0:100]
    original_movie_list=[movie[0] for movie in final_rate_list]
    print(final_rate_list)
    with open("F:/a.txt","w") as tt:
        for fff in final_rate_list:
            tt.write("%s\n"%(fff))

    return final_rate_list,original_movie
#对前一百部电影爬取并筛选
def filter_top_movie(final_rate_list,original_movie_list):
    movie_delte_list=[]
    for movie in original_movie_list:
        pass




# 生成导演参与的电影列表
def get_movie_dir(celebrity):
    mv_list=[]
    star_list=[]
    def request_dir():
        global proxies
        try:
            r=requests.get("%s%s%s%s%s"%(MOVIE_URL_PRE,celebrity,MOVIE_URL_MIDDLE,page_number,MOVIE_URL_DIR_SUFFIX),proxies=proxies,timeout=8)
        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout,socket.timeout):
            proxies=get_next_proxy()
            r=request_dir()
        return r
    for page_number in xrange(0,800,25):
        r=request_dir()
        while 1:
            if r.status_code!=200:
                print(r.status_code)
                proxies=get_next_proxy()
                r=request_dir()
            else:
                break
        soup=BeautifulSoup(r.content)
        href_list=soup.find_all("a",href=re.compile("http://movie.douban.com/subject"))
        part_cele_list=[re.search("\d{7,8}",movieId["href"]).group() for movieId in href_list]
        mv_list.extend(part_cele_list)
        #获取每部电影的评分
        part_star_list=[star.text for star in soup.findAll('span','rating_nums')]
        star_list.extend(part_star_list)
        #如果没有一个影片则退出循环
        if('' in part_star_list):
            break
    print(u"已完成对导演%s的搜索,共有%s部电影"%(celebrity,len(mv_list)))
    return (mv_list,star_list)

# 生成名人参与电影的列表
def get_movie(celebrity):
    mv_list=[]
    star_list=[]
    def request_cele():
        global proxies
        try:
            r=requests.get("%s%s%s%s%s"%(MOVIE_URL_PRE,celebrity,MOVIE_URL_MIDDLE,page_number,MOVIE_URL_SUFFIX),proxies=proxies,timeout=8)
        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout,socket.timeout):
            proxies=get_next_proxy()
            r=request_cele()
        return r
    for page_number in xrange(0,800,25):
        r=request_cele()
        while 1:
            if r.status_code!=200:
                print(r.status_code)
                proxies=get_next_proxy()
                r=request_cele()
            else:
                break
        soup=BeautifulSoup(r.content)
        href_list=soup.find_all("a",href=re.compile("http://movie.douban.com/subject"))
        part_cele_list=[re.search("\d{7,8}",movieId["href"]).group() for movieId in href_list]
        mv_list.extend(part_cele_list)
        #获取每部电影的评分
        part_star_list=[star.text for star in soup.findAll('span','rating_nums')]
        star_list.extend(part_star_list)
        #如果没有一个影片则退出循环
        if('' in part_star_list):
            break
    print(u"已完成对影人%s的搜索,共有%s部电影"%(celebrity,len(mv_list)))
    return (mv_list,star_list)

#生成电影的字典,key是电影id,value是数组,数组中是名人
def get_result(celebrities_list):
    cele_movie_dict={}
    for celebrity in celebrities_list:
        #生成名人参与电影的列表
        movie_list=get_movie(celebrity)
        cele_movie_dict[celebrity]=movie_list

    return cele_movie_dict

def dic_transform(cele_movie_dict):
    movie_cele_dict={}
    for key,values in cele_movie_dict.iteritems():
        for value in values:
            try:
                this_item=movie_cele_dict[value]
                movie_cele_dict[value].append(key)
            except KeyError:
                this_item=[]
                this_item.append(key)
                movie_cele_dict[value]=this_item
    
    for key,values in movie_cele_dict.iteritems():
        if(len(values)>1):
            print("%s:%s"%(key,values))
    

if __name__=="__main__":
    #获得喜欢的电影人
    loved_cele_list=get_celebrities('cliffedge')



    star_movies,movies_have_seen=get_star_movies("cliffedge")
    original_star_movies,loved_cele_mv_dict = cele_filter(star_movies,loved_cele_list)
    final_rate_dic = get_final_rate_dic(original_star_movies)
    final_rate_list,original_movie_list=modify_final_rate(final_rate_dic,movies_have_seen)


