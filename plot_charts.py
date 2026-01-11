from scipy.stats import linregress
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates
from scipy.stats import linregress
import os

# Function to read and process data from JSON
def read_and_process_data(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Process 'daily_kcal'
    daily_kcal_data = data.get('daily_kcal', {})
    df_daily_kcal = pd.DataFrame.from_dict(daily_kcal_data, orient='index')
    df_daily_kcal['Date'] = pd.to_datetime(df_daily_kcal['Date'])
    df_daily_kcal = df_daily_kcal.sort_values(by='Date')

    # Process 'daily_mass_waist'
    daily_mass_waist_data = data.get('daily_mass_waist', {})
    df_daily_mass_waist = pd.DataFrame.from_dict(daily_mass_waist_data, orient='index')
    df_daily_mass_waist['Date'] = pd.to_datetime(df_daily_mass_waist['Date'])
    df_daily_mass_waist = df_daily_mass_waist.sort_values(by='Date')

    return df_daily_kcal, df_daily_mass_waist

def calculate_ema(df, column, span=7):
    ema_values = []
    ema = np.nan  # Initialize EMA as NaN

    for index, row in df.iterrows():
        if pd.isna(row[column]) or row[column] == 0:
            # If net_kcal is NaN or 0, set EMA to NaN
            ema = np.nan
        else:
            if pd.isna(ema):
                # If previous EMA is NaN, set EMA to current net_kcal
                ema = row[column]
            else:
                # Calculate EMA normally
                alpha = 2 / (span + 1)
                ema = ema + alpha * (row[column] - ema)

        ema_values.append(ema)

    return pd.Series(ema_values, index=df.index)

def plot_mass_and_fat(df, show_charts):
    # Filter relevant data
    mass_df = df.dropna(subset=['Mass'])
    fat_df = df.dropna(subset=['Navy_fat'])

    # Create a subplot with 2 y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Plot Mass (KG) with trend line
    fig.add_trace(
        go.Scatter(
            x=mass_df['Date'],
            y=mass_df['Mass'],
            mode='lines+markers',
            name='Mass (KG)',
            marker=dict(
                color='#008837',
                size=10,
                line=dict(
                    color='lightgrey',
                    width=1
                )
            ),
            line=dict(
                color='#a6dba0',
                width=4
            )
        ),
        secondary_y=False
    )

    # Linear trend line for Mass
    slope, intercept, _, _, _ = linregress(mass_df['Date'].astype('int64'), mass_df['Mass'])
    extended_dates = pd.date_range(start=mass_df['Date'].min(), end=pd.Timestamp('2027-11-08'))
    trend_line_mass = slope * extended_dates.astype('int64') + intercept
    fig.add_trace(
        go.Scatter(
            x=extended_dates,
            y=trend_line_mass,
            mode='lines',
            name='Mass Trend',
            line=dict(
                color='#008837',
                width=1,
                dash='dash'
            )
        ),
        secondary_y=False
    )

    # Add goal line with milestone at 100kg
    fig.add_trace(
        go.Scatter(
            x=['2026-01-01', '2026-06-25', '2026-11-15'],
            y=[117, 100, 86],
            mode='lines+markers',
            name='Goal',
            line=dict(
                color='#f7f7f7',
                width=2,
                dash='dash'
            ),
            marker=dict(
                size=[6, 10, 6],  # Larger marker at 100kg milestone
                color='#f7f7f7'
            )
        ),
        secondary_y=False
    )

    # Plot Navy Fat % with trend line
    fig.add_trace(
        go.Scatter(
            x=fat_df['Date'],
            y=fat_df['Navy_fat'],
            mode='lines+markers',
            name='Body Fat %',
            marker=dict(
                color='#7b3294',
                size=10,
                line=dict(
                    color='lightgrey',
                    width=2
                )
            ),
            line=dict(
                color='#c2a5cf',
                width=4
            )

        ),
        secondary_y=True
    )

    # Linear trend line for Navy Fat
    slope, intercept, _, _, _ = linregress(fat_df['Date'].astype('int64'), fat_df['Navy_fat'])
    trend_line_fat = slope * extended_dates.astype('int64') + intercept
    fig.add_trace(
        go.Scatter(
            x=extended_dates,
            y=trend_line_fat,
            mode='lines',
            name='Fat Trend',
            line=dict(
                color='#c2a5cf',
                width=2,
                dash='dash'
            )
        ),
        secondary_y=True
    )

    # Customize the layout
    fig.update_layout(
        title=dict(text='Mass and Body Fat Percentage Over Time', x=0.5),
        title_font=dict(size=40, family='Arial', color='grey'),  # Customize title font here
        plot_bgcolor='#343434',
        paper_bgcolor='#343434',
        xaxis=dict(
            title='Date',
            range=['2026-01-01', '2026-11-15'],
            tickangle=-90,
            tickformat='%d/%m/%Y',
            tickmode='linear',
            tickfont=dict(color='grey',size=18, family='Arial'),
            title_font=dict(color='grey',size=22, family='Arial'),  # Customize x-axis title font here
            dtick=604800000.0,
            showgrid=True,
            gridcolor='grey',
            gridwidth=1,
        ),
        yaxis=dict(
            title='Mass (KG)',
            title_font=dict(color='grey', size=22, family='Arial'),  # Customize y-axis title font here
            tickfont=dict(color='grey', size=18, family='Arial'),  # Customize y-axis tick labels font here
            range=[117, 135],
            dtick=1,
            tickmode='linear',
            showgrid=True,
            gridcolor='grey'
        ),
        yaxis2=dict(
            title='Body Fat (%)',
            title_font=dict(color='grey', size=22, family='Arial'),  # Customize y-axis title font here
            tickfont=dict(color='grey', size=18, family='Arial'),  # Customize y-axis tick labels font here
            range=[30, 39],
            dtick=0.5,
            tickmode='linear',
            showgrid=True,
            gridcolor='grey'
        ),
        legend=dict(font=dict(color='grey')),
        showlegend=True,
        width = 1990,
        height = 1000
    )

    # Show the plot
    if show_charts:
        fig.show()
    # Export the plot to an HTML file
    html_file = 'liam_mass_fat_plot.html'
    fig.write_html(html_file)

    # Save the plot as a PNG file
    png_file = 'liam_mass_fat_plot.png'
    fig.write_image(png_file)

# Function to plot calorie data
def plot_calorie_data(df, show_charts):
    # Filter relevant data for calorie plot
    calorie_df = df[['Date', 'Breakfast', 'Lunch', 'Dinner', 'Snacks', 'Drinks', 'Exercise', '7-day_EMA', 'net_kcal']]
    calorie_df = calorie_df.fillna(0)
    calorie_df = calorie_df.sort_values(by='Date')

    # Initialize columns for start points of each category
    categories = ['Breakfast', 'Lunch', 'Dinner', 'Snacks', 'Drinks']
    for cat in categories:
        calorie_df[cat + '_start'] = 0

    # Calculate start points for each bar
    for index, row in calorie_df.iterrows():
        exercise = row['Exercise']
        start_point = -exercise
        for cat in categories:
            calorie_df.at[index, cat + '_start'] = start_point
            start_point += row[cat]

    # Create the figure
    fig = go.Figure()

    # Define the color scheme
    color_scheme = {
        'Breakfast': '#1b7837',
        'Lunch': '#f7f7f7',
        'Dinner': '#e7d4e8',
        'Snacks': '#af8dc3',
        'Drinks': '#762a83'
    }

    # Define the border color and width
    border_color = 'grey'  # or any other color you prefer
    border_width = 0  # width of the border in pixels

    # Add bars for each category with the specified colors and borders
    for cat in categories:
        fig.add_trace(go.Bar(
            x=calorie_df['Date'],
            y=calorie_df[cat],
            base=calorie_df[cat + '_start'],
            name=cat,
            marker=dict(
                color=color_scheme[cat],  # Set the color for each category
                line=dict(
                    color=border_color,
                    width=border_width)  # Set the border color and width
            )
        ))

    # Add the 7-day EMA line
    fig.add_trace(go.Scatter(
        x=calorie_df['Date'],
        y=calorie_df['7-day_EMA'],
        mode='lines',
        name='7-day EMA',
        line=dict(
            color='#008837',
            width=3)
    ))

    # Add a horizontal red bar at 1500
    fig.add_hline(y=1500, line=dict(color='red', width=3))

    # Customize the layout
    fig.update_layout(
        title=dict(text='Daily Calorie Intake and Exercise', x=0.5),  # Center the title
        title_font=dict(size=40, family='Arial'),  # Customize title font here
        xaxis_title='Date',
        yaxis_title='Caloric Intake / Burn',
        barmode='relative',
        plot_bgcolor='#343434',
        paper_bgcolor='#343434',
        font=dict(color='grey'),
        xaxis=dict(
            range=['2026-01-01', '2026-11-15'],
            tickangle=-90,
            tickformat='%d/%m/%Y',
            tickmode='linear',
            dtick=604800000.0,
            showgrid=True,
            gridcolor='grey',
            gridwidth=1,
            title_font=dict(size=22, family='Arial'),  # Customize x-axis title font here
            tickfont=dict(size=18, family='Arial'),  # Customize x-axis tick labels font here
        ),
        yaxis=dict(
            range=[-1500, 3500],
            tickmode='linear',
            dtick=500,
            showgrid=True,
            gridcolor='grey',
            title_font=dict(size=22, family='Arial'),  # Customize y-axis title font here
            tickfont=dict(size=18, family='Arial'),  # Customize y-axis tick labels font here
        ),
        width=1900,
        height=1000
    )
    # Show the plot
    if show_charts:
        fig.show()
    # Export the plot to an HTML file
    html_file = 'liam_kcal_plot.html'
    fig.write_html(html_file)

    # Save the plot as a PNG file
    png_file = 'liam_kcal_plot.png'
    fig.write_image(png_file)

def create_charts(show_charts):
    # Get data file path from environment variables
    json_file = os.getenv('DATA_FILE', 'daily_data.json')
    print(f"[create_charts] Using data file: {json_file}")

    # Process and plot the data
    df_kcal, df_mass_waist_navy = read_and_process_data(json_file)

    df_kcal['7-day_EMA'] = calculate_ema(df_kcal, 'net_kcal')

    # Plot the Mass and Fat data
    plot_mass_and_fat(df_mass_waist_navy, show_charts)

    # Plot the Calorie data
    plot_calorie_data(df_kcal, show_charts)

if __name__ == "__main__":
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("[plot_charts] Loaded environment variables from .env file")
    except ImportError:
        print("[plot_charts] python-dotenv not installed, using system environment variables only")
    except Exception as e:
        print(f"[plot_charts] Warning: Could not load .env file: {e}")

    create_charts(show_charts = True)
