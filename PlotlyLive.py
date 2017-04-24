import plotly as py
import plotly.graph_objs as go
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed
from IPython.core.display import HTML
from IPython.display import display, clear_output
from plotly.widgets import GraphWidget

import pandas as pd
import numpy as np

import os
import sys

styles = '''<style>.widget-hslider {width: 100%;}
    .widget-hbox {width: 100% !important;}
    .widget-slider {width: 100% !important;}</style>'''

HTML(styles)

def graph():
    dots = go.Scatter(
        x=[1,2,3],
        y=[3,1,2],
    )
    layout = go.Layout(
        xaxis={'title': 'time'},
        yaxis={'title': 'result'},
    )
    fig = go.Figure(data=[dots], layout=layout)
    url = py.offline.plot(fig)
    return url


def main():
    url = graph()
    print(url)
    graph = GraphWidget(url)

    graph.add_traces(go.Scatter(x=[2,3,4], y=[4,1,2]))

if __name__ == '__main__':
    main()
    sys.exit()
