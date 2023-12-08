import streamlit as st
import pandas as pd
from streamlit_extras.switch_page_button import switch_page
#config
from PIL import Image
from st_pages import Page, show_pages


def main():

    # Specify what pages should be shown in the sidebar, and what their titles
    # and icons should be
    # show_pages(
    #     [
    #         Page("finance.py", "Home", "🏠"),
    #         Page("pages/Portfolio.py", "Stock Screener", ":popcorn:"),
    #         Page("pages/Stock.py", "Stock Forecast", ":moneybag:"),
    #     ]
    # )

    st.title(":green[100 DAYS TO FINANCIAL FREEDOM]:moneybag:")

    st.divider()


    # Put in logo

    image = Image.open('/Users/admin/code/derksol/finance/Screenshot 2023-12-08 at 11.13.15.png')
    c1, c2, c3 = st.columns([0.3, 0.4, 0.3])
    with c2:
        st.image(image, use_column_width=False, output_format="PNG", width=249, )

    # Buttons
    # col2.markdown("![Alt Text](https://media.tenor.com/nLekqFnI89UAAAAd/wise-maximize-your-money-and-save-on-transactions-fees.gif)")

    # Left Button - Pick a stock
    c1.write("   ")
    c1.write("   ")
    c1.write("   ")
    c1.subheader("Showcase stock Performance :popcorn:")
    if c1.button("Pick a Stock"):
        switch_page("Stock Screener 🍿")
    # Perform actions to directly go to the stock page

    # col2.image(image, use_column_width=False, output_format="PNG", width=100)

    # Right Button - Create a Portfolio
    c3.write("   ")
    c3.write("   ")
    c3.write("   ")

    c3.subheader("Explore stock Opportunities :boom:")
    if c3.button("Stock Screener"):
        switch_page("Stock Forecast 💰")
    # Perform actions to directly go to the stock page

    #st.divider()
if __name__ == "__main__":
    main()
