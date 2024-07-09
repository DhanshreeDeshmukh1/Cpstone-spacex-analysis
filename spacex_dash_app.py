# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go  # Use plotly.graph_objs for graph objects

# Read the SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Create a Dash application
app = dash.Dash(__name__)

# Define the maximum and minimum payload values for the slider
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create the app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),
    
    # Pie chart to show total successful launches or for selected site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    # Payload range slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={min_payload: str(min_payload), max_payload: str(max_payload)},
        value=[min_payload, max_payload]
    ),
    
    # Scatter chart to show payload vs launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback to update the pie chart based on selected launch site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = go.Figure(data=go.Pie(
            labels=spacex_df['Launch Site'].unique(),
            values=spacex_df.groupby('Launch Site')['class'].sum(),
            name='Total Success vs Failure for All Sites'
        ))
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = go.Figure(data=go.Pie(
            labels=['Success', 'Failure'],
            values=filtered_df['class'].value_counts(),
            name=f'Success vs Failure for {entered_site}'
        ))
    
    fig.update_layout(title='Launch Success Pie Chart')
    return fig

# Callback to update the scatter chart based on selected launch site and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    if entered_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        fig = go.Figure(data=go.Scatter(
            x=filtered_df['Payload Mass (kg)'],
            y=filtered_df['class'],
            mode='markers',
            marker=dict(color='#000'),  # Assuming Booster Version is mapped to colors
            text=filtered_df['Launch Site'],
            hoverinfo='text'
        ))
        fig.update_layout(title='Payload Mass vs Success/Failure (All Sites)',
                          xaxis_title='Payload Mass (kg)',
                          yaxis_title='Class (Success=1, Failure=0)')
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) &
                                (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        fig = go.Figure(data=go.Scatter(
            x=filtered_df['Payload Mass (kg)'],
            y=filtered_df['class'],
            mode='markers',
            marker=dict(color='#000'),  # Assuming Booster Version is mapped to colors
            text=filtered_df['Launch Site'],
            hoverinfo='text'
        ))
        fig.update_layout(title=f'Payload Mass vs Success/Failure ({entered_site})',
                          xaxis_title='Payload Mass (kg)',
                          yaxis_title='Class (Success=1, Failure=0)')
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
