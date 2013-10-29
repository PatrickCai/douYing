#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests,sys,re,cPickle,socket
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
        r=request_cele()
        while 1:
            if (r.status_code==200) :
                break
            elif (r.status_code==404):
                break
            else :
                print(r.status_code)
                proxies=get_next_proxy()
                r=request_cele()

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
                if (r.status_code==200) :
                    break
                elif (r.status_code==404):
                    break
                else :
                    print(r.status_code)
                    proxies=get_next_proxy()
                    r=request_movie_seen()

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
            if (r.status_code==200) :
                break
            elif (r.status_code==404):
                break
            else :
                print(r.status_code)
                proxies=get_next_proxy()
                r=request_movie_seen()



        soup=BeautifulSoup(r.content)
        href_list=soup.findAll("a",href=re.compile('http://movie.douban.com/subject'))
        part_id_list=[re.search('\d{7,8}',href['href']).group() for href in href_list]
        movies_have_seen.extend(part_id_list)
        if len(href_list)==0:
            break
    print(u"已经获取用户喜欢的影片了!")
    return star_movies,movies_have_seen

#几星级的影片对应获得几星级的名人,输入是星级和电影列表,输出是一个等级的电影人列表
def get_star_cele(star_movie_ids,loved_cele_mv_dict,loved_direc_mv_dict):

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
        for cele_id in part_id_list:
            try:
                loved_cele_mv_dict[cele_id].append(star_movie_id)
            except KeyError:
                mv_list=[]
                mv_list.append(star_movie_id)
                loved_cele_mv_dict[cele_id]=mv_list
        #处理什么导演对应什么电影
        for direc_id in part_directors_list:
            try:
                loved_direc_mv_dict[direc_id].append(star_movie_id)
            except KeyError:
                mv_list=[]
                mv_list.append(star_movie_id)
                loved_direc_mv_dict[direc_id]=mv_list
    
        print(u'已经获取喜欢的电影%s所有的演员了 %s'%(star_movie_id,len(part_id_list)))

    return celebrities_list,directors_list

#输入star_movies输出几分对应的影星的字典
def cele_filter(star_movies,loved_cele_list):
    def sort_original_star_movies(original_star_movies):
        #获得{cele_id:rate,cele_id:rate}字典
        cele_rate_dic={}
        direc_rate_dic={}
        for rate,cele_id_list in original_star_movies.iteritems():
            if rate!='directors':
                for cele_id in cele_id_list:
                    try:
                        pre_rate=cele_rate_dic[cele_id]
                        cele_rate_dic[cele_id]=pre_rate+rate
                    except KeyError:
                        cele_rate_dic[cele_id]=rate
            elif rate=='directors':
                for cele_id in cele_id_list:
                    try:
                        pre_rate=direc_rate_dic[cele_id]
                        direc_rate_dic[cele_id]=pre_rate+1
                    except KeyError:
                        direc_rate_dic[cele_id]=1

        #对cele_rate_dic,direc_rate_dic排序生成list
        cele_rate_list=sorted(cele_rate_dic.iteritems(),key=lambda x:x[1],reverse=True)
        direc_rate_list=sorted(direc_rate_dic.iteritems(),key=lambda x:x[1],reverse=True)

        #将original_star_movies重新生成,也产生导演的评分列表
        original_star_movies.clear()
        original_direc_movies={}

        #将所有的影人和导演分成五个等级,评分从6分到2分
        rate_slice=len(cele_rate_list)/5+1
        original_star_movies[6]=[cele[0] for cele in cele_rate_list[0:rate_slice]]
        original_star_movies[5]=[cele[0] for cele in cele_rate_list[rate_slice:2*rate_slice]]
        original_star_movies[4]=[cele[0] for cele in cele_rate_list[2*rate_slice:3*rate_slice]]
        original_star_movies[3]=[cele[0] for cele in cele_rate_list[3*rate_slice:4*rate_slice]]
        original_star_movies[2]=[cele[0] for cele in cele_rate_list[4*rate_slice:len(cele_rate_list)]]

        #将导演分成三个等级,评分从7分到5分
        direc_slice=len(direc_rate_list)/3
        original_direc_movies[7]=[direc[0] for direc in direc_rate_list[0:direc_slice]]
        original_direc_movies[6]=[direc[0] for direc in direc_rate_list[direc_slice:2*direc_slice]]
        original_direc_movies[5]=[direc[0] for direc in direc_rate_list[2*direc_slice:len(direc_rate_list)]]

        return original_star_movies,original_direc_movies


    original_star_movies={}
    original_star_movies["directors"]=[]
    #生成用户喜欢的电影中什么电影有什么演员的字典类型
    loved_cele_mv_dict={}
    loved_direc_mv_dict={}
    for star,movies in star_movies.iteritems():
        cele_list,directors_list=get_star_cele(movies,loved_cele_mv_dict,loved_direc_mv_dict)
        original_star_movies[star-2]=cele_list
        original_star_movies["directors"].extend(directors_list)

    #已经收藏的电影人给予六分
    original_star_movies[6]=loved_cele_list

    original_star_movies,original_direc_movies = sort_original_star_movies(original_star_movies)
    print(u"给影人的打分完成!")
    return (original_star_movies,original_direc_movies, loved_cele_mv_dict)



def get_final_rate_dic(original_star_movies,original_direc_movies):
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
                if (r.status_code==200) :
                    break
                elif (r.status_code==404):
                    break
                else :
                    print(r.status_code)
                    proxies=get_next_proxy()
                    r=request_dir()

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
                if (r.status_code==200) :
                    break
                elif (r.status_code==404):
                    break
                else :
                    print(r.status_code)
                    proxies=get_next_proxy()
                    r=request_cele()
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

    final_rate_dic={}
    print(original_star_movies)
    for rate,celebrities_list in original_star_movies.iteritems():
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
                    if one_cele_star !='':#某些电影可能没有评价则删除
                        rate_and_cele={"rate":0,"celes":[],'star':0,"direc":[]}
                        rate_and_cele["rate"]=rate
                        rate_and_cele['star']=float(one_cele_star)            
                        rate_and_cele["celes"].append(celebrity)
                        final_rate_dic[one_cele_movie]=rate_and_cele

    for rate,direc_list in original_direc_movies.iteritems():
        for direc in direc_list:
            one_cele_mv_list,one_cele_star_list=get_movie_dir(direc)
            for one_cele_movie,one_cele_star in zip(one_cele_mv_list,one_cele_star_list):
                try:
                    if one_cele_star !='':
                        rate_and_cele=final_rate_dic[one_cele_movie]
                        past_rate=rate_and_cele["rate"]
                        final_rate_dic[one_cele_movie]["rate"]=past_rate+rate
                        final_rate_dic[one_cele_movie]["direc"].append(direc)
                except KeyError:
                    if one_cele_star !='':
                        rate_and_cele={"rate":0,"celes":[],'star':0,"direc":[]}
                        rate_and_cele["rate"]=rate
                        rate_and_cele['star']=float(one_cele_star)            
                        rate_and_cele["direc"].append(direc)
                        final_rate_dic[one_cele_movie]=rate_and_cele

    #对此处的评分做标准分转换
    final_rate_list=sorted(final_rate_dic.iteritems(),key=lambda x:x[1]['rate'],reverse=True)[0:200]
    final_rate_slice=len(final_rate_list)/20
    #删除两百名以后的电影
    all_movie_list=[x[0] for x in final_rate_dic.iteritems()]
    good_movie_list=[y[0] for y in final_rate_list]
    delte_movie_list=[z for z in all_movie_list if z not in good_movie_list]
    for movie in delte_movie_list:
        del final_rate_dic[movie]
    #标准分从五十分到三十分
    for after_rate in range(50,30,-1):
        slice_start=50-after_rate
        for movie_id in  [movies_id[0]  for movies_id in final_rate_list[slice_start*final_rate_slice:(slice_start+1)*final_rate_slice]]:
            print(movie_id)
            final_rate_dic[movie_id]['rate']=after_rate
    print(final_rate_dic)
    #对导演寻找相应电影
    return final_rate_dic

#打分系统
def modify_final_rate(final_rate_dic,movies_have_seen):
    for movie_id,movie_item in final_rate_dic.iteritems():
        #增加改进后的评分
        original_rate=movie_item["rate"]
        original_star=movie_item["star"]
        final_rate_dic[movie_id]["final_rate"]=original_rate*(1+original_star/10)


    #如果这部电影已经看过则删除
    for movie_id in movies_have_seen:
        try:
            del final_rate_dic[movie_id] 
        except KeyError:
            pass
        print(u'已经删除看过的电影%s'%(movie_id))
    #根据final_rate来评分
    final_rate_list=sorted(final_rate_dic.iteritems(),key=lambda x:x[1]['final_rate'],reverse=True)[0:200]
    #将数据重新拼接到final_rate_dic
    final_rate_dic.clear()
    for final_rate in final_rate_list:
        final_rate_dic[final_rate[0]]=final_rate[1]

    original_movie_list=[movie[0] for movie in final_rate_list]
    # try:
    #     cPickle.dump(final_rate_dic,open('F:/ct.txt',"w"))
    #     cPickle.dump(original_movie_list,open('F:/clis.txt',"w"))
    # except:
    #     pass
    return final_rate_dic,original_movie_list
#对前两百部电影爬取并筛选
def filter_top_movie(final_rate_dic,original_movie_list):
    movie_delte_list=[]
    def request_movie(movie_id):
        try:
            global proxies
            r=requests.get('%s%s'%(MOVIE_REAL,movie_id),timeout=8,proxies=proxies)
        except (requests.exceptions.ConnectionError,requests.exceptions.Timeout,socket.timeout):
            proxies=get_next_proxy()
            r=request_movie(movie_id)
        return r
    for movie_id in original_movie_list:
        r=request_movie(movie_id)
        while 1:
            if (r.status_code==200) :
                break
            elif (r.status_code==404):
                break
            else :
                print(r.status_code)
                proxies=get_next_proxy()
                r=request_movie(movie_id)
        soup=BeautifulSoup(r.content)
        #判断是不是电视剧或者动画等
        try:
            is_tele=bool(re.search(u'第[\u4e00-\u9fa5]季|Saturday Night Live|周六夜现场|周末夜现场|Globe Awards',soup.find('span',{'property':'v:itemreviewed'}).text))
            is_episode=bool(soup.find('div','episode_list'))
            for genre in soup.findAll('span',{'property':'v:genre'}):
                if(genre.text==u'动画'):
                    is_cartoon=True
                    break
                else:
                    is_cartoon=False
            #只要有一项满足就删除
        except AttributeError:
            is_cartoon=True
            is_episode=True
            is_tele=True
        if(is_cartoon or is_episode or is_tele):
            del final_rate_dic[movie_id]
        #如果没有删除则读取评价
        else:
            comment_item={}
            try:
                comment_p=soup.find('span',class_=re.compile('allstar50')).find_parent('h3').find_next_sibling('p').text
                comment_author=soup.find('span',class_=re.compile('allstar50')).find_previous_sibling('a').text
                comment_star=5
            except AttributeError:
                try:
                    comment_p=soup.find('span',class_=re.compile('allstar40')).find_parent('h3').find_next_sibling('p').text
                    comment_author=soup.find('span',class_=re.compile('allstar40')).find_previous_sibling('a').text
                    comment_star=4
                except AttributeError:
                    try:
                        comment_p=soup.find('span',class_=re.compile('allstar30')).find_parent('h3').find_next_sibling('p').text
                        comment_author=soup.find('span',class_=re.compile('allstar30')).find_previous_sibling('a').text
                        comment_star=3
                    except AttributeError:
                        comment_item={}

            comment_item['comment_p']=comment_p
            comment_item['comment_author']=comment_author
            comment_item['comment_star']=comment_star
            #再插入到final_rate_dic中
            final_rate_dic[movie_id]['comment']=comment_item
        print(u"电影%s已经筛选完毕"%(movie_id))
        
    with open("F:/a.txt","w") as tt:
        for fff in final_rate_dic.iteritems():
            tt.write("%s\n"%(fff[0]))






 

if __name__=="__main__":
    #获得喜欢的电影人
    loved_cele_list=get_celebrities('60461419')



    star_movies,movies_have_seen=get_star_movies("60461419")
    original_star_movies,original_direc_movies, loved_cele_mv_dict = cele_filter(star_movies,loved_cele_list)
    final_rate_dic = get_final_rate_dic(original_star_movies,original_direc_movies)
    final_rate_dic,original_movie_list=modify_final_rate(final_rate_dic,movies_have_seen)
    filter_top_movie(final_rate_dic,original_movie_list)


