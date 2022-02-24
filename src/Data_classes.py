from abc import ABC
import json
from Requests import make_request

class Data(ABC):

    async def fetch_search(self, name) -> bool:
        (b, r) = await make_request("https://api.jikan.moe/v4/{}?q={}&sfw&order_by=popularity".format(self.info["type"], name))
        if not b:
            return False
        self.search = json.loads(r.content)["data"]
        return True

    async def fetch_list(self, username) -> bool:
        self.table = []
        page = 1
        while True:
            (b, r) = await make_request("https://api.jikan.moe/v4/users/{}/{}?page={}".format(username, self.info["list"], page))
            if not b:
                return False
            table = json.loads(r.content)["data"]
            self.table += table
            if len(table) < 300:
                return True
            page += 1    

    def get_search(self):
        return self.search

    def get_table(self):
        return self.table

    def get_header(self):
        return self.header

    def get_search_header(self):
        return self.search_header

    def get_status(self):
        return self.status

    def get_info(self):
        return self.info

    def get_genres(self, entry):
        genres = ""
        for genre in entry["genres"]:
            genres += genre["name"] + ", "
        return genres[:-2]

class AnimeData(Data):
    def __init__(self) -> None:
        self.status = {1: ("Watching", 0x2db039), 2: ("Completed", 0x26448f), 3: ("On Hold", 0xf9d457), 4: ("Dropped", 0xa12f31), 6: ("PTW", 0xc3c3c3)}
        self.header = ["Title", "Status", "Score", "Eps. watched", "Start date", "End date", "Season", "Year", "Genres"]
        self.search_header = ["Title", "Avg. score", "Episodes", "Status", "Season", "Source", "Duration", "Genres"]
        self.info = {"type": "anime", "list": "animelist"}

    def get_element(self, entry):
        year = entry["anime"]["year"] if entry["anime"]["year"] != None else ""
        season = "{} {}".format(entry["anime"]["season"].capitalize(), year) if year != "" else ""
        return ([entry["anime"]["title"],
                 self.status[entry["watching_status"]][0],
                 entry["score"] if entry["score"] != 0 else "",
                 entry["episodes_watched"],
                 entry["watch_start_date"][:10] if entry["watch_start_date"] != None else "", 
                 entry["watch_end_date"][:10] if entry["watch_end_date"] != None else "",
                 season,
                 year,
                 self.get_genres(entry["anime"])],
                 entry["anime"]["url"],
                 entry["anime"]["images"]["jpg"]["large_image_url"])
    
    def get_entry(self, entry):
        year = entry["year"] if entry["year"] != None else "N/A"
        season = "{} {}".format(entry["season"].capitalize(), year) if year != "N/A" else "N/A"
        return ([entry["title"],
                 entry["score"],
                 entry["episodes"] if entry["episodes"] != None else "TBA",
                 entry["status"],
                 season,
                 entry["source"],
                 entry["duration"],
                 self.get_genres(entry)],
                 entry["url"],
                 entry["images"]["jpg"]["large_image_url"])


class MangaData(Data):
    def __init__(self) -> None:
        self.status = {1: ("Reading", 0x2db039), 2: ("Completed", 0x26448f), 3: ("On Hold", 0xf9d457), 4: ("Dropped", 0xa12f31), 6: ("PTR", 0xc3c3c3)}
        self.header = ["Title", "Status", "Score", "Chaps. read", "Vols. read", "Start date", "End date", "Type", "Genres"]
        self.search_header = ["Title", "Avg. score", "Type", "Chapters", "Volumes", "Status", "Genres"]
        self.info = {"type": "manga", "list": "mangalist"}

    def get_element(self, entry):
        return ([entry["manga"]["title"],
                 self.status[entry["reading_status"]][0],
                 entry["score"] if entry["score"] != 0 else "",
                 entry["chapters_read"],
                 entry["volumes_read"],
                 entry["read_start_date"][:10] if entry["read_start_date"] != None else "", 
                 entry["read_end_date"][:10] if entry["read_end_date"] != None else "",
                 entry["manga"]["type"],
                 self.get_genres(entry["manga"])],
                 entry["manga"]["url"],
                 entry["manga"]["images"]["jpg"]["large_image_url"])
            
    def get_entry(self, entry):
        return ([entry["title"],
                 entry["scored"],
                 entry["type"],
                 entry["chapters"] if entry["chapters"] != None else "TBA",
                 entry["volumes"] if entry["volumes"] != None else "TBA",
                 entry["status"],
                 self.get_genres(entry)],
                 entry["url"],
                 entry["images"]["jpg"]["large_image_url"])