from abc import ABC
from Requests import make_request
from datetime import datetime

class Data(ABC):

    async def fetch_search(self, name) -> bool:
        return await make_request("https://api.jikan.moe/v4/{}?q={}&sfw&order_by=popularity".format(self.info["type"], name))

    async def fetch_list(self, username):
        table = []
        i = 1
        while True:
            page = await make_request("https://api.jikan.moe/v4/users/{}/{}?page={}".format(username, self.info["list"], i))
            if page == None:
                return None
            table += page
            if len(page) < 300:
                return table
            i += 1

    def get_header(self):
        return self.header

    def get_info(self):
        return self.info

    def get_genres(self, entry):
        genres = ""
        for genre in entry["genres"]:
            genres += genre["name"] + ", "
        return genres[:-2] if genres != "" else "N/A"

    def get_value(self, value, alt):
        return value if value not in (None, 0) else alt


class AnimeData(Data):

    def __init__(self) -> None:
        self.status = {1: "Watching", 2: "Completed", 3: "On Hold", 4: "Dropped", 6: "PTW"}
        self.colour = {"Watching": 0x2db039, "Currently Airing": 0x2db039, "Completed": 0x26448f, "Finished Airing": 0x26448f, "On Hold": 0xf9d457, "Dropped": 0xa12f31, "PTW": 0xc3c3c3, "Not yet aired": 0xc3c3c3}
        self.header = ["Title", "Status", "Score", "Eps. watched", "Start date", "End date", "Season", "Year", "Genres"]
        self.info = {"type": "anime", "list": "animelist"}

    def get_season(self, season, year, flag):
        if year not in ("", "N/A") and season != None:
            return "{} {}".format(season.capitalize(), year)
        else:
            return "" if flag else "N/A"

    def get_csv_line(self, entry):
        year = self.get_value(entry["anime"]["year"], "")
        season = self.get_season(entry["anime"]["season"], year, True)
        return [entry["anime"]["title"],
                self.status[entry["watching_status"]],
                self.get_value(entry["score"], ""),
                entry["episodes_watched"],
                self.get_value(entry["watch_start_date"], "")[:10], 
                self.get_value(entry["watch_end_date"], "")[:10],
                season,
                year,
                self.get_genres(entry["anime"])]
    
    def get_list_entry(self, entry):
        year = self.get_value(entry["anime"]["year"], "N/A")
        season = self.get_season(entry["anime"]["season"], year, False)
        status = self.status[entry["watching_status"]]
        return {"Title": entry["anime"]["title"],
                "Colour": self.colour[status],
                "Data": {"Status": status,
                         "Score": self.get_value(entry["score"], "N/A"),
                         "Eps. watched": entry["episodes_watched"],
                         "Start date": self.get_value(entry["watch_start_date"], "N/A")[:10], 
                         "End date": self.get_value(entry["watch_end_date"], "N/A")[:10],
                         "Season": season,
                         "Genres": self.get_genres(entry["anime"])},
                "URL": entry["anime"]["url"],
                "Image": entry["anime"]["images"]["jpg"]["large_image_url"]}

    def get_search_entry(self, entry):
        year = self.get_value(entry["year"], "N/A")
        season = self.get_season(entry["season"], year, False)
        status = entry["status"]
        return {"Title": entry["title"],
                "Colour": self.colour[status],
                "Data": {"Status": status,
                         "Avg. score": entry["score"],
                         "Episodes": self.get_value(entry["episodes"], "TBA"),
                         "Season": season,
                         "Source": entry["source"],
                         "Duration per ep.": self.get_value(entry["duration"], "TBA"),
                         "Genres": self.get_genres(entry)},
                "URL": entry["url"],
                "Image": entry["images"]["jpg"]["large_image_url"]}

    def get_stats(self, data):
        return {"Data": {"Total entries": data["total_entries"],
                         "Eps. watched": data["episodes_watched"],
                         "Days watched": data["days_watched"],
                         "Mean score": data["mean_score"],
                         "Watching": data["watching"],
                         "Completed": data["completed"],
                         "On hold": data["on_hold"],
                         "Dropped": data["dropped"],
                         "Plan to Watch": data["plan_to_watch"],
                         "Rewatched": data["rewatched"]}}


class MangaData(Data):

    def __init__(self) -> None:
        self.status = {1: "Reading", 2: "Completed", 3: "On Hold", 4: "Dropped", 6: "PTR"}
        self.colour = {"Reading": 0x2db039, "Publishing": 0x2db039, "Completed": 0x26448f, "Finished": 0x26448f, "On Hold": 0xf9d457, "On Hiatus": 0xf9d457, "Dropped": 0xa12f31, "Discontinued": 0xa12f31, "PTR": 0xc3c3c3, "Not yet published": 0xc3c3c3}
        self.header = ["Title", "Status", "Score", "Chaps. read", "Vols. read", "Start date", "End date", "Type", "Genres"]
        self.info = {"type": "manga", "list": "mangalist"}

    def get_csv_line(self, entry):
        return [entry["manga"]["title"],
                self.status[entry["reading_status"]],
                self.get_value(entry["score"], ""),
                entry["chapters_read"],
                entry["volumes_read"],
                self.get_value(entry["read_start_date"], "")[:10], 
                self.get_value(entry["read_end_date"], "")[:10],
                entry["manga"]["type"],
                self.get_genres(entry["manga"])]

    def get_list_entry(self, entry):
        status = self.status[entry["reading_status"]]
        return {"Title": entry["manga"]["title"],
                "Colour": self.colour[status],
                "Data": {"Status": status,
                         "Score": self.get_value(entry["score"], "N/A"),
                         "Chaps. read": entry["chapters_read"],
                         "Vols. read": entry["volumes_read"],
                         "Start date": self.get_value(entry["read_start_date"], "N/A")[:10], 
                         "End date": self.get_value(entry["read_end_date"], "N/A")[:10],
                         "Type": entry["manga"]["type"],
                         "Genres": self.get_genres(entry["manga"])},
                "URL": entry["manga"]["url"],
                "Image": entry["manga"]["images"]["jpg"]["large_image_url"]}
            
    def get_search_entry(self, entry):
        status = entry["status"]
        return {"Title": entry["title"],
                "Colour": self.colour[status],
                "Data": {"Status": status,
                         "Avg. score": self.get_value(entry["scored"], "N/A"),
                         "Type": entry["type"],
                         "Chapters": self.get_value(entry["chapters"], "TBA"),
                         "Volumes": self.get_value(entry["volumes"], "TBA"),
                         "Genres": self.get_genres(entry)},
                "URL": entry["url"],
                "Image": entry["images"]["jpg"]["large_image_url"]}

    def get_stats(self, data):
        return {"Data": {"Total entries": data["total_entries"],
                         "Chaps. read": data["chapters_read"],
                         "Vols. read": data["volumes_read"],
                         "Days read": data["days_read"],
                         "Mean score": data["mean_score"],
                         "Reading": data["reading"],
                         "Completed": data["completed"],
                         "On hold": data["on_hold"],
                         "Dropped": data["dropped"],
                         "Plan to Read": data["plan_to_read"],
                         "Reread": data["reread"]}}


class User():

    def get_colour(self, gender):
        if gender == "Male":
            return 0x26448f
        elif gender == "Female":
            return 0xff8da1
        return 0xffbf00

    def get_user_data(self, user):
        gender = user["gender"] if user["gender"] != None else "N/A"
        return {"Name": user["username"],
                "Colour": self.get_colour(gender),
                "Data": {"Gender": gender,
                         "Last online": datetime.strptime(user["last_online"], "%Y-%m-%dT%H:%M:%S%z") if user["last_online"] != None else None,
                         "Birthday": datetime.strptime(user["birthday"], "%Y-%m-%dT%H:%M:%S%z").date() if user["birthday"] != None else None,
                         "Joined": datetime.strptime(user["joined"], "%Y-%m-%dT%H:%M:%S%z").date() if user["joined"] != None else None,
                         "Location": user["location"]},
                "URL": user["url"],
                "Image": user["images"]["jpg"]["image_url"]}


class Character():

    def get_nicknames(self, nicknames):
        res = ""
        if nicknames == []:
            return "N/A"
        for el in nicknames:
            res += el + ", "
        return res[:-2]

    def get_about(self, character):
        res = ""
        for el in character["about"].split("."):
            el += ". "
            if len(res) + len(el) > 1025:
                return res[:-2]
            res += el
        return res[:-2] if res != "" else "N/A"

    async def get_images(self, character):
        imgs = await make_request("https://api.jikan.moe/v4/characters/{}/pictures".format(character["MAL_ID"]))
        if imgs == None:
            return
        imgs = [img["jpg"]["image_url"] for img in imgs]
        main = character["Main Image"]
        try:
            imgs.remove(main)
        except:
            pass
        return [main] + imgs

    async def get_character_data(self, character):
        return {"Name": character["name"],
                "Data": {"Nicknames": self.get_nicknames(character["nicknames"]),
                         "Favourites": character["favorites"]},
                "URL": character["url"],
                "About": self.get_about(character),
                "Main Image": character["images"]["jpg"]["image_url"],
                "MAL_ID": character["mal_id"]}