import strawberry
import requests
from strawberry.fastapi import GraphQLRouter
from strawberry.scalars import JSON
from typing import List, Optional
from fastapi import FastAPI
from pymongo import MongoClient
from datetime import date 
from config import * 

client = MongoClient(MONGO_CONNECTION_STRING)
db = client.weather_app
collection = db.weather_favorites

@strawberry.type
class WeatherData:
    time: str
    temperature: float
    humidity: float

@strawberry.type
class Weather:
    city: str
    date: str
    hourlyData: List[WeatherData]

@strawberry.input
class saveFavoriteDataItem:
    time: str
    temperature: float
    humidity: float

@strawberry.input
class SaveFavoriteInput:
    city: str
    date: str
    hourlyData: List[saveFavoriteDataItem]

@strawberry.type
class SaveFavoriteOutput:
    id: str

@strawberry.type
class Query:
    @strawberry.field
    def getWeather(self, city: str, date: date) -> Weather:
        return getWeatherData(city, date)
    
    @strawberry.field
    def getWeatherMapOutput(self, city: str, date: date) -> JSON:
        return getWeatherDataMapOutput(city, date)

    @strawberry.field
    def getWeatherFavorites(self) -> List[Weather]:
        return getWeatherFavoritesByField()
    
    @strawberry.field
    def getWeatherFavoritesByCity(self, city: str) -> List[Weather]:
        return getWeatherFavoritesByField("city", city)

    @strawberry.field
    def getWeatherFavoritesByDate(self, date: str) -> List[Weather]:
        return getWeatherFavoritesByField("date", date)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def saveFavorite(self, weather: SaveFavoriteInput) -> SaveFavoriteOutput:
        existingFavorite = collection.find_one({"city": weather.city, "date": weather.date})
        if existingFavorite:
            raise Exception("Favorite already exists")
            
        favorite = {
        "city": weather.city,
        "date": weather.date,
        "hourlyData": [{"time": entry.time, "temperature": entry.temperature, "humidity": entry.humidity} for entry in weather.hourlyData],
        }     
        try:
            insertResult = collection.insert_one(favorite)
            id = str(insertResult.inserted_id)
            return SaveFavoriteOutput(id=id)
        except Exception as e:
            raise Exception("Failed to save favorite")

def getWeatherData(city: str, date: date) -> Weather:
    url = f"{WEATHER_API_URL_PREFIX}key={API_KEY}&q={city}&dt={date}"
    response = requests.get(url)
    data = response.json()

    if "error" in data:
        raise Exception(data["error"]["message"])

    city = data["location"]["name"]
    forecastData = data["forecast"]["forecastday"][0]
    date = forecastData["date"]
    hourlyData = []

    for hour in forecastData["hour"]:
        timeStr = hour["time"]
        time = timeStr.split()[1]
        temperature = hour["temp_f"]
        humidity = hour["humidity"]
        weatherEntry = WeatherData(time=time, temperature=temperature, humidity=humidity)
        hourlyData.append(weatherEntry)

    weather = Weather(city=city, date=date, hourlyData=hourlyData)
    return weather

def getWeatherDataMapOutput(city: str, date: date) -> JSON:
    url = f"{WEATHER_API_URL_PREFIX}key={API_KEY}&q={city}&dt={date}"
    response = requests.get(url)
    data = response.json()

    if "error" in data:
        raise Exception(data["error"]["message"])

    city = data["location"]["name"]
    forecast_data = data["forecast"]["forecastday"][0]
    date = forecast_data["date"]
    hourlyData = {}

    for hour in forecast_data["hour"]:
        timeStr = hour["time"]
        time = timeStr.split()[1]
        temperature = hour["temp_f"]
        humidity = hour["humidity"]
        weatherEntry = {"temperature": temperature, "humidity":humidity}
        hourlyData[time]=weatherEntry
    

    output = {
        "city": city,
        "date": date,
        "hourlyData": hourlyData
    }
    return output

def getWeatherFavoritesByField(field: Optional[str] = None, value: Optional[str] = None) -> List[Weather]:
    weatherFavorites = []
    query = {}
    if field and value:
        query[field] = value
    try:
        favorites = collection.find(query)
    except Exception as e:
        raise Exception("Failed to retrieve weather favorites")

    for favorite in favorites:
        city = favorite["city"]
        date = favorite["date"]
        hourlyData = [
            WeatherData(
                time=weather_entry["time"],
                temperature=weather_entry["temperature"],
                humidity=weather_entry["humidity"],
            )
            for weather_entry in favorite["hourlyData"]
        ]
        weatherFavorites.append(Weather(city=city, date=date, hourlyData=hourlyData))
    return weatherFavorites


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphqlApp = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphqlApp, prefix="/graphql")



