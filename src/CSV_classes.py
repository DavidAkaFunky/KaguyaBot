from abc import ABC
import json, requests, discord
from aio_jikan import AioJikan

class Data(ABC):

    async def fetch_data(self, ctx, data, csv, username):
        self.table = []
        page = 1
        async with AioJikan() as aio_jikan:
            table = aio_jikan.user(username=username, request=self.info["list"], parameters={'page': page})
            self.table.append(table)
            if len(table) < 300:
                return
            page += 1

    def get_header(self):
        return self.header

    def get_genres(self, entry):
        genres = ""
        for genre in entry[self.info["type"]]["genres"]:
            genres += genre["name"] + ", "
        return genres[:-2]

class AnimeData(Data):
    def __init__(self) -> None:
        self.status = {1: ("Watching", 0x2db039), 2: ("Completed", 0x26448f), 3: ("On Hold", 0xf9d457), 4: ("Dropped", 0xa12f31), 6: ("PTW", 0xc3c3c3)}
        self.header = ["Title", "Status", "Score", "Eps. watched", "Start date", "End date", "Season", "Year", "Genres"]
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
                self.get_genres(entry)],
                entry["anime"]["url"],
                entry["anime"]["images"]["jpg"]["large_image_url"])

class MangaData(Data):
    def __init__(self) -> None:
        self.status = {1: ("Reading", 0x2db039), 2: ("Completed", 0x26448f), 3: ("On Hold", 0xf9d457), 4: ("Dropped", 0xa12f31), 6: ("PTR", 0xc3c3c3)}
        self.header = ["Title", "Status", "Score", "Chaps. read", "Vols. read", "Start date", "End date", "Type", "Genres"]
        self.info = {"type": "manga", "list": "mangalist"}

    def get_element(self, entry):
        return [entry["manga"]["title"],
                self.status[entry["reading_status"]][0],
                entry["score"] if entry["score"] != 0 else "",
                entry["chapters_read"],
                entry["volumes_read"],
                entry["read_start_date"][:10] if entry["read_start_date"] != None else "", 
                entry["read_end_date"][:10] if entry["read_end_date"] != None else "",
                entry["manga"]["type"],
                self.get_genres(entry)]
            
def setup(bot):
    bot.add_cog(CSV_classes(bot))