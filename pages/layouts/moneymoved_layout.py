from dash import html, dcc
import dash_bootstrap_components as dbc

import dash_draggable

from utils.data_preparer import DataPreparer
from utils.data_loader import data_loader

data_preparer = DataPreparer()

unique_fy = data_preparer.get_col_unique_values(
    "merged", "payment_date_fy", sort_desc=True
)

unique_platforms = data_preparer.get_col_unique_values("merged", "payment_platform")
unique_chapter_types = data_preparer.get_col_unique_values(
    "merged", "pledge_chapter_type"
)

last_payment_date = data_preparer.get_column_max_value("payments", "payment_date")

drilldown_by = [
    {"label": "Payment Platform", "value": "payment_platform"},
    {"label": "Source (Chapter Types)", "value": "pledge_chapter_type"},
]

attrition_drilldown_by = [
    # {"label": "Frequency", "value": "pledge_frequency"},
    {"label": "Payment Platform", "value": "pledge_payment_platform"},
    {"label": "Source (Chapter Types)", "value": "pledge_chapter_type"},
]

# One for the World color palette
colors = {
    "primary": "#006466",  # Teal/blue-green
    "secondary": "#065A60",  # Darker teal
    "accent": "#0B525B",  # Another shade
    "light": "#144552",  # Lighter shade
    "text": "#1B3A4B",  # For text
    "highlight": "#F2F2F2",  # Light highlight
    "white": "#FFFFFF",
}

# default_data = data_loader.get_default_target_data()

labels = {
    "money_moved": "Money Moved ($M)",
    "counterfactual_mm": "Counterfactual MM ($M)",
    "active_arr": "Active ARR Run Rate ($M)",
    "pledge_attrition": "Pledge Attrition Rate (%)",
    "active_donors": "Total number of active donors",
    "active_pledges": "Total number of active pledges",
    "chapter_arr": "Chapter ARR ($)",
    "all_pledges": "All Pledges (active + future)",
    "future_pledges": "Future Pledges",
    "future_arr": "Future ARR ($)"
}

fiscal_year_options = list(range(2025, 2046))

# # Read the HTML file content
# with open("./about.html", "r") as f:
#     about_content = f.read()

def chart_header_title_with_ai(chart_id, title):
    component = html.Div(
        className="d-flex justify-content-between align-items-center w-100",
        children=[
            dcc.Store(
                id="ai-message-store",
                data=[],
            ),
            # dcc.Store(id="chart-figure-store"),
            dbc.Row(
                class_name="d-flex justify-content-between align-items-center w-100",
                children=[
                    dbc.Col(html.H6(title, className="mb-0"), width="auto"),
                    dbc.Col(
                        html.Div(
                            html.I(
                                children=[
                                    html.Span(
                                        className="ripple",
                                    ),  # Add your desired content inside the span
                                ],
                                className="bi bi-magic position-relative",
                                id={"type": "ai-icon", "chart": chart_id},
                                style={
                                    "cursor": "pointer",
                                    "fontSize": "1.3rem",
                                    "color": "#065A60",
                                },
                            ),
                            style={"textAlign": "right"},
                        ),
                        width="auto",
                    ),
                ],
                justify="between",
                align="center",
                className="mb-2",
            ),
            dbc.Tooltip(
                "Click here for Actionable Insights (AI)",
                target={"type": "ai-icon", "chart": chart_id},
                placement="top",
            ),
        ],
    )

    return component


def moneymoved_layout():
    return html.Div(
        children=[
            html.Div(
                className="layout-navbar-fixed layout-menu-fixed layout-wide",
                dir="ltr",
                children=[
                    html.Div(
                        className="layout-wrapper layout-navbar-full layout-horizontal layout-without-menu",
                        children=[
                            html.Div(
                                className="layout-container",
                                children=[
                                    html.Div(
                                        className="layout-page",
                                        children=[
                                            # Content Wrapper
                                            html.Div(
                                                className="content-wrapper",
                                                children=[
                                                    html.Header(
                                                        id="main-header",
                                                        children=[
                                                            html.Div(
                                                                html.Img(
                                                                    src="../../assets/img/illustrations/one_of_the_world_logo.png",
                                                                    height="55",
                                                                    className="scaleX-n1-rtl logotext",
                                                                    alt="View Badge User",
                                                                ),
                                                                className="logo oftw",
                                                            ),
                                                        ],
                                                    ),
                                                    html.Div(
                                                        className="container-fluid flex-grow-1 container-p-y p-top-custom",
                                                        children=[
                                                            # -- Filters --
                                                            html.Div(
                                                                className="col-xxl-12 col-lg-12 col-md-12 order-1 mt-1 mb-1",
                                                                children=[
                                                                    html.Div(
                                                                        className="row",
                                                                        children=[
                                                                            html.Div(
                                                                                className="col-lg-4 col-md-4",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="card h-100",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="card-body",
                                                                                                children=[
                                                                                                    html.Span(
                                                                                                        "Select FY",
                                                                                                        className="d-block fw-medium mb-1",
                                                                                                    ),
                                                                                                    dcc.Dropdown(
                                                                                                        id="fy-filter",
                                                                                                        options=[
                                                                                                            dict(
                                                                                                                label=fy,
                                                                                                                value=fy,
                                                                                                            )
                                                                                                            for fy in unique_fy
                                                                                                        ],
                                                                                                        placeholder="Select FY",
                                                                                                        multi=False,
                                                                                                        value=unique_fy[
                                                                                                            0
                                                                                                        ],
                                                                                                        clearable=False,
                                                                                                    ),
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                            ),
                                                                            html.Div(
                                                                                className="col-lg-1 col-md-1 ",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="card h-100",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="card-body ",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="d-flex justify-content-end mt-3",
                                                                                                        children=[
                                                                                                            dbc.Button(
                                                                                                                "Set Target",
                                                                                                                id="set-target-button",
                                                                                                                color="primary",
                                                                                                                className="me-2",
                                                                                                                n_clicks=0,
                                                                                                            ),
                                                                                                            dbc.Modal(
                                                                                                                [
                                                                                                                    dbc.ModalHeader(dbc.ModalTitle("Edit Targets")),
                                                                                                                    dbc.ModalBody([
                                                                                                                        dcc.Dropdown(
                                                                                                                            id="target-form-fy-dropdown",
                                                                                                                            options=[{"label": str(yr-1) + '-' + str(yr), "value": yr} for yr in fiscal_year_options],
                                                                                                                            placeholder="Select Fiscal Year",
                                                                                                                            style={"width": "200px", "marginRight": "10px"}
                                                                                                                        ),
                                                                                                                        # dbc.Button("Edit Targets", id="edit-btn", n_clicks=0,),
                                                                                                                        html.Div(id="target-form"),
                                                                                                                        # create_form()
                                                                                                                    ]),
                                                                                                                    dbc.ModalFooter(
                                                                                                                        dbc.Button("Done", id="done-target-form-button", className="ms-auto", n_clicks=0)
                                                                                                                    ),
                                                                                                                ],
                                                                                                                id="target-form-modal",
                                                                                                                is_open=False,
                                                                                                            ),
                                                                                                            dcc.Store(id='target-form-data-store', data=data_loader.get_default_target_data()),
                                                                                                        ],
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                            ),
                                                                            html.Div(
                                                                                className="col-lg-1 col-md-1 ",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="card h-100",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="card-body ",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="d-flex justify-content-end mt-3",
                                                                                                        children=[
                                                                                                            html.Span(
                                                                                                                "Amounts are in USD",
                                                                                                                className="d-block fw-medium mb-1",
                                                                                                            ),
                                                                                                        ],
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                            ),
                                                                            html.Div(
                                                                                className="col-lg-1 col-md-1 ",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="card h-100",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="card-body ",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="d-flex justify-content-end mt-3",
                                                                                                        children=[
                                                                                                            html.Span(
                                                                                                                f"Payment Data Up to {last_payment_date:%dth %b, %Y}",
                                                                                                                className="d-block fw-medium mb-1",
                                                                                                            ),
                                                                                                        ],
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                            ),
                                                                            # html.Div(
                                                                            #     className="col-lg-4 col-md-4 ",
                                                                            #     children=[
                                                                            #         html.Div(
                                                                            #             className="card h-100",
                                                                            #             children=[
                                                                            #                 html.Div(
                                                                            #                     className="card-body",
                                                                            #                     children=[
                                                                            #                         html.Span(
                                                                            #                             "Select Source (Chapter Types)",
                                                                            #                             className="d-block fw-medium mb-1",
                                                                            #                         ),
                                                                            #                         dcc.Dropdown(
                                                                            #                             id="chapter-type-filter",
                                                                            #                             options=[
                                                                            #                                 dict(
                                                                            #                                     label=chapter,
                                                                            #                                     value=chapter,
                                                                            #                                 )
                                                                            #                                 for chapter in unique_chapter_types
                                                                            #                             ],
                                                                            #                             placeholder="Source (Chapter Types)",
                                                                            #                             multi=True,
                                                                            #                             # value=unique_fy[0],
                                                                            #                             clearable=True,
                                                                            #                         ),
                                                                            #                     ],
                                                                            #                 ),
                                                                            #             ],
                                                                            #         ),
                                                                            #     ],
                                                                            # ),
                                                                        ],
                                                                    ),
                                                                ],
                                                            ),
                                                            # -- End of Filters --
                                                            # -- KPI Cards --
                                                            html.Div(
                                                                className="row gy-4 mt-1 mb-2",
                                                                children=[
                                                                    html.Div(
                                                                        className="col-lg-4 col-md-4 align-self-end order-4",
                                                                        children=[
                                                                            html.Div(
                                                                                className="card back-color-blue",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="d-flex row",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="col-sm-3 col-md-3 text-center text-sm-left",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="card-body pb-0 d-flex align-items-center text-sm-start text-center",
                                                                                                        children=[
                                                                                                            html.Img(
                                                                                                                src="../../assets/img/illustrations/OFTW-Logomark-Logo.png",
                                                                                                                height="120",
                                                                                                                alt="Target User",
                                                                                                            )
                                                                                                        ],
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="col-sm-9 col-md-9",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="card-body right-bg-blue h-100",
                                                                                                        id="money-moved-card",
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    )
                                                                                ],
                                                                            )
                                                                        ],
                                                                    ),
                                                                    html.Div(
                                                                        className="col-lg-4 col-md-4  align-self-end order-4",
                                                                        children=[
                                                                            html.Div(
                                                                                className="card back-color-yellow",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="d-flex row",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="col-sm-3 col-md-3 text-center text-sm-left",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="card-body pb-0  d-flex align-items-center text-sm-start text-center",
                                                                                                        children=[
                                                                                                            html.Img(
                                                                                                                src="../../assets/img/illustrations/OFTW-Logomark-Logo.png",
                                                                                                                height="120",
                                                                                                                alt="Target User",
                                                                                                            )
                                                                                                        ],
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="col-sm-9 col-md-9",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="card-body right-bg-yellow h-100",
                                                                                                        id="cf-money-moved-card",
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    )
                                                                                ],
                                                                            )
                                                                        ],
                                                                    ),
                                                                    html.Div(
                                                                        className="col-lg-4 col-md-4  align-self-end order-4",
                                                                        children=[
                                                                            html.Div(
                                                                                className="card back-color-green",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="d-flex row",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="col-sm-3 col-md-3 text-center text-sm-left",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="card-body pb-0  d-flex align-items-center text-sm-start text-center",
                                                                                                        children=[
                                                                                                            html.Img(
                                                                                                                src="../../assets/img/illustrations/OFTW-Logomark-Logo.png",
                                                                                                                height="120",
                                                                                                                alt="Target User",
                                                                                                            )
                                                                                                        ],
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="col-sm-9 col-md-9",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="card-body right-bg-green h-100",
                                                                                                        id="active-pledge-arr-card",
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    )
                                                                                ],
                                                                            )
                                                                        ],
                                                                    ),
                                                                ],
                                                            ),
                                                            html.Div(
                                                                className="row gy-4 mt-1 mb-2",
                                                                children=[
                                                                    html.Div(
                                                                        className="col-lg-4 col-md-4 align-self-end order-4",
                                                                        children=[
                                                                            html.Div(
                                                                                className="card back-color-blue",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="d-flex row",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="col-sm-3 col-md-3 text-center text-sm-left",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="card-body pb-0 d-flex align-items-center text-sm-start text-center",
                                                                                                        children=[
                                                                                                            html.Img(
                                                                                                                src="../../assets/img/illustrations/OFTW-Logomark-Logo.png",
                                                                                                                height="120",
                                                                                                                alt="Target User",
                                                                                                            )
                                                                                                        ],
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="col-sm-9 col-md-9",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="card-body right-bg-blue h-100",
                                                                                                        id="attrition-rate-card",
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    )
                                                                                ],
                                                                            )
                                                                        ],
                                                                    ),
                                                                    html.Div(
                                                                        className="col-lg-4 col-md-4  align-self-end order-4",
                                                                        children=[
                                                                            html.Div(
                                                                                className="card back-color-yellow",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="d-flex row",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="col-sm-3 col-md-3 text-center text-sm-left",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="card-body pb-0  d-flex align-items-center text-sm-start text-center",
                                                                                                        children=[
                                                                                                            html.Img(
                                                                                                                src="../../assets/img/illustrations/OFTW-Logomark-Logo.png",
                                                                                                                height="120",
                                                                                                                alt="Target User",
                                                                                                            )
                                                                                                        ],
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="col-sm-9 col-md-9",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="card-body right-bg-yellow h-100",
                                                                                                        id="active-donors-card",
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    )
                                                                                ],
                                                                            )
                                                                        ],
                                                                    ),
                                                                    html.Div(
                                                                        className="col-lg-4 col-md-4  align-self-end order-4",
                                                                        children=[
                                                                            html.Div(
                                                                                className="card back-color-green",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="d-flex row",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="col-sm-3 col-md-3 text-center text-sm-left",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="card-body pb-0  d-flex align-items-center text-sm-start text-center",
                                                                                                        children=[
                                                                                                            html.Img(
                                                                                                                src="../../assets/img/illustrations/OFTW-Logomark-Logo.png",
                                                                                                                height="120",
                                                                                                                alt="Target User",
                                                                                                            )
                                                                                                        ],
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="col-sm-9 col-md-9",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="card-body right-bg-green h-100",
                                                                                                        id="active-pledges-card",
                                                                                                    )
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    )
                                                                                ],
                                                                            )
                                                                        ],
                                                                    ),
                                                                ],
                                                            ),
                                                            # -- End of KPI Cards --
                                                            
                                                            # -- KPI Cards --
                                                          
                                                            # html.Div(
                                                            #     children=[
                                                            #         html.Div(
                                                            #             id="money-moved-card",
                                                            #             style={
                                                            #                 "backgroundColor": colors[
                                                            #                     "highlight"
                                                            #                 ],
                                                            #                 "borderRadius": "10px",
                                                            #                 "marginBottom": "20px",
                                                            #                 "padding": "15px",
                                                            # #                 "boxShadow": "0 0 20px rgba(0, 0, 0, 0.15)",
                                                            #             },
                                                            #         ),
                                                            #         html.Div(
                                                            #             id="cf-money-moved-card",
                                                            #             style={
                                                            #                 "backgroundColor": colors[
                                                            #                     "highlight"
                                                            #                 ],
                                                            #                 "borderRadius": "10px",
                                                            #                 "marginBottom": "20px",
                                                            #                 "padding": "15px",
                                                            # #                 "boxShadow": "0 0 20px rgba(0, 0, 0, 0.15)",
                                                            #             },
                                                            #         ),
                                                            #         html.Div(
                                                            #             id = "cf-money-moved-card",
                                                            #             style={
                                                            #                 "backgroundColor": colors[
                                                            #                     "highlight"
                                                            #                 ],
                                                            #                 "borderRadius": "10px",
                                                            #                 "marginBottom": "20px",
                                                            #                 "padding": "15px",
                                                            # #                 "boxShadow": "0 0 20px rgba(0, 0, 0, 0.15)",
                                                            #             }
                                                            #         ),
                                                            #     ],
                                                            #     style={
                                                            #         "display": "flex",
                                                            #         # 'justifyContent': 'center',
                                                            #         "gap": "20px",  # adds space between cards
                                                            #         "flexWrap": "wrap",  # allows wrapping on smaller screens
                                                            #     },
                                                            # ),
                                                            # -- End of KPI Cards --
                                                            # -- Graphs --
                                                            html.Div(
                                                                className="row gy-4 mb-1",
                                                                children=[
                                                                    html.Div(
                                                                        className="col-xxl-6 col-md-6 col-xs-12 col-sm-12 col-xl-12 ",
                                                                        children=[
                                                                            html.Div(
                                                                                className="card h-100",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="card-body",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="card-title d-flex align-items-center mb-1",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="avatar me-2",
                                                                                                        children=[
                                                                                                            html.Span(
                                                                                                                className="avatar-initial rounded-2 bg-label-danger",
                                                                                                                children=[
                                                                                                                    html.I(
                                                                                                                        className="bx bx-trending-up bx-lg text-danger"
                                                                                                                    )
                                                                                                                ],
                                                                                                            )
                                                                                                        ],
                                                                                                    ),
                                                                                                    # html.Div(
                                                                                                    #     children=[
                                                                                                    #         html.H6(
                                                                                                    #             "Money Moved Monthly (Cumulative)",
                                                                                                    #             className="text-lg mb-3 ml-1",
                                                                                                    #         ),
                                                                                                    #         html.Span(
                                                                                                    #             html.I(className="bi bi-magic", id="ai-icon",
                                                                                                    #                 style={"cursor": "pointer", "float": "right", "fontSize": "1.2rem", "marginLeft": "10px"}),
                                                                                                    #         ),
                                                                                                    #         dbc.Tooltip("Click here for Actionable Insights (AI)",
                                                                                                    #                     target="ai-icon", placement="left"),
                                                                                                    #     ],
                                                                                                    # ),
                                                                                                    chart_header_title_with_ai(
                                                                                                        title="Cumulative Money Moved",
                                                                                                        chart_id="money-moved-cumulative-graph",
                                                                                                    ),
                                                                                                    # html.Div([
                                                                                                    #     dbc.Row([
                                                                                                    #         dbc.Col(
                                                                                                    #             html.H6("Money Moved Monthly (Cumulative)", className="mb-0"),
                                                                                                    #             width="auto"
                                                                                                    #         ),
                                                                                                    #         dbc.Col(
                                                                                                    #             html.Div(
                                                                                                    #                 html.I(className="bi bi-magic", id="ai-icon", style={
                                                                                                    #                     "cursor": "pointer",
                                                                                                    #                     "fontSize": "1.3rem",
                                                                                                    #                     "color": "#065A60"
                                                                                                    #                 }),
                                                                                                    #                 style={"textAlign": "right"}
                                                                                                    #             ),
                                                                                                    #             width="auto"
                                                                                                    #         ),
                                                                                                    #     ],
                                                                                                    #     justify="between",
                                                                                                    #     align="center",
                                                                                                    #     className="mb-2"
                                                                                                    #     ),
                                                                                                    #     dbc.Tooltip("Click here for Actionable Insights (AI)", target="ai-icon", placement="left")
                                                                                                    # ]),
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="row",  # Add a row wrapper for proper Bootstrap grid behavior
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="col-md-6 col-12",  # Half width on md and full on smaller screens
                                                                                                        children=[
                                                                                                            dbc.RadioItems(
                                                                                                                options=[
                                                                                                                    {
                                                                                                                        "label": "Actual MM",
                                                                                                                        "value": "payment_amount_usd",
                                                                                                                    },
                                                                                                                    {
                                                                                                                        "label": "Counterfactual MM",
                                                                                                                        "value": "payment_cf_amount_usd",
                                                                                                                    },
                                                                                                                ],
                                                                                                                value="payment_amount_usd",
                                                                                                                id="mm-cf-cumulative-radio-filter",
                                                                                                                inline=True,
                                                                                                            )
                                                                                                        ],
                                                                                                    ),
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="table bordered-table mb-0 dataTable",
                                                                                                children=[
                                                                                                    dcc.Graph(
                                                                                                        id="money-moved-cumulative-graph",
                                                                                                        style={
                                                                                                            "backgroundColor": colors[
                                                                                                                "white"
                                                                                                            ],
                                                                                                            "borderRadius": "10px",
                                                                                                            "padding": "15px",
                                                                                                            "height": "100%",
                                                                                                            "width": "100%",
                                                                                                            'minHeight': '460px'
                                                                                                            # "boxShadow": "0 0 10px rgba(0, 0, 0, 0.1)",
                                                                                                        },
                                                                                                        config={
                                                                                                            "responsive": True,
                                                                                                        },
                                                                                                        # className="card h-100",
                                                                                                    ),
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                            ),
                                                                        ],
                                                                    ),
                                                                    html.Div(
                                                                        className="col-xxl-6 col-md-6 col-xs-12 col-sm-12 col-xl-12 ",
                                                                        children=[
                                                                            html.Div(
                                                                                className="card h-100",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="card-body",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="card-title d-flex align-items-center mb-1",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="avatar me-2",
                                                                                                        children=[
                                                                                                            html.Span(
                                                                                                                className="avatar-initial rounded-2 bg-label-danger",
                                                                                                                children=[
                                                                                                                    html.I(
                                                                                                                        className="bx bx-trending-up bx-lg text-danger"
                                                                                                                    )
                                                                                                                ],
                                                                                                            )
                                                                                                        ],
                                                                                                    ),
                                                                                                    chart_header_title_with_ai(
                                                                                                        title="Reoccuring vs. One-Time Money Moved",
                                                                                                        chart_id="recurring-money-moved-bar-graph",
                                                                                                    ),
                                                                                                    # html.Div(
                                                                                                    #     children=[
                                                                                                    #         html.H6(
                                                                                                    #             "Contribution by Day of the Week",
                                                                                                    #             className="text-lg mb-3 ml-1",
                                                                                                    #         ),
                                                                                                    #     ],
                                                                                                    # ),
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="table bordered-table mb-0 dataTable",
                                                                                                children=[
                                                                                                    dcc.Graph(
                                                                                                        id="recurring-money-moved-bar-graph",
                                                                                                        style={
                                                                                                            "backgroundColor": colors[
                                                                                                                "white"
                                                                                                            ],
                                                                                                            "borderRadius": "10px",
                                                                                                            "padding": "15px",
                                                                                                            # "boxShadow": "0 0 20px rgba(0, 0, 0, 0.15)",
                                                                                                        },
                                                                                                        config={
                                                                                                            "responsive": True,
                                                                                                        },
                                                                                                    ),
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                            ),
                                                                        ],
                                                                    ),
                                                                ],
                                                            ),
                                                            html.Div(
                                                                className="row gy-4 mb-1",
                                                                children=[
                                                                    # html.Div(
                                                                    #     className="col-xxl-6 col-md-6 col-xs-12 col-sm-12 col-xl-12 ",
                                                                    #     children=[
                                                                    #         html.Div(
                                                                    #             className="card h-100",
                                                                    #             children=[
                                                                    #                 html.Div(
                                                                    #                     className="card-body",
                                                                    #                     children=[
                                                                    #                         html.Div(
                                                                    #                             className="card-title d-flex align-items-center mb-4",
                                                                    #                             children=[
                                                                    #                                 html.Div(
                                                                    #                                     className="avatar me-2",
                                                                    #                                     children=[
                                                                    #                                         html.Span(
                                                                    #                                             className="avatar-initial rounded-2 bg-label-danger",
                                                                    #                                             children=[
                                                                    #                                                 html.I(
                                                                    #                                                     className="bx bx-trending-up bx-lg text-danger"
                                                                    #                                                 )
                                                                    #                                             ],
                                                                    #                                         )
                                                                    #                                     ],
                                                                    #                                 ),
                                                                    #                                 html.Div(
                                                                    #                                     children=[
                                                                    #                                         html.H6(
                                                                    #                                             "Money Moved Monthly",
                                                                    #                                             className="text-lg mb-3 ml-1",
                                                                    #                                         ),
                                                                    #                                     ],
                                                                    #                                 ),
                                                                    #                             ],
                                                                    #                         ),
                                                                    #                         html.Div(
                                                                    #                             className="table bordered-table mb-0 dataTable",
                                                                    #                             children=[
                                                                    #                                 dcc.Graph(
                                                                    #                                     id = "money-moved-mosaic-graph",
                                                                    #                                     style = {
                                                                    #                                         'backgroundColor': colors['white'],
                                                                    #                                         'borderRadius': '10px',
                                                                    #                                         'padding': '15px',
                                                                    #                                         'boxShadow': '0 0 20px rgba(0, 0, 0, 0.15)'
                                                                    #                                     }
                                                                    #                                 ),
                                                                    #                             ],
                                                                    #                         ),
                                                                    #                     ],
                                                                    #                 ),
                                                                    #             ],
                                                                    #         ),
                                                                    #     ],
                                                                    # ),
                                                                    html.Div(
                                                                        className="col-xxl-6 col-md-6 col-xs-12 col-sm-12 col-xl-12 ",
                                                                        children=[
                                                                            html.Div(
                                                                                className="card h-100",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="card-body",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="card-title d-flex align-items-center mb-1",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="avatar me-2",
                                                                                                        children=[
                                                                                                            html.Span(
                                                                                                                className="avatar-initial rounded-2 bg-label-danger",
                                                                                                                children=[
                                                                                                                    html.I(
                                                                                                                        className="bx bx-trending-up bx-lg text-danger"
                                                                                                                    )
                                                                                                                ],
                                                                                                            )
                                                                                                        ],
                                                                                                    ),
                                                                                                    chart_header_title_with_ai(
                                                                                                        title="Monthly Donation Trends",
                                                                                                        chart_id="money-moved-line-graph",
                                                                                                    ),
                                                                                                    #  html.Div(
                                                                                                    #      children=[
                                                                                                    #          html.H6(
                                                                                                    #              "Money Moved Monthly Trend",
                                                                                                    #              className="text-lg mb-3 ml-1",
                                                                                                    #          ),
                                                                                                    #      ],
                                                                                                    #  ),
                                                                                                    # TODO: adjust the header properly
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="row",  # Add a row wrapper for proper Bootstrap grid behavior
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="col-md-6 col-12",  # Half width on md and full on smaller screens
                                                                                                        children=[
                                                                                                            dbc.RadioItems(
                                                                                                                options=[
                                                                                                                    {
                                                                                                                        "label": "Actual MM",
                                                                                                                        "value": "payment_amount_usd",
                                                                                                                    },
                                                                                                                    {
                                                                                                                        "label": "Counterfactual MM",
                                                                                                                        "value": "payment_cf_amount_usd",
                                                                                                                    },
                                                                                                                ],
                                                                                                                value="payment_amount_usd",
                                                                                                                id="mm-cf-radio-filter",
                                                                                                                inline=True,
                                                                                                            )
                                                                                                        ],
                                                                                                    ),
                                                                                                    html.Div(
                                                                                                        className="col-md-6 col-12",  # Half width on md and full on smaller screens
                                                                                                        children=[
                                                                                                            dcc.Dropdown(
                                                                                                                id="line-drilldown-by-filter",
                                                                                                                options=[
                                                                                                                    dict(
                                                                                                                        label=item[
                                                                                                                            "label"
                                                                                                                        ],
                                                                                                                        value=item[
                                                                                                                            "value"
                                                                                                                        ],
                                                                                                                    )
                                                                                                                    for item in drilldown_by
                                                                                                                ],
                                                                                                                placeholder="Drilldown by",
                                                                                                                multi=False,
                                                                                                                value="",
                                                                                                                clearable=True,
                                                                                                            )
                                                                                                        ],
                                                                                                        style={
                                                                                                            "minWidth": "250px"
                                                                                                        },  # Optional: Prevents dropdown from shrinking too much
                                                                                                    ),
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="table bordered-table mb-0 dataTable",
                                                                                                children=[
                                                                                                    dcc.Graph(
                                                                                                        id="money-moved-line-graph",
                                                                                                        style={
                                                                                                            "backgroundColor": colors[
                                                                                                                "white"
                                                                                                            ],
                                                                                                            "borderRadius": "10px",
                                                                                                            "padding": "15px",
                                                                                                            "minHeight": "460px",
                                                                                                            "width": "100%",
                                                                                                            "height": "100%",
                                                                                                            # "boxShadow": "0 0 20px rgba(0, 0, 0, 0.15)",
                                                                                                        },
                                                                                                        config={
                                                                                                            "responsive": True,
                                                                                                        },
                                                                                                    ),
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                            ),
                                                                        ],
                                                                    ),
                                                                    # html.Div(
                                                                    #     className="col-xxl-6 col-md-6 col-xs-12 col-sm-12 col-xl-12 ",
                                                                    #     children=[
                                                                    #         html.Div(
                                                                    #             className="card h-100",
                                                                    #             children=[
                                                                    #                 html.Div(
                                                                    #                     className="card-body",
                                                                    #                     children=[
                                                                    #                         html.Div(
                                                                    #                             className="card-title d-flex align-items-center mb-1",
                                                                    #                             children=[
                                                                    #                                 html.Div(
                                                                    #                                     className="avatar me-2",
                                                                    #                                     children=[
                                                                    #                                         html.Span(
                                                                    #                                             className="avatar-initial rounded-2 bg-label-danger",
                                                                    #                                             children=[
                                                                    #                                                 html.I(
                                                                    #                                                     className="bx bx-trending-up bx-lg text-danger"
                                                                    #                                                 )
                                                                    #                                             ],
                                                                    #                                         )
                                                                    #                                     ],
                                                                    #                                 ),
                                                                    #                                 chart_header_title_with_ai(
                                                                    #                                     title="Contributions by Day of the Week",
                                                                    #                                     chart_id="money-moved-heatmap-graph",
                                                                    #                                 ),
                                                                    #                                 # html.Div(
                                                                    #                                 #     children=[
                                                                    #                                 #         html.H6(
                                                                    #                                 #             "Contribution by Day of the Week",
                                                                    #                                 #             className="text-lg mb-3 ml-1",
                                                                    #                                 #         ),
                                                                    #                                 #     ],
                                                                    #                                 # ),
                                                                    #                             ],
                                                                    #                         ),
                                                                    #                         html.Div(
                                                                    #                             className="table bordered-table mb-0 dataTable",
                                                                    #                             children=[
                                                                    #                                 dcc.Graph(
                                                                    #                                     id="money-moved-heatmap-graph",
                                                                    #                                     style={
                                                                    #                                         "backgroundColor": colors[
                                                                    #                                             "white"
                                                                    #                                         ],
                                                                    #                                         "borderRadius": "10px",
                                                                    #                                         "padding": "15px",
                                                                    #                                         'height': '100%', 'width': '100%'
                                                                    #                                         # "boxShadow": "0 0 20px rgba(0, 0, 0, 0.15)",
                                                                    #                                     },
                                                                    #                                     config={
                                                                    #                                         "responsive": True,
                                                                    #                                     },
                                                                    #                                 ),
                                                                    #                             ],
                                                                    #                         ),
                                                                    #                     ],
                                                                    #                 ),
                                                                                    
                                                                    #             ],
                                                                    #         ),
                                                                    #     ],
                                                                    # ),
                                                                     html.Div(
                                                                        className="col-xxl-6 col-md-6 col-xs-12 col-sm-12 col-xl-12 ",
                                                                        children=[
                                                                            html.Div(
                                                                                className="card h-100",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="card-body",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="card-title d-flex align-items-center mb-1",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="avatar me-2",
                                                                                                        children=[
                                                                                                            html.Span(
                                                                                                                className="avatar-initial rounded-2 bg-label-danger",
                                                                                                                children=[
                                                                                                                    html.I(
                                                                                                                        className="bx bx-trending-up bx-lg text-danger"
                                                                                                                    )
                                                                                                                ],
                                                                                                            )
                                                                                                        ],
                                                                                                    ),
                                                                                                    chart_header_title_with_ai(
                                                                                                        title="Attrition Rate Trend",
                                                                                                        chart_id="attrition-rate-line-graph",
                                                                                                    ),
                                                                                                    # html.Div(
                                                                                                    #     children=[
                                                                                                    #         html.H6(
                                                                                                    #             "Contribution by Day of the Week",
                                                                                                    #             className="text-lg mb-3 ml-1",
                                                                                                    #         ),
                                                                                                    #     ],
                                                                                                    # ),
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="row",  # Add a row wrapper for proper Bootstrap grid behavior
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="col-md-6 col-12",  # Half width on md and full on smaller screens
                                                                                                        children=[
                                                                                                            dcc.Dropdown(
                                                                                                                id = "attrition-rate-line-drilldown-by-filter",
                                                                                                                options=[
                                                                                                                    dict(
                                                                                                                        label=item[
                                                                                                                            "label"
                                                                                                                        ],
                                                                                                                        value=item[
                                                                                                                            "value"
                                                                                                                        ],
                                                                                                                    )
                                                                                                                    for item in attrition_drilldown_by
                                                                                                                ],
                                                                                                                placeholder="Drilldown by",
                                                                                                                multi=False,
                                                                                                                value="",
                                                                                                                clearable=True,
                                                                                                            )
                                                                                                        ],
                                                                                                    ),
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="table bordered-table mb-0 dataTable",
                                                                                                children=[
                                                                                                    dcc.Graph(
                                                                                                        id="attrition-rate-line-graph",
                                                                                                        style={
                                                                                                            "backgroundColor": colors[
                                                                                                                "white"
                                                                                                            ],
                                                                                                            "borderRadius": "10px",
                                                                                                            "padding": "15px",
                                                                                                            # "boxShadow": "0 0 20px rgba(0, 0, 0, 0.15)",
                                                                                                        },
                                                                                                        config={
                                                                                                            "responsive": True,
                                                                                                        },
                                                                                                    ),
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                            ),
                                                                        ],
                                                                    ),
                                                                ],
                                                            ),
                                                            html.Div(
                                                                className="row gy-4 mb-1",
                                                                children=[
                                                                    html.Div(
                                                                        className="col-xxl-6 col-md-6 col-xs-12 col-sm-12 col-xl-12 ",
                                                                        children=[
                                                                            html.Div(
                                                                                className="card h-100",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="card-body",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="card-title d-flex align-items-center mb-1",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="avatar me-2",
                                                                                                        children=[
                                                                                                            html.Span(
                                                                                                                className="avatar-initial rounded-2 bg-label-danger",
                                                                                                                children=[
                                                                                                                    html.I(
                                                                                                                        className="bx bx-trending-up bx-lg text-danger"
                                                                                                                    )
                                                                                                                ],
                                                                                                            )
                                                                                                        ],
                                                                                                    ),
                                                                                                    chart_header_title_with_ai(
                                                                                                        title="Active Pledge ARR (Annualized Run Rate)",
                                                                                                        chart_id="active-pledge-arr-sankey-graph",
                                                                                                    ),
                                                                                                    # html.Div(
                                                                                                    #     children=[
                                                                                                    #         html.H6(
                                                                                                    #             "Contribution by Day of the Week",
                                                                                                    #             className="text-lg mb-3 ml-1",
                                                                                                    #         ),
                                                                                                    #     ],
                                                                                                    # ),
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="row",  # Add a row wrapper for proper Bootstrap grid behavior
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="col-md-6 col-12",  # Half width on md and full on smaller screens
                                                                                                        children=[
                                                                                                            dbc.RadioItems(
                                                                                                                id="active-pledge-arr-sankey-view-mode",
                                                                                                                options=[
                                                                                                                    {"label": "Current ARR Only", "value": "actual"},
                                                                                                                    {"label": "Current ARR + Remaining to Target", "value": "target"},
                                                                                                                ],
                                                                                                                value="actual",
                                                                                                                inline=True,
                                                                                                                style={"marginBottom": "20px"}
                                                                                                            ),
                                                                                                        ],
                                                                                                    ),
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="table bordered-table mb-0 dataTable",
                                                                                                children=[
                                                                                                    dcc.Graph(
                                                                                                        id="active-pledge-arr-sankey-graph",
                                                                                                        style={
                                                                                                            "backgroundColor": colors[
                                                                                                                "white"
                                                                                                            ],
                                                                                                            "borderRadius": "10px",
                                                                                                            "padding": "15px",
                                                                                                            "minHeight": "450px",
                                                                                                            # "boxShadow": "0 0 20px rgba(0, 0, 0, 0.15)",
                                                                                                        },
                                                                                                        config={
                                                                                                            "responsive": True,
                                                                                                        },
                                                                                                    ),
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                            ),
                                                                        ],
                                                                    ),

                                                                    html.Div(
                                                                        className="col-xxl-6 col-md-6 col-xs-12 col-sm-12 col-xl-12 ",
                                                                        children=[
                                                                            html.Div(
                                                                                className="card h-100",
                                                                                children=[
                                                                                    html.Div(
                                                                                        className="card-body",
                                                                                        children=[
                                                                                            html.Div(
                                                                                                className="card-title d-flex align-items-center mb-1",
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="avatar me-2",
                                                                                                        children=[
                                                                                                            html.Span(
                                                                                                                className="avatar-initial rounded-2 bg-label-danger",
                                                                                                                children=[
                                                                                                                    html.I(
                                                                                                                        className="bx bx-trending-up bx-lg text-danger"
                                                                                                                    )
                                                                                                                ],
                                                                                                            )
                                                                                                        ],
                                                                                                    ),
                                                                                                    # html.Div(
                                                                                                    #     children=[
                                                                                                    #         html.H6(
                                                                                                    #             "Money Moved Monthly (Cumulative)",
                                                                                                    #             className="text-lg mb-3 ml-1",
                                                                                                    #         ),
                                                                                                    #         html.Span(
                                                                                                    #             html.I(className="bi bi-magic", id="ai-icon",
                                                                                                    #                 style={"cursor": "pointer", "float": "right", "fontSize": "1.2rem", "marginLeft": "10px"}),
                                                                                                    #         ),
                                                                                                    #         dbc.Tooltip("Click here for Actionable Insights (AI)",
                                                                                                    #                     target="ai-icon", placement="left"),
                                                                                                    #     ],
                                                                                                    # ),
                                                                                                    chart_header_title_with_ai(
                                                                                                        title="Top Donor Chapters",
                                                                                                        chart_id="chapter-dumbell-graph",
                                                                                                    ),
                                                                                                    # html.Div([
                                                                                                    #     dbc.Row([
                                                                                                    #         dbc.Col(
                                                                                                    #             html.H6("Money Moved Monthly (Cumulative)", className="mb-0"),
                                                                                                    #             width="auto"
                                                                                                    #         ),
                                                                                                    #         dbc.Col(
                                                                                                    #             html.Div(
                                                                                                    #                 html.I(className="bi bi-magic", id="ai-icon", style={
                                                                                                    #                     "cursor": "pointer",
                                                                                                    #                     "fontSize": "1.3rem",
                                                                                                    #                     "color": "#065A60"
                                                                                                    #                 }),
                                                                                                    #                 style={"textAlign": "right"}
                                                                                                    #             ),
                                                                                                    #             width="auto"
                                                                                                    #         ),
                                                                                                    #     ],
                                                                                                    #     justify="between",
                                                                                                    #     align="center",
                                                                                                    #     className="mb-2"
                                                                                                    #     ),
                                                                                                    #     dbc.Tooltip("Click here for Actionable Insights (AI)", target="ai-icon", placement="left")
                                                                                                    # ]),
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="row",  # Add a row wrapper for proper Bootstrap grid behavior
                                                                                                children=[
                                                                                                    html.Div(
                                                                                                        className="col-md-12 col-12",  # Half width on md and full on smaller screens
                                                                                                        children=[
                                                                                                        html.Div(
                                                                                                            className="col-md-12 col-12",  # Half width on md and full on smaller screens
                                                                                                            children=[
                                                                                                                html.Div([
                                                                                                                    html.Label("Top N Donor Chapters:"),
                                                                                                                    dcc.Slider(
                                                                                                                        id="topn-chapter-slider",
                                                                                                                        min=3,
                                                                                                                        max=50,
                                                                                                                        step=1,
                                                                                                                        value=10,
                                                                                                                        marks={i: str(i) for i in range(3, 51, 3)}
                                                                                                                    )
                                                                                                                ], 
                                                                                                                # style={"width": "40%", "padding": "20px 0"}
                                                                                                                ),
                                                                                                            ],
                                                                                                            # style={
                                                                                                            #     "minWidth": "250px"
                                                                                                            # },  # Optional: Prevents dropdown from shrinking too much
                                                                                                        ),
                                                                                                        ],
                                                                                                    ),
                                                                                                ],
                                                                                            ),
                                                                                            html.Div(
                                                                                                className="table bordered-table mb-0 dataTable",
                                                                                                children=[
                                                                                                    dcc.Graph(
                                                                                                        id="chapter-dumbell-graph",
                                                                                                        style={
                                                                                                            "backgroundColor": colors[
                                                                                                                "white"
                                                                                                            ],
                                                                                                            "borderRadius": "10px",
                                                                                                            "padding": "15px",
                                                                                                            # "boxShadow": "0 0 10px rgba(0, 0, 0, 0.1)",
                                                                                                        },
                                                                                                        config={
                                                                                                            "responsive": True,
                                                                                                        },
                                                                                                    ),
                                                                                                ],
                                                                                            ),
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                            ),
                                                                        ],
                                                                    ),
                                                                ],
                                                            ),
                                                            # Row 4
                                                            html.Div(
                                                                className="row gy-4 mb-1",
                                                                children=[
                                                                    # html.Div(
                                                                    #     className="col-xxl-12 col-md-12 col-xs-12 col-sm-12 col-xl-12 ",
                                                                    #     children=[
                                                                    #         html.Div(
                                                                    #             className="card h-100",
                                                                    #             children=[
                                                                    #                 html.Div(
                                                                    #                     className="card-body",
                                                                    #                     children=[
                                                                    #                         html.Div(
                                                                    #                             className="card-title d-flex align-items-center mb-1",
                                                                    #                             children=[
                                                                    #                                 html.Div(
                                                                    #                                     className="avatar me-2",
                                                                    #                                     children=[
                                                                    #                                         html.Span(
                                                                    #                                             className="avatar-initial rounded-2 bg-label-danger",
                                                                    #                                             children=[
                                                                    #                                                 html.I(
                                                                    #                                                     className="bx bx-trending-up bx-lg text-danger"
                                                                    #                                                 )
                                                                    #                                             ],
                                                                    #                                         )
                                                                    #                                     ],
                                                                    #                                 ),
                                                                    #                                 chart_header_title_with_ai(
                                                                    #                                     title="Attrition Rate Trend",
                                                                    #                                     chart_id="attrition-rate-line-graph",
                                                                    #                                 ),
                                                                    #                                 # html.Div(
                                                                    #                                 #     children=[
                                                                    #                                 #         html.H6(
                                                                    #                                 #             "Contribution by Day of the Week",
                                                                    #                                 #             className="text-lg mb-3 ml-1",
                                                                    #                                 #         ),
                                                                    #                                 #     ],
                                                                    #                                 # ),
                                                                    #                             ],
                                                                    #                         ),
                                                                    #                         # html.Div(
                                                                    #                         #     className="row",  # Add a row wrapper for proper Bootstrap grid behavior
                                                                    #                         #     children=[
                                                                    #                         #         html.Div(
                                                                    #                         #             className="col-md-6 col-12",  # Half width on md and full on smaller screens
                                                                    #                         #             children=[
                                                                    #                         #                 dcc.Dropdown(
                                                                    #                         #                     id = "attrition-rate-line-drilldown-by-filter",
                                                                    #                         #                     options=[
                                                                    #                         #                         dict(
                                                                    #                         #                             label=item[
                                                                    #                         #                                 "label"
                                                                    #                         #                             ],
                                                                    #                         #                             value=item[
                                                                    #                         #                                 "value"
                                                                    #                         #                             ],
                                                                    #                         #                         )
                                                                    #                         #                         for item in attrition_drilldown_by
                                                                    #                         #                     ],
                                                                    #                         #                     placeholder="Drilldown by",
                                                                    #                         #                     multi=False,
                                                                    #                         #                     value="",
                                                                    #                         #                     clearable=True,
                                                                    #                         #                 )
                                                                    #                         #             ],
                                                                    #                         #         ),
                                                                    #                         #     ],
                                                                    #                         # ),
                                                                    #                         html.Div(
                                                                    #                             className="table bordered-table mb-0 dataTable",
                                                                    #                             children=[
                                                                    #                                 dcc.Graph(
                                                                    #                                     id="cell-grid-graph",
                                                                    #                                     style={
                                                                    #                                         "backgroundColor": colors[
                                                                    #                                             "white"
                                                                    #                                         ],
                                                                    #                                         "borderRadius": "10px",
                                                                    #                                         "padding": "15px",
                                                                    #                                         "minHeight": "500px",
                                                                    #                                         # "boxShadow": "0 0 20px rgba(0, 0, 0, 0.15)",
                                                                    #                                     },
                                                                    #                                     config={
                                                                    #                                         "responsive": True,
                                                                    #                                     },
                                                                    #                                 ),
                                                                    #                             ],
                                                                    #                         ),
                                                                    #                     ],
                                                                    #                 ),
                                                                    #             ],
                                                                    #         ),
                                                                    #     ],
                                                                    # ),

                                                                    # html.Div(
                                                                    #     className="col-xxl-6 col-md-6 col-xs-12 col-sm-12 col-xl-12 ",
                                                                    #     children=[
                                                                    #         html.Div(
                                                                    #             className="card h-100",
                                                                    #             children=[
                                                                    #                 html.Div(
                                                                    #                     className="card-body",
                                                                    #                     children=[
                                                                    #                         html.Div(
                                                                    #                             className="card-title d-flex align-items-center mb-1",
                                                                    #                             children=[
                                                                    #                                 html.Div(
                                                                    #                                     className="avatar me-2",
                                                                    #                                     children=[
                                                                    #                                         html.Span(
                                                                    #                                             className="avatar-initial rounded-2 bg-label-danger",
                                                                    #                                             children=[
                                                                    #                                                 html.I(
                                                                    #                                                     className="bx bx-trending-up bx-lg text-danger"
                                                                    #                                                 )
                                                                    #                                             ],
                                                                    #                                         )
                                                                    #                                     ],
                                                                    #                                 ),
                                                                    #                                 chart_header_title_with_ai(
                                                                    #                                     title="Top Donor Chapters",
                                                                    #                                     chart_id="chapter-dumbell-graph",
                                                                    #                                 ),
                                                                    #                             ],
                                                                    #                         ),
                                                                    #                         html.Div(
                                                                    #                             className="row",  # Add a row wrapper for proper Bootstrap grid behavior
                                                                    #                             children=[
                                                                    #                                 html.Div(
                                                                    #                                     className="col-md-12 col-12",  # Half width on md and full on smaller screens
                                                                    #                                     children=[
                                                                    #                                     html.Div(
                                                                    #                                         className="col-md-12 col-12",  # Half width on md and full on smaller screens
                                                                    #                                         children=[
                                                                    #                                             html.Div([
                                                                    #                                                 html.Label("Top N Donor Chapters:"),
                                                                    #                                                 dcc.Slider(
                                                                    #                                                     id="topn-chapter-slider",
                                                                    #                                                     min=3,
                                                                    #                                                     max=50,
                                                                    #                                                     step=1,
                                                                    #                                                     value=10,
                                                                    #                                                     marks={i: str(i) for i in range(3, 51, 3)}
                                                                    #                                                 )
                                                                    #                                             ], 
                                                                    #                                             # style={"width": "40%", "padding": "20px 0"}
                                                                    #                                             ),
                                                                    #                                         ],
                                                                    #                                         # style={
                                                                    #                                         #     "minWidth": "250px"
                                                                    #                                         # },  # Optional: Prevents dropdown from shrinking too much
                                                                    #                                     ),
                                                                    #                                     ],
                                                                    #                                 ),
                                                                    #                             ],
                                                                    #                         ),
                                                                    #                         html.Div(
                                                                    #                             className="table bordered-table mb-0 dataTable",
                                                                    #                             children=[
                                                                    #                                 dcc.Graph(
                                                                    #                                     id="chapter-dumbell-graph",
                                                                    #                                     style={
                                                                    #                                         "backgroundColor": colors[
                                                                    #                                             "white"
                                                                    #                                         ],
                                                                    #                                         "borderRadius": "10px",
                                                                    #                                         "padding": "15px",
                                                                    #                                         # "boxShadow": "0 0 10px rgba(0, 0, 0, 0.1)",
                                                                    #                                     },
                                                                    #                                     config={
                                                                    #                                         "responsive": True,
                                                                    #                                     },
                                                                    #                                 ),
                                                                    #                             ],
                                                                    #                         ),
                                                                    #                     ],
                                                                    #                 ),
                                                                    #             ],
                                                                    #         ),
                                                                    #     ],
                                                                    # ),
                                                                ],
                                                            ),
                                                            # Floating Draggable AI Panel
                                                            dbc.Modal(
                                                                id="ai-modal",
                                                                is_open=False,
                                                                size="lg",
                                                                centered=True,
                                                                backdrop=True,
                                                                style={
                                                                    "maxHeight": "90vh",
                                                                    "overflowY": "auto"
                                                                },
                                                                children=[
                                                                    # html.Div([
                                                                        dash_draggable.GridLayout(
                                                                            # id="ai-draggable",
                                                                            children=[
                                                                                html.Div(
                                                                                    [
                                                                                        dbc.ModalHeader([
                                                                                            # dbc.ModalTitle("Header"),
                                                                                            html.Div(
                                                                                                [
                                                                                                    html.Span("🧠 AI Insights", style={"fontWeight": "bold"}),
                                                                                                    html.Span(" (Wait for few seconds)")
                                                                                                ]
                                                                                            ),
                                                                                        ]),
                                                                                        
                                                                                        html.Hr(),
                                                                                        dcc.Loading(
                                                                                            id="ai-loading",
                                                                                            type="default",  # or "dot", "circle"
                                                                                            fullscreen=False,
                                                                                            children=html.Div(
                                                                                                id="ai-output",
                                                                                                style={
                                                                                                    "overflowY": "auto",
                                                                                                },
                                                                                            ),
                                                                                        ),
                                                                                    ],
                                                                                    style={
                                                                                        "backgroundColor": "white",
                                                                                        "padding": "15px",
                                                                                        "border": "1px solid #ccc",
                                                                                        "borderRadius": "8px",
                                                                                        "boxShadow": "2px 2px 10px rgba(0,0,0,0.1)",
                                                                                        "height": "100%",
                                                                                        "width": "100%",
                                                                                        "display": "flex",
                                                                                        "flexDirection": "column",
                                                                                        "flexGrow": "0",
                                                                                    },
                                                                                )
                                                                            ],
                                                                            # layout=[
                                                                            #     {
                                                                            #         "i": "0",
                                                                            #         "x": 0,
                                                                            #         "y": 0,
                                                                            #         "w": 20,
                                                                            #         "h": 10,
                                                                            #         "static": False,
                                                                            #     }
                                                                            # ],
                                                                            # cols=12,
                                                                            # rowHeight=30,
                                                                            # width=100%,
                                                                            isDraggable=False,
                                                                            isResizable=True,
                                                                        )
                                                                #     ],
                                                                #     style = {
                                                                #         # "position": "fixed",
                                                                #         # "bottom": "20px",
                                                                #         # "right": "20px",
                                                                #         # "width": "300px",
                                                                #         # "zIndex": 9999,
                                                                #         "position": "relative", 
                                                                #         "padding": "20px"
                                                                #     },
                                                                # ),
                                                                ],
                                                            ),
                                                        ],
                                                    ),
                                                    html.Div(
                                                        [
                                                            dbc.Button(
                                                                "About OFTW Dashboard",
                                                                id="collapse-button",
                                                                className="mb-3",
                                                                color="primary",
                                                                n_clicks=0,
                                                            ),
                                                            dbc.Collapse(
                                                                dbc.Card(
                                                                    dbc.CardBody(
                                                                        html.Iframe(
                                                                            src="/assets/about.html",
                                                                            style={"width": "100%", "height": "400px", "border": "none"}
                                                                        )
                                                                    )
                                                                ),                                                               
                                                                id="collapse",
                                                                is_open=False,
                                                            ),
                                                        ]
                                                    ),
                                                    html.Div([
                                                        html.Footer(
                                                            className="content-footer footer bg-footer-theme",
                                                            children=[
                                                                html.Div(
                                                                    className="container-fluid",
                                                                    children=[
                                                                        html.Div(
                                                                            className="footer-container d-flex align-items-center justify-content-center py-4 flex-md-row flex-column",
                                                                            children=[
                                                                                html.Div(
                                                                                    className="text-body txt-white",
                                                                                    children=[
                                                                                        "© 2025.",
                                                                                    ],
                                                                                ),
                                                                                html.A(
                                                                                    html.Img(
                                                                                        src="../../assets/img/illustrations/93064_Arkimetrix-Analytics-Ltd-1.png",
                                                                                        height="55",
                                                                                        alt="View Badge User",
                                                                                        # className="scaleX-n1-rtl logotext",
                                                                                    ),
                                                                                    href="https://arkimetrix.com/",
                                                                                    target="_blank",  # optional, opens in a new tab
                                                                                    # className="logo arkimetrix",
                                                                                )
                                                                            ],
                                                                        )
                                                                    ],
                                                                )
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ]
    )
