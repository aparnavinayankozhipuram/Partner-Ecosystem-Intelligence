import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="AI Partner Advisor",
    layout="wide"
)

st.title("AI Partner Advisor")
st.caption(
    "Ask strategic questions about your partner ecosystem, "
    "pipeline, revenue and partnership opportunities."
)

# -------------------------
# LOAD DATA
# -------------------------

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


# -------------------------
# CALCULATE BUSINESS EVIDENCE
# -------------------------

highest_score = df.loc[df["PartnerScore"].idxmax()]
highest_pipeline = df.loc[df["Pipeline"].idxmax()]
highest_revenue = df.loc[df["Revenue"].idxmax()]

zero_revenue = df[df["Revenue"] == 0].sort_values(
    "PartnerScore",
    ascending=False
)

active_partners = df[df["Stage"] == "Active"]

total_pipeline = df["Pipeline"].sum()
total_revenue = df["Revenue"].sum()


# -------------------------
# CREATE EVIDENCE SUMMARY
# -------------------------

evidence_summary = f"""
ECOSYSTEM SUMMARY

Total Partners: {len(df)}
Total Pipeline: ${total_pipeline:,.0f}
Total Revenue: ${total_revenue:,.0f}

Highest Partner Score:
{highest_score['PartnerName']}
Score: {highest_score['PartnerScore']}/100
Pipeline: ${highest_score['Pipeline']:,.0f}
Revenue: ${highest_score['Revenue']:,.0f}
Stage: {highest_score['Stage']}

Highest Pipeline:
{highest_pipeline['PartnerName']}
Pipeline: ${highest_pipeline['Pipeline']:,.0f}
Score: {highest_pipeline['PartnerScore']}/100
Revenue: ${highest_pipeline['Revenue']:,.0f}
Stage: {highest_pipeline['Stage']}

Highest Revenue:
{highest_revenue['PartnerName']}
Revenue: ${highest_revenue['Revenue']:,.0f}
Pipeline: ${highest_revenue['Pipeline']:,.0f}
Score: {highest_revenue['PartnerScore']}/100
Stage: {highest_revenue['Stage']}
"""


# Add zero-revenue opportunities
evidence_summary += "\nHIGH-POTENTIAL PARTNERS WITH ZERO REVENUE\n"

for _, partner in zero_revenue.iterrows():

    evidence_summary += f"""
{partner['PartnerName']}
Score: {partner['PartnerScore']}/100
Pipeline: ${partner['Pipeline']:,.0f}
Stage: {partner['Stage']}
"""


# -------------------------
# CREATE FULL PARTNER CONTEXT
# -------------------------

def create_partner_context(dataframe):

    context = []

    for _, partner in dataframe.iterrows():

        partner_info = f"""
Partner: {partner['PartnerName']}
Type: {partner['PartnerType']}
Industry: {partner['Industry']}
Region: {partner['Region']}
Stage: {partner['Stage']}

Partner Score: {partner['PartnerScore']}/100

Strategic Fit: {partner['StrategicFit']}/10
Technical Fit: {partner['TechnicalFit']}/10
Market Overlap: {partner['MarketOverlap']}/10
Revenue Potential: {partner['RevenuePotential']}/10
Integration Potential: {partner['IntegrationPotential']}/10

Pipeline: ${partner['Pipeline']:,.0f}
Revenue: ${partner['Revenue']:,.0f}
"""

        context.append(partner_info)

    return "\n".join(context)


partner_context = create_partner_context(df)


# -------------------------
# OLLAMA AI FUNCTION
# -------------------------

def ask_ollama(question):

    prompt = f"""
You are an AI Partner Ecosystem Advisor supporting a
Partnership Manager.

Python has already calculated important commercial facts.
Treat these calculated facts as authoritative.

CALCULATED BUSINESS EVIDENCE
----------------------------
{evidence_summary}


FULL PARTNER DATA
-----------------
{partner_context}


USER QUESTION
-------------
{question}


INSTRUCTIONS
------------

Use ONLY the supplied partner data and calculated evidence.

Do not invent partners, numbers, stages, industries,
revenue, pipeline or scores.

Do not recalculate numerical rankings if Python has already
provided them.

If the user asks which partner to concentrate on, do not
choose a partner arbitrarily.

Evaluate the decision using:

1. Partner Score
2. Pipeline
3. Current Revenue
4. Partnership Stage
5. Strategic Fit
6. Revenue Potential
7. Integration Potential

Explain the trade-off between:

- protecting existing revenue;
- converting pipeline;
- developing high-potential partners.

When useful, recommend different partners for different
objectives rather than pretending one partner is best
for every objective.

Support recommendations with actual numbers from the data.

If the available data is insufficient for a confident
recommendation, clearly state what additional information
would help.

Keep the answer concise and commercially practical.
"""

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:3b",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        return response.json()["response"]

    except requests.exceptions.RequestException as error:

        return (
            "Unable to connect to Ollama. "
            "Please check that Ollama is running.\n\n"
            f"{error}"
        )


# -------------------------
# STREAMLIT INTERFACE
# -------------------------

st.subheader("Ask about your partner ecosystem")

question = st.text_input(
    "What would you like to know?",
    placeholder="Example: Which partner should I concentrate on?"
)

if st.button("Analyse Partnership Data"):

    if question.strip():

        with st.spinner("Analysing partner ecosystem..."):

            answer = ask_ollama(question)

        st.subheader("AI Partnership Analysis")

        st.write(answer)

    else:

        st.warning(
            "Enter a question about the partner ecosystem."
        )


# -------------------------
# SHOW SUPPORTING EVIDENCE
# -------------------------

with st.expander("View calculated partnership evidence"):

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Highest Partner Score",
        highest_score["PartnerName"],
        f"{highest_score['PartnerScore']}/100"
    )

    col2.metric(
        "Largest Pipeline",
        highest_pipeline["PartnerName"],
        f"${highest_pipeline['Pipeline']:,.0f}"
    )

    col3.metric(
        "Highest Revenue",
        highest_revenue["PartnerName"],
        f"${highest_revenue['Revenue']:,.0f}"
    )

    st.subheader("Zero-Revenue Opportunities")

    st.dataframe(
        zero_revenue[
            [
                "PartnerName",
                "Stage",
                "PartnerScore",
                "Pipeline",
                "Revenue"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


# -------------------------
# EXAMPLE QUESTIONS
# -------------------------

st.divider()

st.caption(
    "Try: Which partner should I concentrate on? • "
    "Which partners have strong potential but no revenue? • "
    "Compare FinConnect and NexaCloud • "
    "Where is the biggest conversion opportunity? • "
    "Which existing partnership should I protect?"
)