import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="WFID app - experimental",
    # page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

def main():
    st.title("Infohub")
    
    # create three columns and put the iframe in the middle one
    col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
    with col1:
        components.iframe("https://www.arcgis.com/apps/dashboards/f895207e631f496988040f4716cc57bc", width=1920, height=1080, scrolling=False)
        
    # add the iframe using html and markdown
    # st.markdown("<iframe src='https://www.arcgis.com/apps/dashboards/f895207e631f496988040f4716cc57bc' width='100%' height='100%'></iframe>", unsafe_allow_html=True)
    
if __name__ == "__main__":
    main()