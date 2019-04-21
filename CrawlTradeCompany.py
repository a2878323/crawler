# 匯入套件
import requests, time, pandas as pd, warnings,pickle
from bs4 import BeautifulSoup
warnings.filterwarnings('ignore')
from multiprocessing import Pool

# request 設定
cookies = {'CheckCode': '12345', #驗證碼
          'TS01f995a3':'01ce097c29e8f6542eace22c1d7d10adfd27b8f535daa2c6addaf145b26eb3d82462162853051f418996ec67af77177e303b61a17e'}
headers={
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Host': 'fbfh.trade.gov.tw',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}

# 讀入要爬的統編
all_ID = pd.read_csv('BGMOPEN1.csv',dtype=object) #全統編 <全國營業(稅籍)登記資料集 https://data.nat.gov.tw/comment/6229>
all_ID=all_ID['統一編號'][~all_ID['統一編號'].isna()]


def chunks(l,n): #把待爬的統編分組,爬完一組存檔一次
    for i in range(0, len(l), n):
        yield l[i:i+n]

def getdata(one_id): #爬一個統編的function
    global count
    try:
        res = requests.get('https://fbfh.trade.gov.tw/rich/text/fbj/asp/fbji150Q2.asp?Page=&uni_no={}&e_name=&c_name=&rep_name=&txtCheckCode=12345&sent=%E6%9F%A5++++%E8%A9%A2'.format(one_id), 
                   cookies=cookies,headers=headers,verify = False)	
    except: #如果被擋,休息一分鐘繼續爬
        try:
            time.sleep(60)
            res = requests.get('https://fbfh.trade.gov.tw/rich/text/fbj/asp/fbji150Q2.asp?Page=&uni_no={}&e_name=&c_name=&rep_name=&txtCheckCode=12345&sent=%E6%9F%A5++++%E8%A9%A2'.format(one_id), 
                   cookies=cookies,headers=headers,verify = False)    
        except: #如果又被擋,休息兩分鐘繼續爬
            try:
                time.sleep(120)
                res = requests.get('https://fbfh.trade.gov.tw/rich/text/fbj/asp/fbji150Q2.asp?Page=&uni_no={}&e_name=&c_name=&rep_name=&txtCheckCode=12345&sent=%E6%9F%A5++++%E8%A9%A2'.format(one_id), 
                       cookies=cookies,headers=headers,verify = False)	
            except: #如果又被擋,休息三分鐘繼續爬		
                time.sleep(180)
                res = requests.get('https://fbfh.trade.gov.tw/rich/text/fbj/asp/fbji150Q2.asp?Page=&uni_no={}&e_name=&c_name=&rep_name=&txtCheckCode=12345&sent=%E6%9F%A5++++%E8%A9%A2'.format(one_id), 
                       cookies=cookies,headers=headers,verify = False)			
    res.encoding='utf-8'
    soup = BeautifulSoup(res.text, 'lxml')
    if soup.select_one('td').text != '找不到查詢資料': #如果有抓到資料,開始存取網頁內容
        raw = pd.read_html(str(soup.select_one('body > div > table')))[0]
        df=pd.read_html(str(soup.select_one('body > div > table')),header=2)[0]#直接讀整個table
        df['ID'] = one_id #加一欄紀錄ID
        df['廠商中文名稱']=raw.loc[0,1].replace(' 基本資料','') #加一欄紀錄廠商中文名
        df['廠商英文名稱']=raw.loc[1,1] #加一欄紀錄廠商英文名
        time.sleep(0.5)
    else: #如果找不到資料,回傳空dataframe
        df=pd.DataFrame()
        time.sleep(0.5)
    return df
	
if __name__ == '__main__':
    data_list = list(chunks(all_ID,10000)) #把統編分成一萬個一組,爬一組存一個檔案
    print('number of chunks:',len(data_list))
    i=1
    for data1 in data_list:
        p = Pool(15)  #開15個Python同步爬文
        mr = p.map_async(getdata, data1)
        p.close()
        p.join()
        pickle.dump( mr.get(), open( "save_{}.p".format(i), "wb" ) )
        print(i)
        i+=1
    print ("!!!!!!!!!! DONE !!!!!!!!!!")