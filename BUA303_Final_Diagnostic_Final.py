#!/usr/bin/env python
# coding: utf-8

# In[7]:


import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd

# Load the dataset
df = pd.read_csv("Cleaned_Movies_Updated.csv")

# Remove 'Multiple Genres' from the dataset
df = df[df['Genre'] != 'Multiple Genres']

# Aggregate data for genre trends over time
genre_trends = df.groupby(['Release Year', 'Genre'])['Domestic Box Office (USD)'].sum().reset_index()

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("🎥 Movie Industry Box Office Analysis", style={'textAlign': 'center', 'color': 'gold'}),
    
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='📈 Genre Trends Over Time', value='tab1', style={'backgroundColor': '#1a1a1a', 'color': 'gold'}),
        dcc.Tab(label='📊 Total Genre Revenue Comparison', value='tab2', style={'backgroundColor': '#1a1a1a', 'color': 'gold'}),
        dcc.Tab(label='📊 Yearly Genre Comparison', value='tab3', style={'backgroundColor': '#1a1a1a', 'color': 'gold'})
    ]),
    
    html.Div([
        html.Div(id='genre-trends-container', children=[
            dcc.Graph(id='line-chart'),
            dcc.RangeSlider(
                id='line-year-slider',
                min=genre_trends['Release Year'].min(),
                max=genre_trends['Release Year'].max(),
                step=1,
                value=[genre_trends['Release Year'].min(), genre_trends['Release Year'].max()],
                marks={i: str(i) for i in range(genre_trends['Release Year'].min(), genre_trends['Release Year'].max()+1, 5)}
            ),
            html.H3(id="summary-title", style={'color': 'gold'}),
            dash_table.DataTable(
                id='summary-table',
                style_table={'overflowX': 'auto'},
                style_header={'backgroundColor': 'black', 'color': 'gold', 'fontWeight': 'bold'},
                style_cell={'backgroundColor': '#1a1a1a', 'color': 'white', 'textAlign': 'left'},
),

        ], style={'display': 'block'}),

        html.Div(id='total-revenue-container', children=[
            dcc.Dropdown(
                id='genre-dropdown',
                options=[{'label': genre, 'value': genre} for genre in df['Genre'].unique()],
                multi=True,
                placeholder='Select genres...',
                style={'color': 'black'}
            ),
            dcc.Graph(id='total-bar-chart'),
            dcc.RangeSlider(
                id='total-year-slider',
                min=genre_trends['Release Year'].min(),
                max=genre_trends['Release Year'].max(),
                step=1,
                value=[genre_trends['Release Year'].min(), genre_trends['Release Year'].max()],
                marks={i: str(i) for i in range(genre_trends['Release Year'].min(), genre_trends['Release Year'].max()+1, 5)}
            )
        ], style={'display': 'none'}),

        html.Div(id='yearly-revenue-container', children=[
            dcc.Dropdown(
                id='yearly-genre-dropdown',
                options=[{'label': genre, 'value': genre} for genre in df['Genre'].unique()],
                multi=True,
                placeholder='Select genres...',
                style={'color': 'black'}
            ),
            dcc.Graph(id='yearly-bar-chart'),
            dcc.RangeSlider(
                id='yearly-year-slider',
                min=genre_trends['Release Year'].min(),
                max=genre_trends['Release Year'].max(),
                step=1,
                value=[genre_trends['Release Year'].min(), genre_trends['Release Year'].max()],
                marks={i: str(i) for i in range(genre_trends['Release Year'].min(), genre_trends['Release Year'].max()+1, 5)}
            ),
            html.H3(id="yearly-summary-title", style={'color': 'gold'}),  # Dynamic title
            dash_table.DataTable(
                id='yearly-summary-table',
                style_table={'overflowX': 'auto'},
                style_header={'backgroundColor': 'black', 'color': 'gold', 'fontWeight': 'bold'},
                style_cell={'backgroundColor': '#1a1a1a', 'color': 'white', 'textAlign': 'left'},
),

        ], style={'display': 'none'})
    ])
])

# Callback to toggle visibility of sections
@app.callback(
    [dash.Output('genre-trends-container', 'style'),
     dash.Output('total-revenue-container', 'style'),
     dash.Output('yearly-revenue-container', 'style')],
    [dash.Input('tabs', 'value')]
)
def toggle_sections(selected_tab):
    return (
        {'display': 'block'} if selected_tab == 'tab1' else {'display': 'none'},
        {'display': 'block'} if selected_tab == 'tab2' else {'display': 'none'},
        {'display': 'block'} if selected_tab == 'tab3' else {'display': 'none'}
    )

# Callback to update the genre trends line chart
@app.callback(
    dash.Output('line-chart', 'figure'),
    [dash.Input('line-year-slider', 'value')]
)
def update_line_chart(year_range):
    filtered_data = genre_trends[(genre_trends['Release Year'] >= year_range[0]) & (genre_trends['Release Year'] <= year_range[1])]
    fig = px.line(
        filtered_data,
        x='Release Year',
        y='Domestic Box Office (USD)',
        color='Genre',
        title='🎬 Domestic Box Office Revenue by Genre Over Time',
        labels={'Domestic Box Office (USD)': 'Revenue (USD)'},
        template='plotly_dark'
    )
    return fig

# Callback to update the yearly genre comparison chart
@app.callback(
    dash.Output('yearly-bar-chart', 'figure'),
    [dash.Input('yearly-year-slider', 'value'),
     dash.Input('yearly-genre-dropdown', 'value')]
)
def update_yearly_genre_chart(year_range, selected_genres):
    # Filter data by selected year range
    filtered_data = genre_trends[(genre_trends['Release Year'] >= year_range[0]) & 
                                 (genre_trends['Release Year'] <= year_range[1])]

    # If genres are selected, filter by genre
    if selected_genres:
        filtered_data = filtered_data[filtered_data['Genre'].isin(selected_genres)]
    
    # Create grouped bar chart
    fig = px.bar(
        filtered_data,
        x='Release Year',
        y='Domestic Box Office (USD)',
        color='Genre',
        barmode='group',
        title=f'🎬 Yearly Domestic Box Office by Genre ({year_range[0]}-{year_range[1]})',
        labels={'Domestic Box Office (USD)': 'Revenue (USD)'},
        template='plotly_dark'
    )

    return fig

# Callback to update the total genre revenue chart
@app.callback(
    dash.Output('total-bar-chart', 'figure'),
    [dash.Input('total-year-slider', 'value'),
     dash.Input('genre-dropdown', 'value')]
)
def update_total_revenue_chart(year_range, selected_genres):
    filtered_data = genre_trends[(genre_trends['Release Year'] >= year_range[0]) & (genre_trends['Release Year'] <= year_range[1])]
    if selected_genres:
        filtered_data = filtered_data[filtered_data['Genre'].isin(selected_genres)]
    
    total_revenue = filtered_data.groupby('Genre')['Domestic Box Office (USD)'].sum().reset_index()
    
    fig = px.bar(
        total_revenue,
        x='Genre',
        y='Domestic Box Office (USD)',
        title=f'🎬 Total Domestic Box Office Revenue by Genre ({year_range[0]}-{year_range[1]})',
        labels={'Domestic Box Office (USD)': 'Revenue (USD)'},
        template='plotly_dark'
    )
    return fig

# Callback to summary table
@app.callback(
    [dash.Output('summary-table', 'data'),
     dash.Output('summary-table', 'columns'),
     dash.Output('summary-title', 'children')],  # New Output for Title
    [dash.Input('line-year-slider', 'value')]
)
def update_summary_table(year_range):
    filtered_data = genre_trends[
        (genre_trends['Release Year'] >= year_range[0]) & 
        (genre_trends['Release Year'] <= year_range[1])
    ]
    
    # Calculate Start and End Revenue for Selected Genres
    genre_revenue_start = filtered_data[filtered_data['Release Year'] == year_range[0]].groupby("Genre")["Domestic Box Office (USD)"].sum()
    genre_revenue_end = filtered_data[filtered_data['Release Year'] == year_range[1]].groupby("Genre")["Domestic Box Office (USD)"].sum()
    
    # Align the index to ensure both DataFrames have the same genres
    all_genres = genre_revenue_start.index.union(genre_revenue_end.index)
    genre_revenue_start = genre_revenue_start.reindex(all_genres, fill_value=0)
    genre_revenue_end = genre_revenue_end.reindex(all_genres, fill_value=0)
    
    # Merge Data & Calculate Percent Change
    summary_df = pd.DataFrame({
        "Genre": all_genres, 
        "Start Revenue": genre_revenue_start.values, 
        "End Revenue": genre_revenue_end.values
    })
    summary_df["Percent Change (%)"] = ((summary_df["End Revenue"] - summary_df["Start Revenue"]) / summary_df["Start Revenue"].replace(0, 1)) * 100
    
    # Format columns
    summary_df["Start Revenue"] = summary_df["Start Revenue"].apply(lambda x: f"{x:,.0f}")
    summary_df["End Revenue"] = summary_df["End Revenue"].apply(lambda x: f"{x:,.0f}")
    summary_df["Percent Change (%)"] = summary_df["Percent Change (%)"].apply(lambda x: f"{x:.2f}%")
    
    # Sort by Percent Change in Descending Order
    summary_df = summary_df.sort_values(by="Percent Change (%)", ascending=False, key=lambda col: col.str.rstrip('%').astype(float))

    # Dynamically update table title based on selected year range
    table_title = f"📊 Percent Change in Domestic Box Office Revenue by Genre ({year_range[0]} - {year_range[1]})"

    return summary_df.to_dict('records'), [{'name': col, 'id': col} for col in summary_df.columns], table_title

# Callback to summary table (yearly genre)
@app.callback(
    [dash.Output('yearly-summary-table', 'data'),
     dash.Output('yearly-summary-table', 'columns'),
     dash.Output('yearly-summary-title', 'children')],  # New Output for Dynamic Title
    [dash.Input('yearly-year-slider', 'value'),
     dash.Input('yearly-genre-dropdown', 'value')]  # Input from Yearly Genre Section
)
def update_yearly_summary_table(year_range, selected_genres):
    filtered_data = genre_trends[
        (genre_trends['Release Year'] >= year_range[0]) & 
        (genre_trends['Release Year'] <= year_range[1])
    ]
    
    # If genres are selected, filter by genre
    if selected_genres:
        filtered_data = filtered_data[filtered_data["Genre"].isin(selected_genres)]
    
    # Calculate Start and End Revenue for Selected Genres
    genre_revenue_start = filtered_data[filtered_data['Release Year'] == year_range[0]].groupby("Genre")["Domestic Box Office (USD)"].sum()
    genre_revenue_end = filtered_data[filtered_data['Release Year'] == year_range[1]].groupby("Genre")["Domestic Box Office (USD)"].sum()
    
    # Align the index to ensure both DataFrames have the same genres
    all_genres = genre_revenue_start.index.union(genre_revenue_end.index)
    genre_revenue_start = genre_revenue_start.reindex(all_genres, fill_value=0)
    genre_revenue_end = genre_revenue_end.reindex(all_genres, fill_value=0)
    
    # Merge Data & Calculate Percent Change
    summary_df = pd.DataFrame({
        "Genre": all_genres, 
        "Start Revenue": genre_revenue_start.values, 
        "End Revenue": genre_revenue_end.values
    })
    summary_df["Percent Change (%)"] = ((summary_df["End Revenue"] - summary_df["Start Revenue"]) / summary_df["Start Revenue"].replace(0, 1)) * 100
    
    # Format columns
    summary_df["Start Revenue"] = summary_df["Start Revenue"].apply(lambda x: f"{x:,.0f}")
    summary_df["End Revenue"] = summary_df["End Revenue"].apply(lambda x: f"{x:,.0f}")
    summary_df["Percent Change (%)"] = summary_df["Percent Change (%)"].apply(lambda x: f"{x:.2f}%")
    
    # Sort by Percent Change in Descending Order
    summary_df = summary_df.sort_values(by="Percent Change (%)", ascending=False, key=lambda col: col.str.rstrip('%').astype(float))

    # Dynamically update table title based on selected year range
    table_title = f"📊 Percent Change in Domestic Box Office Revenue by Genre ({year_range[0]} - {year_range[1]})"

    return summary_df.to_dict('records'), [{'name': col, 'id': col} for col in summary_df.columns], table_title


# Run the app
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True, port=8051)

