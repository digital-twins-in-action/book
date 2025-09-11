import graphene, requests
from flask import Flask
from flask_graphql import GraphQLView


class WeatherData(graphene.ObjectType):
    time = graphene.List(graphene.String)
    rain = graphene.List(graphene.Float)
    surface_temperature = graphene.List(graphene.Float)


class Query(graphene.ObjectType):
    weather = graphene.Field(WeatherData, city=graphene.String(required=True))

    def resolve_weather(self, info, city):
        geo_data = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/" f"search?name={city}&count=1"
        ).json()

        if not geo_data.get("results"):
            raise Exception(f"City '{city}' not found")

        lat, lon = (geo_data["results"][0][k] for k in ["latitude", "longitude"])

        weather_data = requests.get(
            f"https://api.open-meteo.com/v1/"
            f"forecast?latitude={lat}&longitude={lon}"
            f"&hourly=rain,surface_temperature&models=ecmwf_ifs025"
            f"&forecast_days=7"
        ).json()

        return WeatherData(**weather_data["hourly"])


app = Flask(__name__)
app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql", schema=graphene.Schema(query=Query), graphiql=True
    ),
)

if __name__ == "__main__":
    app.run(debug=True)
