import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table

import pandas as pd

import plotly.graph_objects as go
import pandas as pd
from scipy.signal import find_peaks

import json
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
fig = go.Figure()

colors = {

    "background": "#fffffa",
    "text": "#000000"
}

app.layout = html.Div([

     html.Div([ html.H2('A-Scan')],style={'text-align':'center','color': 'green'}),
    dcc.Upload(id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
        ),
    html.Div(id='output-data-upload'),
    html.Button('Plot', id='submit', n_clicks=0,style={'backgroundColor':'yellow','margin-left': '500px'}),
    html.Button('Select points', id='again', n_clicks=0,style={'backgroundColor':'yellow','margin-left': '100px'}),
    html.Div(id='count',style={'margin-left': '700px'}),
    dcc.Graph(id='graph'), 
    
    html.Div(id='space'),
    html.Div(id='points',style={'margin-left': '550px'}),
    dcc.RadioItems(options=['Peak to Peak','Zeroes befor peak','Zeroes after peak'],id='mybuttons',inline=True,style={'margin-left': '550px'}),
    html.Div(id='time',style={'margin-left': '550px'}),
    html.Div([
        "Enter the thickness in cm:",
        dcc.Input(id='thickness', value='0', type='number')
    ],style={'margin-left': '550px'}),
    html.Div(id='speed',style={'margin-left': '550px'}),
    html.Div([
        "Enter the speed in m/s:",
        dcc.Input(id='speed2', value='0', type='number')
    ],style={'margin-left': '550px'}),
    html.Div(id='thickness2',style={'margin-left': '550px'}),
    
    
    html.Div([ html.H2('B-Scan')],style={'text-align':'center','color': 'green'}),
    dcc.Upload(id='upload-data2',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
        ),
            html.Div(id='output-data-upload2'),
         html.Button('Plot', id='submit2', n_clicks=0,style={'backgroundColor':'yellow','margin-left': '500px'}),
    
         dcc.Graph(id='graph2'),
        
])

df=pd.DataFrame()

data3=pd.DataFrame()


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    global df
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            data = pd.read_csv(io.StringIO(decoded.decode('utf-16')),sep=';', header=None)
            df=data.copy()
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            data= pd.read_excel(io.BytesIO(decoded),sheet_name='A-Scan')
            df=data.copy()
        return html.Div([ html.H6('file Uploaded Successfully'),])
        
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])



def parse_contents2(contents, filename, date):
    content_type, content_string = contents.split(',')
    global data3
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            data3=data.copy()
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            data= pd.read_excel(io.BytesIO(decoded),sheet_name='A-Scan')
            data3=data.copy()
        return html.Div([ html.H6('file Uploaded Successfully'),])
        
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])



@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              )
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

val=0


@app.callback(

                Output('graph', 'figure'),
                Input('submit','n_clicks'),
                State('upload-data', 'filename'),
               

)
def get_output(n_clicks,name):
           global val
           global indices
           global time
           global amp
            
          
           if 'xls' in name[0]:
          
            for i in range(len(df)):
              if(df.iloc[i][0]=='Time(us)'):
                val=i
                break
            data=df.iloc[val+1:,:]
            data=data.iloc[:,0:2]
            data.columns=['Time','Amplitude']
            data=data.reset_index(drop=True)
            time=data['Time']
            amp=data['Amplitude']
            indices = find_peaks(amp)[0]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                     y=amp,
                     mode='lines+markers',
                      name='Original Plot'
                       ))
            return fig
           if 'csv' in name[0]:
               for i in range(len(df)):
                if(df.iloc[i][0][0:4]=='Time'):
                 val=i
                
                 break
               data=df.iloc[val+1:,:]
               data=data.iloc[:,0:1]
               time=[]
               amp=[]
               for i in range(len(data)):
                 x=data.iloc[i][0].split(',')
                 time.append(float(x[0]))
                 amp.append(float(x[1][1:]))
               indices = find_peaks(amp)[0]
               fig = go.Figure()
               fig.add_trace(go.Scatter(
                     y=amp,
                     mode='lines+markers',
                      name='Original Plot'
                       ))
               return fig           

vals=[]

@app.callback(
    Output('points','children'),
    Input('graph','clickData'),
)
def click(clickData):
    if not clickData:
        raise dash.exceptions.PreventUpdate
    vals.append({k: clickData["points"][0][k] for k in ["x", "y"]})
    a=json.dumps({k: clickData["points"][0][k] for k in ["x", "y"]})
    return f'Threshold set at:{str(a)}'




@app.callback(

                Output('space','children'),
                Input('again','n_clicks'),

)

def remove_vals(clicks):
         vals.clear()
         return ' '   





@app.callback(
       Output('time','children'),
       Input('mybuttons','value'),
       
)

def get_time(selection):
    global time_diff
    if(selection=='Peak to Peak'):
          start1=vals[0]['x']
          start2=vals[1]['x']
          for num in indices:
            if(num>=start1):
              peak1=num
              break
          for num in indices:
            if(num>=start2):
              peak2=num
              break
          time_diff=time[peak2]-time[peak1]
          
          return f'Time difference is: {str(time_diff)}'
    if(selection=='Zeroes befor peak'):
          start1=vals[0]['x']
          start2=vals[1]['x']
          prev1=start1-1
          prev2=start2-1
          while(amp[start1]*amp[prev1]>0):
             start1=start1-1
             prev1=prev1-1
          time1=(time[start1]+time[prev1])/2
          while(amp[start2]*amp[prev2]>0):
             start2=start2-1
             prev2=prev2-1
          time2=(time[start2]+time[prev2])/2
          time_diff=time2-time1
         
          return f'Time difference is: {str(time_diff)}'
    if(selection=='Zeroes after peak'):
          start1=vals[0]['x']
          start2=vals[1]['x']
          prev1=start1+1
          prev2=start2+1
          while(amp[start1]*amp[prev1]>0):
             start1=start1+1
             prev1=prev1+1
          time1=(time[start1]+time[prev1])/2
          while(amp[start2]*amp[prev2]>0):
             start2=start2+1
             prev2=prev2+1
          time2=(time[start2]+time[prev2])/2
          time_diff=time2-time1
         
          return f'Time difference is: {str(time_diff)}'
          
@app.callback(
     Output('speed','children'),
     Input('thickness','value'),
)

def get_speed(value):
    spd=(value/time_diff)*10000
    return f'Measured Speed is: {str(spd)} m/s'
    
    
@app.callback(
     Output('thickness2','children'),
     Input('speed2','value'),
)

def get_thickness(value):
    dist=(value*time_diff)/10000
    return f'Measured thickness is: {str(dist)} cm' 
    
@app.callback(
     Output('count','children'),
     Input('graph','clickData'),
     Input('again','n_clicks'),
     
)

def get_count(click1,click2):
     return f'Number of points selected:{str(len(vals))}'
     
     
     
@app.callback(Output('output-data-upload2', 'children'),
              Input('upload-data2', 'contents'),
              State('upload-data2', 'filename'),
              State('upload-data2', 'last_modified'),
              )
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents2(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children



@app.callback(

                Output('graph2', 'figure'),
                Input('submit2','n_clicks'),
                State('upload-data2', 'filename'),
               

)
def get_output(n_clicks,name):
            
            x=data3.iloc[0]
            y=x[0].split('\t')

            col=[]
            for i in range(len(y)):
               st='col'+str(i);
               col.append(st)
            empty_df=pd.DataFrame(columns=col)
            for i in range(len(data3)):
             x=data3.iloc[i]
             y=x[0].split('\t')
             empty_df.loc[i] = y   
             fig = px.imshow(empty_df)  
                        
            return fig
            






if __name__ == '__main__':
    app.run_server(debug=True)

