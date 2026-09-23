import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Partner Profile",
    layout="wide"
)

st.title("Partner Profile")
st.caption("Detailed partnership performance and strategic assessment")

df = pd.read_csv("partners.csv")

# Calculate Partner Score
df["PartnerScore"] = (
    df["StrategicFit"] * 0.25 +
    df["TechnicalFit"] * 0.20 +
    df["MarketOverlap"] * 0.20 +
    df["RevenuePotential"] * 0.20 +
    df["IntegrationPotential"] * 0.15
) * 10

df["PartnerScore"] = df["PartnerScore"].round(1)

# Partner selector
selected_partner = st.selectbox(
    "Select Partner",
    df["PartnerName"].tolist()
)

partner = df[
    df["PartnerName"] == selected_partner
].iloc[0]

st.divider()

# Partner name
st.header(selected_partner)

# Main metrics
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Partner Score",
    f"{partner['PartnerScore']}/100"
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

# Partnership Assessment
st.subheader("Partnership Assessment")

assessment = pd.DataFrame({
    "Category": [
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

chart = (
    alt.Chart(assessment)
    .mark_bar()
    .encode(
        x=alt.X(
            "Score:Q",
            scale=alt.Scale(domain=[0, 10]),
            title="Score"
        ),
        y=alt.Y(
            "Category:N",
            sort=None,
            title=None
        ),
        tooltip=[
            "Category",
            "Score"
        ]
    )
)

st.altair_chart(
    chart,
    use_container_width=True
)

# Recommendation
st.subheader("Recommended Partnership Action")

score = partner["PartnerScore"]
pipeline = partner["Pipeline"]
revenue = partner["Revenue"]
stage = partner["Stage"]

if score >= 85:
    recommendation = "Strategic Priority"
    action = (
        "Prioritise this partner for deeper strategic engagement, "
        "joint opportunities and potential co-selling initiatives."
    )

elif score >= 75 and pipeline >= 300000:
    recommendation = "High Growth Opportunity"
    action = (
        "Focus on converting the existing pipeline and identifying "
        "additional joint opportunities."
    )

elif revenue > 0 and stage == "Active":
    recommendation = "Expand Existing Partnership"
    action = (
        "Explore cross-sell opportunities, joint campaigns "
        "and deeper integration."
    )

elif stage in ["Qualified", "Discovery"]:
    recommendation = "Develop Partnership"
    action = (
        "Continue discovery and validate strategic, commercial "
        "and technical alignment."
    )

else:
    recommendation = "Monitor and Nurture"
    action = (
        "Maintain engagement while gathering more information."
    )

st.success(f"Recommendation: {recommendation}")
st.write(action)