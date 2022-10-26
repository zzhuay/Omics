import colorlover as cl
import plotly.graph_objs as go
import numpy as np
from sklearn import metrics
import pandas as pd
import matplotlib.pyplot as plt

def colorfun(x, t):
    if x>t:
        return 'lightblue'
    else:
        return '#ff8989'

def serve_prediction_plot(df, threshold):

    # Colorscale
    bright_cscale = [[0, "#ff3700"], [1, "#0b8bff"]]
    cscale = [
        [0.0000000, "#ff744c"],
        [0.1428571, "#ff916d"],
        [0.2857143, "#ffc0a8"],
        [0.4285714, "#ffe7dc"],
        [0.5714286, "#e5fcff"],
        [0.7142857, "#c8feff"],
        [0.8571429, "#9af8ff"],
        [1.0000000, "#20e6ff"],
    ]
    df = df.sort_values('Pr')
    # Plot Test Data
    trace4 = go.Bar(
        
        x=df.index,
        y=df['Pr'],
        # color=['red' for j in range(1,750)],
        # mode="markers",
        marker=dict(
            color=[colorfun(j, threshold) for j in df['Pr']]
        ),
    )

    layout = go.Layout(
        title="Pr(Response)",
        xaxis=dict(ticks="", showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(ticks="", showticklabels=True, showgrid=True, zeroline=True),
        hovermode="closest",
        legend=dict(x=0, y=-0.01, orientation="h"),
        # margin=dict(l=0, r=0, t=0, b=0),
        margin=dict(l=10, r=50, t=50, b=75),
        plot_bgcolor="#f0f0f0",
        paper_bgcolor="#ffffff",
        font={"color": "#666666", 'family':'Helvetica'},
    )

    # data = [trace0, trace1, trace2, trace3]
    data = [trace4]
    figure = go.Figure(data=data, layout=layout)

    return figure

    
def plot_two_group(df, threshold):
    from lifelines import KaplanMeierFitter
    kmf = KaplanMeierFitter()
    from lifelines.statistics import logrank_test

    df['y'] = 1*(df['Pr'] > threshold)
    df = df.dropna(subset=['DFS_MONTHS','DFS_STATUS','y'])
    # df = df.loc[df['DFS_MONTHS']!='[Not Available]']
    fig, ax = plt.subplots(figsize=[4,4])

    if df[df['y']==1].shape[0] >= 1:
        kmf.fit(df[df['y']==1]['DFS_MONTHS'].astype(float), \
                event_observed=df[df['y']==1]['DFS_STATUS'], \
                label="pCR (N=%s)"%len(df[df['y']==1]['DFS_MONTHS']))
        kmf.plot(ax=ax, linewidth=2, color='lightblue', ci_show=False, show_censors=True)

    if df[df['y']==0].shape[0] >= 1:
        kmf.fit(df[df['y']==0]['DFS_MONTHS'].astype(float), \
                event_observed=df[df['y']==0]['DFS_STATUS'], \
                label="RD (N=%s)"%len(df[df['y']==0]['DFS_MONTHS']))
        kmf.plot(ax=ax, linewidth=2, color='#ff7878', ci_show=False, show_censors=True)


def serve_pie_confusion_matrix(df, threshold):
    
    if 'DFS_MONTHS' in set(df.columns):
        import plotly.tools as tls

        plot_two_group(df, threshold)
        kmf1 = plt.gcf()
        trace0 = tls.mpl_to_plotly(kmf1, resize=True)
        
        df['y'] = 1*(df['Pr'] > threshold)
        df = df.dropna(subset=['DFS_MONTHS','DFS_STATUS','y'])
        # df = df.loc[df['DFS_MONTHS']!='[Not Available]']
        
        try:
            from lifelines.statistics import logrank_test
            results = logrank_test(\
                                   durations_A=df[df['y']==0]['DFS_MONTHS'].astype(float), \
                                   durations_B=df[df['y']==1]['DFS_MONTHS'].astype(float), \
                                   event_observed_A=df[df['y']==0]['DFS_STATUS'], \
                                   event_observed_B=df[df['y']==1]['DFS_STATUS'])
            pval = str(results.p_value)
        except:
            pval = 'NA'
        

        layout = go.Layout(
            title="Disease Free Survival",
            yaxis_title="Probability",
            xaxis_title="Months",
            margin=dict(l=50, r=50, t=75, b=120),
            legend=dict(bgcolor="#ffffff", font={"color": "#666666", "family": "Helvetica"}, orientation="v"),
            plot_bgcolor="#f0f0f0",
            paper_bgcolor="#ffffff",
            font={"color": "#666666", 'family':'Helvetica'},
        )

        if len(trace0['data']) > 2:
            trace0['data'][0]['name'] = ''
            trace0['data'][2]['name'] = ''
            data = [trace0['data'][0], trace0['data'][1], trace0['data'][2], trace0['data'][3]]
            figure = go.Figure(data=data, layout=layout)
            
            anno_xpos = max(max(trace0['data'][0]['x']), max(trace0['data'][2]['x']))/2
            
            figure.add_annotation(x=anno_xpos, y=1, text="P = "+str(pval), showarrow=False, yshift=10)
            
            # figure.update_layout(showlegend=False)
        else:
            trace0['data'][0]['name'] = ''
            data = [trace0['data'][0], trace0['data'][1]]
            figure = go.Figure(data=data, layout=layout)
            
            anno_xpos = max(trace0['data'][0]['x'])/2
            
            figure.add_annotation(x=anno_xpos, y=1, text="P = "+str(pval), showarrow=False, yshift=10)
            # figure.update_layout(showlegend=False)

        return figure
    
    else:
        y = df['Pr']

        values = [(y>threshold).sum(), (y<=threshold).sum()]
        label_text = ["Response", "Residual"]
        labels = ["pCR", "RD"]
        blue = cl.flipper()["seq"]["9"]["Blues"]
        red = cl.flipper()["seq"]["9"]["Reds"]
        colors = ["lightblue", "#ff7878"]

        trace0 = go.Pie(
            labels=label_text,
            values=values,
            hoverinfo="label+value+percent",
            textinfo="text+value",
            text=labels,
            sort=False,
            marker=dict(colors=colors),
            insidetextfont={"color": "white"},
            rotation=90,
        )

        layout = go.Layout(
            title="Distribution",
            margin=dict(l=50, r=50, t=75, b=120),
            legend=dict(bgcolor="#ffffff", font={"color": "#666666", "family": "Helvetica"}, orientation="h"),
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font={"color": "#666666", 'family':'Helvetica'},
        )

        data = [trace0]
        figure = go.Figure(data=data, layout=layout)

        return figure