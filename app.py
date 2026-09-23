import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Partner Ecosystem Intelligence",
    layout="wide"
)

st.title("Partner Ecosystem Intelligence")
st.caption("Partner portfolio, pipeline and ecosystem performance")

# Load partner data
df = pd.read_csv("partners.csv")
# -------------------------
# PARTNER SCORING ENGINE
# -------------------------

df["PartnerScore"] = (
    df["StrategicFit"] * 0.25 +
    df["TechnicalFit"] * 0.20 +
    df["MarketOverlap"] * 0.20 +
    df["RevenuePotential"] * 0.20 +
    df["IntegrationPotential"] * 0.15
)

# Convert score from 0-10 to 0-100
df["PartnerScore"] = (df["PartnerScore"] * 10).round(1)
# -------------------------
# PARTNER FILTERS
# -------------------------

st.sidebar.header("Partner Filters")

selected_region = st.sidebar.multiselect(
    "Region",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

selected_type = st.sidebar.multiselect(
    "Partner Type",
    options=sorted(df["PartnerType"].unique()),
    default=sorted(df["PartnerType"].unique())
)

selected_stage = st.sidebar.multiselect(
    "Stage",
    options=sorted(df["Stage"].unique()),
    default=sorted(df["Stage"].unique())
)

filtered_df = df[
    (df["Region"].isin(selected_region)) &
    (df["PartnerType"].isin(selected_type)) &
    (df["Stage"].isin(selected_stage))
]
# -------------------------
# KPI CALCULATIONS
# -------------------------

total_partners = len(filtered_df)

active_partners = len(
    filtered_df[filtered_df["Stage"] == "Active"]
)

total_pipeline = filtered_df["Pipeline"].sum()

total_revenue = filtered_df["Revenue"].sum()

# -------------------------
# KPI DASHBOARD
# -------------------------

st.subheader("Ecosystem Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Partners",
    total_partners
)

col2.metric(
    "Active Partners",
    active_partners
)

col3.metric(
    "Partner Pipeline",
    f"${total_pipeline:,.0f}"
)

col4.metric(
    "Partner Revenue",
    f"${total_revenue:,.0f}"
)

st.divider()

# -------------------------
# PARTNER PORTFOLIO
# -------------------------

st.subheader("Partner Portfolio")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)
st.divider()

st.subheader("Partner Prioritisation")

ranked_partners = filtered_df.sort_values(
    "PartnerScore",
    ascending=False
)

st.dataframe(
    ranked_partners[
        [
            "PartnerName",
            "PartnerType",
            "Stage",
            "PartnerScore",
            "Pipeline",
            "Revenue"
        ]
    ],
    column_config={
        "PartnerScore": st.column_config.NumberColumn(
            "Partner Score",
            format="%.1f"
        ),
        "Pipeline": st.column_config.NumberColumn(
            "Pipeline",
            format="$%d"
        ),
        "Revenue": st.column_config.NumberColumn(
            "Revenue",
            format="$%d"
        )
    },
    use_container_width=True,
    hide_index=True
)
# -------------------------
# PARTNERSHIP FUNNEL
# -------------------------

st.divider()
st.subheader("Partnership Lifecycle")

stage_order = [
    "Identified",
    "Qualified",
    "Discovery",
    "Negotiation",
    "Active"
]

stage_counts = (
    filtered_df["Stage"]
    .value_counts()
    .reindex(stage_order, fill_value=0)
)

funnel_df = pd.DataFrame({
    "Stage": stage_order,
    "Partners": stage_counts.values
})

lifecycle_chart = alt.Chart(funnel_df).mark_bar().encode(
    x=alt.X(
        "Stage:N",
        sort=[
            "Identified",
            "Qualified",
            "Discovery",
            "Negotiation",
            "Active"
        ],
        title="Partnership Stage"
    ),
    y=alt.Y(
        "Partners:Q",
        title="Number of Partners"
    ),
    tooltip=["Stage", "Partners"]
)

st.altair_chart(
    lifecycle_chart,
    use_container_width=True
)
# -------------------------
# PARTNER INTELLIGENCE PROFILE
# -------------------------

st.divider()
st.subheader("Partner Intelligence Profile")

selected_partner = st.selectbox(
    "Select a Partner",
    options=sorted(filtered_df["PartnerName"].unique())
)

partner = filtered_df[
    filtered_df["PartnerName"] == selected_partner
].iloc[0]

st.markdown(f"### {partner['PartnerName']}")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Partner Score",
    f"{partner['PartnerScore']:.1f}/100"
)

col2.metric(
    "Pipeline",
    f"${partner['Pipeline']:,.0f}"
)

col3.metric(
    "Revenue",
    f"${partner['Revenue']:,.0f}"
)

col4.metric(
    "Stage",
    partner["Stage"]
)

st.markdown("#### Partnership Assessment")

assessment_df = pd.DataFrame({
    "Dimension": [
        "Strategic Fit",
        "Technical Fit",
        "Market Overlap",
        "Revenue Potential",
        "Integration Potential"
    ],
    "Score": [
        partner["StrategicFit"],
        partner["TechnicalFit"],
        partner["MarketOverlap"],
        partner["RevenuePotential"],
        partner["IntegrationPotential"]
    ]
})

assessment_chart = alt.Chart(assessment_df).mark_bar().encode(
    x=alt.X(
        "Score:Q",
        scale=alt.Scale(domain=[0, 10]),
        title="Score"
    ),
    y=alt.Y(
        "Dimension:N",
        sort=None,
        title=""
    ),
    tooltip=["Dimension", "Score"]
)

st.altair_chart(
    assessment_chart,
    use_container_width=True
)
# -------------------------
# PARTNER RECOMMENDATION ENGINE
# -------------------------

# -------------------------
# PARTNER RECOMMENDATION ENGINE
# -------------------------

st.subheader("Recommended Partnership Action")

selected_partner_data = filtered_df[
    filtered_df["PartnerName"] == selected_partner
].iloc[0]

score = selected_partner_data["PartnerScore"]
pipeline = selected_partner_data["Pipeline"]
revenue = selected_partner_data["Revenue"]
stage = selected_partner_data["Stage"]

if score >= 85:
    recommendation = "Strategic Priority"
    action = (
        "Prioritise this partner for deeper strategic engagement, "
        "joint opportunities and potential co-selling initiatives."
    )

elif score >= 75 and pipeline >= 300000:
    recommendation = "High Growth Opportunity"
    action = (
        "Focus on converting the existing pipeline and identify "
        "additional joint opportunities to expand the partnership."
    )

elif revenue > 0 and stage == "Active":
    recommendation = "Expand Existing Partnership"
    action = (
        "The partnership is already generating revenue. Explore "
        "cross-sell opportunities, joint campaigns and deeper integration."
    )

elif stage in ["Qualified", "Discovery"]:
    recommendation = "Develop Partnership"
    action = (
        "Continue discovery and validate strategic alignment, "
        "commercial potential and technical compatibility."
    )

else:
    recommendation = "Monitor and Nurture"
    action = (
        "Maintain engagement while gathering more information "
        "before committing significant partnership resources."
    )

st.success(f"Recommendation: {recommendation}")

st.write(action)