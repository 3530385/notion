from datetime import timedelta,date
import plotly.express as px
import pandas as pd

def not_to_dt(notion_time):
    months=['January', 'February', 'March',
            'April', 'May', 'June', 'July',
            'August', 'September', 'October',
            'November', 'December']
    timesplit=notion_time.replace(',', '').split()
    month=months.index(timesplit[0])+1
    day=int(timesplit[1])
    year=int(timesplit[2])
    return date(year, month, day)

def get_profits(days,full_dates,profits):
    days=sorted(days)
    days+=[date.today()]
    full_profits=[]
    i=0
    for day in full_dates:
        if days[i+1]<=day and i!=len(profits)-1:
            i+=1
            full_profits.append(profits[i])
            continue
        full_profits.append(profits[i])
    return full_profits


def get_days(days):
    full_dates=[]
    start=days[0]
    full_dates.append(start)
    stop=date.today()
    delta=stop-start
    for _ in range(delta.days):
        start+=timedelta(days=1)
        full_dates.append(start)
    return full_dates

def plot_graph():
	df = pd.read_csv('tablenow.csv')
	dfn=df.loc[df['Done']=='Yes']
	dfn['Time done in dt']=dfn['Time done'].apply(not_to_dt)
	days=dfn['Time done in dt'].unique()
	profits=[0]
	for day in days:
	    profits+=[profits[-1]+dfn.loc[dfn['Time done in dt']==day,'Cost'].sum()]
	profits=profits[1:]
	full_dates=get_days(days)
	full_profits=get_profits(days,full_dates,profits)
	fig=px.area(x=full_dates, y=full_profits,markers=True)
	fig.update_layout( 
	    xaxis=dict(
	        showline=True,
	        showgrid=True,
	        showticklabels=True,
	        linecolor='rgb(204, 204, 204)',
	        linewidth=2,
	        ticks='outside',
	        tickfont=dict(
	            family='Arial',
	            size=12,
	            color='rgb(82, 82, 82)',
	        )),
	    yaxis=dict(
	        showline=True,
	        showgrid=True,
	        showticklabels=True,
	        linecolor='rgb(204, 204, 204)',
	        linewidth=2,
	        ticks='outside',
	        tickfont=dict(
	            family='Arial',
	            size=12,
	            color='rgb(82, 82, 82)',
	        )),
	    xaxis_title="",
	    yaxis_title="")
	return fig

if __name__ == '__main__':
	plot_graph()

