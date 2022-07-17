import discord, csv
from os import remove, environ

class CSV:

    async def get_csv(self, ctx, username, data):
        filename = username + ".csv"
        with open(filename, "w", newline = "") as out:
            csv_writer = csv.writer(out, delimiter  = ";")
            content = await data.fetch_list(username)
            if content != None:
                csv_writer.writerow(data.get_header())
                for entry in content:
                    csv_writer.writerow(data.get_csv_line(entry))
        with open(filename, "rb") as out:
            await ctx.send("Hey there! Here's your CSV file. If there's data missing, be sure to make it public on MAL!", file = discord.File(out, filename), hidden = True)
        remove(filename)
        with open("Graph.xlsx", "rb") as out:
            await ctx.send("Import your CSV file to this Excel file:", file = discord.File(out, "Graph.xlsx"), hidden = True)