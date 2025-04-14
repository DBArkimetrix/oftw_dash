import dash
from dash import Input, Output, callback, ctx, html, ALL, State, dcc
import dash_bootstrap_components as dbc

import polars as pl
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.data_loader import data_loader
from utils.data_preparer import DataPreparer
from utils.figure import Figure

from pages.layouts import moneymoved_layout

dash.register_page(__name__, path = '/', title = "OFTW Dashboard")

data_preparer = DataPreparer()
figure_instance = Figure()

# One for the World color palette
colors = {
    'primary': '#006466',     # Teal/blue-green
    'secondary': '#065A60',   # Darker teal
    'accent': '#0B525B',      # Another shade
    'light': '#144552',       # Lighter shade
    'text': '#1B3A4B',        # For text
    'highlight': '#F2F2F2',   # Light highlight
    'white': '#FFFFFF'
}

def layout(**kwargs):
    return moneymoved_layout()


@callback(
    Output("active-donors-card", "children"),
    Output("active-pledges-card", "children"),
    Input("fy-filter", "value"),
)
def active_donors_pledges_card(selected_fy):
    filters = []     

    ACTIVE_DONORS_TARGET = 1200
    ACTIVE_PLEDGES_TARGET = 850

    if selected_fy:
        filters.append(("pledge_starts_at_fy", "==", selected_fy))

    pledges_lf = data_preparer.filter_data("pledges", filters)

    active_donors_value = (pledges_lf
        .filter(pl.col("pledge_status").is_in(["Active donor", "One-Time"]))
        .pipe(lambda lf: data_preparer.get_unique_col_count_lf(lf, "pledge_donor_id"))
    )

    active_pledges_value = (pledges_lf
        .filter(pl.col("pledge_status").is_in(["Active donor"]))
        .pipe(lambda lf: data_preparer.get_unique_col_count_lf(lf, "pledge_donor_id"))
    )

    active_donors_card = figure_instance.create_absolute_value_kpi_card(active_donors_value, goal = ACTIVE_DONORS_TARGET, body_text = "Active Donors")
    active_pledges_card = figure_instance.create_absolute_value_kpi_card(active_pledges_value, goal = ACTIVE_PLEDGES_TARGET, body_text = "Active Pledges")
    
    return active_donors_card, active_pledges_card

@callback(
    Output("money-moved-card", "children"),
    Output("cf-money-moved-card", "children"),
    Output("money-moved-cumulative-graph", "figure"),
    Output("recurring-money-moved-bar-graph", "figure"),
    Output("chapter-dumbell-graph", "figure"),
    # Output("cf-money-moved-cumulative-graph", "figure"),
    # Output("money-moved-mosaic-graph", "figure"),
    # Output("money-moved-heatmap-graph", "figure"),
    Output("ai-message-store", "data", allow_duplicate = True),
    Input("fy-filter", "value"),
    Input("mm-cf-cumulative-radio-filter", "value"),
    Input("topn-chapter-slider", "value"),
    # Input("payment-platform-filter", "value"),
    # Input("chapter-type-filter", "value"),
    Input({"type": "ai-icon", "chart": ALL}, "n_clicks"),
    [
        State("ai-message-store", "data"),
    ],
    prevent_initial_call = "initial_duplicate"
)
def update_kpis_graphs(selected_fy, selected_amount_type, topn_donor_chapter_value, ai_icon_clicks_list, existing_ai_messages):
    triggered_id = ctx.triggered_id
    chart_insight = None

    # Check if the triggered_id is a dictionary and has a "type" key
    # This is to check if the triggered_id is from the ai-icon
    if triggered_id and isinstance(triggered_id, dict) and "type" in triggered_id:
        chart_insight = triggered_id.get("chart")

    filters = []     
    prior_fy_value = f"FY{int(selected_fy[2:6]) - 1}-{int(selected_fy[7:]) - 1}"
    sy_py_filters = [("payment_date_fy", "in", [selected_fy, prior_fy_value])]

    fund_raise_target = 1_800_000
    cf_fund_raise_target = 1_260_000

    if selected_fy:
        filters.append(("payment_date_fy", "==", selected_fy))

    # if selected_payment_platform:
    #     filters.append(("payment_platform", "in", selected_payment_platform))

    # if selected_chapter_type:
    #     filters.append(("pledge_chapter_type", "in", selected_chapter_type))

    merged_lf = data_preparer.filter_data("merged", filters)

    money_moved_lf = (merged_lf
                   .select(["payment_date_fy", "payment_date_fm", "payment_date_calendar_year", "payment_date_calendar_month", "payment_date_calendar_monthname", 
                            "payment_date_calendar_monthyear", "payment_date_day_of_week", "payment_date_week_of_fy", "pledge_status", "pledge_chapter_type", 
                            "payment_portfolio", "payment_platform", "payment_date", "payment_amount_usd", "payment_cf_amount_usd", "pledge_frequency_type"
                    ])
                   .filter(~pl.col("payment_portfolio").is_in(["One for the World Discretionary Fund", "One for the World Operating Costs"]))
                   .sort("payment_date_fm")
                )

    # mm FYTD
    money_moved_ytd_value = money_moved_lf.select(pl.col("payment_amount_usd").sum()).collect().item()
    mm_card = figure_instance.create_kpi_card(money_moved_ytd_value, goal = fund_raise_target, body_text = "Money Moved FYTD")

    # cf mm FYTD
    cf_money_moved_ytd_value = money_moved_lf.select(pl.col("payment_cf_amount_usd").sum()).collect().item()
    cf_mm_card = figure_instance.create_kpi_card(cf_money_moved_ytd_value, goal = cf_fund_raise_target, body_text = "CF Money Moved FYTD")


    # money moved monthly
    # dumbell_chart_filters = [("payment_date_fy", "in", [selected_fy, prior_fy_value])]
    money_moved_ytd_df = (merged_lf
        .group_by(["payment_date_fy", "payment_date_fm", "payment_date_calendar_month", "payment_date_calendar_monthyear"])
        .agg([
            pl.col("payment_amount_usd").sum().alias("money_moved_monthly"),
            pl.col("payment_cf_amount_usd").sum().alias("cf_money_moved_monthly"),
        ])
        .sort("payment_date_fm")
        .with_columns([
            pl.cum_sum("money_moved_monthly").alias("money_moved_cumulative"),
            pl.cum_sum("cf_money_moved_monthly").alias("cf_money_moved_cumulative"),
        ])
        .select(["payment_date_fm", "payment_date_calendar_monthyear", "money_moved_cumulative", "cf_money_moved_cumulative"])
        .collect()
    )

    money_moved_py_df = (data_loader.get_data("merged")
        .filter(pl.col("payment_date_fy") == prior_fy_value)
        .filter(~pl.col("payment_portfolio").is_in(["One for the World Discretionary Fund", "One for the World Operating Costs"]))
        .group_by(["payment_date_fy", "payment_date_fm", "payment_date_calendar_month", "payment_date_calendar_monthyear"])
        .agg([
            pl.col("payment_amount_usd").sum().alias("money_moved_monthly"),
            pl.col("payment_cf_amount_usd").sum().alias("cf_money_moved_monthly"),
        ])
        .with_columns([
            ((fund_raise_target / pl.sum("money_moved_monthly") ) * pl.col("money_moved_monthly")).alias("monthly_target_runrate"),
            ((cf_fund_raise_target / pl.sum("cf_money_moved_monthly")) * pl.col("cf_money_moved_monthly")).alias("cf_monthly_target_runrate"),
        ])
        .sort("payment_date_fm")
        .with_columns([
            pl.cum_sum("monthly_target_runrate").alias("money_moved_cumulative"),
            pl.cum_sum("cf_monthly_target_runrate").alias("cf_money_moved_cumulative"),
        ])
        .drop(["money_moved_monthly", "cf_money_moved_monthly"])
        .collect()
    )

    # print(money_moved_py_df)

    mm_monthly_fig = go.Figure()

    if "cf" in selected_amount_type:
        mm_monthly_fig = figure_instance.create_monthly_mm_graph(money_moved_ytd_df, "cf_money_moved_cumulative", cf_fund_raise_target, money_moved_py_df)
    else:
        mm_monthly_fig = figure_instance.create_monthly_mm_graph(money_moved_ytd_df, "money_moved_cumulative", fund_raise_target, money_moved_py_df)

    # mm_mosaic_fig = figure_instance.create_money_mural_mosaic(money_moved_ytd_df)

    # Recurring vs One-Time bar graph
    money_moved_reoccuring_df = (money_moved_lf
            .group_by(["payment_date_fm", "payment_date_calendar_month", "payment_date_calendar_monthyear", "pledge_frequency_type"])
            .agg([
                pl.col("payment_amount_usd").sum().alias("money_moved_usd"),
            ])
            .sort(["payment_date_fm", "pledge_frequency_type"])
            # .with_columns([
            #     pl.sum("money_moved_usd").over(["payment_date_fm"]).alias("money_moved_monthly"),
            # ])
            # .with_columns([
            #     pl.col("money_moved_monthly").cum_sum().over(["pledge_frequency_type"]).alias("money_moved_usd_cumulative"),
            # ])
            .collect()  
        )
            
    reoccuring_vs_onetime_fig = figure_instance.create_reoccuring_vs_onetime_bar_graph(money_moved_reoccuring_df)
    # End of recurring vs one-time bar graph

    # Top N Donor Chapter Dumbell Chart (Selected FY vs Prior FY)

    money_moved_top_n_donors_df_pd = (data_preparer.filter_data("merged", sy_py_filters)
        .collect()
        .pivot(
            values="payment_amount_usd",  # Replace with the column you want to aggregate
            index=["pledge_donor_chapter"],  # Replace with the columns you want as index
            on="payment_date_fy",
            aggregate_function="sum"  # Replace with the aggregation function you need
        )    
        .rename({
            selected_fy: "selected_fy",
            prior_fy_value: "prior_fy"
        })
        .filter(pl.col("pledge_donor_chapter").is_not_null())
        .with_columns([
            pl.col("selected_fy").fill_null(0),
            pl.col("prior_fy").fill_null(0),
        ])
        .with_columns([
            (pl.col("selected_fy") + pl.col("prior_fy")).alias("total")
        ])
        .sort("total", descending=True)
        .to_pandas()                         
    )

    if len(money_moved_top_n_donors_df_pd) > topn_donor_chapter_value:
        top = money_moved_top_n_donors_df_pd.head(topn_donor_chapter_value)
        other = money_moved_top_n_donors_df_pd.iloc[topn_donor_chapter_value:]
        other_row = pd.DataFrame({
            "pledge_donor_chapter": ["Other"],
            "selected_fy": [other["selected_fy"].sum()],
            "prior_fy": [other["prior_fy"].sum()],
            "total": [other["total"].sum()]
        })
        top = pd.concat([top, other_row], ignore_index=True)
    else:
        top = money_moved_top_n_donors_df_pd

    # Move "Unknown" to bottom after sorting
    top_sorted = top.sort_values(by="total", ascending=False)
    top_sorted["sort_key"] = top_sorted.apply(
        lambda row: -1 if row["pledge_donor_chapter"] == "Unknown" or row["pledge_donor_chapter"] == "Other" else row["total"], axis=1
    )
    top_sorted = top_sorted.sort_values(by="sort_key", ascending=False).drop(columns="sort_key")

    # Get the donor chapter ordering for the y-axis
    donor_order = top_sorted["pledge_donor_chapter"].tolist()[::-1]    

    dumbell_chart_fig = figure_instance.create_dumbell_chart_w_logo(top_sorted, selected_fy, prior_fy_value, donor_order)

    #End of Top N Donor Chapter Dumbell Chart

    # Calendar heatmap
    # mm_heatmap_fig = figure_instance.create_calendarplot(money_moved_lf.collect())
    # End of calendar heatmap

    # For AI insight
    ai_insight = []
    if chart_insight:
        if chart_insight == "money-moved-cumulative-graph":
            ai_insight.append(data_preparer.get_llm_insight(mm_monthly_fig.to_json()))
        # elif chart_insight == "cf-money-moved-cumulative-graph":
        #     ai_insight.append(data_preparer.get_llm_insight(mm_monthly_fig.to_json()))
        # elif chart_insight == "money-moved-heatmap-graph":
        #     ai_insight.append(data_preparer.get_llm_insight(mm_heatmap_fig.to_json()))
        elif chart_insight == "recurring-money-moved-bar-graph":
            ai_insight.append(data_preparer.get_llm_insight(reoccuring_vs_onetime_fig.to_json()))
        elif chart_insight == "chapter-dumbell-graph":
            ai_insight.append(data_preparer.get_llm_insight(dumbell_chart_fig.to_json()))
        # else:
        #     ai_insight.append("No insight available for this chart.")

    new_ai_messages = ai_insight + existing_ai_messages if len(ai_insight) > 0 else existing_ai_messages

    return mm_card, cf_mm_card, mm_monthly_fig, reoccuring_vs_onetime_fig, dumbell_chart_fig, new_ai_messages


@callback(
    Output("money-moved-line-graph", "figure"),
    Output("ai-message-store", "data", allow_duplicate = True),
    Input("fy-filter", "value"),
    Input("mm-cf-radio-filter", "value"),
    Input("line-drilldown-by-filter", "value"),
    Input({"type": "ai-icon", "chart": ALL}, "n_clicks"),
    State("ai-message-store", "data"),
    prevent_initial_call = "initial_duplicate"
)
def update_mm_monthly_trendline(selected_fy, selected_amount_type, selected_drilldown_by, ai_icon_clicks_list, existing_ai_messages):
    triggered_id = ctx.triggered_id
    chart_insight = None

    # Check if the triggered_id is a dictionary and has a "type" key
    # This is to check if the triggered_id is from the ai-icon
    if triggered_id and isinstance(triggered_id, dict) and "type" in triggered_id:
        chart_insight = triggered_id.get("chart")

    filters = []

    if selected_fy:
        filters.append(("payment_date_fy", "==", selected_fy))

    merged_lf = data_preparer.filter_data("merged", filters)

    money_moved_lf = (merged_lf
                        .select(["payment_date_fy", "payment_date_fm", "payment_date_calendar_year", "payment_date_calendar_month", "payment_date_calendar_monthname", 
                            "payment_date_calendar_monthyear", "payment_date_day_of_week", "payment_date_week_of_fy", "pledge_status", "pledge_chapter_type", 
                            "payment_portfolio", "payment_platform", "payment_date", "payment_amount_usd", "payment_cf_amount_usd"
                        ])                   
                        .filter(~pl.col("payment_portfolio").is_in(["One for the World Discretionary Fund", "One for the World Operating Costs"]))
                    .sort("payment_date_fm")
                    )
    
    mm_monthly_trendline_fig = figure_instance.create_mm_monthly_trendline(money_moved_lf, selected_amount_type, selected_drilldown_by)      
    
    # For AI insight
    ai_insight = []
    if chart_insight:
        if chart_insight =="money-moved-line-graph":
            ai_insight.append(data_preparer.get_llm_insight(mm_monthly_trendline_fig.to_json()))
        # else:
        #     ai_insight.append("No insight available for this chart.")

    new_ai_messages = ai_insight + existing_ai_messages if len(ai_insight) > 0 else existing_ai_messages

    return mm_monthly_trendline_fig , new_ai_messages

@callback(
    Output("active-pledge-arr-sankey-graph", "figure"),
    Output("active-pledge-arr-card", "children"),
    Output("ai-message-store", "data", allow_duplicate = True),
    Input("fy-filter", "value"),
    Input("active-pledge-arr-sankey-view-mode", "value"),
    Input({"type": "ai-icon", "chart": ALL}, "n_clicks"),
    State("ai-message-store", "data"),
    prevent_initial_call = "initial_duplicate"
)
def update_active_pledge_arr_sankey(selected_fy, selected_view_mode, ai_icon_clicks_list, existing_ai_messages):
    triggered_id = ctx.triggered_id
    chart_insight = None

    # Check if the triggered_id is a dictionary and has a "type" key
    # This is to check if the triggered_id is from the ai-icon
    if triggered_id and isinstance(triggered_id, dict) and "type" in triggered_id:
        chart_insight = triggered_id.get("chart")

    filters = []

    if selected_fy:
        filters.append(("pledge_starts_at_fy", "==", selected_fy))

    pledge_active_arr_df = data_preparer.filter_data("pledge_active_arr", filters).collect()


    total_arr_value = pledge_active_arr_df.select(pl.sum("pledge_contribution_arr_usd")).item()
    active_pledge_arr_card = figure_instance.create_kpi_card(total_arr_value, goal = 1_200_000, body_text = "Active Annualized Run Rate")

    # Sankey graph
    active_pledge_arr_sankey_fig = figure_instance.create_active_pledge_arr_sankey(pledge_active_arr_df, selected_view_mode)

    # For AI insight
    ai_insight = []
    if chart_insight:
        if chart_insight =="active-pledge-arr-sankey-graph":
            ai_insight.append(data_preparer.get_llm_insight(active_pledge_arr_sankey_fig.to_json()))
        # else:
        #     ai_insight.append("No insight available for this chart.")

    new_ai_messages = ai_insight + existing_ai_messages if len(ai_insight) > 0 else existing_ai_messages

    return active_pledge_arr_sankey_fig, active_pledge_arr_card, new_ai_messages


@callback(
    Output("attrition-rate-card", "children"),
    Output("attrition-rate-line-graph", "figure"),
    Output("ai-message-store", "data", allow_duplicate = True),
    Input("fy-filter", "value"),
    Input("attrition-rate-line-drilldown-by-filter", "value"),
    Input({"type": "ai-icon", "chart": ALL}, "n_clicks"),
    State("ai-message-store", "data"),
    prevent_initial_call = "initial_duplicate"
)
def update_attrition_rate_line_graph(selected_fy, selected_drilldown_by, ai_icon_clicks_list, existing_ai_messages):
    triggered_id = ctx.triggered_id
    chart_insight = None

    # Check if the triggered_id is a dictionary and has a "type" key
    # This is to check if the triggered_id is from the ai-icon
    if triggered_id and isinstance(triggered_id, dict) and "type" in triggered_id:
        chart_insight = triggered_id.get("chart")

    filters = []
    target = 18/100

    if selected_fy:
        filters.append(("pledge_starts_at_fy", "==", selected_fy))

    attrition_lf = data_preparer.filter_data("pledge_attrition", filters)

    # Hardcode
    if selected_fy == "FY2024-2025":
        attrition_lf = (attrition_lf
                        .filter(pl.col("pledge_starts_at_fm") < 9)  # No greater than Feb'25
                    )

    attrition_rate_line_fig = figure_instance.create_attrition_rate_trendline(attrition_lf, selected_drilldown_by)

    # Attrition rate kpi card
    ATTRITION_RATE_TARGET = 18
    yearly_attrition_rate = (attrition_lf
        .group_by(["pledge_starts_at_fy"])
        .agg([
            (pl.sum("total_pledge_count") / pl.sum("is_cancelled_count")).alias("attrition_rate"),
        ])
        .select("attrition_rate")
        .collect()
        .item()
    )

    attrition_rate_card = figure_instance.create_kpi_card(yearly_attrition_rate, goal = ATTRITION_RATE_TARGET, body_text = "Pledge Attrition Rate", value_type = "%")

    return attrition_rate_card, attrition_rate_line_fig, existing_ai_messages 

@callback(
    Output("ai-modal", "is_open"),
    Output("ai-output", "children"),
    Input("ai-message-store", "data"),
    Input({"type": "ai-icon", "chart": ALL}, "n_clicks"),
    State("ai-modal", "is_open"),
)
def render_ai_output(messages, ai_icon_click_list, is_ai_modal_open):
    triggered_id = ctx.triggered_id

    # Check if the triggered_id is a dictionary and has a "type" key
    # This is to check if the triggered_id is from the ai-icon
    if triggered_id and isinstance(triggered_id, dict) and "type" in triggered_id:
        is_ai_modal_open = not is_ai_modal_open

    output_content = [
        html.Div([
            dcc.Markdown(msg),
            html.Hr(style={"margin": "10px 0"})  # ← clean separator
        ]) for msg in messages
    ]

    return is_ai_modal_open, output_content


# @callback(
#     Output("ai-modal", "is_open"),
#     Input({"type": "ai-icon", "chart": ALL}, "n_clicks"),
#     [
#         State("ai-modal", "is_open"),
#     ],
# )
# def toggle_ai_modal(ai_icon_click_list, is_ai_modal_open):
#     triggered_id = ctx.triggered_id

#     # Check if the triggered_id is a dictionary and has a "type" key
#     # This is to check if the triggered_id is from the ai-icon
#     if triggered_id and isinstance(triggered_id, dict) and "type" in triggered_id:
#         is_ai_modal_open = not is_ai_modal_open

#     return is_ai_modal_open
    

@callback(
    Output("target-form-modal", "is_open"),
    # Output("target-body-modal", "children"),
    Input("set-target-button", "n_clicks"),
    Input("done-target-form-button", "n_clicks"),
    State("target-form-modal", "is_open"),
    # State("target-form-data-store", "data")
)
def toggle_modal(open_clicks, close_clicks, is_open):
    if open_clicks or close_clicks:
        return not is_open
    return is_open

@callback(
    Output("target-form-data-store", "data"),
    Input("done-target-form-button", "n_clicks"),
    [State(f"input-{key}", "value") for key in data_loader.get_default_target_data()],
    prevent_initial_call=True
)
def update_store(n_clicks, *values):
    updated_data = dict(zip(data_loader.get_default_target_data().keys(), values))
    return updated_data

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

# Helper: Create form inputs
def create_form(data = data_loader.get_default_target_data()):
    return [
        html.Div([
            html.Label(labels.get(key), className="form-label"),
            dbc.Input(
                id=f"input-{key}",
                type="number",
                value=value,
                className="form-control text-dark bg-white border"
            )
        ], className="mb-3")  # spacing between fields
        for key, value in data.items()
    ]

@callback(
    Output("target-form", "children"),
    Input("target-form-fy-dropdown", "value"),
    # Input("edit-btn", "n_clicks"),
    # State("fy-target-form", "value"),
    State("target-form-data-store", "data")
)
def show_target_form(selected_fy, existing_data):
    if not selected_fy:
        return html.Div("Please select a valid Fiscal Year.")

    return create_form(existing_data)


@callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open