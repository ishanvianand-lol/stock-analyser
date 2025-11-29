import streamlit as st

main_page = st.Page("main_page.py", title="Home", icon=":material/home:", default=True)
stocks_page = st.Page("stocks.py", title="List of All Stocks", icon=":material/document_search:")
compare_page = st.Page("compare_stocks.py", title="Compare Stocks", icon=":material/text_compare:")

pg = st.navigation([main_page, stocks_page, compare_page], position="top")
st.set_page_config(page_title="Stock Analyser", page_icon=":material/finance_chip:")
pg.run()