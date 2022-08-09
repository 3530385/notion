import pandas as pd
from datetime import datetime, timedelta

class Tabler:
    def __init__(self,tablename):
        self.df_dash=pd.read_csv('table_dash.csv')
        self.current_task_index=self.df_dash[self.df_dash['Done']=='No'].index[0]
        self.current_task=self.df_dash.iloc[self.current_task_index]

    def get_current_task(self):
        return self.current_task

    def done_task(self,current_time):
        self.df_dash.loc[self.current_task_index,'Done']='Yes'
        self.df_dash.loc[self.current_task_index,'Time done']=str(current_time)
        self.df_dash.loc[self.current_task_index,'Time_seconds']=current_time.total_seconds()
        self.df_dash.loc[self.current_task_index,'Time done']=str(datetime.now())
        self.df_dash.loc[self.current_task_index,'Efficiency']=self.current_task['Cost']/self.current_task['Time_seconds']*3600
        self.df_dash.to_csv('table_dash.csv',index=False)
        self.current_task_index=self.df_dash[self.df_dash['Done']=='No'].index[0]
        self.current_task=self.df_dash.iloc[self.current_task_index]
        return self.current_task


class Timer:
    def __init__(self,previous_time):
        with open('clockify_token.txt','r') as f:
            self.clockify_token=f.read()
        self.timer_start=None
        self.Clock=Clockify_updater(self.clockify_token)
        self.previous_timing=previous_time

    def start_timer(self,task):
        self.current_task=task
        self.timer_start=datetime.now()
        self.Clock.start_task(self.current_task)
        print('start timed in '+str(self.timer_start))

    def get_current_time(self):
        return (datetime.now()-self.timer_start)+self.previous_timing

    def stop_timer(self):
        self.previous_timing=self.get_current_time()
        self.Clock.stop_task()
        print('stop timed in '+str(self.previous_timing))
        return self.previous_timing

    def reset_timer(self):
        self.timer_start=None
        self.previous_timing=timedelta(0)



































import requests
import json
from clockifyclient.api import APIServer
from clockifyclient.client import APISession
from notion_database.properties import Properties
from notion_database.page import Page
from pytz import timezone
import isodate
from datetime import datetime, timedelta
import time



class Parser:
    pages=None
    work_pages_id=None
    def __init__(self,token):
        self.token=token 
    def get_pages(self,database_id='1abc122ef7464fe0ba0612718f635475'):
        headers={'Authorization': self.token,
                 'Notion-Version': '2021-08-16'}
        query={ "sorts": [
	    {
	      "property": "Order",
	      "direction": "ascending"
	    }] }
        res=requests.post('https://api.notion.com/v1/databases/'+database_id+'/query',headers=headers,data=query)
        self.pages=[{**page['properties'],**{'id':page['id']}} for page in res.json()['results']]
        return self.pages
    def get_work_pages_id(self):
        self.pages=self.get_pages()
        #print(self.pages)
        self.work_pages=[page for page in self.pages if page['Process']['checkbox'] and not page['Done']['checkbox']]
        self.work_pages_id=[page['id'] for page in self.pages if page['Process']['checkbox'] and not page['Done']['checkbox']]
        return self.work_pages, self.work_pages_id
    def get_time(self):
        time_dict={}
        for page in self.pages:
            if page['id'] in self.work_pages_id:
                time_dict[page['id']]=page['Time']['rich_text'][0]['text']['content']
        return time_dict

    def updatePageTotal(self,Total_sum):
        Total_sum=round(Total_sum,2)
        headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json",
            "Notion-Version": "2021-05-13"
        }

        updateUrl = f"https://api.notion.com/v1/blocks/09e380f2-092c-48b3-8f74-affd6c4ffd99"

        updateData={'heading_1': {'text': [{'type': 'text',
        'text': {'content': 'Всего заработано: ', 'link': None},
        'annotations': {'bold': False,
         'italic': False,
         'strikethrough': False,
         'underline': False,
         'code': False,
         'color': 'default'},
        'plain_text': 'Всего заработано: ',
        'href': None},
       {'type': 'text',
        'text': {'content': str(Total_sum)+' ₽', 'link': None},
        'annotations': {'bold': False,
         'italic': True,
         'strikethrough': False,
         'underline': True,
         'code': True,
         'color': 'green'},
        'plain_text': str(Total_sum)+' ₽',
        'href': None}]}}
        data = json.dumps(updateData)

        response = requests.request("PATCH", updateUrl, headers=headers, data=data)
        
    def updatePageToday(self,Today_sum):
        Today_sum=round(Today_sum,2)
        headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json",
            "Notion-Version": "2021-05-13"
        }

        updateUrl = f"https://api.notion.com/v1/blocks/0456e753-e42f-4a6e-ae6b-2bf68c7123c1"

        updateData={'heading_1': {'text': [{'type': 'text',
          'text': {'content': 'За сегодня:             ', 'link': None},
          'annotations': {'bold': False,
           'italic': False,
           'strikethrough': False,
           'underline': False,
           'code': False,
           'color': 'default'},
          'plain_text': 'За сегодня:             ',
          'href': None},
         {'type': 'text',
          'text': {'content': str(Today_sum)+' ₽', 'link': None},
          'annotations': {'bold': True,
           'italic': True,
           'strikethrough': False,
           'underline': True,
           'code': True,
           'color': 'green'},
          'plain_text': str(Today_sum)+' ₽',
          'href': None}]}}
        data = json.dumps(updateData)

        response = requests.request("PATCH", updateUrl, headers=headers, data=data)



class Clockify_updater:
    def __init__(self,api_key,
                        zone = timezone('Europe/Moscow')):
        self.api_key=api_key
        self.headers={'x-api-key': api_key}
        self.workspace_id='5f2917242e64803a9cabb758'
        self.user_id='5f2917242e64803a9cabb757'
        self.zone = zone
        self.session = APISession(
                api_server=APIServer("https://api.clockify.me/api/v1"), api_key=api_key)
        if self.session.get_projects():
            self.project = self.session.get_projects()[2]
    
    def is_active(self):
        url='https://api.clockify.me/api/v1/workspaces/{}/user/{}/time-entries'
        re=requests.get(url.format(self.workspace_id,self.user_id),headers=self.headers)
        if not re.json()[0]['timeInterval']['end']: #Если время окончания задачи не None
            return True
        else:
            return False
                      
    def start_task(self,description):
        moscow_time = datetime.now(self.zone) # текущее время по Москве
        response = self.session.add_time_entry(
            start_time=moscow_time, description=description, project=self.project # В проектеWork начинается отсчёт времени 
        )                                                                            # с названием discription

        #print(response)
    
    def stop_task(self):
        moscow_time = datetime.now(self.zone)
        self.session.stop_timer(stop_time=moscow_time)
        
    def get_dt_start(self):#,task_name):
        tasks=requests.get('https://api.clockify.me/api/v1/workspaces/{}/user/{}/time-entries'.format(self.workspace_id,self.user_id),
                           headers=self.headers).json()
        #duration=[{task['name']:task[0]['timeInterval']['duration']} for task in tasks]
        time_start=tasks[0]['timeInterval']['start']
        time_start=datetime.strptime(time_start,"%Y-%m-%dT%H:%M:%SZ")
        return time_start
        


def get_sec(time_str):
    """Get Seconds from time."""
    try:
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)
    except ValueError:
        return time_str

def add_time(tmdlt,time,page_id,token):
    PROPERTY = Properties()
    format_time=str(timedelta(seconds=int(time)+int(tmdlt)+1))
    PROPERTY.set_rich_text("Time", format_time)
    PROPERTY.set_number("Time_seconds",int(time)+int(tmdlt)+1)
    #print(time+timedelta+1)
    P = Page(integrations_token=token)
    P.update_page(page_id=page_id, properties=PROPERTY)
    return format_time


def main():
    with open('notion_token.txt','r') as f:
        token_notion=f.read()

    with open('clockify_token.txt','r') as f:
        token_clockify=f.read()
    flag=0
    p=Parser(token_notion)
    Clock=Clockify_updater(token_clockify)
    active_pages,active_pages_id=p.get_work_pages_id()
    rubls={'today':sum((datetime.strptime(page['Time done']['last_edited_time'],'%Y-%m-%dT%H:%M:%S.000Z').date() == datetime.now().date() and page['Done']['checkbox'] for page in p.pages))*273.73,
            'all_time':sum((page['Done']['checkbox'] for page in p.pages))*273.73}
    while 1:
        active_pages,active_pages_id=p.get_work_pages_id()
        past_rubls=rubls
        rubls={'today':sum((datetime.strptime(page['Time done']['last_edited_time'],'%Y-%m-%dT%H:%M:%S.000Z').date() == datetime.now().date() and page['Done']['checkbox'] for page in p.pages))*273.73,
            'all_time':sum((page['Done']['checkbox'] for page in p.pages))*273.73}
        if past_rubls['today']!=rubls['today']:
            p.updatePageToday(rubls['today'])
        if past_rubls['all_time']!=rubls['all_time']:
            p.updatePageTotal(rubls['all_time'])
        if active_pages:
            if flag ==1:
                page_name=active_pages[0]['Name']['title'][0]['plain_text']
                Clock.start_task(page_name)
                start=datetime.now()
                time_past=get_sec(p.get_time()[active_pages_id[0]])
                print('Отсчёт времени для задачи: '+page_name)
                flag=0
            tmdlt=datetime.now()-start
            
            format_time=add_time(tmdlt.seconds,time_past,page_id=active_pages_id[0],token=token_notion)
            print(f"{format_time}\r", end="")
            time.sleep(1)
        else:
            is_actv=Clock.is_active()
            if is_actv:
                Clock.stop_task()
                print('\n'+page_name + ' остановлен')
            flag=1
            time.sleep(1)

if __name__ == '__main__':
    main()

