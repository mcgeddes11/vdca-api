import re
import pandas
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import numpy


def get_html_from_response(response_text):
    parsed = re.findall(r'\(\"([^}]*)\"\)', response_text)
    if len(parsed) > 1:
        raise Exception("Parsing of crappy document.write() encoded response failed")
    return parsed[0]


def get_table_from_html(html):
    soup = BeautifulSoup(html, features="lxml")
    data = []
    urls = []
    table = soup.find('table')

    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        col_vals = []
        for ele in cols:
            if ele.find("a"):
                urls.append(ele.find("a").get("href"))
            col_vals.append(ele.text.strip())
        data.append(col_vals)

    # we expect first row to be headers
    col_headers = data[0]
    data = data[1:]

    # check we got a url for everyone
    assert(len(data) == len(urls))

    # Add the player url to our table
    col_headers.append("player_url")
    for ix, el in enumerate(urls):
        data[ix].append(el)

    # Create a table from the results
    df = pandas.DataFrame(data=data, columns=col_headers)
    df.drop("#", axis=1, inplace=True)
    return df


def get_playerid_from_url(url):
    # Extract player_id from URL
    match = re.findall(r"playerid=\d+", url)
    if len(match) == 0:
        raise Exception("Unable to extract playerid from url: {}".format(url))
    player_id = int(match[0].replace("playerid=", ""))
    return player_id


def get_team_season_grade_combinations(seasons, fixtures):
    # Convert to dataframe, parse the dates, get year component for season
    fixtures = pandas.DataFrame.from_records(fixtures)
    fixtures["yr"] = [datetime.strptime(x,"%Y-%m-%dT%H:%M:%S").year for x in fixtures["DatePlayed"].values]
    fixtures.drop(["DatePlayed", "Ground", "MatchID"], axis=1, inplace=True)
    # Split out, stack, take unique
    fhome = fixtures[["HomeTeam", "Grade", "yr"]]
    faway = fixtures[["AwayTeam", "Grade", "yr"]]
    fhome.columns = ["Team", "Grade", "Season"]
    faway.columns = ["Team", "Grade", "Season"]
    f_all = pandas.concat((fhome, faway), axis=0)
    f_all.reset_index(inplace=True, drop=True)
    f_all.drop_duplicates(inplace=True)
    ix = numpy.array([x in seasons for x in f_all["Season"].values])
    f_all = f_all[ix]
    f_all.reset_index(drop=True, inplace=True)
    return f_all


def get_teams(url, club_id):
    url = url + "getteams.aspx?league={}".format(club_id)
    response = requests.get(url)
    response.raise_for_status()
    team_list = response.json()
    team_dict = {}
    for t in team_list:
        team_dict[t["TeamID"]] = t["Name"]
    return team_dict

