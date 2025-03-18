import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from stocknews import StockNews

st.set_page_config(page_title="Finserve Dashboard", layout="wide")

page = st.sidebar.radio("Navigation", ["Home", "Stock Analysis"])

if page == "Home":
    st.title("Home Page")
    st.title("Finserve Dashboard 💹")
    st.subheader("Stay updated with real-time stock market trends!")

    # Display popular indices
    indices = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "Dow Jones": "^DJI",
        "Nifty 50": "^NSEI",
        "Sensex": "^BSESN"
    }

    index_data = {name: yf.Ticker(symbol).history(period="1d") for name, symbol in indices.items()}

    st.subheader("📊 Market Indices")
    col1, col2 = st.columns(2)
    for i, (name, data) in enumerate(index_data.items()):
        if not data.empty:
            price = data["Close"].iloc[-1]
            (col1 if i % 2 == 0 else col2).metric(name, f"{price:.2f}")

    # Display trending stocks
    col1, col2 =st.columns(2)
   
    with col1:
        st.subheader("Global Treding Stocks 🔥")
        trending_tickers = ["AAPL", "TSLA", "GOOGL", "AMZN", "MSFT"]
        for ticker in trending_tickers:
            stock = yf.Ticker(ticker)
            price = stock.history(period="1d")["Close"].iloc[-1]
            st.write(f"**{ticker}:** ${price:.2f}")

    with col2:
        # List of popular Indian stocks (NSE)
        st.subheader("Indian Trending Stocks 📌")
        indian_trending_tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]

        for ticker in indian_trending_tickers:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")

            if not data.empty:
                price = data["Close"].iloc[-1]
                st.write(f"**{ticker.replace('.NS', '')}:** ₹{price:.2f}")
            else:
                st.write(f"**{ticker.replace('.NS', '')}:** Data unavailable")

    # Function to plot real-time intraday charts
    def plot_intraday_chart(symbol, title, chart_key):
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d", interval="5m")

        if not data.empty:
            fig = go.Figure()

            # Line chart with color change
            fig.add_trace(go.Scatter(
                x=data.index, 
                y=data["Close"], 
                mode="lines", 
                fill="tozeroy",
                line=dict(color="red" if data["Close"].iloc[-1] < data["Open"].iloc[0] else "green"),
                name="Price"
            ))

            # Customize layout
            fig.update_layout(
                title=title,
                xaxis_title="Time",
                yaxis_title="Price",
                hovermode="x unified",
                template="plotly_white"
            )

            st.plotly_chart(fig, use_container_width=True, key=chart_key)
        else:
            st.warning(f"⚠ No intraday data available for {title}.")

 # 📈 Live Intraday Chart for Nifty 50
    st.subheader("📈 Nifty 50 - Intraday Chart (Live)")

    nifty = yf.Ticker("^NSEI")
    intraday_data = nifty.history(period="1d", interval="5m")

    if not intraday_data.empty:
        fig = go.Figure()

        # Line chart with color change
        fig.add_trace(go.Scatter(
            x=intraday_data.index, 
            y=intraday_data["Close"], 
            mode="lines", 
            line=dict(color="red" if intraday_data["Close"].iloc[-1] < intraday_data["Open"].iloc[0] else "green"),
            name="Price"
        ))

        # Customize layout
        fig.update_layout(
            title="Nifty 50 Intraday (5-min interval)",
            xaxis_title="Time",
            yaxis_title="Price",
            hovermode="x unified",
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠ No intraday data available.")

    # 📈 Live Intraday Chart for Dow Jones
    st.subheader("📈 Dow Jones - Intraday Chart (Live)")

    dow_jones = yf.Ticker("^DJI")
    intraday_data = dow_jones.history(period="1d", interval="5m")

    if not intraday_data.empty:
        fig = go.Figure()

        # Line chart with color change
        fig.add_trace(go.Scatter(
            x=intraday_data.index, 
            y=intraday_data["Close"], 
            mode="lines", 
            line=dict(color="red" if intraday_data["Close"].iloc[-1] < intraday_data["Open"].iloc[0] else "green"),
            name="Price"
        ))

        # Customize layout
        fig.update_layout(
            title="Dow Jones Intraday (5-min interval)",
            xaxis_title="Time",
            yaxis_title="Price",
            hovermode="x unified",
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("⚠ No intraday data available.")

elif page == "Stock Analysis":
    # Your existing stock analysis code goes here
    pass

    # Set page title
    st.title("📈 Stock Market Dashboard")

    # Sidebar inputs with default dates
    today = datetime.now()
    default_start = today - timedelta(days=365)
    ticker = st.sidebar.text_input('Stock Ticker Symbol', value='MSFT')
    start_date = st.sidebar.date_input('Start Date', value=default_start)
    end_date = st.sidebar.date_input('End Date', value=today)

    # Validate inputs
    if not ticker:
        st.warning("Please enter a stock ticker symbol.")
    elif start_date >= end_date:
        st.error("Start date must be before end date.")
    else:
        # Fetch stock data
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            intraday = stock.history(period="1d", interval="5m")  # 1-day intraday data
            info = stock.info

            if hist.empty:
                st.error("No historical data found! Check the stock symbol or date range.")
            elif intraday.empty:
                st.error("No intraday data found!")
            else:
                # Extract key financial data
                current_price = info.get("regularMarketPrice", "N/A")
                prev_close = info.get("regularMarketPreviousClose", "N/A")
                price_change = current_price - prev_close if current_price != "N/A" and prev_close != "N/A" else "N/A"
                percent_change = (price_change / prev_close * 100) if prev_close != "N/A" and price_change != "N/A" else "N/A"
                after_hours_price = info.get("postMarketPrice", "N/A")

                # Display stock price and percentage change
                st.markdown(f"## {info.get('longName', ticker)} ({ticker})")
                st.markdown(f"### **{current_price} USD**")
                
                if price_change != "N/A" and percent_change != "N/A":
                    st.markdown(f"**{'🔺' if price_change >= 0 else '🔻'} {price_change:.2f} ({percent_change:.2f}%) today**")
                else:
                    st.markdown("**Price change data not available**")

                if after_hours_price != "N/A":
                    st.markdown(f"📌 **After Hours: {after_hours_price} USD**")

                # Display key stock details
                col1, col2, col3 = st.columns(3)
                col1.metric("Open", info.get("open", "N/A"))
                col2.metric("High", info.get("dayHigh", "N/A"))
                col3.metric("Low", info.get("dayLow", "N/A"))

                col1, col2, col3 = st.columns(3)
                col1.metric("Mkt Cap", f"{info.get('marketCap', 'N/A'):,}" if info.get('marketCap') else "N/A")
                col2.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else "N/A")
                col3.metric("Div Yield", f"{info.get('dividendYield', 'N/A'):.2%}" if info.get('dividendYield') else "N/A")

                # Stock Price Chart - Historical
                if isinstance(hist.columns, pd.MultiIndex):
                    hist.columns = [col[0] for col in hist.columns]  # Flatten multi-index
                if isinstance(intraday.columns, pd.MultiIndex):
                    intraday.columns = [col[0] for col in intraday.columns]

                fig1 = px.line(hist, x=hist.index, y='Close', title=f'{ticker} Stock Price History')
                st.plotly_chart(fig1)

                # Stock Price Chart - Intraday (1-Day)
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=intraday.index, y=intraday["Close"], mode="lines", name="Stock Price"))
                fig2.update_layout(title="Stock Price (1D)", xaxis_title="Time", yaxis_title="Price (USD)")
                st.plotly_chart(fig2)

                pricing_data, fundamental_data, news = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

                # Pricing Data Section (Updated)
                with pricing_data:
                    st.header("Price Movements")
                    st.subheader("Historical Data Table")

                    # Reset index to make date a column
                    hist_display = hist.reset_index()

                    # Format the date column
                    hist_display['Date'] = hist_display['Date'].dt.strftime('%Y-%m-%d')

                    # Calculate % Change (Daily Returns)
                    hist_display["% Change"] = hist_display["Close"].pct_change().fillna(0) * 100  # Convert to percentage

                    # Columns to display
                    selected_columns = ['Date', 'Open', 'High', 'Low', 'Close', '% Change', 'Volume']

                    # Check if "Adj Close" exists and add it
                    if 'Adj Close' in hist_display.columns:
                        selected_columns.insert(5, 'Adj Close')

                    # Filter only the selected columns
                    hist_display = hist_display[selected_columns]

                    # Round numeric columns to 2 decimal places
                    for col in ['Open', 'High', 'Low', 'Close', '% Change', 'Volume']:
                        if col in hist_display:
                            hist_display[col] = hist_display[col].round(2)

                    # Display the dataframe
                    st.dataframe(hist_display, use_container_width=True)

                    # Add download button for CSV
                    csv = hist_display.to_csv(index=False)
                    st.download_button(
                        label="Download data as CSV",
                        data=csv,
                        file_name=f'{ticker}_stock_data.csv',
                        mime='text/csv',
                    )
                    
                    # Multiple line charts for different metrics
                    st.subheader("Price Charts")
                    
                    # OHLC Chart
                    fig_ohlc = go.Figure()
                    fig_ohlc.add_trace(go.Scatter(x=hist.index, y=hist['Open'], mode='lines', name='Open'))
                    fig_ohlc.add_trace(go.Scatter(x=hist.index, y=hist['High'], mode='lines', name='High'))
                    fig_ohlc.add_trace(go.Scatter(x=hist.index, y=hist['Low'], mode='lines', name='Low'))
                    fig_ohlc.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Close'))
                    fig_ohlc.update_layout(title='OHLC Price Data', xaxis_title='Date', yaxis_title='Price (USD)')
                    st.plotly_chart(fig_ohlc, use_container_width=True)
                    
                    # Volume Chart
                    fig_volume = px.bar(hist, x=hist.index, y='Volume', title='Trading Volume')
                    st.plotly_chart(fig_volume, use_container_width=True)
                    
                    # Candlestick Chart
                    fig_candle = go.Figure(data=[go.Candlestick(
                        x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close'],
                        name='Candlestick'
                    )])
                    fig_candle.update_layout(title='Candlestick Chart', xaxis_title='Date', yaxis_title='Price (USD)')
                    st.plotly_chart(fig_candle, use_container_width=True)

                with fundamental_data:
                    st.header('Fundamental Data')
                    
                    # Create two columns
                    col1, col2 = st.columns(2)
                    
                    # Company info in first column
                    with col1:
                        st.subheader("Company Information")
                        company_info = {
                            "Sector": info.get("sector", "N/A"),
                            "Industry": info.get("industry", "N/A"),
                            "Employees": info.get("fullTimeEmployees", "N/A"),
                            "Country": info.get("country", "N/A"),
                            "Website": info.get("website", "N/A")
                        }
                        for key, value in company_info.items():
                            st.write(f"**{key}:** {value}")
                    
                    # Financial metrics in second column
                    with col2:
                        st.subheader("Financial Metrics")
                        financial_metrics = {
                            "Market Cap": f"${info.get('marketCap', 'N/A'):,}" if info.get('marketCap') else "N/A",
                            "Forward P/E": f"{info.get('forwardPE', 'N/A'):.2f}" if info.get('forwardPE') else "N/A",
                            "Trailing P/E": f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else "N/A",
                            "Dividend Yield": f"{info.get('dividendYield', 'N/A'):.2%}" if info.get('dividendYield') else "N/A",
                            "52 Week High": f"${info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if info.get('fiftyTwoWeekHigh') else "N/A",
                            "52 Week Low": f"${info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if info.get('fiftyTwoWeekLow') else "N/A"
                        }
                        for key, value in financial_metrics.items():
                            st.write(f"**{key}:** {value}")

                    # Fetch financial statements
                    st.subheader("📊 Financial Statements")

                    try:
                        balance_sheet = stock.balance_sheet
                        income_statement = stock.financials
                        cash_flow = stock.cashflow

                        st.write("### Balance Sheet")
                        st.dataframe(balance_sheet)

                        st.write("### Income Statement")
                        st.dataframe(income_statement)

                        st.write("### Cash Flow Statement")
                        st.dataframe(cash_flow)

                    except Exception as e:
                        st.error(f"Could not fetch financial statements: {e}")


                    # Business Summary
                    st.subheader("Business Summary")

                    # Fetch the business summary
                    business_summary = info.get("longBusinessSummary", "No business summary available.")

                    # Split the summary into three paragraphs
                    if business_summary != "No business summary available.":
                        sentences = business_summary.split(". ")  # Split by sentence
                        third = len(sentences) // 3  # Divide into 3 parts

                        # Ensure at least three sections exist
                        para1 = ". ".join(sentences[:third]) + "." if third > 0 else business_summary
                        para2 = ". ".join(sentences[third:2 * third]) + "." if third > 0 else ""
                        para3 = ". ".join(sentences[2 * third:]) if third > 0 else ""

                        # Display as separate paragraphs
                        st.write(para1)
                        st.write(para2)
                        st.write(para3)
                    else:
                        st.write(business_summary)
                with news:
                    st.header('Top 10 News')

                    try:
                        # Fetch stock news using StockNews
                        sn = StockNews(ticker, save_news=False)
                        news_data = sn.read_rss()

                        if not news_data.empty:
                            for i, row in news_data.head(10).iterrows():  # Display top 10 news
                                st.subheader(row["title"])
                                st.write(f"**Date & Time:** {row.get('published', 'N/A')}")
                                st.write(row["summary"] if "summary" in row else "No summary available.")
                                if "link" in row:
                                    st.markdown(f"[Read more]({row['link']})")
                                st.markdown("---")
                        else:
                            st.write("No recent news available.")
                    
                    except Exception as e:
                        st.error(f"Could not fetch news: {e}")
                        st.write("No recent news available.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.write("Please check the stock ticker symbol and try again.")
