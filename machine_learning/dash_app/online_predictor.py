import time
import importlib

import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
from dash.dependencies import Input, Output, State
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn import datasets
from sklearn.svm import SVC

import utils.dash_reusable_components as drc
import utils.figures as figs
import pandas as pd
import base64
import io
from flask import request
import time
import os


import dash_uploader as du
import uuid

import utils.models as models

VALID_USERNAME_PASSWORD_PAIRS = {
    'user1': '123',
    'user2': '1234'
}

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

du.configure_upload(app, "/home/zzhuay/brca/uploaded/")


# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )

app.title = "BRCA"
server = app.server

def get_app_layout():
    print(uuid.uuid1())
    return html.Div(
        children = [
            # .container class is fixed, .container.scalable is scalable
            html.Div(
                className="banner",
                children=[
                    # Change App Name here
                    html.Div(
                        className="container scalable",
                        children=[
                            # Change App Name here
                            html.H2(
                                id="banner-title",
                                children=[
                                    html.A(
                                        "Response Predictor",
                                        href="https://wang-lab.hkust.edu.hk/software/Software.html",
                                        style={
                                            "text-decoration": "none",
                                            "color": "inherit",
                                        },
                                    )
                                ],
                            ),
                            html.A(
                                id="banner-logo",
                                children=[
                                    html.Img(src=app.get_asset_url("wanglab_logo.jpeg"))
                                ],
                                href="https://wang-lab.hkust.edu.hk/",
                            ),
                        ],
                    )
                ],
            ),
            html.Div(
                id="body",
                className="container scalable",
                children=[
                    html.Div(
                        id="app-container",
                        children=[
                            html.Div(
                                id="left-column",
                                children=[
                                    drc.Card(
                                        id="first-card",
                                        children=[
                                            drc.NamedDropdown(
                                                name="HER2 status",
                                                id="dropdown-select-her2",
                                                options=[
                                                    {"label": "Positive", "value": "P"},
                                                    {"label": "Negative", "value": "N"},
                                                    {"label": "NA", "value": "U"},
                                                ],
                                                clearable=False,
                                                searchable=False,
                                            ),
                                            drc.NamedDropdown(
                                                name="ER status",
                                                id="dropdown-select-er",
                                                options=[
                                                    {"label": "Positive", "value": "P"},
                                                    {"label": "Negative", "value": "N"},
                                                    {"label": "NA", "value": "U"},
                                                ],
                                                clearable=False,
                                                searchable=False,
                                            ),

                                            drc.NamedUpload(
                                                name="Upload Clinical Dataset (Required)",
                                                id="upload-clin-dataset",
                                            ),
                                            drc.NamedUpload(
                                                name="Upload Methylation Dataset",
                                                id="upload-meth-dataset",
                                            ),
                                            drc.NamedUpload(
                                                name="Upload RNA (TPM) Dataset",
                                                id="upload-rna-dataset",
                                            ),
                                            drc.NamedUpload(
                                                name="Upload Protein Dataset",
                                                id="upload-prot-dataset",
                                            ),
                                            drc.NamedUpload(
                                                name="Upload Phosphoprotein Dataset",
                                                id="upload-pp-dataset",
                                            ),
                                        ],
                                    ),

                                    drc.Card(
                                        children=[
                                            html.Button("Get Prediction", id="download_csv"),
                                            drc.NamedDownload(
                                                name="Download Dataset",
                                                id="download-dataframe-csv",
                                            ),
                                            drc.NamedSlider(
                                                name="Cutoff",
                                                id="slider-threshold",
                                                min=0,
                                                max=1,
                                                value=0.5,
                                                step=0.01,
                                            ),
                                            html.Button(
                                                "Reset",
                                                id="button-zero-threshold",
                                            ),
                                        ],
                                    ),

                                    html.Div(id='callback-clin-output'),
                                    html.Div(id='callback-meth-output'),
                                    html.Div(id='callback-rna-output'),
                                    html.Div(id='callback-prot-output'),
                                    html.Div(id='callback-pp-output'),

                                ],
                            ),

                            html.Div(
                                id="div-graphs",
                                children=[
                                    dcc.Graph(
                                    id="graph-sklearn-svm",
                                    figure=dict(
                                        layout=dict(
                                            plot_bgcolor="#282b38", paper_bgcolor="#282b38"
                                            )
                                        ),
                                    ),
                                ]
                            ),
                        ],
                    )
                ],
            ),
        ]
    )

# get_app_layout is a function
# This way we can use unique session id's as upload_id's
app.layout = get_app_layout

@du.callback(
    output=Output("callback-clin-output", "children"),
    id="upload-clin-dataset",
)
def callback_clin_on_completion(status: du.UploadStatus):
    return html.Ul([html.Li(str(x)) for x in status.uploaded_files], hidden=True)

@du.callback(
    output=Output("callback-meth-output", "children"),
    id="upload-meth-dataset",
)
def callback_meth_on_completion(status: du.UploadStatus):
    return html.Ul([html.Li(str(x)) for x in status.uploaded_files], hidden=True)

@du.callback(
    output=Output("callback-rna-output", "children"),
    id="upload-rna-dataset",
)
def callback_rna_on_completion(status: du.UploadStatus):
    return html.Ul([html.Li(str(x)) for x in status.uploaded_files], hidden=True)

@du.callback(
    output=Output("callback-prot-output", "children"),
    id="upload-prot-dataset",
)
def callback_prot_on_completion(status: du.UploadStatus):
    return html.Ul([html.Li(str(x)) for x in status.uploaded_files], hidden=True)

@du.callback(
    output=Output("callback-pp-output", "children"),
    id="upload-pp-dataset",
)
def callback_pp_on_completion(status: du.UploadStatus):
    return html.Ul([html.Li(str(x)) for x in status.uploaded_files], hidden=True)


@app.callback(
    Output("slider-threshold", "value"),
    [
        Input("button-zero-threshold", "n_clicks"),
    ],
    [State("graph-sklearn-svm", "figure")],
    prevent_initial_call=True,
)
def reset_threshold_center(set_zero,
                           figure):
    return 0.5

@app.callback(
    Output("download-dataframe-csv", "data"),
    [
        Input("dropdown-select-her2", "value"),
        Input("dropdown-select-er", "value"),
        Input("callback-clin-output", "children"),
        Input("callback-meth-output", "children"),
        Input("callback-rna-output", "children"),
        Input("callback-prot-output", "children"),
        Input("callback-pp-output", "children"),
        Input("download_csv", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def predict(
    her2,
    er,
    file_clin, 
    file_meth,
    file_rna,
    file_prot,
    file_pp,
    n_download, 
):
    if n_download is not None:
        if dash.callback_context.triggered[-1]['prop_id'] == 'download_csv.n_clicks':
            df_tmp = models.predict(
                her2,
                er,
                file_clin,
                file_meth,
                file_rna,
                file_prot,
                file_pp,
            )
            return dcc.send_data_frame(df_tmp.to_csv, \
                                       file_clin['props']['children'][0]['props']['children'].split('/')[-1]+her2+er+".prediction.csv")

        
        
@app.callback(
    Output("div-graphs", "children"),
    [
        Input("dropdown-select-her2", "value"),
        Input("dropdown-select-er", "value"),
        Input("callback-clin-output", "children"),
        Input("slider-threshold", "value"),
        Input("download_csv", "n_clicks"),
    ],
)
def update_output(
    her2,
    er,
    file_clin,
    threshold,
    n_download, 
):
        
    if file_clin is not None:
        print(file_clin['props']['children'][0]['props']['children'])
        file_pred = file_clin['props']['children'][0]['props']['children']+her2+er+'.prediction.csv'
    
    if dash.callback_context.triggered[-1]['prop_id'] == 'download_csv.n_clicks':
        while True:
            try:
                time.sleep(0.1)
                df = pd.read_csv(file_pred, index_col=0)
                break
            except:
                time.sleep(0.1)
    else:
        try:
            df = pd.read_csv(file_pred, index_col=0)
        except:
            df = pd.DataFrame({'Pr':[]})
    
    prediction_figure = figs.serve_prediction_plot(
        df=df,
        threshold=threshold,
    )

    confusion_figure = figs.serve_pie_confusion_matrix(
        df=df,
        threshold=threshold,
    )
    
    return [
        html.Div(
            id="svm-graph-container",
            children=[
                html.H6('Readme:'), 
                html.P('1. For academic use only.'),
                html.P('2. Please use comma-seperated table.'),
                html.P('3. Please include sample ID in the first columns, and gene names as column names.'),
                html.P('4. Please include feature XXX in the clinical table.'),
                html.P('5. Reload this page will reset all dataset.'),
                dcc.Loading(
                className="graph-wrapper",
                children=dcc.Graph(id="graph-sklearn-svm", figure=prediction_figure),
                style={"display": "none"},
                ),
            ],
        ),
        html.Div(
            id="graphs-container",
            children=[
                html.H6(' '), 
                html.P(' '),
                html.P(' '),
                html.P(' '),
                html.P(' '),
                html.P(' '),
                html.P(' '),
                html.P(' '),
                html.P(' '),
                html.P(' '),
                html.P(' '),
                dcc.Loading(
                    className="graph-wrapper",
                    children=dcc.Graph(
                        id="graph-pie-confusion-matrix", figure=confusion_figure
                    ),
                ),
            ],
        ),
    ]



# Running the server
if __name__ == "__main__":
    # app.run_server(debug=True)
    # app.run_server(host='0.0.0.0', debug=True)
    app.run_server(host='0.0.0.0', debug=False)