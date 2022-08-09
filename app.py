from dash import Dash, html, dcc, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
import dash_daq as daq
import pandas as pd
import plotly.express as px
import plotly.io as poi
poi.renderers.default = 'browser'
from dashlib import Tabler,Timer
from datetime import timedelta,datetime
from plotly_money_graph import plot_graph

table=Tabler('table_dash.csv')
current_task=table.get_current_task()
current_task_name=current_task['Name']
current_task_time=datetime.strptime(current_task['Time'], "%H:%M:%S") - datetime(1900, 1, 1)
timer=Timer(current_task_time)
current_task_time=str(current_task_time)


fig=plot_graph()

app=Dash(__name__)
app.title = "GDZ Dashboard"

app.layout = html.Div([
    dcc.Interval(
            id="interval-component",
            interval=2* 1000,  # in milliseconds
            n_intervals=0,  # start at batch 50
            disabled=True,
        ),
    html.Div('Dasboard for GDZ'),
	daq.StopButton(buttonText='Start', id="start-button", n_clicks=0),
    daq.StopButton(buttonText='Done', id="done-button", n_clicks=0),
    html.Div(current_task_name, id='task_label'),
    html.Div(current_task_time, id='timer_label'),
	dcc.Graph(figure=fig)])



@app.callback(
    [Output("interval-component", "disabled"),
     Output("start-button", "buttonText"),
     Output('timer_label', 'children'),
     Output('task_label', 'children'),
     ],
    [Input("start-button", "n_clicks"),
     Input('done-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    [State("interval-component", "disabled")],
)
def stop_production(btn_start_n, btn_done_n, n_int, current, ):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    print(changed_id)
    print(btn_start_n)
    if 'start-button' in changed_id:
        print('start-button')
        if current:
            timer.start_timer('working in a Dash')
            current_time=str(timer.get_current_time())
        else:
            current_time=str(timer.stop_timer())
        return not current, "stop" if current else "start", html.Div(current_time),html.Div(current_task_name)
    if 'done-button' in changed_id:
        print('done-button')
        if current:
            current_time=timer.stop_timer()
        timer.reset_timer()
        current_task=table.done_task(current_time)
        return True, "start", html.Div(str(timedelta(0))),html.Div(current_task['Name'])
    if 'interval-component' in changed_id:
        if n_int!=0 and not current:
            return False, 'stop', html.Div(str(timer.get_current_time())),html.Div(current_task_name)
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate

# Callbacks for stopping interval update
# @app.callback(
#     [Output("interval-component", "disabled")],
#     [Input("done-button", "n_clicks")],
#     [State("interval-component", "disabled")],
# )
# def done_production(n_clicks, current):
#     if n_clicks == 0:
#         return False
#     if current:
#         return False
#     else:
#         timer.reset_timer()
#         return False



#     Input('btn-stop', 'n_clicks'),
#     Input('btn-done', 'n_clicks'),
#     Input('interval1', 'n_intervals')
# )

# @app.callback(
#     Output('current-process', 'children'),
#     Input('btn-start', 'n_clicks'),
#     Input('btn-stop', 'n_clicks'),
#     Input('btn-done', 'n_clicks'),
#     Input('interval1', 'n_intervals')
# )
# def displayClick(btn1, btn2, btn3,n):
#     changed_id = [p['prop_id'] for p in callback_context.triggered][0]
#     print([p['prop_id'] for p in callback_context.triggered])
#     if 'btn-start' in changed_id:
#         msg=n
#     elif 'btn-stop' in changed_id:
#         #msg = '§16 Вопрос 4 stopped on 00:15:26'
#         msg = 'stop_timing()'
#     elif 'btn-done' in changed_id:
#         #msg = '§16 Вопрос 5 ready to fight'
#         msg = 'done_task()'
#     else:
#         current_task = table.get_current_task()
#         msg=' '.join([current_task['Name'],'потрачено',
#             current_task['Time'],'продолжим??'])
#     return html.Div(msg)




if __name__ == '__main__':
    app.run_server(debug=True)