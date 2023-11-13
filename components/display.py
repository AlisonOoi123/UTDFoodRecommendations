
import streamlit as st

class Display:
    def __init__(self):
        pass

    def display_recommendation(self, user, recommendations):
        st.header('Dallas Area Restaurants')  
        with st.spinner('Generating recommendations...'): 
            neighborhoods = user.neighborhoods
            st.subheader('Recommendations:')
            # If there are more than 2 neighborhoods, arrange recommendations in two columns per row
            if len(neighborhoods) > 2:
                i = 0  # Initialize a counter variable
                neighborhood_idx = 0
                while neighborhood_idx < len(neighborhoods):
                    row_columns = st.columns(2)
                    for col_idx, column in enumerate(row_columns):
                        if neighborhood_idx < len(neighborhoods):
                            neighborhood = neighborhoods[neighborhood_idx]
                            recommendation = recommendations[neighborhood_idx]
                            # Skip columns without any recommendations
                            while not any(recommendation) and neighborhood_idx < len(neighborhoods) - 1:
                                neighborhood_idx += 1
                                neighborhood = neighborhoods[neighborhood_idx]
                                recommendation = recommendations[neighborhood_idx]
                            if any(recommendation):
                                with column:
                                    st.markdown(f'##### {neighborhood.upper()}')   
                                    for j, restaurant_info in enumerate(recommendation, start=1):
                                        if restaurant_info is not None:
                                            restaurant_name = restaurant_info[0]
                                            expander = st.expander(f'{j}: {restaurant_name}')
                                            expander.write(f"Cost: {restaurant_info[5]}")  
                                            expander.write(f"Rating: {restaurant_info[4]}")
                                            expander.write(f"Review: {restaurant_info[3]}")
                
                                    neighborhood_idx += 1
                                    i += len(recommendation)
            else:   
                # If there are 2 or fewer neighborhoods, use a single column per row
                for neighborhood, column, recommendation in zip(neighborhoods, st.columns(len(neighborhoods)), recommendations):
                    # Skip columns without any recommendations
                    if any(recommendation):
                        with column:
                            st.markdown(f'##### {neighborhood.upper()}')   
                            for i, restaurant_info in enumerate(recommendation, start=1):
                                if restaurant_info is not None:
                                    restaurant_name = restaurant_info[0]
                                    # Set a fixed height for the expander
                                    expander = st.expander(f'{i}: {restaurant_name}')
                                    expander.write(f"Cost: {restaurant_info[5]}")  
                                    expander.write(f"Rating: {restaurant_info[4]}")
                                    expander.write(f"Review: {restaurant_info[3]}")


