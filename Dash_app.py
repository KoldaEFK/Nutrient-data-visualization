#IMPORTS
import pandas as pd
import numpy as np
import os
from itertools import chain

import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#DASH
from dash import Dash, dcc, html, Input, Output
import dash_daq as daq
import dash_bootstrap_components as dbc #dash bootstrap componenets for layout

#Color scales
viridis = px.colors.sequential.Viridis
magma = px.colors.sequential.Magma

#DATA
path = "./"
df_no3 = pd.read_csv(os.path.join(path,"no3data.csv")).drop(["Unnamed: 0"], axis=1) #original no3 dataframe (no3 average for each year&month&depth)
df_po4 = pd.read_csv(os.path.join(path,"po4data.csv")).drop(["Unnamed: 0"], axis=1) #po4 dataframe (po4 average for each year&month&depth)
halocline_df = pd.read_csv(os.path.join(path,"haloclinedata271.csv")).drop(["Unnamed: 0"], axis=1) #halocline depth for each year&month

app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
server = app.server

#LAYOUT
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("seavisualization", style={'text-align': 'center'}),
            html.Div("Explore the nutrient data", style={'text-align': 'center', 'font-style':'italic'}),
            html.Br(),
            html.Div("The data are from the 271 Gotland Deep Station in the Baltic Sea"),
            html.Div("For any questions email me -> petr.kolar@student.manchester.ac.uk"),
            html.Br(),
        ], width=12) 
    ]),
    dbc.Row([
        dbc.Col([
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
            value=[3,5]),

            dcc.Dropdown(id="slct_scale",
                options=[
                {"label": "Log scale", "value": "log"},
                {"label": "Linear scale", "value": "lin"}],
                multi=False,
                value="log"),
    
            dcc.Dropdown(id="slct_plot",
                options=[
                {"label": "Discrete measurements (scatter)", "value": "Scatter"},
                {"label": "Interpolated (heatmap)", "value": "Heatmap"}],
                multi=False,
                value='Scatter')], width=10),
    ]),

    dbc.Row([
        dbc.Col([
                html.Div(["Choose the depth:"], style={'font-weight':'bold', 'text_align':"center"}),

                dcc.Slider(id='slct_depth',
                    min=50, 
                    max=250, 
                    step=50,
                    value=100,
                    vertical=True,
                    verticalHeight=150)], width={'size':2,'offset':0}),
        dbc.Col([
            dcc.Checklist(id='slct_var',
                        options=[
                        {'label': 'Nitrate(NO3)', 'value': 'no3'},
                        {'label': 'Phosphate(PO4)', 'value': 'po4'},
                        ],
                    value=['no3'])], width={'size':2,'offset':2}),     
        dbc.Col([
            daq.BooleanSwitch(id='slct_halocline',
                label='Show halocline',
                on=False)], width={'size':2,'offset':2})
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='graph_no3', figure={})
        ], width=12)
    ])
    
])


#CALLBACK
@app.callback(
    [Output(component_id='graph_no3', component_property='figure')],
    [Input(component_id='slct_month', component_property='value'), 
    Input(component_id='slct_scale', component_property='value'),
    Input(component_id='slct_plot', component_property='value'),
    Input(component_id='slct_depth', component_property='value'),
    Input(component_id='slct_var', component_property='value'),
    Input(component_id='slct_halocline', component_property='on')
    ]
)
#IMPORTANT - in the @app.callback the order of the inputs is determined, and has to be in the same order in the update_graph function

def update_graph(month_slct, scale_slct, plot_slct, depth_slct, var_slct, halocline_slct):
    print(month_slct)
    print(scale_slct)
    print(plot_slct)
    print(depth_slct)
    print(var_slct)
    print(halocline_slct)
    
    dff_no3 = df_no3.copy() #no3
    dff_po4 = df_po4.copy() #po4

    """
    PARAMETERS CHOSEN IN WEB APP
    """
    months = month_slct #months to be displayed
    colorscale = scale_slct #log - logartmic; lin - linear
    plot_type = plot_slct #scatter/heatmap
    depth_range = [depth_slct,0]
    vars = var_slct #no3 AND/OR po4 
    halocline = halocline_slct #True/False

    #it is not nessesary to reassign all these variables

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

    #dictionary of dataframe for no3 and po4
    vars_dfs = {
        "no3":dff_no3,
        "po4":dff_po4
    }

    #dictionary for the units of each variable
    units_dict = {
        "no3":"[mmol NO3/m**3]",
        "po4":"[mmol PO4/m**3]"
    }

    #there might be outlayers and measurement errors, so the easiest method to get the max and min (reasonable) values for each variable
    #is looking at the data and choosing it manually
    max_min_dict = { 
    "no3":{
        "max":12,
        "min":0},
    "po4":{
        "max":4,
        "min":0}
    }

    #different colors for no3 and po4
    colorscales = {
        'no3':{"log":[[0, viridis[0]],[1./1000, viridis[2]],[1./100, viridis[4]],[1./10, viridis[7]],[1., viridis[9]]],
                "lin":viridis
        },
        'po4':{"log":[[0, magma[0]],[1./1000, magma[2]],[1./100, magma[4]],[1./10, magma[7]],[1., magma[9]]],
                "lin":magma
        }
    }

    #THE FIGURE - subplots
    rows = len(months) 
    cols = 1 if len(vars)==0 else len(vars)
    subplot_titles = tuple(chain.from_iterable([month_dict[m], month_dict[m]] for m in sorted(months))) if len(vars)==2 else tuple(month_dict[m] for m in sorted(months))
    fig = make_subplots(rows=rows, cols=cols, vertical_spacing = 0.2/float(len(months)), subplot_titles=subplot_titles)
    
    
    """
    PLOT CODE
    """
    #SCATTER
    if plot_type=="Scatter":
        for col_i, var in enumerate(vars): #for each var (column)
            dff = vars_dfs[var]
            for row_i,month in enumerate(sorted(months)): #for each month (row)
                fig.add_trace(go.Scatter(x=dff[dff["Month"]==month]["Year"], 
                                        y=dff[dff["Month"]==month]["Depth"],
                                        customdata = dff[dff["Month"]==month][[var,"Day","Month"]],
                                        mode='markers',
                                        showlegend=False,
                                        hovertemplate='<br>'.join([
                                            'Depth: %{y}',
                                            'Year: %{x}',
                                            'Month %{customdata[2]}',
                                            'Day: %{customdata[1]}',
                                            str(var)+': %{customdata[0]}'
                                        ]),
                                        marker=dict(
                                            size=12,
                                            cmax=max_min_dict[var]['max'], #the max and min values of the var (differ between no3 and po4)
                                            cmin=max_min_dict[var]['min'],
                                            color=dff[dff["Month"]==month][var],
                                            colorscale=colorscales[var][colorscale],
                                            colorbar=dict(title=units_dict[var],
                                                len=1/len(months), 
                                                x=(1+col_i*0.15)))), #so that the colorbars dont overlap
                            row=row_i+1, col=col_i+1)
                
                
                fig.update_yaxes(title_text="Depth [m]", range=depth_range, row=row_i+1, col=col_i+1)
                fig.update_xaxes(title_text="Year", range=[1970, 2020], row=row_i+1, col=col_i+1)
            
    #HEATMAP
    else:
        for col_i, var in enumerate(vars):
            dff = vars_dfs[var]
            for row_i, month in enumerate(sorted(months)):
                fig.add_trace(go.Heatmap(z=dff[dff["Month"]==month][var], 
                    x=dff[dff["Month"]==month]["Year"], 
                    y=dff[dff["Month"]==month]["Depth"], 
                    zsmooth = 'best',
                    zmax = max_min_dict[var]['max'],
                    zmin = max_min_dict[var]['min'],
                    colorscale = colorscales[var][colorscale],
                    hoverinfo = ['z'],
                    colorbar=dict(
                        title=units_dict[var],
                        len=1/len(months), 
                        x=(1+col_i*0.15))),
                    row=row_i+1, col=col_i+1)
            
                fig.update_yaxes(title_text="Depth [m]", range=depth_range, row=row_i+1, col=col_i+1)
                fig.update_xaxes(title_text="Year", range=[1970, 2020], row=row_i+1, col=col_i+1)

    #ADD HALOCLINE
    if halocline:
        for col_i, var in enumerate(var_slct):
            for row_i,month in enumerate(sorted(months)):
                fig.add_trace(go.Scatter(x=halocline_df[halocline_df["Month"]==month]["Year"], 
                                        y=halocline_df[halocline_df["Month"]==month]["halocline"],
                                        mode='markers',
                                        name='halocline',
                                        hoverinfo = ['y'],
                                        showlegend=True if row_i==0 and col_i==0 else False,
                                        marker=dict(
                                            symbol="triangle-down", 
                                            color="red",
                                            size=8)),
                            row=row_i+1, col=col_i+1)
            

    fig.update_layout(height=400*len(months)) #the height of the figure must increase with each new row (month)
    
    return [fig] #The callback function must by definition return a list
        
if __name__ == '__main__':
    app.run_server(debug=True)