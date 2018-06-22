import urllib, urllib2, sys
import json


allda = [];
#curl   "http://route.showapi.com/341-1?showapi_appid=66173&page=1&maxResult=10&showapi_sign=844e06d697e04e9dbd3c52286c89a69a"
#https://m.shensuantang.com/index.php?m=huangli&c=index&a=huangli_api&appid=wx8fbb92307d1cde11&date=2018-06-21
host = 'https://m.shensuantang.com/'
path = 'index.php'
method = 'GET'

def getyiji(date):
  #global allda
#date= '2018-06-21'
  querys = 'm=huangli&c=index&a=huangli_api&appid=wx8fbb92307d1cde11&date='+date
  bodys = {}
  url = host + path + '?' + querys

  request = urllib2.Request(url)
  response = urllib2.urlopen(request)
  content = response.read()
  if (content):
      print(content)
      allda.append(content)
      #da = json.loads(content)
      #allda[date] = da

      #print(da)
      #for k in da:
        #print k,da[k]

#getyiji('2018-06-21')
#getyiji('2018-06-22')

for yy in range(2000,2010,1):
  for mm in range(1,13,1):
    for dd in range(1,32,1):
      print "%s-%s-%s" % (yy,mm,dd)
      getyiji("%s-%s-%s" % (yy,mm,dd))


text_file = open("huangli-yiji-1.json", "w")
text_file.write('\n'.join(allda))
text_file.close()