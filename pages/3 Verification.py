import streamlit as st
import pandas as pd
import requests
from arcgis.gis import GIS
from arcgis.gis import User
from arcgis.features import FeatureLayerCollection, FeatureLayer
from arcgis.features import Feature, FeatureSet, FeatureCollection
from arcgis.geometry import Point
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


def main():
    
    # Layout: Create two columns of equal width
    col1, col2 = st.columns(2, gap='large')
    
    # Column 2: Maps Display
    with col2:
        # add a markdown element that creates two new lines
        st.markdown("""\n \n \n""")
                        
        # Displaying two maps - Placeholder for actual map data
        map_container = st.empty()
        with map_container.container():
            st.info("This page allows you to determine the most likely geolocation of harvest for your traded sample, based on all of the reference data available to train the model. You can view the full range of reference samples and data used to make the determination in Map A. The result returned in response to your query will be visible in Map B below. Different users consider different confidence levels 'actionable' so please consider the area that most closely matches your risk tolerance.")
            arcgis_map(key="map")

    
    # Column 1: User inputs
    with col1:
        
        # Username and Password Inputs
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if username and password:
            gis = GIS(url="https://wfid.maps.arcgis.com/", username=username, password=password)
            user = User(gis, username)
        
        # File Upload Button
        uploaded_file = st.file_uploader("Upload traded sample measurement spreadsheet to compute the most likely geolocation of harvest.", type="csv")
        # read the uploaded file if it exists
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write(df)
            
        st.markdown("""---""")
        
        # select the type of location claim
        type_of_location_claim_option = st.radio(
            "What's your favorite movie genre",
            ["Input coordinates", "Upload shapefile", "FSC concession number"],
            index=None,
        )
        
        if type_of_location_claim_option == "Input coordinates":
            with st.form("my_form"):
                longitude = st.number_input(label='Longitude', placeholder='Longitude', value=3.7081386)
                latitude = st.number_input(label='Latitude', placeholder='Latitude', value=51.0536918)

                # Every form must have a submit button.
                submitted = st.form_submit_button("Verified claimed origin")
                if submitted:
                    # create a point geometry, and then a feature, and then a feature set and then add it to the map
                    point = Point({"x": longitude, "y": latitude, "spatialReference": {"wkid": 4326}})
                    feature = Feature(geometry=point)
                    feature_set = FeatureSet([feature])
                    
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
                    # add the feature collection to the map
                    with map_container.container():
                        st.info("This page allows you to determine the most likely geolocation of harvest for your traded sample, based on all of the reference data available to train the model. You can view the full range of reference samples and data used to make the determination in Map A. The result returned in response to your query will be visible in Map B below. Different users consider different confidence levels 'actionable' so please consider the area that most closely matches your risk tolerance.")
                        arcgis_map(layer_data=json.dumps(feature_set.to_dict()), layer_styling=json.dumps(markerSymbol))
        
        elif type_of_location_claim_option == "Upload shapefile":
            uploaded_shapefile = st.file_uploader("Upload shapefile", type="zip")
            # create a feature layer from the uploaded shapefile using the arcgis python api
            if uploaded_shapefile is not None:
                # Set the portal URL and the endpoint for the generate operation
                portal_url = "https://www.arcgis.com/sharing/rest/content/features/generate"
                # Prepare the parameters as a dictionary
                params = {
                    'name': 'fileName',  # Replace this with the actual name of your file
                    'targetSR': 'mapView.spatialReference',  # You'll need to replace this with actual spatial reference
                    'maxRecordCount': 1000,
                    'enforceInputFileSizeLimit': True,
                    'enforceOutputJsonSizeLimit': True,
                    'generalize': True,
                    'maxAllowableOffset': 10,
                    'reducePrecision': True,
                    'numberOfDigitsAfterDecimal': 0
                }

                # Additional content parameters for the request
                my_content = {
                    'filetype': 'shapefile',
                    'publishParameters': json.dumps(params),
                    'f': 'json',
                }

                # The 'files' parameter should include the actual file you want to upload
                files = {'file': ('filename.zip', uploaded_shapefile, 'application/zip')}
                # Make the request
                response = requests.post(portal_url, data=my_content, files=files)
                # Check if the request was successful
                if response.status_code == 200:
                    # Print the feature collection
                    print('Feature Collection:', response.json())
                else:
                    st.write('Failed to generate feature collection', response.text)
                    
                polygon_markerSymbol = {
                    "type": "simple-fill",  #  autocasts as new SimpleFillSymbol()
                    "color": [227, 139, 79, 0.8],
                    "outline": {  #  autocasts as new SimpleLineSymbol()
                        "color": [255, 255, 255],
                        "width": 1
                    }
                }
                
                # add the feature layer to the map
                with map_container.container():
                    st.info("This page allows you to determine the most likely geolocation of harvest for your traded sample, based on all of the reference data available to train the model. You can view the full range of reference samples and data used to make the determination in Map A. The result returned in response to your query will be visible in Map B below. Different users consider different confidence levels 'actionable' so please consider the area that most closely matches your risk tolerance.")
                    arcgis_map(layer_data=json.dumps(response.json()['featureCollection']['layers'][0]['featureSet']) if response else None, layer_styling=json.dumps(polygon_markerSymbol))

        elif type_of_location_claim_option == "FSC concession number":
            with st.form("my_form"):
                fsc_code = st.text_input(label='FSC concession number', placeholder='FSC concession number', value='FC-FM/COC-643208')
                
                # Every form must have a submit button.
                submitted = st.form_submit_button("Verified claimed origin")
                if submitted:
                    # create a feature layer from the FSC concession number using the arcgis python api
                    if fsc_code is not None:
                        # create a feature layer from the FSC concession number using the arcgis python api
                        fsc_concession_layer = FeatureLayer("https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/FSC_CertifiedForests_data/FeatureServer/0")
                        fsc_concession = fsc_concession_layer.query(where="fsc_cert = '"+fsc_code+"'", out_fields='*', return_geometry=True)
                        polygon_markerSymbol = {
                            "type": "simple-fill",  #  autocasts as new SimpleFillSymbol()
                            "color": [227, 139, 79, 0.8],
                            "outline": {  #  autocasts as new SimpleLineSymbol()
                                "color": [255, 255, 255],
                                "width": 1
                            }
                        }
                        # add the feature layer to the map
                        with map_container.container():
                            st.info("This page allows you to determine the most likely geolocation of harvest for your traded sample, based on all of the reference data available to train the model. You can view the full range of reference samples and data used to make the determination in Map A. The result returned in response to your query will be visible in Map B below. Different users consider different confidence levels 'actionable' so please consider the area that most closely matches your risk tolerance.")
                            arcgis_map(layer_data=json.dumps(fsc_concession.to_dict()) if fsc_concession else None, layer_styling=json.dumps(polygon_markerSymbol))
        
            
    

            
            

if __name__ == "__main__":
    main()
    