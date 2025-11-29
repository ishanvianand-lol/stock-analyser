# importing required modules -> streamlit, yfinance, pandas, time

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import mplfinance as mpf

st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .block-container {
        padding-top: 3rem; /* Adjust this value as needed */
        padding-bottom: 10rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    /* Button Styling */
    .stButton > button {
        font-family: "Poppins", sans-serif;
        width: 100%;
        background-color: #f0f0f0;
        color: #333333;
        font-weight: 600;
        font-size: 14px;
        padding: 0.35rem 1.5rem;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #e8e8e8;
        border-color: #d0d0d0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
    }
    
    .stButton > button:active {
        background-color: #e0e0e0;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
            
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

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

# Skelaton of the website
st.markdown("<h1 style='text-align: center;'>STOCK PRICES ANALYSER</h1>", unsafe_allow_html=True)
st.text_input("Stock Name", key="stock_name",placeholder="Enter Stock Symbol (Refer to List of All Stocks)")
stock_name = st.session_state.stock_name.upper()
stocks = pd.read_csv(r'D:\Downloads\nasdaq_screener_1764260895479.csv')


end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=50)).strftime('%Y-%m-%d')

def get_stock_data(stock_name, period, interval):

    df = yf.download(stock_name, period=period, interval=interval, auto_adjust=True)

    # ----------------------------
    # SPECIAL FIX FOR 1-DAY INTRADAY DATA
    # ----------------------------
    if period == "1d":
        # Fix MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]

        # Remove timezone
        if hasattr(df.index, "tz"):
            df.index = df.index.tz_localize(None)

        # Convert OHLCV to numeric
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna()

        return df  # For intraday, return here (already indexed by Datetime)

    # ----------------------------
    # NORMAL DAILY / WEEKLY / MONTHLY HANDLING
    # ----------------------------
    df = df.reset_index(drop=False).copy()

    # Flatten MultiIndex if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if col[0] != "Date" else "Date" for col in df.columns]

    # Convert to numeric
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna()

    # Convert Date to index
    if len(df) > 0 and "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)

    return df


if stock_name:
    if stock_name not in stocks['Symbol'].values:
        st.warning("Please enter a valid stock symbol from the 'List of All Stocks' page.")
    else: 
        Company_Name = stocks[stocks['Symbol'] == stock_name]['Name'].values[0]

        # Initialize session state
        if 'analyze_clicked' not in st.session_state:
            st.session_state.analyze_clicked = False

        if st.button("ANALYSE", type="secondary"):
            st.session_state.analyze_clicked = True

        if st.session_state.analyze_clicked and stock_name in stocks['Symbol'].values:
            # All your analysis code goes here
            # (the entire code block that currently runs after the button click)

            # fetching stock data using yfinance
            stock_data = yf.download(stock_name, start=start_date, 
                                        end=end_date, auto_adjust=True)
            stock_data.reset_index(inplace=True)

            # handling missing data
            if stock_data.isna().sum().sum() > 0:
                stock_data.fillna(method="ffill", inplace=True)

            data = pd.DataFrame()
            data["Date"] = stock_data["Date"]
            data["Close"] = stock_data["Close"]

            # calculating moving averages
            data["MA5"] = stock_data['Close'].rolling(window=5).mean()
            data["MA10"] = stock_data['Close'].rolling(window=10).mean()
            data["MA20"] = stock_data['Close'].rolling(window=20).mean()

            # daily returns
            data['Daily Return'] = stock_data['Close'].pct_change()

            # volatility of the stock
            data["Volatility"] = data['Daily Return'].std() * (252**0.5)

            # average rolling volume
            data["Avg Rolling Volume (10 days)"] = stock_data['Volume'].rolling(window=10).mean()

            # st.table((pd.concat([data.head(3), data.iloc[[4, 9, 19]]]))[["Date","Close","MA5","MA10","MA20"]])

            # local maximas and minimas
            data['Minima'] = data['Close'][(data['Close'].shift(1) > data['Close']) & (data['Close'].shift(-1) > data['Close'])]
            data['Maxima'] = data['Close'][(data['Close'].shift(1) < data['Close']) & (data['Close'].shift(-1) < data['Close'])]
            
            minimas = data["Minima"].dropna().tolist()
            maximas = data["Maxima"].dropna().tolist()
            indices_maxima = [i for i in range(len(data)) if pd.notna(data['Maxima'].iloc[i])]
            indices_minima = [i for i in range(len(data)) if pd.notna(data['Minima'].iloc[i])]

            # linear regression to estimate trend line
            X = np.array(range(len(data))).reshape(-1, 1)

            Y = np.array(data['Close']).reshape(-1, 1)
            Y2 = np.array(minimas).reshape(-1, 1)
            Y3 = np.array(maximas).reshape(-1, 1)

            model1 = LinearRegression().fit(X, Y)
            model2 = LinearRegression().fit(np.array(indices_minima).reshape(-1, 1), Y2)  
            model3 = LinearRegression().fit(np.array(indices_maxima).reshape(-1, 1), Y3)

            y_pred = model1.predict(np.array(range(len(data))).reshape(-1, 1))
            slope = model1.coef_[0][0]
            slope_minima = model2.coef_[0][0]
            slope_maxima = model3.coef_[0][0]

            if slope > 0 and slope_minima > 0 and slope_maxima > 0:
                trend = 'Uptrend'
            elif slope < 0 and slope_minima < 0 and slope_maxima < 0:
                trend = 'Downtrend'
            else:
                trend = 'Sideways'

            col1, col2 = st.columns([2.5,1.5])
            with col1:
                # Create figure and axis
                fig, ax = plt.subplots(figsize=(9,5), facecolor="#FFFFFFC2")  # wide figure for readability
                ax.set_facecolor("#FFFFFF94")  # subtle background

                # Plot actual closing price
                ax.plot(data['Date'], data['Close'], label='Close', color='black', linewidth=3)

                # Plot moving averages
                ax.plot(data['Date'], data['MA5'], label='MA5', color="#987A42", linewidth=2)
                ax.plot(data['Date'], data['MA10'], label='MA10', color="#4BB7E1", linewidth=2)
                ax.plot(data['Date'], data['MA20'], label='MA20', color="#E36DCE", linewidth=2)

                # Highlight bullish/bearish zones (MA5 vs MA20)
                ax.fill_between(
                    data['Date'], data['MA5'], data['MA20'],
                    where=data['MA5'] >= data['MA20'], facecolor="#2CE038", alpha=0.4,
                    interpolate=True, label='Bullish Zone'
                )
                ax.fill_between(
                    data['Date'], data['MA5'], data['MA20'],
                    where=data['MA5'] < data['MA20'], facecolor="#BB1414", alpha=0.4,
                    interpolate=True, label='Bearish Zone'
                )

                # Add title, labels, and legend
                ax.set_title(f'{Company_Name} ({stock_name})'.upper(), fontsize=18, fontweight='bold')
                ax.set_xlabel('Date', fontsize=14)
                ax.set_ylabel('Price', fontsize=14)
                ax.legend()

                # Rotate x-axis dates for readability
                plt.xticks(rotation=20)

                # Add grid for easier trend reading
                ax.grid(True, color='gray', linestyle='--', alpha=0.3)

                # Display in Streamlit
                st.pyplot(fig)
                col_1, col_2, col_3 = st.columns([1,1,2])

                col_1.metric("Open", f"${stock_data['Open'].iloc[-1][0]:.2f}")
                col_2.metric("Close", f"${stock_data['Close'].iloc[-1][0]:.2f}")
                col_3.metric("Volume", f"${stock_data['Volume'].iloc[-1][0]:.2f}")


            with col2:
                st.markdown("""
                    <style>
                    [data-testid=column]:nth-of-type(2) [data-testid=stVerticalBlock]{
                        gap: 0.5rem;  /* Reduce gap between elements */
                    }
                    [data-testid=column]:nth-of-type(2) .element-container {
                        margin-bottom: 0.3rem;  /* Reduce margin */
                    }
                    </style>
                    """, unsafe_allow_html=True)
                st.markdown("## 📊**OBSERVATIONS**")

                # Trend
                if trend == 'Uptrend':
                    st.success(f"📈 **Trend:** {trend}")
                elif trend == 'Downtrend':
                    st.error(f"📉 **Trend:** {trend}")
                else:
                    st.warning(f"↔️ **Trend:** {trend}")
                
            
                # Moving Average Crossover Signals  
                crossover_found = False
                crossover_type = None
                crossover_date = None

                for i in range(len(data)-1, 0, -1):
                    if pd.notna(data['MA5'].iloc[i]) and pd.notna(data['MA20'].iloc[i]) and pd.notna(data['MA5'].iloc[i-1]) and pd.notna(data['MA20'].iloc[i-1]):
                        if data['MA5'].iloc[i-1] > data['MA20'].iloc[i-1] and data['MA5'].iloc[i] <= data['MA20'].iloc[i]:
                            crossover_found = True
                            crossover_type = "Bullish Crossover"
                            crossover_date = data['Date'].iloc[i].strftime('%Y-%m-%d')
                            break
                        elif data['MA5'].iloc[i-1] < data['MA20'].iloc[i-1] and data['MA5'].iloc[i] >= data['MA20'].iloc[i]:
                            crossover_found = True
                            crossover_type = "Bearish Crossover"
                            crossover_date = data['Date'].iloc[i].strftime('%Y-%m-%d')
                            break   
                if crossover_found:
                    if crossover_type == "Bullish Crossover":
                        st.success(f"🔄 **{crossover_type}** detected on {crossover_date}")
                    else:
                        st.error(f"🔄 **{crossover_type}** detected on {crossover_date}")
                else:
                    st.info("🔄 No recent moving average crossovers detected")      
                
            
                # Short-term trend
                recent_slope = (data['Close'].iloc[-1] - data['Close'].iloc[-5]) / 5
                if recent_slope > 0:
                    st.metric("📈 Short-term Trend", "Increasing", f"+${recent_slope:.2f}/day", delta_color="normal")
                elif recent_slope < 0:
                    st.metric("📉 Short-term Trend", "Decreasing", f"-${abs(recent_slope):.2f}/day", delta_color="inverse")
                else:
                    st.metric("➡️ Short-term Trend", "Flat", "0.00/day", delta_color="off")
                
            
                # Support and Resistance
                if len(minimas) > 0:
                    support = minimas[-1]
                else:
                    support = data['Close'].min()

                if len(maximas) > 0:
                    resistance = maximas[-1]
                else:
                    resistance = data['Close'].max()
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("🟢 Support", f"${support:.2f}")
                with col_b:
                    st.metric("🔴 Resistance", f"${resistance:.2f}")
                
            
                # Volume Signal
                recent_vol = data['Avg Rolling Volume (10 days)'].iloc[-2:]
                avg_vol = data['Avg Rolling Volume (10 days)'].iloc[:-2].mean()

                if recent_vol.mean() > avg_vol:
                    st.success("📊 **Volume:** Spiked in last 2 days (Trend confirmed)")
                else:
                    st.info("📊 **Volume:** Normal levels")
                
            
                # Volatility Level
                vol = data["Volatility"].iloc[-1]

                if vol < 0.02:
                    st.success(f"📉 **Volatility:** Low ({vol:.2%})")
                elif vol < 0.05:
                    st.warning(f"📊 **Volatility:** Moderate ({vol:.2%})")
                else:
                    st.error(f"📈 **Volatility:** High ({vol:.2%})")
            st.divider()
            
            time_period_for_chart = st.pills("Time Period", 
                                 options=['1 day', '1 month', '3 months', '6 months', '1 year'], 
                                 selection_mode="single", default = "3 months",
                                 key="time_period_for_chart")

            time_period = st.session_state.time_period_for_chart

            interval = "1d" # default interval for time period > 1 day
            if time_period == "1 day":
                period = "1d"
                interval = "5m"
            elif time_period == "1 month":
                period = "1mo"
            elif time_period == "3 months":
                period = "3mo"
            elif time_period == "6 months":
                period = "6mo"
            elif time_period == "1 year":
                period = "1y"
           
            # ALWAYS refresh chart data when time period or interval changes
            data_chart = get_stock_data(stock_name, period, interval)
            
            col1, col2 = st.columns([2,1])
            with col1:
                if len(data_chart) == 0:
                    st.error(f"No data available for {time_period} with the selected interval. Try a different time period.")
                else:
                    # Calculating VWAP Volume-Weighted Average Price

                    data_chart['TP'] = (data_chart['High']
                                + data_chart['Low']
                                + data_chart['Close']) / 3 # Average of High, Low, Close = Typical Price
                    
                    data_chart['CumSumVolume'] = data_chart['Volume'].cumsum()
                    data_chart['CumTPVolume'] = (data_chart['TP'] * data_chart['Volume']).cumsum()
                    
                    data_chart['VWAP'] = data_chart['CumTPVolume'] / data_chart['CumSumVolume']

                    apds = [
                        mpf.make_addplot(data_chart["VWAP"], color='blue', width=1.2),
                    ]
                    fig_chart, axes_stock = mpf.plot(data_chart,
                                                    type='candle', 
                                                    figratio=(10,4),      # wider than tall
                                                    figscale=0.9,         # scales down entire chart
                                                    style='yahoo', 
                                                    title=f'{stock_name} Candlestick Chart', 
                                                    ylabel='Price (USD)', 
                                                    addplot = apds,
                                                    returnfig=True)  
                
                    st.pyplot(fig_chart)
               
                with col2:
                    recent_close = data_chart['Close'].iloc[-1]
                    recent_vwap = data_chart['VWAP'].iloc[-1]

                    st.subheader('VWAP INTERPRETATION')

                    if recent_close > recent_vwap:
                        st.success('Price is **above VWAP** → buyers in control, bullish environment.')
                    elif recent_close < recent_vwap:
                        st.error("Price is **below VWAP** → sellers in control, bearish environment.")
                    else:
                        st.info("Price is exactly at VWAP → neutral / mean reversion zone.")


                # Support Resistance Behaviour

                last_2_close = data_chart['Close'].iloc[-2]
                last_2_vwap = data_chart['VWAP'].iloc[-2]

                if last_2_close < last_2_vwap and recent_close > recent_vwap:
                    st.warning("Price **broke above VWAP** → potential upward reversal.")
                elif last_2_close > last_2_vwap and recent_close < recent_vwap:
                    st.warning("Price **broke below VWAP** → potential downward reversal.")
                else:
                    st.info('No Trend Reversal')
            
            st.divider()

            # FINAL ADVICE -> not best

            last3 = data_chart.tail(3)

            # using VWAP
            above_vwap = (last3['Close'] > last3['VWAP']).sum()
            below_vwap = (last3['Close'] < last3['VWAP']).sum()




from footer import footer
footer()
