import streamlit as st
import pandas as pd
from arcgis.gis import GIS
from arcgis.gis import User
from arcgis.features import FeatureLayerCollection, FeatureLayer
from  streamlit_arcgis_map import streamlit_arcgis_map as arcgis_map
import json


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

attributeMapping = {
    'Is_it_possible_to_extract_enoug': 'Is it possible to extract enough high quality DNA from this category of product for effective testing?',
    'Any_qualifiers___CAVEAT_TEXT_': 'Any qualifiers?',
    'Is_there_evidence_that_stable_i': 'Is there evidence that stable isotope measurements taken from this category of forest products is consistent with stable isotope measurements taken from reference samples of unprocessed wood?',
    'Any_qualifiers___isotope_measur': 'Any qualifiers? (stable isotope)',
    'Is_there_evidence_that_trace_el': 'Is there evidence that trace element measurements taken from this category of forest products is consistent with trace element measurements taken from reference samples of unprocessed wood?',
    'Any_qualifiers___trace_element_': 'Any qualifiers? (trace element)',
    'F1__Covered_under_the_scope_of_': 'Covered under the scope of the UKTR in 2023',
    'F2__Lacey_Declaration_requireme': 'Lacey Declaration requirement as of 2023',
    'F3__Covered_under_the_scope_of_': 'Covered under the scope of the Australian ILPA in 2023',
    'F4__Covered_under_the_scope_of_': 'Covered under the scope of the EUDR (to become operational in 2024)',
    'Genus___Species_qualifier_in_HS': 'Genus / Species qualifier in HS code',
}

displayAttributes = [
    'Is_it_possible_to_extract_enoug', 'Any_qualifiers___CAVEAT_TEXT_', 
    'Is_there_evidence_that_stable_i', 'Any_qualifiers___isotope_measur',  
    'Is_there_evidence_that_trace_el', 'Any_qualifiers___trace_element_',
    'F1__Covered_under_the_scope_of_',
    'F2__Lacey_Declaration_requireme',
    'F3__Covered_under_the_scope_of_',
    'F4__Covered_under_the_scope_of_',
    'Genus___Species_qualifier_in_HS'
]

@st.cache_data
def load_data():
    # load a csv file as a hosted feature layer from arcgis online
    hs_code_data_layer = FeatureLayer("https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/20231207_HS_codes_testing_reference_data_integration___Timber/FeatureServer/0")
    # return the feature set to a dataframe
    hs_code_data_df = hs_code_data_layer.query(where="1=1", out_fields='*').sdf
    hs_codes_list = hs_code_data_df['HS_code'].unique().tolist()
    return hs_code_data_df, hs_codes_list

@st.cache_data
def get_reference_data(genus_name):
    reference_data_layer = FeatureLayer("https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/analyzed_unanalyzed_combined_data_dev/FeatureServer/0")
    reference_data = reference_data_layer.query(where="Category = 'CAT3' AND Analyzed = 'analyzed' AND Genus = '"+genus_name+"'", out_fields='*', return_geometry=True)
    
    num_countries_set = set()
    num_samples_set = set()
    geom_points = []  # List to store geometry points
    for feature in reference_data.features:
        num_countries_set.add(feature.attributes['Country'])
        num_samples_set.add(feature.attributes['Identifier'])
        geom = feature.geometry
        # geom_points.append([geom['x'], geom['y']])  # Assuming points; adjust if necessary
        geom_points.append([feature.attributes['Longitude'], feature.attributes['Latitude']])  # Assuming points; adjust if necessary
        
    return num_countries_set, num_samples_set, reference_data

def main():
    
    
    st.header('Can I test it?', divider='gray')
    with st.spinner("Loading data..."):
        hs_code_data_df, hs_codes_list = load_data()

    # st.dataframe(hs_code_data_df)
    
    hs_code_selected = st.selectbox(
        'Select an HS-code',
        hs_codes_list,
        index = None
    )
    if hs_code_selected is not None:
        row = hs_code_data_df[hs_code_data_df['HS_code'] == hs_code_selected]
        for attribute in displayAttributes:
            if not pd.isna(row[attribute]).any():
                st.subheader(attributeMapping[attribute])
                st.write(row[attribute].values[0])
                st.divider()
                
        genus_name = row['Genus___Species_qualifier_in_HS'].values[0]
        if not pd.isnull(genus_name):
            num_countries_set, num_samples_set, reference_data = get_reference_data(genus_name)
            st.subheader('There are '+str(len(num_samples_set))+' of '+genus_name+' across '+str(len(num_countries_set))+' countries')
            
            # Check if there are points to display
            if reference_data:                
                markerSymbol = {
                    "type": "simple-marker",  #  autocasts as new SimpleMarkerSymbol()
                    "style": "circle",
                    "color": "red",
                    "size": "10px",  #  pixels
                    "outline": {  #  autocasts as new SimpleLineSymbol()
                    "color": "red",
                    "width": 5  #  points
                    }
                }
                st.subheader("Map A: shows the extent of reference sample data available in the platform, as well as the full genus distribution, to give context to the conclusions of the model.")
                arcgis_map(layer_data=json.dumps(reference_data.to_dict()), layer_styling=json.dumps(markerSymbol))

        
        

            
if __name__ == "__main__":
    main()