import streamlit as st
import pandas as pd
import requests
from arcgis.gis import GIS
from arcgis.gis import User
from arcgis.features import FeatureLayerCollection, FeatureLayer
import geopandas as gpd
from shapely import Geometry, Polygon, MultiPolygon
from shapely.ops import unary_union
import math
from arcgis.features import Feature, FeatureSet, FeatureCollection
from arcgis.features.analyze_patterns import interpolate_points
import os
import time
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

requiredSiraHeaders = [
    "Genus",
    "Species",
    "d18O_lipidextracted",
    "d18O_std_lipidextracted",
    "d18O_Reference (VSMOW…)",
    "d18O_cellulose",
    "d18O_std_cellulose",
    "d18O_nitrated",
    "d18O_std_nitrated",
    "d2H_lipidextracted",
    "d2H_std_lipidextracted",
    "d2H_Reference (VSMOW…)",
    "d2H_cellulose",
    "d2H_std_cellulose",
    "d2H_cellulose_Reference (VSMOW…)",
    "d2H_nitrated",
    "d2H_std_nitrated",
    "d2H_nitrated_Reference (VSMOW…)",
    "d13C_lipidextracted",
    "d13C_std_lipidextracted",
    "d13C_Reference (VPDB...)",
    "d13C_cellulose",
    "d13C_std_cellulose",
    "d13C_cellulose_Reference (VPDB...)",
    "d13C_nitrated",
    "d13C_std_nitrated",
    "d13C_nitrated_Reference (VPDB...)",
    "d15N_lipidextracted",
    "d15N_std_lipidextracted",
    "d15N_lipidextracted_Reference (Air...)",
    "d15N_cellulose",
    "d15N_std_cellulose",
    "d15N_cellulose_Reference (Air...)",
    "d15Nnitrated",
    "d15N_std_nitrated",
    "d15Nnitrated_Reference (Air...)",
    "d34S_lipidextracted",
    "d34S_std_lipidextracted",
    "d34S_lipidextracted_Reference (VCDT...)",
    "d34S_cellulose",
    "d34S_std_cellulose",
    "d34S_cellulose_Reference (VCDT...)",
    "d34Snitrated",
    "d34S_std_nitrated",
    "d34Snitrated_Reference (VCDT...)",
]
siraColumnsToAnalyze = [
    "d18O_lipidextracted",
    "d18O_nitrated",
    "d2H_lipidextracted",
    "d2H_nitrated",
    "d13C_lipidextracted",
    "d13C_nitrated",
    "d15N_lipidextracted",
    "d15Nnitrated",
    "d34S_lipidextracted",
    "d34Snitrated"
]

requiredXrfHeaders = [
    "Genus",
    "Species",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "K",
    "Ca",
    "Mn",
    "Fe",
    "Ni",
    "Cu",
    "Zn",
    "Br",
    "Rb",
    "Sr",
    "Ba",
    "Pb",
    "Ti",
    "V",
    "Cr",
    "Ga",
    "Ge",
    "As",
    "Se",
    "Y",
    "Zr",
    "Nb",
    "Mo",
    "Cd",
    "I",
    "Cs",
    "Bi",
    "Th",
    "U",
]
requiredIcpMsHeaders = [
    "Genus",
    "Species",
    "Li",
    "Be",
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "K",
    "Ca",
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Ga",
    "Ge",
    "As",
    "Se",
    "Rb",
    "Sr",
    "Y",
    "Zr",
    "Nb",
    "Mo",
    "Rh",
    "Ag",
    "Cd",
    "In",
    "Sn",
    "Sb",
    "Te",
    "Cs",
    "Ba",
    "La",
    "Ce",
    "Pr",
    "Nd",
    "Sm",
    "Eu",
    "Gd",
    "Tb",
    "Dy",
    "Ho",
    "Er",
    "Tm",
    "Yb",
    "Lu",
    "Hf",
    "Ta",
    "W",
    "Re",
    "Hg",
    "Tl",
    "Pb",
    "Bi",
    "Th",
    "U",
]

interpolationClipperLayerPerGenus = {
    "Fagus": "https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/Fagus_interpolation_clipped/FeatureServer/0",
    "Tilia": "https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/Tilia_interpolation_clipped/FeatureServer/0",
    "Fraxinus": "https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/Fraxinus_interpolation_clipped/FeatureServer/0",
    "Betula": "https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/Betula_interpolation_clipped/FeatureServer/0",
    "Acer": "https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/Acer_interpolation_clipped/FeatureServer/0",
    "Picea": "https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/Picea_interpolation_clipped/FeatureServer/0",
    "Ulmus": "https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/Ulmus_interpolation_clipped/FeatureServer/0",
    "Quercus": "https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/Quercus_interpolation_clipped/FeatureServer/0",
    "Pinus": "https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/Pinus_interpolation_clipped/FeatureServer/0",
    "Alnus": "https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/Alnus_interpolation_clipped/FeatureServer/0",
}

def gaussian_pdf(mean, stddev, x):
    """
    Calculates the value of the Gaussian PDF at a specific point.
    
    Parameters:
    - mean: The mean of the Gaussian distribution.
    - stddev: The standard deviation of the Gaussian distribution.
    - x: The point at which to evaluate the PDF.
    
    Returns:
    - The value of the Gaussian PDF at x.
    """
    return math.exp(-0.5 * ((x - mean) / stddev) ** 2) / (stddev * math.sqrt(2 * math.pi))



# # Function to display maps - placeholder for actual map rendering logic
# def display_top_map():
#     # center on Liberty Bell, add marker
#     # top_map = folium.Map(location=[39.949610, -75.150282], zoom_start=16)
#     # folium.Marker(
#     #     [39.949610, -75.150282], popup="Liberty Bell", tooltip="Liberty Bell"
#     # ).add_to(top_map)
#     # st_top_map_data = st_folium(top_map, key="top_map", width=2000)
#     st.map()
    
# def display_bottom_map():
#     # center on Liberty Bell, add marker
#     # bottom_map = folium.Map(location=[39.949610, -75.150282], zoom_start=16)
#     # folium.Marker(
#     #     [39.949610, -75.150282], popup="Liberty Bell", tooltip="Liberty Bell"
#     # ).add_to(bottom_map)
#     # st_bottom_map_data = st_folium(bottom_map, key="bottom_map", width=2000)
#     st.map()

# Function to fetch and download a file based on analysis type
def download_file(analysis_type):
    if analysis_type == "SIRA":
        file_url = "https://docs.google.com/spreadsheets/d/16rIQPLKl93Y8f7uL2sL_2zAS3tCv0VsV/export?format=xlsx"
    elif analysis_type == 'XRF':
        file_url = "https://docs.google.com/spreadsheets/d/1MNRV-kzbFQRdtKLz5bWfgNzzkIoxYPs6/export?format=xlsx"
    elif analysis_type == 'ICPMS':
        file_url = "https://docs.google.com/spreadsheets/d/1jTpRMEd7mvL2x6QfTebS4tRF5JZx_475/export?format=xlsx"
        
    response = requests.get(file_url)
    if response.status_code == 200:
        # Prepare the file to download
        filename = analysis_type+"_Analysis_Data.xlsx"
        download_button_label = f"Download {analysis_type} template file"
        st.download_button(label=download_button_label, 
                            data=response.content, 
                            file_name=filename, 
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
@st.cache_data
def get_genus_distribution_layers_from_folder(user):
    items = user.items(folder="genus_distribution_shapefiles_clipped", max_items=1000)
    feature_layer_per_genus_dict = {}
    for item in items:
        extracted_genus = item.title.split('_')[0]
        if item.type == 'Feature Service':
            print(item)
            feature_layer_url = item.url+'/0'
            feature_layer_per_genus_dict[extracted_genus] = feature_layer_url
    return feature_layer_per_genus_dict

@st.cache_data
def get_genus_distribution_layer(genus_name, user, return_only_url=False):
    feature_layer_per_genus_dict = get_genus_distribution_layers_from_folder(user)
    if return_only_url:
        return feature_layer_per_genus_dict[genus_name]

    genus_feature_layer = FeatureLayer(feature_layer_per_genus_dict[genus_name]).query(where='1=1', out_fields='', return_geometry=True)
    polygons = []
    for poly in genus_feature_layer.features:
        for ring in poly.geometry['rings']:
            polygons.append(Polygon(ring))
    multi_poly = MultiPolygon(polygons)
        
    boundary = gpd.GeoDataFrame(geometry=[multi_poly], crs="EPSG:3857")
    boundary = boundary.to_crs("EPSG:4326")          
    
    geojson = boundary.__geo_interface__  
    return geojson
    
@st.cache_data
def get_forest_presence_layer():
    forest_presence_feature_layer = FeatureLayer("https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/GEE_ForestCover_Copernicus_FriekeUGent_EUandRussia_20240219T171249Z_001/FeatureServer/0").query(where='1=1', out_fields='', return_geometry=True)
    polygons = []
    for poly in forest_presence_feature_layer.features:
        for ring in poly.geometry['rings']:
            polygons.append(Polygon(ring))
    st.subheader("There are "+str(len(polygons))+" forest presence polygons")
    # multi_poly = MultiPolygon(polygons)
    
    boundary = gpd.GeoSeries(unary_union(polygons), crs="EPSG:3857")
    boundary = boundary.to_crs("EPSG:4326")          
    st.subheader("There are "+str(len(boundary))+" forest presence polygons after the union operation is applied")
    
    geojson = boundary.__geo_interface__ 
    return geojson
    
if 'top_map_rendered_flag' not in st.session_state:
    st.session_state['top_map_rendered_flag'] = False
    
if 'top_map_data' not in st.session_state:
    st.session_state['top_map_data'] = None
    
if 'genus_distribution_layers' not in st.session_state:
    st.session_state['genus_distribution_layers'] = None

def main():
    reference_data_layer = None
    correct_input_headers_flag = False
    # Title of the app
    st.title('Analysis Prediction App')
    
    app_header_col1, app_header_col2 = st.columns(2, gap='large')
    app_header_col1.info("**This page allows you to determine the most likely geolocation of harvest for your traded sample, based on all of the reference data available to train the model. You can view the full range of reference samples and data used to make the determination in Map A. The result returned in response to your query will be visible in Map B below. Different users consider different confidence levels 'actionable' so please consider the area that most closely matches your risk tolerance.**")
    app_header_col2.header("")

    # Layout: Create two columns of equal width
    col1, col2 = st.columns(2, gap='large')
    
    # Column 2: Maps Display
    with col2:
        # add a markdown element that creates two new lines
        st.markdown("""\n \n \n""")
                
        # st.header("Analysis Maps")
        
        # Displaying two maps - Placeholder for actual map data
        top_map_container = st.empty()
        # r = pdk.Deck(layers=[], initial_view_state=pdk.ViewState(zoom=1,))
        # r = pdk.Deck()
        # top_map_container.pydeck_chart(r)
        with top_map_container.container():
            st.info("Map A: shows the extent of reference sample data available in the platform, as well as the full genus distribution, to give context to the conclusions of the model.")
            arcgis_map(key="top_map")
        
        bottom_map_container = st.empty()
        with bottom_map_container.container():
            st.info("Map B: shows most likely pixel in which the model determines that the tree or plant grew, based on all of the reference information summarized in Map A. Confidence level bands show the larger areas in which the model is 99, 95 or 75% confident that the tree or plant grew.")
            arcgis_map(key="bottom_map")
        

    # Column 1: User Inputs
    with col1:
        
        # st.markdown("**This page allows you to determine the most likely geolocation of harvest for your traded sample, based on all of the reference data available to train the model. You can view the full range of reference samples and data used to make the determination in Map A. The result returned in response to your query will be visible in Map B below. Different users consider different confidence levels 'actionable' so please consider the area that most closely matches your risk tolerance.**")
        
        st.header("User Inputs")
        
        # Username and Password Inputs
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if username and password:
            gis = GIS(url="https://wfid.maps.arcgis.com/", username=username, password=password)
            user = User(gis, username)
        
        st.markdown("""---""")
        
        # Radio Buttons for Selection
        analysis_type = st.radio("Select a method of analysis:", ("SIRA", "XRF", "ICPMS"))
        # add a download button that downloads a different file depending on the analysis type selected
        download_file(analysis_type)
        
        st.markdown("""---""")
        
        # File Upload Button
        uploaded_file = st.file_uploader("Upload traded sample measurement spreadsheet to compute the most likely geolocation of harvest.", type="csv")
        # read the uploaded file if it exists
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write(df)
            
            genus_name = df['Genus'][0]
            
            # isolate the header template that will be used to compare the uploaded file's headers
            headers_to_compare = None
            if analysis_type == "SIRA":
                headers_to_compare = requiredSiraHeaders
            elif analysis_type == 'XRF':
                headers_to_compare = requiredXrfHeaders
            elif analysis_type == 'ICPMS':
                headers_to_compare = requiredIcpMsHeaders
            
            # calculate the missing headers from the uploaded file and the unknown headers in the uploaded file
            missing_headers_list = [col_name for col_name in headers_to_compare if col_name not in df.columns]
            unknown_headers_list = [col_name for col_name in df.columns if col_name not in headers_to_compare]
            
            # depending on the missing and unknown headers, display a error or success message to the user
            correct_input_headers_flag = False
            if missing_headers_list:
                # correct_input_headers_flag = False
                st.error(f"Missing headers: {missing_headers_list}")
            elif unknown_headers_list:
                # correct_input_headers_flag = False
                st.error(f"Unknown headers: {unknown_headers_list}")     
                
            if not correct_input_headers_flag and not unknown_headers_list:
                correct_input_headers_flag = True
                st.success("All required headers are present")     
                
                with st.spinner('Wait for it...'):
                    
                    if not st.session_state['top_map_rendered_flag']:
                        st.session_state['top_map_rendered_flag'] = True
                        reference_data_layer = FeatureLayer("https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/analyzed_unanalyzed_combined_data_dev/FeatureServer/0")
                        # st.write(referenceDataFeatureLayer)
                        reference_data = reference_data_layer.query(where="Category = 'CAT3' AND Analyzed = 'analyzed' AND Genus = '"+genus_name+"' AND Technique = '"+analysis_type+"'", out_fields='', return_geometry=True)
                        st.write(len(reference_data))
                        st.session_state['top_map_data'] = reference_data
                        
                        st.session_state['genus_distribution_layers']  = get_genus_distribution_layer(genus_name, user, return_only_url=True)

                    with top_map_container.container():
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
                        st.info("Map A: shows the extent of reference sample data available in the platform, as well as the full genus distribution, to give context to the conclusions of the model.")
                        arcgis_map(layers_urls=[st.session_state['genus_distribution_layers'] ], layer_data=json.dumps(st.session_state['top_map_data'].to_dict()) if st.session_state['top_map_data'] else None, layer_styling=json.dumps(markerSymbol))
                    # top_map_container.pydeck_chart(st.session_state['top_map'])
                    # st.components.v1.html(r.to_html(as_string=True), width=800, height=600)
                
                  
        
        # Predict Button
        st.subheader("Predict")
        if st.button("Determine Origin", disabled=not correct_input_headers_flag):
            if uploaded_file is not None:
                
                # Define the schema for the feature layer
                fields = [
                    {
                        "name": "OBJECTID",
                        "type": "esriFieldTypeOID",
                        "alias": "OBJECTID",
                        "sqlType": "sqlTypeOther",
                        "nullable": False,
                        "editable": False,
                        "domain": None,
                        "defaultValue": None,
                    },
                    # {
                    #     "name": "Name",
                    #     "type": "esriFieldTypeString",
                    #     "alias": "Name",
                    #     "sqlType": "sqlTypeOther",
                    #     "length": 255,
                    #     "nullable": true,
                    #     "editable": true,
                    #     "domain": None,
                    #     "defaultValue": None,
                    # },
                    {
                        "name": "sampledValue",
                        "type": "esriFieldTypeDouble",
                        "alias": "sampledValue",
                        "sqlType": "sqlTypeOther",
                        # "nullable": True,
                        # "editable": True,
                        # "domain": None,
                        # "defaultValue": None,
                    }
                ]
                
                # Define the geometry type (point, line, or polygon) and the spatial reference
                geometry_type = "esriGeometryPoint"
                spatial_reference = {"wkid": 4326}  # WGS 84
            
                predictions_data_layer = FeatureLayer("https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/betula_predictions/FeatureServer/0")
                # st.write(referenceDataFeatureLayer)
                predictions_data = predictions_data_layer.query(where="1=1", return_geometry=True)
                st.write('There are '+str(len(predictions_data))+' entries in the predictions data')
                
                sampled_features_list = []
                with st.spinner('Creating new points before interpolation...'):
                    for idx, prediction_point in enumerate(predictions_data.features):
                        
                        # extract the first rown of the df dataframe and get the columns that have values
                        trace_elements_to_use = ['_'.join(k.split('_')[0:2]) for k in df.iloc[0].dropna().to_dict().keys() if k.startswith('d') and k.split('_')[1] != 'std' and 'Reference' not in k]
                        
                        total_prob = 1
                        for te in trace_elements_to_use: # iterate over the trace elements that exist in the csv provided by the user

                            mean = prediction_point.attributes[te]
                            std = prediction_point.attributes[te.split('_')[0]+'_std_'+te.split('_')[1]]
                            sampling_point = df[te][0]
                        
                            sampled_value_for_point = gaussian_pdf(mean, std, sampling_point)
                            total_prob *= sampled_value_for_point
                        
                        sampled_features_list.append(Feature(
                            geometry=prediction_point.geometry,
                            attributes={"OBJECTID": idx, "sampledValue": total_prob}
                        ))
                st.success('Creating new points before interpolation... Done!')
                
                feature_set = FeatureSet(features=sampled_features_list, geometry_type=geometry_type, spatial_reference=spatial_reference)
                # st.write('feature set before interpolation: '+str(feature_set))
                
                with st.spinner('Running interpolation...'):
                    try:
                        print('FeatureLayer: '+str(FeatureLayer("https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/python_interpolated_predictions_testing_overwrite/FeatureServer/0")))
                        interpolated_predictions_result = interpolate_points(FeatureCollection.from_featureset(feature_set),
                                        field='sampledValue',
                                        interpolate_option=5,
                                        output_prediction_error=False,
                                        classification_type='GeometricInterval',
                                        bounding_polygon_layer = interpolationClipperLayerPerGenus[genus_name],
                                        num_classes=30,
                                        output_name='python_interpolated_predictions_'+time.strftime("%Y_%m_%d_%H_%M_%S")
                                        # output_name=FeatureLayer("https://services2.arcgis.com/HlCEjEqEP9GdOQeZ/arcgis/rest/services/python_interpolated_predictions_testing_overwrite/FeatureServer/0")
                                        )
                        print('interpolated_predictions_result: '+str(interpolated_predictions_result))
                        st.warning('interpolated_predictions_result: '+str(interpolated_predictions_result))
                    except Exception as e:
                        print('interpolated_predictions_result: '+str(interpolated_predictions_result))
                        st.warning('interpolated_predictions_result: '+str(interpolated_predictions_result))
                        print('This is an error: '+str(e))
                        st.error('This is the error: '+str(e))
                        
                st.success('Running interpolation... Done')                
                
                # load the published feature layer that was just published from the interpolated results
                search_results = gis.content.search('title: '+interpolated_predictions_result['title'],
                                    'Feature Layer')
                # add the interpolated predictions to the map using the url of the published feature layer
                with bottom_map_container.container():
                    st.info("Map B: shows most likely pixel in which the model determines that the tree or plant grew, based on all of the reference information summarized in Map A. Confidence level bands show the larger areas in which the model is 99, 95 or 75% confident that the tree or plant grew.")
                    arcgis_map(layers_urls=[search_results[0].url+'/0'])
                
                
            else:
                st.error("Please upload a CSV file.")
                
        
if __name__ == "__main__":
    main()