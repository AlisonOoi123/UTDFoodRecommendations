import streamlit as st
from streamlit_gsheets import GSheetsConnection
import folium
from streamlit_folium import folium_static
import plotly.express as px
import webbrowser
from components.user import User
from components.display import Display
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="UTD Food Guide", page_icon=":knife_fork_plate:",layout="wide")

st.title(" :knife_fork_plate: Food Recs Near UTD")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

st.markdown(
    """
    Hello! Explore restaurants in the DFW area using the filters on the left. 
    For personalized recommendations, see form at the bottom of the page! See
    original Google Spreadsheet [here](https://tinyurl.com/utdfoodguide). 
    """
)

# Open the URL in the browser
spreadsheet_url = st.secrets["connections"]["spreadsheet"]
#if st.button("Open Google Sheets"):
    #webbrowser.open_new_tab(spreadsheet_url)

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

url = st.secrets["connections"]["spreadsheet3"]
df = conn.read(spreadsheet=url)

st.sidebar.header("Filters: ")

# Create for neighborhood
neighborhood = st.sidebar.multiselect("DFW Neighborhood", df["Neighborhood"].unique())
if not neighborhood:
    df2 = df.copy()
else:
    df2 = df[df["Neighborhood"].isin(neighborhood)]

# Create for cuisine
cuisine = st.sidebar.multiselect("Cuisine", df2["Cuisine"].unique())
if not cuisine:
    df3 = df2.copy()
else:
    df3 = df2[df2["Cuisine"].isin(cuisine)]

# Create for rating
rating = st.sidebar.multiselect("Rating", df3["Rating"].unique())
if not rating:
    df4 = df3.copy()
else:
    df4 = df3[df3["Rating"].isin(rating)]

# Create for cost
cost = st.sidebar.multiselect("Cost", df4["Cost"].unique())

if not neighborhood and not cuisine and not rating and not cost:
    filtered_df = df
elif not cuisine and not rating and not cost:
    filtered_df = df[df["Neighborhood"].isin(neighborhood)]
elif not neighborhood and not rating and not cost:
    filtered_df = df[df["Cuisine"].isin(cuisine)]
elif not neighborhood and not cuisine and not cost:
    filtered_df = df[df["Rating"].isin(rating)]
elif not neighborhood and not cuisine and not rating:
    filtered_df = df[df["Cost"].isin(cost)]
else:
    filtered_df = df[
        (df["Neighborhood"].isin(neighborhood) if neighborhood else True) &
        (df["Cuisine"].isin(cuisine) if cuisine else True) &
        (df["Rating"].isin(rating) if rating else True) &
        (df["Cost"].isin(cost) if cost else True)
    ]

ratings_key = {
    "godly": "🌟🌟🌟🌟🌟",
    "poppin'": "🌟🌟🌟🌟",
    "p good": "🌟🌟🌟",
    "aight": "🌟🌟",
    "meh": "🌟",
    "blegh": "💔",
}

cl1, cl2 = st.columns((1, 2))

with cl1:
    st.subheader("Ratings Key:")
    for rating, emoji in ratings_key.items():
        st.markdown(f"<div style='font-size: 25px;'>{rating} : {emoji}</div>", unsafe_allow_html=True)

with cl2:
    st.subheader("Top-Rated (Godly) Restaurants")
    top_rated_df = filtered_df[filtered_df['Rating'] == 'godly']
    st.dataframe(top_rated_df[['Name', 'Neighborhood', 'Cuisine']])

st.title("Restaurants")
st.dataframe(filtered_df[['Name', 'Neighborhood', 'Cuisine', 'Rating', 'Cost']])

df_with_coordinates = filtered_df[(filtered_df['latitude'].notna()) & (filtered_df['longitude'].notna())]

# Display a title
st.title("Map View")

utd_coords = ['32.98624579282655', '-96.75043445562082']  

# Create a Folium map centered around the mean of coordinates
if not neighborhood:
    my_map = folium.Map(location=utd_coords, zoom_start=12)
elif neighborhood[0] == "Richardson":
    my_map = folium.Map(location=utd_coords, zoom_start=12)
else:
    my_map = folium.Map(location=utd_coords, zoom_start=10)

for index, row in df_with_coordinates.iterrows():
    tooltip = f"{row['Name']} - Cuisine: {row['Cuisine']} - Rating: {row['Rating']} - Cost: {row['Cost']}"
    icon = folium.Icon(color='red', icon='flag')
    folium.Marker([row['latitude'], row['longitude']], icon=icon, tooltip=tooltip).add_to(my_map)

folium.Marker(location=utd_coords, tooltip='UTD', icon=folium.Icon(color='green')).add_to(my_map)

st_folium_map = folium_static(my_map)

# Ratings Count by Neighborhood
if neighborhood:
    neighborhood_df = df[df["Neighborhood"].isin(neighborhood)]
    col1, col2 = st.columns((2))
    with col1:
        st.subheader(f"Ratings Distribution for {', '.join(neighborhood) if len(neighborhood) > 1 else neighborhood[0]}")
        fig = px.bar(neighborhood_df, x="Rating", color="Neighborhood",
                category_orders={"Rating": ["godly", "poppin'", "p good", "aight", "meh", "blegh"]},
                template="seaborn", color_discrete_map = {
                    'Mesquite': '#fdcc9e',
                    'Carrollton': '#8af0c7',
                    'Northside': '#ffb663',
                    'Fairview': '#e7f0cd',
                    'Ft. Worth': '#9dc5b4',
                    'Grapevine': '#7fc1b2',
                    'SMU': '#743558',
                    'Denton': '#a76054',
                    'Allen': '#c68aff',
                    'Garland': '#ffadad',
                    'Frisco': '#ffa8a8',
                    'Dallas': '#cbafed',
                    'Addison': '#88616d',
                    'Bishop Arts': '#2c1847',
                    'Downtown Dallas': '#7364cb',
                    'Sachse': '#aa7c6b',
                    'The Colony': '#11e399',
                    'Richardson': '#50b8e7',
                    'Plano': '#84cdee',
                    'Durant, Oklahoma': '#cf29b1',})                      
        st.plotly_chart(fig, use_container_width=True, height=400)

    # Cost Count by Neighborhood
    with col2:
        st.subheader(f"Cost Distribution for {', '.join(neighborhood) if len(neighborhood) > 1 else neighborhood[0]}")
        fig = px.pie(neighborhood_df, names="Cost", hole=0.5,
                category_orders={"Cost": ["$", "$-$$", "$$", "$$-$$$", "$$$", "$$$$", "$$$$$"]},
                template="seaborn", color="Cost", color_discrete_map={
                    '$': '#ff9999',   
                    '$-$$': '#ff7f7f',     
                    '$$': '#ff6b6b',        
                    '$$$': '#e36262',    
                    '$$-$$$': '#ff4040',   
                    '$$$$': '#c24242',     
                    '$$$$$': '#8b1414'   },)
        fig.update_traces(textinfo='label+percent')
        st.plotly_chart(fig, use_container_width=True, height=400)

st.write("# Restaurant Recommendations 🍕🍔🍟")
st.markdown(
    """
    Personalized DFW restaurant recommendation web application using a nearest-neighbors approach with Scikit-Learn.
    """
)

with st.form("recommendation_form"):
    st.write("If you don't see a result for a certain neighborhood, there are no recommendations matching your criteria :(")
    neighborhood_choices = st.multiselect('Neighborhood', ['Richardson',
                    'Plano',
                    'Frisco',
                    'Allen',
                    'Bishop Arts',
                    'Mesquite',
                    'Carrollton',
                    'Northside',
                    'Fairview',
                    'Ft. Worth',
                    'Grapevine',
                    'SMU',
                    'Denton',
                    'Garland',
                    'Dallas',
                    'Addison',
                    'Sachse',
                    'The Colony',
                    'Durant, Oklahoma'])
    cuisine_choice = st.multiselect('Cuisine', df["Cuisine"].unique())
    cost_choice = st.select_slider('Cost',options=["$", "$-$$", "$$", "$$-$$$", "$$$", "$$$$", "$$$$$"])
    review_preference = st.text_input('Preferences (Optional, example:"friendly employees")')
    generated = st.form_submit_button("Generate")

display = Display()

if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'user' not in st.session_state:
    st.session_state.user = None

if generated:
    st.session_state.generated=True
    if not neighborhood_choices:
        neighborhood_choices=df['Neighborhood'].unique()
    if not cuisine_choice:
        st.warning("Please fill in the cuisine field before generating recommendations.")
    else:
        user = User(neighborhood_choices,cuisine_choice,cost_choice,review_preference, df)
        with st.spinner('Generating recommendations...'):     
            recommendations=user.generate_recommendations()
            st.session_state.recommendations=recommendations
            st.session_state.user=user

if st.session_state.generated:
    with st.container():
        if st.session_state.user is not None:
            display.display_recommendation(st.session_state.user,st.session_state.recommendations)
            st.success('Generated Successfully!', icon="✅")
    
#st.markdown(f"<div style='font-size: 10px;'>*Data collection courtesy of Neha Thomas and Khushi Thakkar</div>", unsafe_allow_html=True)







