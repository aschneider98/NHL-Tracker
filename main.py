import requests
import json
import pandas as pd
import plotly.graph_objects as go

seasonTitle = '2020-2021'
season = seasonTitle.replace('-', '')

colors = {
    'Edmonton Oilers': 'rgb(252, 76, 0)',
    'Vancouver Canucks': 'rgb(10,134,61)',
    'Columbus Blue Jackets': 'rgb(0,38,84)',
    'Chicago Blackhawks': 'rgb(207,10,44)',
    'Arizona Coyotes': 'rgb(169,67,30)',
    'St. Louis Blues': 'rgb(0, 47, 135)',
    'Toronto Maple Leafs': 'rgb(0, 32, 91)',
    'Ottawa Senators': 'rgb(197, 32, 50)',
    'San Jose Sharks': 'rgb(0, 109, 117)',
    'Los Angeles Kings': 'rgb(162,170,173)',
    'New Jersey Devils': 'rgb(206, 17, 38)',
    'Pittsburgh Penguins': 'rgb(252,181,20)',
    'Montréal Canadiens': 'rgb(175, 30, 45)',
    'Calgary Flames': 'rgb(200,16,46)',
    'Vegas Golden Knights': 'rgb(185,151,91)',
    'Carolina Hurricanes': 'rgb(226,24,54)',
    'Detroit Red Wings': 'rgb(206,17,38)',
    'Boston Bruins': 'rgb(252, 181, 20)',
    'Washington Capitals': 'rgb(200, 16, 46)',
    'New York Rangers': 'rgb(0,56,168)',
    'Buffalo Sabres': 'rgb(0,38,84)',
    'Winnipeg Jets': 'rgb(4,30,66)',
    'Florida Panthers': 'rgb(200,16,46)',
    'Minnesota Wild': 'rgb(2, 73, 48)',
    'Anaheim Ducks': 'rgb(252, 76, 2)',
    'New York Islanders': 'rgb(244, 125, 48)',
    'Colorado Avalanche': 'rgb(111, 38, 61)',
    'Dallas Stars': 'rgb(0, 104, 71)',
    'Tampa Bay Lightning': 'rgb(0, 40, 104)',
    'Philadelphia Flyers': 'rgb(247, 73, 2)',
    'Seattle Kraken': 'rgb(153, 217, 217)',
    'Nashville Predators': 'rgb(255,184,28)'
}

pd.options.plotting.backend = 'plotly'


# Returns total number of games played this season (Number of teams * Number of games)
def getTotal():
    url = f"""https://api.nhle.com/stats/rest/en/team/summary?isAggregate=false&isGame=true&
    start=0&limit=100&cayenneExp=gameTypeId=2%20and%20seasonId%3C={season}%20and%20seasonId%3E={season}"""

    headers = {
        'authority': 'api.nhle.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'accept': '*/*',
        'sec-gpc': '1',
        'origin': 'http://www.nhl.com',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'http://www.nhl.com/',
        'accept-language': 'en-US,en;q=0.9'
    }

    r = requests.get(url, headers=headers)
    standings = r.json()
    return standings['total']


# Fetches data 100 games at a time due to API limitations
def getData(interval):
    url = f'https://api.nhle.com/stats/rest/en/team/summary?isAggregate=false&isGame=true&limit=100&cayenneExp=gameTypeId=2%20and%20seasonId%3C={season}%20and%20seasonId%3E={season}&start={interval}'

    headers = {
        'authority': 'api.nhle.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'accept': '*/*',
        'sec-gpc': '1',
        'origin': 'http://www.nhl.com',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'http://www.nhl.com/',
        'accept-language': 'en-US,en;q=0.9'
    }

    r = requests.get(url, headers=headers)
    standings = r.json()
    gamedata = standings['data']
    return gamedata


# Calculates partial sums of points and games played for each team
def partialSum(df):
    start = 1
    for i in range(start, totalGames):
        if df.iat[i, 2] == df.iat[i - 1, 2]:
            df.iat[i, 1] = df.iat[i, 1] + df.iat[i - 1, 1]  # partial sum for points
            df.iat[i, 3] = df.iat[i, 3] + df.iat[i - 1, 3]  # partial sum for games played
        else:
            start = i


# Plots standings using plotly
def plotStandings(graph='all', xvals='gamesPlayed'):
    fig = go.Figure()
    if xvals == 'gameDate':
        xtitle = 'Date'
    elif xvals == 'gamesPlayed':
        xtitle = 'Games Played'
    if graph == 'all':
        for team in seasonData['teamFullName'].unique():
            df = seasonData.loc[seasonData['teamFullName'] == team]
            fig.add_trace(go.Scatter(x=df[xvals], y=df['points'], mode='lines', name=team, line_color=colors[team],
                                     line_width=3))
            fig.update_layout(title=f'NHL Standings {seasonTitle}', xaxis_title=xtitle, yaxis_title='Points')
            fig.update_layout(
                yaxis=dict(
                    tickmode='linear',
                    tick0=0,
                    dtick=2
                )
            )
    elif graph == 'divisions':
        print('Still working on that, come back later')
    elif graph in seasonData['teamFullName'].unique():
        df = seasonData.loc[seasonData['teamFullName'] == graph]
        fig.add_trace(go.Scatter(x=df[xvals], y=df['points'], mode='lines', name=graph, line_color=colors[graph],
                                 line_width=3))
        fig.update_layout(title=graph + ' ' + seasonTitle, xaxis_title=xtitle, yaxis_title='Points')
    if xvals == 'gamesPlayed':
        fig.update_layout(
            xaxis=dict(
                tickmode='linear',
                tick0=0
            )
        )
    fig.show()


# Retrieve data from NHL, store as list of JSON objects for each game
totalGames = getTotal()
gamesList = []
for i in range(0, totalGames, 100):
    gamesList.extend(getData(i))

# Use Pandas to put data into dataframe, isolate columns needed, and sort
seasonData = pd.json_normalize(gamesList)
seasonData = seasonData[['gameDate', 'points', 'teamFullName', 'gamesPlayed']]
seasonData = seasonData.sort_values(['teamFullName', 'gameDate'])

# Calculate partial sums
partialSum(seasonData)

# Plot standings
# First argument is name of single team to graph, or all teams
# Second argument is x value in graph, shows how the season progresses (by number of games played or by calendar date)
# Second argument can either be gamesPlayed or gameDate
plotStandings('all', 'gameDate')
