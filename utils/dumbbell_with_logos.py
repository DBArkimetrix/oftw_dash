import pandas as pd
import polars as pl
import plotly.graph_objects as go
from utils.logo_utils import find_best_logo_match, get_logo_as_base64

def create_dumbell_chart_with_logos(data_preparer, selected_fy, prior_fy_value, top_n, logo_mapping):
    # Step 1: Load and pivot the data
    df = (
        data_preparer.filter_data("merged", [("payment_date_fy", "in", [selected_fy, prior_fy_value])])
        .collect()
        .pivot(
            values="payment_amount_usd",
            index=["pledge_donor_chapter"],
            on="payment_date_fy",
            aggregate_function="sum"
        )
        .rename({selected_fy: "selected_fy", prior_fy_value: "prior_fy"})
        .fill_null(0)
        .to_pandas()
    )

    df["pledge_donor_chapter"] = df["pledge_donor_chapter"].fillna("Unknown")
    df["total"] = df["selected_fy"] + df["prior_fy"]

    # Step 2: Sort and select top N with grouping of "Other"
    df_sorted = df.sort_values("total", ascending=False)
    df_top = df_sorted.head(top_n)
    df_other = df_sorted.iloc[top_n:]

    if not df_other.empty:
        df_other_row = pd.DataFrame({
            "pledge_donor_chapter": ["Other"],
            "selected_fy": [df_other["selected_fy"].sum()],
            "prior_fy": [df_other["prior_fy"].sum()],
            "total": [df_other["total"].sum()]
        })
        df_top = pd.concat([df_top, df_other_row], ignore_index=True)

    # Step 3: Ensure no duplicate "Unknown" or "Other" before sorting
    df_top = df_top.groupby("pledge_donor_chapter", as_index=False).agg({
        "selected_fy": "sum",
        "prior_fy": "sum",
        "total": "sum"
    })

    # Step 4: Assign explicit sort rank
    df_top["sort_rank"] = df_top.apply(
        lambda row: -2 if row["pledge_donor_chapter"] == "Unknown" else (-1 if row["pledge_donor_chapter"] == "Other" else row["total"]),
        axis=1
    )

    df_top = df_top.sort_values(by="sort_rank", ascending=False).drop(columns=["sort_rank"])
    donor_order = df_top["pledge_donor_chapter"].tolist()[::-1]

    # Step 5: Build dumbbell chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_top["prior_fy"],
        y=df_top["pledge_donor_chapter"],
        mode="markers",
        name=f"{prior_fy_value}",
        marker=dict(color="red", size=10)
    ))

    fig.add_trace(go.Scatter(
        x=df_top["selected_fy"],
        y=df_top["pledge_donor_chapter"],
        mode="markers",
        name=f"{selected_fy}",
        marker=dict(color="green", size=10)
    ))

    for _, row in df_top.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["prior_fy"], row["selected_fy"]],
            y=[row["pledge_donor_chapter"]]*2,
            mode="lines",
            line=dict(color="gray", width=1),
            showlegend=False
        ))

    # Step 6: Add logos (fixed placement using paper coordinates)
    layout_images = []
    for donor in donor_order:
        logo_candidate = find_best_logo_match(donor, logo_mapping)
        if logo_candidate:
            if logo_candidate.startswith("data:image"):
                logo_b64 = logo_candidate
            else:
                logo_b64 = get_logo_as_base64(logo_candidate)

            if logo_b64:
                layout_images.append({
                    "source": logo_b64,
                    "xref": "paper",
                    "yref": "y",
                    "x": 0.02,
                    "y": donor,
                    "sizex": 0.04,
                    "sizey": 0.6,
                    "xanchor": "right",
                    "yanchor": "middle",
                    "layer": "above"
                })

    # Step 7: Layout
    fig.update_layout(
        title=f"Top {top_n} Donor Chapters - {selected_fy} vs {prior_fy_value}",
        xaxis=dict(title="Amount (USD)", domain=[0.25, 1]),
        yaxis=dict(
            title="Donor Chapter",
            categoryorder="array",
            categoryarray=donor_order,
            side="left",
            position=0.25,
            automargin=False
        ),
        images=layout_images,
        height=100 + 40 * len(donor_order),
        margin=dict(l=160, r=40, t=50, b=40),
        template="plotly_white"
    )

    return fig