from instagramy import InstagramLocation

from instagramy.core.parser import Parser, Viewer
from instagramy.core.exceptions import LocationNotFound, RedirectionError
from instagramy.core.exceptions import HTTPError
from instagramy.core.requests import get

""" Wrapper for urllib.request """
import requests
import random
from typing import Any
from urllib.request import urlopen, Request
import urllib.request as req
from instagramy.core.user_agent import user_agents

def get(url: str, sessionid='4526877383%3A73r9DocYUXeRMk%3A15') -> Any:
    """
    Function send the HTTP requests to Instagram and
    Login into Instagram with session id
    and return the Html Content
    """

    # request = Request(
    #     url=url, headers={"User-Agent": f"user-agent: {random.choice(user_agents)}"}
    # )

    # proxy = req.ProxyHandler({'http': r'http://ylnmpdzr-rotate:fcyzrvj2mpa3@144.168.240.154:80'})
    # auth = req.HTTPBasicAuthHandler()
    # opener = req.build_opener(proxy, auth, req.HTTPHandler)
    # if sessionid:
    #     opener.addheaders = [('Cookie', f"sessionid={sessionid}"), ('User-Agent', random.choice(user_agents))]
    #     # req.add_header("Cookie", f"sessionid={sessionid}")

    # req.install_opener(opener)
    # with req.urlopen(url) as response:
    #     html = response.read()

    response = requests.get(url, headers={'User-Agent': random.choice(user_agents), 'Cookie': f'sessionid={sessionid}'})
    return str(response.text)



class InstaLocation(InstagramLocation):

    def __init__(self, location_id: str, slug: str, sessionid=None, from_cache=False):
        self.url = f"https://www.instagram.com/explore/locations/{location_id}/{slug}"
        self.sessionid = sessionid
        # location = location_id + "_" + slug
        # cache = Cache("location")
        # if from_cache:
        #     if cache.is_exists(location):
        #         self.location_data = cache.read_cache(location)
        #     else:
        #         data = self.get_json()
        #         cache.make_cache(
        #             location, data["entry_data"]["LocationsPage"][0]["graphql"]["location"]
        #         )
        #         self.location_data = data["entry_data"]["LocationsPage"][0]["graphql"]["location"]
        # else:
        #     data = self.get_json()
        #     cache.make_cache(
        #         location, data["entry_data"]["LocationsPage"][0]["graphql"]["location"]
        #     )
        #     try:
        #         self.location_data = data["entry_data"]["LocationsPage"][0]["graphql"]["location"]
        #     except KeyError:
        #         raise RedirectionError

        data = self.get_json()
        # print(data["entry_data"]["LocationsPage"])
        try:
            self.location_data = data["entry_data"]["LocationsPage"][0]["graphql"]["location"]
        except KeyError:
            raise RedirectionError
        # if sessionid:
        #     try:
        #         self.viewer = Viewer(data=data["config"]["viewer"])
        #     except UnboundLocalError:
        #         self.viewer = None
        # else:
        #     self.viewer = None
            

    def get_json(self) -> dict:
        """ Get Location information from Instagram """

        try:
            html = get(self.url, sessionid=self.sessionid)
        except HTTPError:
            raise LocationNotFound(self.url.split("/")[-2] + "_" + self.url.split("/")[-1])
        parser = Parser()
        parser.feed(html)
        return parser.Data