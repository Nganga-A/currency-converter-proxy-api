# Currency Converter App API proxy using FastAPI with Redis

A RESTful API proxy made using FastAPI for the currency converter app project

The API proxy is able to:
- Receive, process and respond to requests from the currency-converter app
- Cache results for the most frequent API calls with Redis
- Periodically update cached responses
- Improve access times when returning cached results instead of making new API calls