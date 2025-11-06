import streamlit as st
from streamlit_option_menu import option_menu
import home
import survey
import recommand
import chatbot

sidebar_bg = """
<style>
[data-testid="stSidebar"] {
    background-color: #20314e;
}
</style>
"""
st.markdown(sidebar_bg, unsafe_allow_html=True)

with st.sidebar:
    st.image("YOUME_logo.png", width=120)
    choice = option_menu("", ["시작", "내 입맛 찾기","상품추천","챗봇"],
    icons=['bi bi-house-fill', 'bi bi-clipboard2-x-fill', 'bi bi-gear-fill','bi bi-graph-up'],
                        menu_icon="bi bi-pin-angle-fill", default_index=0,
                        styles={
                            "container": {"padding": "5!important", "background-color": "#20314e", "border-radius": "0px!important" },
                            "icon": {"color": "#fe9600", "font-size": "15px"},
                            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#2a3f5f", "color": "#ffffff"},
                            "nav-link-selected": {"background-color": "#2a3f5f", "color": "#ffffff"},
                            "menu-title": {"font-size": "15px", "color": "#ffffff"},
                            "menu-icon": {"font-size": "15px", "color": "#fe9600"}
                        }
                        )
                        
if choice == "시작":
    home.run_home()
elif choice == "내 입맛 찾기":
    survey.run_survey()
elif choice == "상품추천":
    recommand.run_recommend()
elif choice == "챗봇":
    chatbot.run_chatbot()