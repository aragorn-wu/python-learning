from bs4 import BeautifulSoup
import pymysql
import requests
import re
import os


def get_html(web_url):  # 爬虫获取网页没啥好说的
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.108 Safari/537.36 2345Explorer/8.5.1.15355"}
    html = requests.get(url=web_url, headers=header).text
    Soup = BeautifulSoup(html, "lxml")
    data = Soup.find("ol").find_all("li")  # 还是有一点要说，就是返回的信息最好只有你需要的那部分，所以这里进行了筛选
    return data


def get_info(all_move,filepath):
    for info in all_move:

        #    编号  
        nums = re.findall(r'<em class="">\d+</em>', str(info), re.S | re.M)  # 编号我使用的是正则表达式来获取
        nums = re.findall(r'\d+', str(nums), re.S | re.M)
        num = nums[0]

        #    名字  
        names = info.find("span")  # 名字比较简单 偷了一下懒直接获取第一个span就是
        name = names.get_text()

        #    导演  
        charactors = info.find("p")  # 这段信息中有太多非法符号你需要替换掉
        charactor = charactors.get_text().replace(" ", "").replace("\n", "")  # 使信息排列规律
        charactor = charactor.replace("\xa0", "").replace("\xee", "").replace("\xf6", "").replace("\u0161", "").replace(
            "\xf4", "").replace("\xfb", "").replace("\u2027", "")
        charactor = charactor[0:30]  # 由于本人不才，数据库才入门所以需要控制信息长度，以免存入超范围  (大神忽略)

        #    评语  
        remarks = info.find_all("span", {"class": "inq"})
        print(remarks)
        if remarks:  # 这个判断是因为有的电影没有评语，你需要做判断
            remark = remarks[0].get_text().replace("\u22ef", "")
            remark = remark[0:30]  # 同上面一个
        else:
            remark = "此影片没有评价"

            #    评分
        scores = info.find_all("span", {"class": "rating_num"})  # 没啥好说 匹配就行
        score = scores[0].get_text()

        f = open(filepath, "a")  # 将上面的信息每一行以按逗号分隔的规律存入本地
        f.write(num + ",")
        f.write(name + ",")
        f.write(charactor + ",")
        f.write(remark + ",")
        f.write(score)
        f.write("\n")
    f.close()  # 记得关闭文件


if __name__ == "__main__":

    dic='/tmp'
    filepath="/tmp/douban.txt"

    if os.path.exists(dic) == False:  # 两个if来判断是否文件路径存在 新建文件夹 删除文件
        os.mkdir(dic)
    if os.path.exists(filepath) == True:
        os.remove(filepath)


    page = 0  # 初始化页数，TOP一共有250部   每页25部
    while page <= 225:
        web_url = "https://movie.douban.com/top250?start=%s&filter=" % page
        all_move = get_html(web_url)  # 返回每一页的网页
        get_info(all_move,filepath)  # 匹配对应信息存入本地
        page += 25

    connect = pymysql.connect(  # 连接数据库
        user="root",
        password="wuqf",
        host="127.0.0.1",
        db="spider",
        port=3306,
        charset=("utf8"),  # 注意编码一定要设置，否则gbk你懂的
        use_unicode=True,
    )
    con = connect.cursor()  # 设置游标
    # con.execute('SET NAMES UTF8')  
    # con.execute("drop database douban")  # 以下7行表示删除原有的数据库和其中的表，新建数据库和表
    # con.execute("create database douban")
    #con.execute("use douban")  # 使用douban这个数据库
    con.execute("drop table if exists t_doubantop")
    sql = 'create table t_doubantop(num BIGINT,name VARCHAR(40) NOT NULL,charactor VARCHAR(40),remark VARCHAR(40),score VARCHAR(20))'
    con.execute(sql)  # sql中的字符表示创建一个表 对应的信息有   num  name  charactor  remark  score


    f = open(filepath, "r")  # 打开路径复制其中的数据，以便导入数据库
    while True:
        line = f.readline()
        if line:
            line = line.strip("\n")
            line = line.split(",")  # 你写如.txt文件的数据用逗号分开，此时用逗号将他们转化为列表
            # print(line)  
            num = line[0]  # 将需要的几个量复制
            name = line[1]
            charactor = line[2]
            remark = line[3]
            score = line[4]
            con.execute("insert into t_doubantop(num,name,charactor,remark,score)values(%s,%s,%s,%s,%s)",
                        [num, name, charactor, remark, score])
        else:  # 导入数据库
            break
    connect.commit()  # 这句记得写上提交数据，否则导入为空(有的DDL是不需要导入的)
    con.close()  # 最后记得关掉连接
    connect.close()
