
from hoshino import Service
from urllib import request
import json
import datetime
import re

URL = 'https://static.biligame.com/pcr/gw/calendar.js'
header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'

data = {
    'calendar_days' : 7,#日程表返回包括今天在内多长时间的日程，默认是7天
    'Refresh_date' : '',#上次爬取日程表的日期
    'schedule_data' : ''#从官方日历爬取下来的数据
    }


#day_key里保存的是每天的信息分类，"qdhd"是多倍掉落庆典，"tdz"是公会战，
#"tbhd"是公会之家家具上架，"jqhd"是活动地图，"jssr"是角色生日
#你可以自定义这个列表，删掉不想看到的活动
day_key = ["qdhd","tdz","tbhd","jqhd","jssr"]



sv = Service('日程表')

@sv.on_fullmatch('国服日程表')
async def Schedule(bot,ev):
    #调用的时候比对上次爬取日程表时间，不是今天就重新爬取日程表，是今天就直接返回

    if data['Refresh_date'] != str(datetime.date.today()):

        status = refresh_schedule()
        if not status[0]:
            await bot.send(ev, f'刷新日程表失败，错误代码{status[1]}')
            return
        data['Refresh_date'] = str(datetime.date.today())#爬取时间改为今天
        await bot.send(ev, return_schedule())
    else:
        await bot.send(ev, return_schedule())


@sv.on_fullmatch('刷新日程表')
async def re_Schedule(bot,ev):
    status = refresh_schedule()
    if status[0]:
        await bot.send(ev, '刷新日程表成功')
    else:
        await bot.send(ev, f'刷新日程表失败，错误代码{status[1]}')




def refresh_schedule():
    #刷新日程表
    schedule = request.Request(URL)
    schedule.add_header('User-Agent', header)

    with request.urlopen(schedule) as f:
        if f.code != 200:
            return [False,f.code]

        rew_data = f.read().decode('utf-8')

        data['schedule_data'] = json.loads(rew_data[152:-35])
        return [True,"ok"]


def return_schedule():
    #返回日程表信息

    t = datetime.date.today()#要读取的日期
    year, month, day = str(t).split("-")#分割年月日
    activity_inof_list = []
    inof_list = []
    inofs = ''

    for _ in range(data['calendar_days']):
        for i in data['schedule_data']:
            if i['year'] == year and i['month'] == month:
                
                for key in day_key:
                    if i['day'][day][key] != '':

                        inof_list.extend(re.findall("class='cl-t'>.+?</div>", i['day'][day][key]))

                activity_inof_list = [inof[13:-6] for inof in inof_list]

                inofs += '=========' + str(t).replace("-","年",1).replace("-","月",1) + '日' + '=========\n'
                for i in activity_inof_list:
                    inofs += '>>> ' + i + '\n'

        t += datetime.timedelta(days=1)#改为下一天的日期
        year, month, day = str(t).split("-")#分割年月日
        activity_inof_list = []
        inof_list = []

    #返回活动信息字符串
    return inofs




