
# coding: utf-8

# In[4]:


import requests, time, pandas as pd, warnings,pickle
from bs4 import BeautifulSoup
warnings.filterwarnings('ignore')
from multiprocessing import Pool
import datetime


# In[12]:


key = pd.read_csv('key.csv')


newkey=[]
for v in key.values:
    newkey.append(str(v[0]).zfill(6))
    
    


# In[5]:


def chunks(l,n): #把待爬的統編分組,爬完一組存檔一次
    for i in range(0, len(l), n):
        yield l[i:i+n]


# In[16]:


def getdata(num):
    try:
        res = requests.get('https://admin.taiwan.net.tw/TravelIndustryDetail.aspx?Cond={}'.format(num))
        soup = BeautifulSoup(res.text,"lxml")
        t= soup.select('.promote_table')
        t1 = pd.read_html(str(t[0]))
        t1=t1[0].transpose()
        col = t1.iloc[0,]
        t1.columns = col
        t1 = t1.drop(t1.index[0])
        title= soup.select('.promote_tit')
        t1['旅行社'] = title[0].text.replace('\u3000','')
        time.sleep(1)
    except:
        t1=pd.DataFrame()
    return t1


# In[18]:


if __name__ == '__main__':
    data_list = list(chunks(newkey,300)) #把統編分成一萬個一組,爬一組存一個檔案
    print('number of chunks:',len(data_list))
    i=1
    start=datetime.datetime.now()
    for data1 in data_list:
        p = Pool(13)  #開15個Python同步爬文
        mr = p.map_async(getdata, data1)
        p.close()
        p.join()
        pickle.dump( mr.get(), open( "save_{}.p".format(i), "wb" ) )
        end=datetime.datetime.now()
        print(i,end - start , end)
        i+=1
    print ("!!!!!!!!!! DONE !!!!!!!!!!")

