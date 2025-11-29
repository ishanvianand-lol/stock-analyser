import streamlit as st
import pandas as pd
import pathlib

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .block-container {
        padding-top: 3rem; /* Adjust this value as needed */
        padding-bottom: 0rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');
        
    .stock-row {
    display: flex;
    padding: 10px 15px;
    border-bottom: 1px solid #333;
    align-items: center;
    transition: background 0.2s;
    }
    .stock-row:hover {
    background-color: rgba(255,255,255,0.05);
    }
    .stock-row .symbol {
    width: 15%;
    font-weight: bold;
    color: var(--primary-color);
    }
    .stock-row .name {
    width: 45%;
    }
    .stock-row .sector {
    width: 20%;
    opacity: 0.8;
    }
    .stock-row .country {
    width: 20%;
    opacity: 0.6;
    }
    body {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: "Poppins", sans-serif;
    }

    .col2 {
        max-height: 75vh;
        overflow-y: auto;
    }


    </style>
    """, unsafe_allow_html=True)

path = pathlib.Path("data/nasdaq_screener.csv")
df = pd.read_csv(path)

st.title("List of All Stocks")
filtered_df = df.copy()

# Search bar
query = st.text_input(
    label="", placeholder="Stock Name", label_visibility="collapsed"
)

# Search filter
if query:
    # Only search text columns
    text_cols = ["Symbol", "Name"]
    mask = filtered_df[text_cols].apply(lambda col: col.str.contains(query, case=False, na=False))
    filtered_df = filtered_df[mask.any(axis=1)]

col1, col2  = st.columns([4,10])

with col1:
        st.write("Filters")

        # Country Filter
        country = st.text_input("Country Name", value="")
        if country: 
            mask = filtered_df["Country"].str.contains(country, case=False, na=False)
            filtered_df = filtered_df[mask]

        # Market Cap Filter
        selection = st.pills("Market Cap", options=["Large","Mid","Small"], selection_mode="single")
        if selection == "Large":
            filtered_df = filtered_df[filtered_df["Market Cap"] >= 10**10]
        elif selection == "Mid":
            filtered_df = filtered_df[(filtered_df["Market Cap"] >= 2*10**9) & (filtered_df["Market Cap"] < 10**10)]
        elif selection == "Small":
            filtered_df = filtered_df[filtered_df["Market Cap"] < 2*10**9]

        # Sector Filter
        sector = st.pills("Sector",
                          options=["Industrial","Finance","Real Estate","Consumer Discretionary",
                                   "Health Care","Technology","Basic Materials","Consumer Staples","Energy",
                                   "Utilities","Telecommunications","Miscellaneous"],
                          selection_mode="multi")
        if sector:
            pattern = "|".join(sector)  
            mask = filtered_df["Sector"].str.contains(pattern, case=False, na=False)
            filtered_df = filtered_df[mask]
    
with col2:
    st.markdown(f"""
    <div class="stock-row">
    <span class="symbol">Symbol</span>
    <span class="name">Name</span>
    <span class="sector">Sector</span>
    <span class="country">Country</span>
    </div>
    """, unsafe_allow_html=True)

    for idx, row in filtered_df.iterrows():
        st.markdown(f"""
        <div class="stock-row">
        <span class="symbol">{row['Symbol']}</span>
        <span class="name">{row['Name']}</span>
        <span class="sector">{row['Sector']}</span>
        <span class="country">{row['Country']}</span>
        </div>
        """, unsafe_allow_html=True)
        
from footer import footer
footer()
