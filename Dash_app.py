#IMPORTS
import pandas as pd
import numpy as np
import os

import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Viridis color scale
viridis = px.colors.sequential.Viridis

#DATA
path = "./"
df = pd.read_csv(os.path.join(path,"no3data.csv")).drop(["Unnamed: 0"], axis=1)

#DASH
from dash import Dash, dcc, html, Input, Output

app = Dash(__name__)
server = app.server

#LAYOUT
app.layout = html.Div([

    html.H1("Simple app for visualising the NO3 data", style={'text-align': 'center'}),

    dcc.Checklist(id='slct_month',
                options=[
                {'label': 'January', 'value': 1},
                {'label': 'February', 'value': 2},
               {'label': 'March', 'value': 3},
               {'label': 'April', 'value': 4},
                {'label': 'May', 'value': 5},
               {'label': 'June', 'value': 6},
               {'label': 'July', 'value': 7},
                {'label': 'August', 'value': 8},
               {'label': 'September', 'value': 9},
               {'label': 'October', 'value': 10},
                {'label': 'November', 'value': 11},
               {'label': 'December', 'value': 12},
                ],
            value=[3]),

    dcc.Dropdown(
        id="slct_scale",
        options=[
        {"label": "Log scale", "value": "log"},
        {"label": "Linear scale", "value": "lin"}],
        multi=False,
        value="log"),
    
    dcc.Dropdown(
        id="slct_plot",
        options=[
        {"label": "Discrete measurements (scatter)", "value": "Scatter"},
        {"label": "Interpolated (heatmap)", "value": "Heatmap"}],
        multi=False,
        value='Scatter'),

    html.Label(["Choose the depth:"], style={'font-weight':'bold'}),

    dcc.Slider(
        id='slct_depth',
        min=50, 
        max=250, 
        step=50,
        value=100,
        vertical=True,
        verticalHeight=100),
   
    html.Br(),

    dcc.Graph(id='graph', figure={})

])

#CALLBACK
@app.callback(
    [Output(component_id='graph', component_property='figure')],
    [Input(component_id='slct_month', component_property='value'), 
    Input(component_id='slct_scale', component_property='value'),
    Input(component_id='slct_plot', component_property='value'),
    Input(component_id='slct_depth', component_property='value')
    ]
)
#here the order of the inputs was determined, and has to be in the same order in the update_graph function

def update_graph(month_slct, scale_slct, plot_slct, depth_slct):
    print(month_slct)
    print(scale_slct)
    print(plot_slct)
    print(depth_slct)

    dff = df.copy()

    """
    PARAMETERS CHOSEN IN WEB APP
    """
    months = month_slct #months to be displayed
    colorscale = scale_slct #log - logartmic; lin - linear
    plot_type = plot_slct
    depth_range = [depth_slct,0]

    """
    PARAMETERS PRE-DEFINED
    """
    
    month_dict = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
    }

    colorscales = {"log":[[0, viridis[0]],[1./1000, viridis[2]],[1./100, viridis[4]],[1./10, viridis[7]],[1., viridis[9]]],
                "lin":viridis}

    rows = len(months)
    cols = 1
    fig = make_subplots(rows=rows, cols=cols, vertical_spacing = 0.2/float(len(months)), subplot_titles=tuple(month_dict[m] for m in sorted(months)))

    """
    PLOT CODE for SCATTER
    """
    if plot_type=="Scatter":
        for i,month in enumerate(sorted(months)):
            fig.add_trace(go.Scatter(x=dff[dff["Month"]==month]["Year"], 
                                    y=dff[dff["Month"]==month]["Depth"],
                                    customdata = dff[dff["Month"]==month][["no3","Day","Month"]],
                                    mode='markers',
                                    showlegend=False,
                                    hovertemplate='<br>'.join([
                    'Depth: %{y}',
                    'Year: %{x}',
                    'Month %{customdata[2]}',
                    'Day: %{customdata[1]}',
                    'no3: %{customdata[0]}'
                ]),
                                    marker=dict(
                                        size=12,
                                        cmax=12,
                                        cmin=0,
                                        color=df[df["Month"]==month]["no3"],
                                        colorscale=colorscales[colorscale],
                                        colorbar=dict(title='[mmol NO3/m**3]',len=1/len(months)))),
                        row=i+1, col=1)
            
            fig.update_yaxes(title_text="Depth [m]", range=depth_range, row=i+1, col=1)
            fig.update_xaxes(title_text="Year", range=[1970, 2020], row=i+1, col=1)
            

        fig.update_layout(title="NO3 overview",
                        yaxis = dict(range=depth_range),
                        height=400*len(months), width=1000)
        
        return [fig]

    #HEATMAP
    else:
        for i,month in enumerate(sorted(months)):
            fig.add_trace(go.Heatmap(z=dff[dff["Month"]==month]["no3"], 
                x=dff[dff["Month"]==month]["Year"], 
                y=dff[dff["Month"]==month]["Depth"], 
                zsmooth = 'best',
                zmax = 12,
                zmin = 0,
                colorscale = colorscales[colorscale],
                hoverinfo = ['z'],
                colorbar=dict(title='[mmol NO3/m**3]', len=1/len(months))),
                row=i+1, col=1)
        
            fig.update_yaxes(title_text="Depth [m]", range=depth_range, row=i+1, col=1)
            fig.update_xaxes(title_text="Year", range=[1970, 2018], row=i+1, col=1)

        fig.update_layout(title="NO3 overview",
                    yaxis = dict(range=depth_range),
                    height=400*len(months), width=1000)

        #fig.update_traces(selector=dict(type='heatmap'))
        return [fig]
        
if __name__ == '__main__':
    app.run_server(debug=True)