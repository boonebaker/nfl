import streamlit as st
import requests
from uuid import uuid4

# ESPN MLB scoreboard API for today's games
SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"

# Function to fetch today's games
def fetch_games():
    response = requests.get(SCOREBOARD_URL)
    data = response.json()
    games = []
    for event in data.get("events", []):
        game_id = event.get("id")
        name = event.get("name")
        competitions = event.get("competitions", [])
        if competitions:
            competitors = competitions[0].get("competitors", [])
            teams = [team["team"]["displayName"] for team in competitors]
            games.append({"id": game_id, "name": name, "teams": teams})
    return games

# Function to fetch players from a game
def fetch_players(game_id):
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/summary?event={game_id}"
    response = requests.get(url)
    data = response.json()
    players = []
    for team in data.get("boxscore", {}).get("players", []):
        for group in team.get("statistics", []):
            for athlete in group.get("athletes", []):
                name = athlete["athlete"]["displayName"]
                players.append(name)
    return sorted(set(players))

# Function to fetch player stats
def fetch_player_stat(game_id, player_name, stat_type):
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/summary?event={game_id}"
    response = requests.get(url)
    data = response.json()
    for team in data.get("boxscore", {}).get("players", []):
        for group in team.get("statistics", []):
            desc = group.get("descriptions", [])
            for athlete in group.get("athletes", []):
                if athlete["athlete"]["displayName"] == player_name:
                    stats = athlete.get("stats", [])
                    stat_dict = dict(zip(desc, stats))
                    return int(stat_dict.get(stat_type, "0"))
    return 0

# Streamlit UI
st.title("⚾ MLB Real-Time Stat Tracker")

games = fetch_games()
game_options = {game["name"]: game["id"] for game in games}
selected_games = st.multiselect("Select Games", options=list(game_options.keys()))

if "cards" not in st.session_state:
    st.session_state.cards = []

for game_name in selected_games:
    game_id = game_options[game_name]
    with st.expander(f"Select Player and Stat for {game_name}"):
        players = fetch_players(game_id)
        player = st.selectbox(f"Player from {game_name}", players, key=f"player_{game_id}")
        stat_type = st.text_input("Stat to Monitor (e.g., Hits)", key=f"stat_{game_id}")
        target = st.number_input("Target Value", min_value=0, step=1, key=f"target_{game_id}")
        if st.button("Add Tracker", key=f"add_{game_id}_{uuid4()}"):
            st.session_state.cards.append({
                "game_id": game_id,
                "game_name": game_name,
                "player": player,
                "stat_type": stat_type,
                "target": target
            })

st.subheader("📊 Tracking Cards")

for card in st.session_state.cards:
    stat_value = fetch_player_stat(card["game_id"], card["player"], card["stat_type"])
    color = "lightgreen" if stat_value >= card["target"] else "lightcoral"
    st.markdown(
        f"<div style='background-color:{color};padding:10px;border-radius:5px;'>"
        f"<strong>{card['player']}</strong> in <em>{card['game_name']}</em><br>"
        f"{card['stat_type']}: {stat_value} / {card['target']}"
        f"</div>",
        unsafe_allow_html=True
    )
