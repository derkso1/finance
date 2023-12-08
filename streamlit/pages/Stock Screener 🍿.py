import streamlit as st
import pandas as pd
import time
from IPython.display import Image, HTML
import plotly.express as px
import plotly.io as pio
#pio.templates - for preety plotly templates

#cache help avoid downloading the dataset again and again when rerunning app
@st.cache_data
def get_data() -> pd.DataFrame:
    return pd.read_csv("/Users/admin/code/derksol/finance/raw_data/df_final_3.csv")

def get_information() -> pd.DataFrame:
    return pd.read_csv("/Users/admin/code/derksol/finance/raw_data/features_industry_raw.csv")

def path_to_image_html(path):
    return '<img src="' + path + '" style=max-height:48px;"/>'

def convert_df(input_df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
     return input_df.to_html(escape=False, formatters=dict(Image=path_to_image_html),index=False)



sector_dict = {'Basic Materials': 'sector_Basic Materials',
               'Communication Services': 'sector_Communication Services',
               'Consumer Cyclical': 'sector_Consumer Cyclical',
               'Consumer Defensive': 'sector_Consumer Defensive',
               'Energy': 'sector_Energy',
               'Financial Services':'sector_Financial Services',
               'Healthcare': 'sector_Healthcare',
               'Industrials': 'sector_Industrials',
               'Real Estate':'sector_Real Estate',
               'Technology':'sector_Technology',
               'Utlities':'sector_Utilities'}

size_dict = {'Large':'size_large',
             'Medium':'size_medium',
             'Small':'size_small'}



st.title("Stock Screener")

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

#Risk Appetite Slider
st.subheader("Select your preferences:")
risk_options = ['low', 'medium', 'high']
strategy = st.select_slider("Choose your level of risk",
                            options=risk_options)
if strategy == "low":
    st.success(f"Your risk strategy is {strategy}")
elif strategy == "medium":
    st.warning(f"Your risk strategy is {strategy}")
elif strategy == "high":
    st.error(f"Your risk strategy is {strategy}")
#Company size
size = st.radio("Select your company size:", ["All", "Small", "Medium", "Large"])
# Check if "None" is selected
st.info(f"Selected Company Size: {size}")
#Company sector
sector = [None, 'Basic Materials', 'Communication Services', 'Consumer Cyclical', 'Consumer Defensive',
                    'Energy', 'Financial Services', 'Healthcare', 'Industrials', 'Real Estate', 'Technology', 'Utilities']
selected_sector = st.selectbox("Select the sector to invest in:", sector_dict.keys(), index=None, placeholder="Leave empty if no sector preference")
# Display the selected company sector
st.info(f"Selected Sector: {selected_sector}")

# Checkbox for terms and conditions
terms_and_conditions = st.checkbox("I agree to the Terms and Conditions - 100 days is not a licensed financial service provider and will not be liable for any losses incurred.")
#Getting data

def model_chosen(size, sector,df): # Paramters here need be strings (e.g. 'small', 'indutrials')
    # This will split dataset by chosen sector (sector will be matched by chosen drop down list of sector options)
    sector_input = sector # This should be inputted as a string
    sector_input = selected_sector.title() ## This will capitalise first letter of each word to align with sector column names
    df_by_sector = df[df[f'sector_{sector_input}'] == 1]
    df_by_sector.head()
    # This will split this previous dataset by chosen size (size will be matched by chosen drop down list of size options)
    size_input = size # This should be interpreted as a string
    size_input = size_input.lower() ## This will make letters of each word lowercase to align with size column names
    df_by_both = df_by_sector[df_by_sector[f'size_{size_input}'] == 1]
    df_by_both.head()
     # Create column for average quarterly return in new dataframe
    df_return = df_by_both.groupby('symbol').mean()[['close_percent']].reset_index()
    df_return.sort_values(by=['close_percent'], inplace=True, ascending=False)
    df_return.rename(columns={'close_percent':'avg_quarterly_return'}, inplace=True)
    # Create column for average volatility in new dataframe
    df_volatility = df_by_both.groupby('symbol').std()[['close_percent']].reset_index()
    df_volatility.sort_values(by=['close_percent'], inplace=True, ascending=False)
    df_volatility.rename(columns={'close_percent':'volatility'}, inplace=True)
    # Merge these into one
    df_merged = pd.merge(df_return, df_volatility[['symbol', 'volatility']], how='left', left_on=['symbol'], right_on=['symbol'])
    if strategy == 'high':
        return df_merged.sort_values(by=['avg_quarterly_return'], ascending=False).head(5)[['symbol', 'avg_quarterly_return']] # Giving top 5 stocks based purely on return
    if strategy == 'medium':
        return df_merged[df_merged['volatility'] < 0.4].sort_values(by=['avg_quarterly_return'], ascending=False).head(5)
    if strategy == 'low':
        return df_merged[df_merged['volatility'] < 0.2].sort_values(by=['avg_quarterly_return'], ascending=False).head(5)


def model_recommend(size=None, sector=None, risk='medium', df_all=get_data()): # Paramters here need be strings (e.g. 'small', 'indsutrials')
    df_filtered = df_all
    # If size is given, find corresponding column name from dict and filter for it
    if size=="All":
        size=None
    if size:
        size = size_dict[size]
        df_filtered = df_filtered[df_filtered[size] == 1]
    # If sector is given, find corresponding column name from dict and filter for it
    if sector:
        sector = sector_dict[sector]
        df_filtered = df_filtered[df_filtered[sector] == 1]

    predict_timeframe = '2023Q3 vs 2023Q2'
    df_predict = df_filtered[df_filtered['time_frame'] == predict_timeframe]

    # Create column for average volatility in new dataframe
    df_volatility = df_all.groupby('symbol').std()[['close_percent']].reset_index()
    df_volatility.sort_values(by=['close_percent'], inplace=True, ascending=False)
    df_volatility.rename(columns={'close_percent':'volatility'}, inplace=True)

    # Merge volatility into one
    df_predict = pd.merge(left=df_predict, right=df_volatility, how='left', left_on='symbol', right_on='symbol')

    # Show biggest returns first
    df_predict.sort_values(by=['predicted_price_change'], ascending=False, inplace=True)

    if risk == 'high':
        df_predict = df_predict.head(5)[['symbol', 'predicted_price_change', 'volatility']] # Giving top 5 stocks based purely on return
    if risk == 'medium':
        df_predict = df_predict[df_predict['volatility'].between(-0.4, 0.4)].sort_values(by=['predicted_price_change', 'volatility'], ascending=[False, True]).head(5)[['symbol', 'predicted_price_change', 'volatility']]
    if risk == 'low':
        df_predict = df_predict[df_predict['volatility'].between(-0.2, 0.2)].sort_values(by=['predicted_price_change', 'volatility'], ascending=[False, True]).head(5)[['symbol', 'predicted_price_change', 'volatility']]

    df_information = get_information()

    result_df = pd.merge(left=df_predict, right=df_information[["image", 'companyName', "symbol", "country", 'sector']], how='left', left_on='symbol', right_on='symbol')

    #return HTML(result_df.to_html(escape=False ,formatters=dict(image=path_to_image_html)))
    return result_df

# Submit Button, check point and progress bas
if st.button("Submit") and terms_and_conditions:
    with st.spinner(text='In progress'):
        time.sleep(3)
        st.success('Done')
    #st.success(f"Thank you, {name}! Your information has been submitted. You've invested ${amount:.2f}.")

    stock_data=get_data()

    result = model_recommend(size=size,sector=selected_sector, risk=strategy)

    # Capitalize column titles
    result.columns = result.columns.str.capitalize()

    # Round column to 2 decimal places
    result['predicted_price_change'] = result['Predicted_price_change'].round(4)
    result['Avg. stock volatility'] = result['Volatility'].round(2)

    # Format as percentage
    result['predicted_price_change'] = result['predicted_price_change'].apply(lambda x: x*100)

    # Rename specific columns
    result = result.rename(columns={'predicted_price_change': 'Predicted stock price change (%)', 'Companyname': 'Company Name'})

    # Specify the desired column order
    column_order = ['Image', 'Company Name', 'Predicted stock price change (%)', 'Avg. stock volatility', 'Country', 'Sector']

    #Reorder columns
    result = result[column_order]

    html = convert_df(result)
    html=html.replace("text-align: right;","text-align: center;")

    st.markdown(
        html,
        unsafe_allow_html=True
    )
    # result['Avg. stock volatility']=result['Avg. stock volatility']*100
    # result['Predicted stock price change (%)']=result['Predicted stock price change (%)']*100
    # result['Avg. stock volatility']=result['Avg. stock volatility'].astype("int")
    result['Predicted stock price change (%)']=result['Predicted stock price change (%)'].astype("int")
    # Create an interactive scatter plot using plotly
    fig = px.scatter(result, x='Predicted stock price change (%)', y='Avg. stock volatility', text='Company Name',
                    hover_data=['Company Name', 'Country', 'Sector'],
                    title='Stock Analysis', color='Company Name',size='Predicted stock price change (%)')

    st.plotly_chart(fig)
