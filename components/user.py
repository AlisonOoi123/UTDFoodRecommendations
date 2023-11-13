from components.generator import Generator

class User:
    def __init__(self,neighborhood_choices,cuisine_choice,cost_choice,review_preference, dataframe):
        self.neighborhoods=neighborhood_choices
        self.cuisine=cuisine_choice
        self.cost=cost_choice
        self.review=review_preference
        self.df=dataframe

    def generate_recommendations(self,):
        recommendations=[]
        for neighborhood in self.neighborhoods:
            generator=Generator(neighborhood, self.cuisine, self.cost, self.review)
            recommended_restaurants=generator.generate(self.df)
            recommendations.append(recommended_restaurants)
        return recommendations