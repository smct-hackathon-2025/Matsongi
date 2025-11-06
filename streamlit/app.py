import streamlit as st
from streamlit_option_menu import option_menu
import home
# from pages import survey
import survey


with st.sidebar:
    choice = option_menu("YOUME", ["시작", "내 입맛 찾기","내 레시피 만들기","설정"],
    icons=['bi bi-house-fill', 'bi bi-clipboard2-x-fill', 'bi bi-gear-fill','bi bi-graph-up'],
                        menu_icon="bi bi-pin-angle-fill", default_index=0,
                        styles={
                            "container": {"padding": "5!important", "background-color": "#FFFFFF"},
                            "icon": {"color": "black", "font-size": "15px"},
                            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                            "nav-link-selected": {"background-color": "#8DBBD3"},
                            "menu-title": {"font-size": "15px"},
                            "menu-icon": {"font-size": "15px"}
                        }
                        )
                        
if choice == "시작":
    home.run_home()
elif choice == "내 입맛 찾기":
    survey.run_survey()