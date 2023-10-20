import requests
from requests.structures import CaseInsensitiveDict
from requests import Response
from bs4 import BeautifulSoup
import json

USERAGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
)

BASE_URL = "https://www.pinterest.com/"

class Profile:
    def __init__(self, json):
        self.__process(json)

    def __process(self, json):
        self.__process_profile(json)

    def __process_profile(self, json):
        USER_RESOURCE = json["resources"]["UserResource"]
        key = list(USER_RESOURCE.keys())[1]
        USER_DATA = USER_RESOURCE[key]["data"]

        IS_PRIVATE = USER_DATA["is_private_profile"]

        attributes = ["id","image_xlarge_url","about","username","follower_count","board_count"]

        for attribute in attributes:
            setattr(self, "pfp_url" if attribute == "image_xlarge_url" else attribute, None if attribute not in USER_DATA else USER_DATA[attribute])

        self.full_name = USER_DATA["full_name"]
        self.first_name = USER_DATA["first_name"]
        self.last_name = None if IS_PRIVATE else USER_DATA["full_name"].replace(USER_DATA["first_name"] + " ","",1)

        self.is_private_profile = IS_PRIVATE

class Pinterest:
    def __init__(
        self,
        proxies = None,
        user_agent = None
    ):
        self.proxies = proxies
        self.user_agent = user_agent
        self.http = requests.session()

        if self.user_agent is None:
            self.user_agent = USERAGENT
    
    def request(self, method, url, data=None, files=None, extra_headers=None) -> Response:
        headers = CaseInsensitiveDict(
            [
                ("Referer", BASE_URL),
                ("X-Requested-With", "XMLHttpRequest"),
                ("Accept", "application/json"),
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
            ]
        )
        csrftoken = self.http.cookies.get("csrftoken")
        if csrftoken:
            headers.update([("X-CSRFToken", csrftoken)])

        if extra_headers is not None:
            for h in extra_headers:
                headers.update([(h, extra_headers[h])])

        response = self.http.request(
            method, url, data=data, headers=headers, files=files, proxies=self.proxies
        )
        response.raise_for_status()

        return response

    def get_profile(self, username) -> Profile:
        res = self.request("GET",f"https://www.pinterest.com/{username}")
        soup = BeautifulSoup(res.text, 'html.parser')

        scripts = soup.find_all('script')

        for script in scripts:
            if(script.get("id") == "__PWS_DATA__"):
                open("__PWS_DATA__.json","w",encoding="utf-8").write(script.string);
                DATA = json.loads(script.string)["props"]["initialReduxState"]
                return Profile(json=DATA)


if __name__ == "__main__":
    pinterest = Pinterest()
    profile = pinterest.get_profile("eggogbolle")
    print(profile.username)
    print(profile.first_name)
    print(profile.last_name)
    print(profile.pfp_url)
    print(profile.follower_count)