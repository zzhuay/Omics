from textwrap import dedent

import dash_core_components as dcc
import dash_html_components as html

import dash_uploader as du
import uuid
from flask import request
import time 

# Display utility functions
def _merge(a, b):
    return dict(a, **b)


def _omit(omitted_keys, d):
    return {k: v for k, v in d.items() if k not in omitted_keys}


# Custom Display Components
def Card(children, **kwargs):
    return html.Section(className="card", children=children, **_omit(["style"], kwargs))


def FormattedSlider(**kwargs):
    return html.Div(
        style=kwargs.get("style", {}), children=dcc.Slider(**_omit(["style"], kwargs))
    )

def NamedDropdown(name, **kwargs):
    return html.Div(
        style={"margin": "10px 0px"},
        children=[
            html.P(children=f"{name}:", style={"margin-left": "6px"}),
            dcc.Dropdown(**kwargs),
        ],
    )


def NamedRadioItems(name, **kwargs):
    return html.Div(
        style={"padding": "20px 10px 25px 4px"},
        children=[html.P(children=f"{name}:"), dcc.RadioItems(**kwargs)],
    )


def NamedSlider(name, **kwargs):
    return html.Div(
        style={"padding": "0px 10px 10px 0px"},
        children=[
            html.P(f"{name}:"),
            dcc.Slider(**kwargs),

        ],
    )


def NamedUpload(name, **kwargs):
    return html.Div(
        style={"padding": "2px 10px 5px 4px", },
        children=[html.P(children=f"{name}:"), 
                  du.Upload(**kwargs, \
                            max_files=1, \
                            default_style={'minHeight': 1, 'lineHeight': 1}),
                 ],
    )


def NamedDownload(name, **kwargs):
    return html.Div(
        style={"padding": "0px 10px 10px 4px", },
        children=[html.P(dcc.Download(**kwargs))],
    )


# Non-generic
def DemoDescription(filename, strip=False):
    with open(filename, "r") as file:
        text = file.read()

    if strip:
        text = text.split("<Start Description>")[-1]
        text = text.split("<End Description>")[0]

    return html.Div(
        className="row",
        style={
            "padding": "15px 30px 27px",
            "margin": "45px auto 45px",
            "width": "80%",
            "max-width": "1024px",
            "borderRadius": 5,
            "border": "thin lightgrey solid",
            "font-family": "Roboto, sans-serif",
        },
        children=dcc.Markdown(dedent(text)),
    )