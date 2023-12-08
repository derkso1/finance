import streamlit as st
import time
import plotly.express as px  # for interactive charts
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import re


st.set_option('deprecation.showPyplotGlobalUse', False)


#cache help avoid downloading the dataset again and again when rerunning app
@st.cache_data
def get_data() -> pd.DataFrame:
    return pd.read_csv("/Users/admin/code/derksol/finance/raw_data/df_graph.csv")


df_graph = get_data()

symbol_list = df_graph["symbol"].unique()
company_list = df_graph["companyName"].unique()

company_index = None

st.title("Stock Forecast")
st.subheader("Input your details:")



c10, c11 = st.columns(2)
with c10:
    name = st.text_input("Enter your name:")
with c11:
    surname = st.text_input("Enter your surname:")

c12, c13 = st.columns(2)
with c12:
    age = st.number_input("Enter your age:", min_value=18, max_value=100, step=1, key="age_input")
with c13:
    gender = st.selectbox("Select your gender:", ["Male", "Female"])

st.markdown("***")

company = st.selectbox('Chose the company you would like to invest in', company_list, index=None)

if not company == None:
    company_index = list(company_list).index(company)
else:
    company_index = None
'''
'''
st.markdown("_Alternatively select the symbol for that company directly_")
symbol = st.selectbox('Company symbol:', symbol_list, index=company_index)

st.markdown("***")

c15,c16,c17 = st.columns([0.25, 0.5, 0.25])
with c16:
    amount_invest = st.number_input("How much money would you like to invest (in $)?", value=1000, min_value=0, step=100, key="amount_input")


# Checkbox for terms and conditions
terms_and_conditions = st.checkbox("I agree to the Terms and Conditions - 100 days is not a licensed financial service provider and will not be liable for any losses incurred.")


def stock_graph(symbol, n_years, df):
    df_symbol = df[df['symbol'] == symbol].tail(n_years*4) # Here, can change .head based on user parameter (e.g., 2 years/ 8 quarters = head(8))
    df_symbol = df_symbol[['year_adj', 'close', 'close_predict']]
    df_symbol.rename(columns= {'close': 'Actual stock price', 'close_predict': 'Predicted stock price'}, inplace=True)
    df_symbol.set_index('year_adj', inplace=True)
    df_symbol.iloc[:-2, 1] = np.nan

     # Add a graph next to it for a chosen feature to analyse its % change alongside stock price change

    sns.set_theme(style="whitegrid") # White grid background
    plt.figure(figsize=(12, 6)) # Changing figure size
    plt.title(f'Quarterly Stock Price for {company}', fontsize=20, color='Black', pad='20', fontstyle='oblique')
    plt.ylabel('Stock Price', labelpad= 10.2, fontdict={
        'color':  'black',
        'weight': 'bold',
        'size': 14,
        } )
    plt.xlabel('Time Period', fontdict={
        'color':  'black',
        'weight': 'bold',
        'size': 14,
        } )
    plt.locator_params(nbins=6)
    plt.xticks(
        rotation=45,
        horizontalalignment='center',
        fontweight='light',
        fontsize='medium'
    )
    sns.lineplot(data=df_symbol, linewidth=4)

def stock_info(symbol, n_years, df):
    df_symbol = df[df['symbol'] == symbol].tail(n_years*4) # Here, can change .head based on user parameter (e.g., 2 years/ 8 quarters = head(8))
    df_symbol = df_symbol[['year_adj', 'close', 'close_predict']]
    df_symbol.rename(columns= {'close': 'Actual stock price', 'close_predict': 'Predicted stock price'}, inplace=True)
    df_symbol.set_index('year_adj', inplace=True)
    df_symbol.iloc[:-2, 1] = np.nan
    return df_symbol


# Submit Button, check point and progress bas
if st.button("Submit") and terms_and_conditions:
    with st.spinner(text='In progress'):
        time.sleep(0.5)
        st.success('Done')
    #st.success(f"Thank you, {name}! Your information has been submitted. You've invested ${amount:.2f}.")

    if company == None:
        company = company_list[list(symbol_list).index(symbol)]
    description = df_graph[df_graph["symbol"] == symbol]["description"].head(1).unique()[0]

    st.markdown("***")

    col1, col2 = st.columns([0.3, 0.7])
    #f"Show information for __{company}__"
    col1.image(df_graph[df_graph["symbol"] == symbol]["image"].head(1).unique()[0])
    col2.markdown(' '.join(re.split(r'(?<=[.])\s', description)[:3]))

    st.markdown("***")

    stock_info = stock_info(symbol=symbol, n_years=2, df=df_graph)

    act_value = stock_info.iloc[-1, 0]
    act_percent = (((stock_info.iloc[-1, 0]/stock_info.iloc[-2, 0])-1)*100)

    pred_value = stock_info.iloc[-1, 1]
    pred_percent = (((stock_info.iloc[-1, 1]/stock_info.iloc[-2, 1])-1)*100)

    delta_value =  (amount_invest * (1 + act_percent/100)) - amount_invest

    col3, col4, col5 = st.columns(3)
    col3.metric("Actual stock price Q4'23", '{0:.2f}$'.format(act_value), '{0:.2f}%'.format(act_percent))
    col4.metric("Predicted stock price Q4'23", '{0:.2f}$'.format(pred_value), '{0:.2f}%'.format(pred_percent))
    col5.metric("Profit/loss from the investment ", '{0:.2f}$'.format(delta_value), '{0:.2f}%'.format(act_percent))

    st.markdown("***")

    st.pyplot(fig=stock_graph(symbol=symbol, n_years=4, df=df_graph))
