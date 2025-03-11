import requests
from abc import ABC, abstractmethod
from settings import TMDB_ACCESS_TOKEN

TMDB_BASE_URL = "https://api.themoviedb.org/3/"


class TMDBAPIError(Exception):
    pass


class TMDBClient:
    def __init__(self):
        self.headers = {'Authorization': f'Bearer {TMDB_ACCESS_TOKEN}'}

    def get(self, url: str) -> requests.Response:
        response = requests.get(url=url, headers=self.headers)
        if response.status_code == 200:
            return response
        else:
            raise TMDBAPIError(
                f"Unexpected response {response.text}."
            )


class TMDBEndpoint(ABC):
    @abstractmethod
    def get_url(self) -> str:
        pass


class TMDBMovieAPI:
    def __init__(self, client: TMDBClient, endpoint: TMDBEndpoint):
        self.client = client
        self.endpoint = endpoint

    def fetch(self):
        url = self.endpoint.get_url()
        return self.client.get(url=url)


class TMDBMovieSearch(TMDBEndpoint):
    def __init__(self, query: str, page: int, include_adult: bool = False):
        self.query = query
        self.page = page
        self.include_adult = include_adult

    def get_url(self) -> str:
        return f"{TMDB_BASE_URL}search/movie?query={self.query}&include_adult={self.include_adult}&page={self.page}"


class TMDBMovieDiscovery(TMDBEndpoint):
    def __init__(self, page: int, include_adult: bool = False):
        self.page = page
        self.include_adult = include_adult

    def get_url(self) -> str:
        return f"{TMDB_BASE_URL}discover/movie?include_adult={self.include_adult}&page={self.page}"


class TMDBMovieById(TMDBEndpoint):
    def __init__(self, movie_id: int):
        self.movie_id = movie_id

    def get_url(self) -> str:
        return f"{TMDB_BASE_URL}movie/{self.movie_id}"
