# Weather GraphQL API

This project provides a GraphQL API for retrieving weather data based on city and date, saving favorite weather data, and retrieving weather data for favorite cities and dates.

## Features

- Get weather data for a specific city and date, including temperature and humidity grouped by time.
- Save your favorite weather data, including city, date, and hourly temperature and humidity.
- Retrieve your favorite weather data. Favorites can be retrieved based on a particular city and date as well. 

## Technologies Used

- Python
- FastAPI
- Strawberry GraphQL
- MongoDB
- WeatherAPI

## Setup

1. Clone the repository:

`git clone git@github.com:siddhantbagga15/czero_weather.git`

2. Install dependencies

3. Set up MongoDB and configure the connection string in the `config.py` file.

4. Obtain an API key from `https://www.weatherapi.com/` update the `config.py` file with the API key.

5. Start the server: `uvicorn main:app --reload`

6. You can use Insomnia to test these GraphQL queries. Interact with the API at `http://localhost:8000/graphql` .

## Usage

### Get Weather Data

To retrieve weather data for a specific city and date, use the following query:
```
query {
  getWeather(city: "CityName", date: "YYYY-MM-DD") {
    city
    date
    hourlyData {
      time
      temperature
      humidity
    }
  }
}
```

### Get Weather Data - Map Output

In addition to the previous query, you can also retrieve weather data in a map-like format using the `getWeatherMapOutput` query. This query returns weather data grouped by time, with each time as the key and the corresponding temperature and humidity as values. This map-like output allows for efficient data retrieval. With this format, you can directly access weather data for a specific time without needing to iterate through an array or list of hourly data. This can be particularly useful when you are interested in analyzing or displaying weather information for a specific point in time. Moreover, this map-like format provides flexibility in visualizing weather data. You can create visualizations that showcase temperature and humidity changes over time, such as line charts or graphs, by utilizing the data structure returned by the getWeatherMapOutput query.

To retrieve weather data in map format for a specific city and date, use the following query:

```
query {
  getWeatherMapOutput(city: "CityName", date: "YYYY-MM-DD")
}
```

Output would be something like the following:

		"getWeatherMapOutput": {
			"city": "London",
			"date": "2023-01-15",
			"hourlyData": {
				"00:00": {
					"temperature": 42.1,
					"humidity": 63
				},
				"01:00": {
					"temperature": 41.7,
					"humidity": 64
				},
				"02:00": {
					"temperature": 41.2,
					"humidity": 65
				}
            }
        }

### Save Favorite Weather Data

To save your favorite weather data, use the following mutation:

```
mutation {
  saveFavorite(weather: {
    city: "CityName"
    date: "YYYY-MM-DD"
    hourlyData: [
      {
        time: "HH:MM"
        temperature: 25.5
        humidity: 70.0
      },
      // Add more hourlyData items as needed
    ]
  }) {
    id
  }
}
```

This returns the id of the document inserted in MongoDB database. 

### Get Weather Favorites

To retrieve weather data of your favorites, use the following query:

```
query {
  getWeatherFavorites(page:pageNumber, limit:itemLimit) {
    weatherFavorites {
      city
      date
      hourlyData {
        time
        temperature
        humidity
      }
    }
    page
  }
}
```
This will return a list of your favorite weather data items, including city, date, and hourly temperature and humidity. Adjust the page and limit parameters as needed for pagination.

### Get Weather Favorites by City

To retrieve weather data of your saved favorites based on a specific city, use the `getWeatherFavoritesByCity` query. Example is as follows:

```
query {
  getWeatherFavoritesByCity(city: "CityName", page: 1, limit: 10) {
    weatherFavorites {
      city
      date
      hourlyData {
        time
        temperature
        humidity
      }
    }
    page
  }
}
```

The page field in the response indicates the current page number, allowing you to implement pagination.

### Get Weather Favorites by Date

To retrieve weather data of your saved favorites based on a specific date, use the `getWeatherFavoritesByDate` query. Example is as follows:

```
query {
  getWeatherFavoritesByDate(date: "YYYY-MM-DD", page: 1, limit: 10) {
    weatherFavorites {
      city
      date
      hourlyData {
        time
        temperature
        humidity
      }
    }
    page
  }
}
```

### Pagination

To enhance the retrieval of weather favorites, pagination has been implemented in the GraphQL API.

In the example above, I've specified the page parameter as 1 and the limit parameter as 10. This means I am requesting the first page of weather favorites for the specified date, with a limit of 10 items per page.