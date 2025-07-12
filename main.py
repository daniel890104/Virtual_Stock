from bs4 import BeautifulSoup
import requests
import pymysql
import time
import prettytable as pt
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk

class Stock:
    #建構式
    def __init__(self, *stock_numbers):
        self.stock_numbers = stock_numbers
    
    #爬取
    def scrape(self):
        result = list()
        for stock_number in self.stock_numbers:
            response = requests.get(
			"https://tw.stock.yahoo.com/q/q?s=" + stock_number)
            soup = BeautifulSoup(response.text.replace("加到投資組合", ""), "lxml")
            stock_date = soup.find(
			"font", {"class": "tt"}).getText().strip()[-9:]  #資料日期
            tables = soup.find_all("table")[2]  #取得網頁中第三個表格(索引從0開始計算)
            tds = tables.find_all("td")[0:11]  #取得表格中1到10格
            result.append((stock_date,) +
			tuple(td.getText().strip() for td in tds))
        return result
    #可以查詢指定月份的每日收盤價
    def daily(self, year, month):
        browser = webdriver.Chrome(ChromeDriverManager().install())
        browser.get(
            "https://www.twse.com.tw/zh/page/trading/exchange/STOCK_DAY_AVG.html")
        select_year = Select(browser.find_element_by_name("yy"))
        select_year.select_by_value(year)  # 選擇傳入的年份
        select_month = Select(browser.find_element_by_name("mm"))
        select_month.select_by_value(month)  # 選擇傳入的月份
        stockno = browser.find_element_by_name("stockNo")  # 定位股票代碼輸入框
        result = []
        for stock_number in self.stock_numbers:
            stockno.clear()  # 清空股票代碼輸入框
            stockno.send_keys(stock_number)
            stockno.submit()
            time.sleep(2)
            soup = BeautifulSoup(browser.page_source, "lxml")
            table = soup.find("table", {"id": "report-table"})
            elements = table.find_all(
                "td", {"class": "dt-head-center dt-body-center"})
            data = (stock_number,) + tuple(element.getText()
                                           for element in elements)
            result.append(data)
        print(result)
            
    def realsave(self,Buynum):#買零股股票
        Buy = int(Buynum)
        result = list()
        for stock_number in self.stock_numbers:
            response = requests.get(
			"https://tw.stock.yahoo.com/q/q?s=" + stock_number)
            soup = BeautifulSoup(response.text.replace("加到投資組合", ""), "lxml")
            tables = soup.find_all("table")[2]  #取得網頁中第三個表格(索引從0開始計算)
            tds = tables.find_all("td")[0:1] #公司名稱
            #print(type(tds))
            ts = tables.select("td")[3:4]   #成交價錢
            Price=tuple(td.getText().strip() for td in ts)
            result.append(tuple(td.getText().strip() for td in tds)+Price+tuple([Buy]))
        db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "daniel0104",
            "db": "stock",
            "charset": "utf8"
        }
        try:
            conn = pymysql.connect(**db_settings)
            with conn.cursor() as cursor:
                sql = """INSERT INTO savestock(
                                stock_name,
                                price,
                                buy_num)
                         VALUES(%s, %s, %s)
                         ON DUPLICATE KEY UPDATE price = (price*buy_num+VALUES(price)*VALUES(buy_num))/(buy_num+VALUES(buy_num)) , buy_num = buy_num+VALUES(buy_num)"""
                for re in result:
                    cursor.execute(sql,re)
                conn.commit()
        except Exception as ex:
            print("Exception:", ex)
        #都轉為小數點後二位
        f_result=list()
        try:
            conn1 = pymysql.connect(**db_settings)
            with conn1.cursor() as cursor:
                sql1 = "SELECT price FROM savestock"
                cursor.execute(sql1)
                conn1.commit()
                test=cursor.fetchall()
        except Exception as ex:
            print("Exception:", ex)
        for i in range(len(test)):
            tm=float(test[i][0])
            tm=format(tm,'.2f')
            f_result.append(tuple([tm]))
        #找公司
        ans_result=list()
        try:
            conn2 = pymysql.connect(**db_settings)
            with conn2.cursor() as cursor:
                sql2 = "SELECT stock_name FROM savestock"
                cursor.execute(sql2)
                conn1.commit()
                company=cursor.fetchall()
        except Exception as ex:
            print("Exception:", ex)
        for j in range(len(company)):
            ans_result.append(f_result[j]+company[j])
        #存回去
        try:
            conn3 = pymysql.connect(**db_settings)
            with conn3.cursor() as cursor:
                sql3 = "UPDATE savestock SET price = %s WHERE  stock_name = %s"
                for ans in ans_result:
                    cursor.execute(sql3,ans)
                conn3.commit()
        except Exception as ex:
            print("Exception:", ex)
            
    def savesheet(self,Buynum):#買整張股票
        Buy = int(Buynum)
        Buy *=1000 
        result = list()
        for stock_number in self.stock_numbers:
            response = requests.get(
			"https://tw.stock.yahoo.com/q/q?s=" + stock_number)
            soup = BeautifulSoup(response.text.replace("加到投資組合", ""), "lxml")
            tables = soup.find_all("table")[2]  #取得網頁中第三個表格(索引從0開始計算)
            tds = tables.find_all("td")[0:1] #公司名稱
            ts = tables.select("td")[3:4]   #成交價錢
            Price=tuple(td.getText().strip() for td in ts)
            result.append(tuple(td.getText().strip() for td in tds)+Price+tuple([Buy]))
        db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "daniel0104",
            "db": "stock",
            "charset": "utf8"
        }
        try:
            conn = pymysql.connect(**db_settings)
            with conn.cursor() as cursor:
                sql = """INSERT INTO savestock(
                                stock_name,
                                price,
                                buy_num)
                         VALUES(%s, %s, %s)
                         ON DUPLICATE KEY UPDATE price = (price*buy_num+VALUES(price)*VALUES(buy_num))/(buy_num+VALUES(buy_num)) , buy_num = buy_num+VALUES(buy_num)"""
                for re in result:
                    cursor.execute(sql,re)
                conn.commit()
        except Exception as ex:
            print("Exception:", ex)
        #都轉為小數點後二位
        f_result=list()
        try:
            conn1 = pymysql.connect(**db_settings)
            with conn1.cursor() as cursor:
                sql1 = "SELECT price FROM savestock"
                cursor.execute(sql1)
                conn1.commit()
                test=cursor.fetchall()
        except Exception as ex:
            print("Exception:", ex)
        for i in range(len(test)):
            tm=float(test[i][0])
            tm=format(tm,'.2f')
            f_result.append(tuple([tm]))
        #找公司
        ans_result=list()
        try:
            conn2 = pymysql.connect(**db_settings)
            with conn2.cursor() as cursor:
                sql2 = "SELECT stock_name FROM savestock"
                cursor.execute(sql2)
                conn1.commit()
                company=cursor.fetchall()
        except Exception as ex:
            print("Exception:", ex)
        for j in range(len(company)):
            ans_result.append(f_result[j]+company[j])
        #存回去
        try:
            conn3 = pymysql.connect(**db_settings)
            with conn3.cursor() as cursor:
                sql3 = "UPDATE savestock SET price = %s WHERE  stock_name = %s"
                for ans in ans_result:
                    cursor.execute(sql3,ans)
                conn3.commit()
        except Exception as ex:
            print("Exception:", ex)
    
    def savetime(self,Buynum):
        Buy = int(Buynum)
        result = list()
        for stock_number in self.stock_numbers:
            response = requests.get(
			"https://tw.stock.yahoo.com/q/q?s=" + stock_number)
            soup = BeautifulSoup(response.text.replace("加到投資組合", ""), "lxml")
            stock_date = soup.find(
			"font", {"class": "tt"}).getText().strip()[-9:]  #資料日期
            tables = soup.find_all("table")[2]  #取得網頁中第三個表格(索引從0開始計算)
            tds = tables.find_all("td")[0:1] #公司名稱
            ts = tables.select("td")[3:4]   #成交價錢
            result.append((stock_date,)+tuple(td.getText().strip() for td in tds)+tuple(["購買"])+tuple(td.getText().strip() for td in ts)+tuple([Buy]))
        db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "daniel0104",
            "db": "stock",
            "charset": "utf8"
        }
        try:
            conn = pymysql.connect(**db_settings)
            with conn.cursor() as cursor:
                sql = """INSERT INTO detail(
                                date,
                                stock_name,
                                action,
                                price,
                                num)
                         VALUES(%s, %s, %s, %s, %s)
                         ON DUPLICATE KEY UPDATE num = num+VALUES(num)"""
                for re in result:
                    cursor.execute(sql,re)
                conn.commit()
        except Exception as ex:
            print("Exception:", ex)
            
    def savesheettime(self,Buynum):
        Buy = int(Buynum)
        Buy *=1000 
        result = list()
        for stock_number in self.stock_numbers:
            response = requests.get(
			"https://tw.stock.yahoo.com/q/q?s=" + stock_number)
            soup = BeautifulSoup(response.text.replace("加到投資組合", ""), "lxml")
            stock_date = soup.find(
			"font", {"class": "tt"}).getText().strip()[-9:]  #資料日期
            tables = soup.find_all("table")[2]  #取得網頁中第三個表格(索引從0開始計算)
            tds = tables.find_all("td")[0:1] #公司名稱
            ts = tables.select("td")[3:4]   #成交價錢
            result.append((stock_date,)+tuple(td.getText().strip() for td in tds)+tuple(["購買"])+tuple(td.getText().strip() for td in ts)+tuple([Buy]))
        db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "daniel0104",
            "db": "stock",
            "charset": "utf8"
        }
        try:
            conn = pymysql.connect(**db_settings)
            with conn.cursor() as cursor:
                sql = """INSERT INTO detail(
                                date,
                                stock_name,
                                action,
                                price,
                                num)
                         VALUES(%s, %s, %s, %s, %s)
                         ON DUPLICATE KEY UPDATE num = num+VALUES(num)"""
                for re in result:
                    cursor.execute(sql,re)
                conn.commit()
        except Exception as ex:
            print("Exception:", ex)
    
    def sellstock(self,Sellnum):#賣股票
        Sell = int(Sellnum)
        result = list()
        searchname = list()
        for stock_number in self.stock_numbers:
            response = requests.get(
			"https://tw.stock.yahoo.com/q/q?s=" + stock_number)
            soup = BeautifulSoup(response.text.replace("加到投資組合", ""), "lxml")
            tables = soup.find_all("table")[2]  #取得網頁中第三個表格(索引從0開始計算)
            tds = tables.find_all("td")[0:1] #公司名稱
            ts = tables.find_all("td")[4:5]
            name = tuple(td.getText().strip() for td in tds)
            takeprice= tuple(td.getText().strip() for td in ts)
        result.append(tuple([Sell])+name)
        searchname.append(name)
        #讀取賣出價錢
        """db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "daniel0104",
            "db": "stock",
            "charset": "utf8"
        }
        try:
            conn = pymysql.connect(**db_settings)
            with conn.cursor() as cursor:
                sql = "SELECT price FROM savestock  WHERE stock_name = %s " 
                for se in searchname:   
                    cursor.execute(sql,se)
                takeprice = cursor.fetchone()
                conn.commit()
        except Exception as ex:
                    print("Exception:", ex)"""
        t = float(takeprice[0])
        sellnum = float(Sell)
        winprice = t*sellnum
        winprice = format(winprice,".2f") 
        #存取賣出獲利
        db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "daniel0104",
            "db": "stock",
            "charset": "utf8"
        }
        try:
            conn = pymysql.connect(**db_settings)
            with conn.cursor() as cursor:
                sql = """INSERT INTO cost(cost_id, allprice)
                                VALUES('2', %s)
                                ON DUPLICATE KEY UPDATE allprice = allprice+VALUES(allprice)"""
                cursor.execute(sql,str(winprice))
                conn.commit()
        except Exception as ex:
            print("Exception:", ex)
        #賣出
        db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "daniel0104",
            "db": "stock",
            "charset": "utf8"
        }
        try:
            conn = pymysql.connect(**db_settings)
            with conn.cursor() as cursor:
                sql = "UPDATE savestock SET buy_num = buy_num-%s WHERE stock_name = %s " 
                for re in result:
                    cursor.execute(sql,re)
                conn.commit()
        except Exception as ex:
                    print("Exception:", ex)
        
    def sellsheet(self,Sellnum):#賣股票
        Sell = int(Sellnum)
        Sell *= 1000
        result = list()
        searchname = list()
        for stock_number in self.stock_numbers:
            response = requests.get(
			"https://tw.stock.yahoo.com/q/q?s=" + stock_number)
            soup = BeautifulSoup(response.text.replace("加到投資組合", ""), "lxml")
            tables = soup.find_all("table")[2]  #取得網頁中第三個表格(索引從0開始計算)
            tds = tables.find_all("td")[0:1] #公司名稱
            ts = tables.find_all("td")[4:5]
            name = tuple(td.getText().strip() for td in tds)
            takeprice= tuple(td.getText().strip() for td in ts)
        result.append(tuple([Sell])+name)
        searchname.append(name)
        #讀取賣出價錢
        """db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "daniel0104",
            "db": "stock",
            "charset": "utf8"
        }
        try:
            conn = pymysql.connect(**db_settings)
            with conn.cursor() as cursor:
                sql = "SELECT price FROM savestock  WHERE stock_name = %s " 
                for se in searchname:   
                    cursor.execute(sql,se)
                takeprice = cursor.fetchone()
                conn.commit()
        except Exception as ex:
                    print("Exception:", ex)"""
        t = float(takeprice[0])
        sellnum = float(Sell)
        winprice = t*sellnum
        winprice = format(winprice,".2f")
        #存取賣出獲利
        db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "daniel0104",
            "db": "stock",
            "charset": "utf8"
        }
        try:
            conn = pymysql.connect(**db_settings)
            with conn.cursor() as cursor:
                sql = """INSERT INTO cost(cost_id, allprice)
                                VALUES('2', %s)
                                ON DUPLICATE KEY UPDATE allprice = allprice+VALUES(allprice)"""
                cursor.execute(sql,str(winprice))
                conn.commit()
        except Exception as ex:
            print("Exception:", ex)
        #賣出
        db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "daniel0104",
            "db": "stock",
            "charset": "utf8"
        }
        try:
            conn = pymysql.connect(**db_settings)
            with conn.cursor() as cursor:
                sql = "UPDATE savestock SET buy_num = buy_num-%s WHERE stock_name = %s " 
                for re in result:
                    cursor.execute(sql,re)
                conn.commit()
        except Exception as ex:
                    print("Exception:", ex)
                    
    def selltime(self,Sellnum):#賣股票
        Sell = int(Sellnum)
        result = list()
        for stock_number in self.stock_numbers:
            response = requests.get(
			"https://tw.stock.yahoo.com/q/q?s=" + stock_number)
            soup = BeautifulSoup(response.text.replace("加到投資組合", ""), "lxml")
            stock_date = soup.find(
			"font", {"class": "tt"}).getText().strip()[-9:]  #資料日期
            tables = soup.find_all("table")[2]  #取得網頁中第三個表格(索引從0開始計算)
            tds = tables.find_all("td")[0:1] #公司名稱
            ts = tables.select("td")[4:5]   #成交價錢
            result.append((stock_date,)+tuple(td.getText().strip() for td in tds)+tuple(["賣出"])+tuple(td.getText().strip() for td in ts)+tuple([Sell]))
        db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "daniel0104",
            "db": "stock",
            "charset": "utf8"
        }
        try:
            conn = pymysql.connect(**db_settings)
            with conn.cursor() as cursor:
                sql = """INSERT INTO detail(
                                date,
                                stock_name,
                                action,
                                price,
                                num)
                         VALUES(%s, %s, %s, %s, %s)
                         ON DUPLICATE KEY UPDATE num = num+VALUES(num)"""
                for re in result:
                    cursor.execute(sql,re)
                conn.commit()
        except Exception as ex:
            print("Exception:", ex)
            
    def sellsheettime(self,Sellnum):#賣股票
        Sell = int(Sellnum)
        Sell *= 1000
        result = list()
        for stock_number in self.stock_numbers:
            response = requests.get(
			"https://tw.stock.yahoo.com/q/q?s=" + stock_number)
            soup = BeautifulSoup(response.text.replace("加到投資組合", ""), "lxml")
            stock_date = soup.find(
			"font", {"class": "tt"}).getText().strip()[-9:]  #資料日期
            tables = soup.find_all("table")[2]  #取得網頁中第三個表格(索引從0開始計算)
            tds = tables.find_all("td")[0:1] #公司名稱
            ts = tables.select("td")[4:5]   #成交價錢
            result.append((stock_date,)+tuple(td.getText().strip() for td in tds)+tuple(["賣出"])+tuple(td.getText().strip() for td in ts)+tuple([Sell]))
        db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "daniel0104",
            "db": "stock",
            "charset": "utf8"
        }
        try:
            conn = pymysql.connect(**db_settings)
            with conn.cursor() as cursor:
                sql = """INSERT INTO detail(
                                date,
                                stock_name,
                                action,
                                price,
                                num)
                         VALUES(%s, %s, %s, %s, %s)
                         ON DUPLICATE KEY UPDATE num = num+VALUES(num)"""
                for re in result:
                    cursor.execute(sql,re)
                conn.commit()
        except Exception as ex:
            print("Exception:", ex)
            
def countcost():
    #算出總成本
    db_settings = {
                "host": "127.0.0.1",
                "port": 3306,
                "user": "root",
                "password": "daniel0104",
                "db": "stock",
                "charset": "utf8"
            }
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "SELECT price FROM savestock"
            cursor.execute(sql)
            re = cursor.fetchall()
    except Exception as ex:
                print("Exception:", ex)
                
    db_settings = {
                "host": "127.0.0.1",
                "port": 3306,
                "user": "root",
                "password": "daniel0104",
                "db": "stock",
                "charset": "utf8"
            }
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "SELECT buy_num FROM savestock"
            cursor.execute(sql)
            ne = cursor.fetchall()
    except Exception as ex:
                print("Exception:", ex)
          
    r = [re]
    n = [ne]
    length = len(r[0])
    allprices = 0.0
    for i in range(length):
        allprices += float(r[0][i][0]) * float(n[0][i][0])
    allprices = format(allprices,".2f")
    print(allprices)
    db_settings = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "daniel0104",
        "db": "stock",
        "charset": "utf8"
    }
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = """INSERT INTO cost(cost_id, allprice)
                            VALUES('1', %s)
                            ON DUPLICATE KEY UPDATE allprice = VALUES(allprice)"""
            cursor.execute(sql,str(allprices))
            conn.commit()
    except Exception as ex:
        print("Exception:", ex)
#可以隨總成本更動

def countmoney():
    #總金額
    db_settings = {
                "host": "127.0.0.1",
                "port": 3306,
                "user": "root",
                "password": "daniel0104",
                "db": "stock",
                "charset": "utf8"
            }
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "SELECT allprice FROM cost WHERE cost_id = '1' "
            cursor.execute(sql)
            re = cursor.fetchall()
    except Exception as ex:
                print("Exception:", ex)
                
    db_settings = {
                "host": "127.0.0.1",
                "port": 3306,
                "user": "root",
                "password": "daniel0104",
                "db": "stock",
                "charset": "utf8"
            }
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "SELECT allprice FROM cost WHERE cost_id = '2'"
            cursor.execute(sql)
            ne = cursor.fetchall()
    except Exception as ex:
                print("Exception:", ex)
          
    r = [re]
    n = [ne]
    allmoney = 0.0
    allmoney = float(r[0][0][0]) - float(n[0][0][0])
    allmoney = format(allmoney,".2f")
    print(allmoney)
    db_settings = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "daniel0104",
        "db": "stock",
        "charset": "utf8"
    }
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = """INSERT INTO cost(cost_id, allprice)
                            VALUES('0', %s)
                            ON DUPLICATE KEY UPDATE allprice = 2000000-VALUES(allprice)"""
            cursor.execute(sql,str(allmoney))
            conn.commit()
    except Exception as ex:
        print("Exception:", ex)



window=tk.Tk()
window.title('VirtualStock')
window.geometry('830x400')
window.resizable(False, False)
#################
def BUY_STOCK():
    var1 = num_ent.get()
    stock=Stock(var1)
    var2 = buy_ent.get()
    if radioValue.get()=='買':
        if radioValue2.get()=='張':
            stock.savesheet(var2)
            stock.savesheettime(var2)
        if radioValue2.get()=='股':
            stock.realsave(var2)
            stock.savetime(var2)
    if radioValue.get()=='賣':
        if radioValue2.get()=='張':
            stock.sellsheet(var2)
            stock.sellsheettime(var2)
        if radioValue2.get()=='股':
            stock.sellstock(var2)
            stock.selltime(var2)
    countcost()
    countmoney()
    all_txt.config(text='總資產:'+Allmoney())
    cost_txt.config(text='總成本:'+Cost())
    win_txt.config(text='已獲利:'+Winmoney())
    print_stock()
    print_detail()

def print_sel():
    if radioValue.get()=='買':
        lb_choice.config(text='選擇:'+radioValue.get(),fg='red')
        choice_btn.config(text='購買',bg='red')
    if radioValue.get()=='賣':
        lb_choice.config(text='選擇:'+radioValue.get(),fg='#90EE90')
        choice_btn.config(text='賣出',bg='#90EE90')
def print_num():
    c_lab.config(text='數量:'+radioValue2.get())    

frame1 = tk.Frame(window, width=100, height=80, bg='#00008B')
frame1.pack(side=tk.TOP, fill=tk.BOTH)

num_lab = tk.Label(frame1, text='股票代號：', bg='#00008B', fg='white', font=('微軟正黑體', 12))
num_lab.place(x=10, y=10)

num_ent = tk.Entry(frame1, width=5, fg='black', font=('微軟正黑體', 12))
num_ent.place(x=99, y=11)

buy_ent = tk.Entry(frame1, show = None,width=10)#顯示成明文形式
buy_ent.place(x=400,y=40)


lb_choice = tk.Label(frame1,text='選擇:',bg='#00008B',fg='white',font=('微軟正黑體', 12),width=6,height=1)
lb_choice.place(x=250,y=10) 

choice_btn = tk.Button(frame1, text='買或賣', width=10, height='1',command=BUY_STOCK)
choice_btn.place(x=500,y=15)

radioValue=tk.StringVar(None,'買')
rdioBuy = tk.Radiobutton(frame1, text='買', bg='#00008B', fg='white', font=('微軟正黑體', 12),variable=radioValue,value='買',command=print_sel) #這怪怪的，按下去就知道了
rdioBuy.place(x=200, y=10)
rdioSale = tk.Radiobutton(frame1, text='賣', bg='#00008B', fg='white', font=('微軟正黑體', 12),variable=radioValue,value='賣',command=print_sel)
rdioSale.place(x=200, y=40)

c_lab = tk.Label(frame1,text='數量:',bg='#00008B',fg='white',font=('微軟正黑體', 12))
c_lab.place(x=400,y=10) 

radioValue2=tk.StringVar(None,'張')
rdioSheet = tk.Radiobutton(frame1,text='整張',bg='#00008B', fg='white',font=('微軟正黑體', 12),variable=radioValue2,value='張',command=print_num)
rdioZero = tk.Radiobutton(frame1,text='零股',bg='#00008B', fg='white',font=('微軟正黑體', 12),variable=radioValue2,value='股',command=print_num)
rdioSheet.place(x=320,y=10)
rdioZero.place(x=320,y=40)
################

frame2 = tk.Frame(window, width=200, height=80, bg='#00BFFF')
frame2.pack(side=tk.TOP, fill=tk.BOTH)
search_txt = tk.Text(frame2,bg='#00BFFF',height=80,width=200)
search_txt.place(x=0,y=0)
tb1 = pt.PrettyTable()
tb1.field_names = ["日期","公司名稱","市場時間","收盤價","買價","賣價","漲幅","總量","昨日收盤價","開盤價","最高點","最低點"]
def search():
    search_txt.delete("1.0","end")
    tb1.clear_rows()
    var1 = num_ent.get()
    stock=Stock(var1)
    s = stock.scrape()
    for i in s:
        tb1.add_row(i)
    search_txt.insert('end',tb1)

num_btn = tk.Button(frame1, text='搜尋' , width=5, bg='#0000CD', fg='white',command=search)
num_btn.place(x=100, y=40)
###############
def Allmoney():
    db_settings = {
                "host": "127.0.0.1",
                "port": 3306,
                "user": "root",
                "password": "daniel0104",
                "db": "stock",
                "charset": "utf8"
            }
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "SELECT allprice FROM cost WHERE cost_id = '0' "
            cursor.execute(sql)
            mmm = cursor.fetchall()
    except Exception as ex:
                print("Exception:", ex)
    m = mmm[0][0]
    mf = float(m)
    mf = format(mf,'.2f')
    return mf

def Cost():
    db_settings = {
                "host": "127.0.0.1",
                "port": 3306,
                "user": "root",
                "password": "daniel0104",
                "db": "stock",
                "charset": "utf8"
            }
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "SELECT allprice FROM cost WHERE cost_id = '1' "
            cursor.execute(sql)
            ccc = cursor.fetchall()
    except Exception as ex:
                print("Exception:", ex)
    c = ccc[0][0]
    cf = float(c)
    cf = format(cf,'.2f')
    return cf

def Winmoney():
    db_settings = {
                "host": "127.0.0.1",
                "port": 3306,
                "user": "root",
                "password": "daniel0104",
                "db": "stock",
                "charset": "utf8"
            }
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "SELECT allprice FROM cost WHERE cost_id = '2' "
            cursor.execute(sql)
            www = cursor.fetchall()
    except Exception as ex:
                print("Exception:", ex)
    w = www[0][0]
    wf = float(w)
    wf = format(wf,'.2f')
    return wf

frame3 = tk.Frame(window, width=600, height=160, bg='black')
frame3.pack(side=tk.TOP, fill=tk.BOTH)

code_1 = tk.Frame(frame3, width=250, height=160, bg="#E0FFFF")
code_1.pack(side=tk.LEFT)

code_2 = tk.Frame(frame3, width=350, height=160, bg="#E0FFFF")
code_2.pack(side=tk.LEFT)

code_3 = tk.Frame(frame3, width=250, height=160, bg="#4169E1")
code_3.pack(side=tk.LEFT)

tb2 = pt.PrettyTable()
tb2.field_names = ["公司名稱","均價","股數"]
tb2.set_style(pt.DEFAULT)
tb3 = pt.PrettyTable()
tb3.field_names = ["日期","公司名稱","買賣","均價","股數"]
tb3.set_style(pt.DEFAULT)
now_txt = tk.Text(code_1,bg='#E0FFFF',height=12,width=250)
now_txt.place(x=0,y=0)
do_txt = tk.Text(code_2,bg='#E0FFFF',height=12,width=350)
do_txt.place(x=0,y=0)
all_txt = tk.Label(code_3,text='總資產:'+Allmoney(),bg='#4169E1',fg='black',font=('微軟正黑體', 12),width=25,height=2)
all_txt.place(x=0,y=0)
cost_txt = tk.Label(code_3,text='總成本:'+Cost(),bg='#4169E1',fg='black',font=('微軟正黑體', 12),width=25,height=2)
cost_txt.place(x=0,y=50)
win_txt = tk.Label(code_3,text='已獲利:'+Winmoney(),bg='#4169E1',fg='black',font=('微軟正黑體', 12),width=25,height=2)
win_txt.place(x=0,y=100)
def print_stock():
    db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "daniel0104",
            "db": "stock",
            "charset": "utf8"
        }
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "SELECT * FROM savestock"
            cursor.execute(sql)
            re = cursor.fetchall()
    except Exception as ex:
            print("Exception:", ex)
    now_txt.delete("1.0","end")
    tb2.clear_rows()
    for i in range(len(re)):
        tb2.add_row(re[i])
    now_txt.insert('end',tb2)

def print_detail():
    db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "daniel0104",
            "db": "stock",
            "charset": "utf8"
        }
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "SELECT * FROM detail"
            cursor.execute(sql)
            re = cursor.fetchall()
    except Exception as ex:
            print("Exception:", ex)
    do_txt.delete("1.0","end")
    tb3.clear_rows()
    for i in range(len(re)):
        tb3.add_row(re[i])
    do_txt.insert('end',tb3)
#################
print_stock()
print_detail()
#################

frame4 = tk.Frame(window, width=600, height=120, bg='#00BFFF')
frame4.pack(side=tk.TOP, fill=tk.BOTH)
 
month_frame=tk.Frame(frame4, width=150, height=120, bg='#4169E1')
month_frame.pack(side=tk.LEFT)
warining_frame=tk.Frame(frame4, width=450, height=120, bg='#00BFFF')
warining_frame.pack(side=tk.LEFT)

lby = tk.Label(month_frame,text='年:', bg='#4169E1',fg='black',font=('微軟正黑體', 14),width=4,height=1)
lby.place(x=0,y=0)
lby1 = tk.Label(month_frame,text='月:', bg='#4169E1',fg='black',font=('微軟正黑體', 14),width=4,height=1)
lby1.place(x=0,y=25)
e3 = tk.Entry(month_frame, show = None,width=4)#顯示成明文形式
e3.place(x=50,y=5)
e4 = tk.Entry(month_frame, show = None,width=4)#顯示成明文形式
e4.place(x=50,y=30)
def ym():
    var1 =num_ent.get()
    stock=Stock(var1)
    year = e3.get()
    month = e4.get()
    stock.daily(year, month)

bym = tk.Button(month_frame, text='過去年月股價',bg='#4169E1',fg='white', width=10, height=1,command=ym)
bym.place(x=0,y=55)
deli = 250         # milliseconds of delay per character
svar = tk.StringVar()
lbw = tk.Label(warining_frame,textvariable=svar,bg='#00BFFF',fg='red',font=('微軟正黑體', 14),width=60,height=2)
lbw.pack(side=tk.LEFT)
def shif():
    shif.msg = shif.msg[1:] + shif.msg[0]
    svar.set(shif.msg)
    warining_frame.after(deli, shif)

shif.msg = '投資一定有風險，基金投資有賺有賠，申購前應詳閱公開說明書。'
svar.set(shif.msg)
shif()
#################

window.mainloop()