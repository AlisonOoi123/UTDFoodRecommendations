import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from components.reviews import extract_features_from_reviews

class Generator:
    def __init__(self, neighborhoods, cuisine, cost, review):
        self.neighborhoods = neighborhoods.split(',')
        self.cuisine = cuisine
        self.cost = cost
        self.review = review

    def scaling(self, dataframe):
        encoder=OneHotEncoder(handle_unknown='ignore')
        scaler=StandardScaler(with_mean=False)
        prep_data=encoder.fit_transform(dataframe.iloc[:, [2, 5]])
        prep_data = prep_data.toarray()

        prep_data=scaler.fit_transform(prep_data)
        return prep_data,scaler,encoder

    def nn_predictor(self, prep_data):
        neigh = NearestNeighbors(metric='cosine', algorithm='brute')
        neigh.fit(prep_data)
        return neigh

    def build_pipeline(self, neigh, scaler, params):
        transformer = FunctionTransformer(neigh.kneighbors, kw_args=params)
        pipeline = Pipeline([('std_scaler', scaler), ('NN', transformer)])
        return pipeline
    
    def recommend(self, dataframe, params={'n_neighbors': 5, 'return_distance': False}):
        extracted_data = self.extract_data(dataframe)
        if extracted_data.shape[0] < 5:
            return extracted_data
        if extracted_data.shape[0] >= params['n_neighbors']:
            recommendations =[]            
            # Extract features from existing reviews
            reviews = extracted_data["Review/Recs"].tolist()
            #extracted_data["Reviews/Recs"] = extract_features_from_reviews(reviews)

            prep_data, scaler, encoder = self.scaling(extracted_data)
            neigh = self.nn_predictor(prep_data)
            pipeline = self.build_pipeline(neigh, scaler, params)
            for cuisine_value in self.cuisine:
                user_input = np.array([cuisine_value, self.cost])
                user_input = user_input.reshape(1, -1)
                user_input = scaler.transform(encoder.transform(user_input))
                recommendation_for_cuisine = self.apply_pipeline(pipeline, user_input, extracted_data)
                recommendations.append(recommendation_for_cuisine)
            # Concatenate recommendations for all cuisines
            if isinstance(recommendations, list):
                recommended_restaurants = pd.concat(recommendations)
            else:
                recommended_restaurants = recommendations
            return recommended_restaurants
        else:
            return None

    def extract_data(self, dataframe):
        extracted_data = dataframe.copy()
        extracted_data = extracted_data[(extracted_data['Cuisine'].isin(self.cuisine)) & 
                                        (extracted_data['Neighborhood'].isin(self.neighborhoods))]
        return extracted_data

    def apply_pipeline(self, pipeline, _input, extracted_data):
        return extracted_data.iloc[pipeline.transform(_input)[0]]

    def generate(self, dataframe):
        recommendations = []
        recommended_restaurants = self.recommend(dataframe).drop_duplicates()
        if recommended_restaurants is None:
            recommendations.append(recommended_restaurants)
        elif recommended_restaurants.shape[0] == 1:
            recommendations.extend(recommended_restaurants.values.tolist())
        else:
            custom_sort_order = {'godly': 6, "poppin'": 5, 'p good': 4, 'aight': 3, 'meh': 2, 'blegh': 1}
            recommended_restaurants['CustomSort'] = recommended_restaurants['Rating'].map(custom_sort_order)
            sorted_recommendations = recommended_restaurants.sort_values(by='CustomSort', ascending=False)
            recommendations.extend(sorted_recommendations.values.tolist())
        return recommendations
