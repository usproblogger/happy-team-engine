import os
import math
import json
import requests
from datetime import datetime, timedelta, timezone

API_KEY = os.environ.get("ODDS_API_KEY")
HISTORY_FILE = "travel_history.json"

STADIUMS = {
    # NBA
    "Atlanta Hawks": (33.757, -84.396, -5), "Boston Celtics": (42.366, -71.062, -5),
    "Brooklyn Nets": (40.683, -73.975, -5), "Charlotte Hornets": (35.225, -80.839, -5),
    "Chicago Bulls": (41.881, -87.674, -6), "Cleveland Cavaliers": (41.496, -81.688, -5),
    "Dallas Mavericks": (32.790, -96.810, -6), "Denver Nuggets": (39.749, -105.008, -7),
    "Detroit Pistons": (42.341, -83.055, -5), "Golden State Warriors": (37.768, -122.388, -8),
    "Houston Rockets": (29.751, -95.362, -6), "Indiana Pacers": (39.764, -86.156, -5),
    "LA Clippers": (34.043, -118.267, -8), "Los Angeles Lakers": (34.043, -118.267, -8),
    "Memphis Grizzlies": (35.138, -90.051, -6), "Miami Heat": (25.781, -80.187, -5),
    "Milwaukee Bucks": (43.045, -87.917, -6), "Minnesota Timberwolves": (44.980, -93.276, -6),
    "New Orleans Pelicans": (29.949, -90.082, -6), "New York Knicks": (40.751, -73.993, -5),
    "Oklahoma City Thunder": (35.463, -97.515, -6), "Orlando Magic": (28.539, -81.384, -5),
    "Philadelphia 76ers": (39.901, -75.172, -5), "Phoenix Suns": (33.446, -112.071, -7),
    "Portland Trail Blazers": (45.532, -122.667, -8), "Sacramento Kings": (38.580, -121.500, -8),
    "San Antonio Spurs": (29.427, -98.438, -6), "Toronto Raptors": (43.643, -79.379, -5),
    "Utah Jazz": (40.768, -111.901, -7), "Washington Wizards": (38.898, -77.021, -5),

    # NHL
    "Anaheim Ducks": (33.808, -117.877, -8), "Boston Bruins": (42.366, -71.062, -5),
    "Buffalo Sabres": (42.875, -78.876, -5), "Calgary Flames": (51.037, -114.052, -7),
    "Carolina Hurricanes": (35.803, -78.722, -5), "Chicago Blackhawks": (41.881, -87.674, -6),
    "Colorado Avalanche": (39.749, -105.008, -7), "Columbus Blue Jackets": (39.969, -83.006, -5),
    "Dallas Stars": (32.790, -96.810, -6), "Detroit Red Wings": (42.341, -83.055, -5),
    "Edmonton Oilers": (53.547, -113.498, -7), "Florida Panthers": (26.158, -80.326, -5),
    "Los Angeles Kings": (34.043, -118.267, -8), "Minnesota Wild": (44.945, -93.101, -6),
    "Montreal Canadiens": (45.496, -73.569, -5), "Nashville Predators": (36.159, -86.779, -6),
    "New Jersey Devils": (40.734, -74.171, -5), "New York Islanders": (40.712, -73.726, -5),
    "New York Rangers": (40.751, -73.993, -5), "Ottawa Senators": (45.297, -75.927, -5),
    "Philadelphia Flyers": (39.901, -75.172, -5), "Pittsburgh Penguins": (40.439, -79.989, -5),
    "San Jose Sharks": (37.333, -121.901, -8), "Seattle Kraken": (47.622, -122.354, -8),
    "St. Louis Blues": (38.627, -90.203, -6), "Tampa Bay Lightning": (27.943, -82.452, -5),
    "Toronto Maple Leafs": (43.643, -79.379, -5), "Utah Hockey Club": (40.768, -111.901, -7),
    "Vancouver Canucks": (49.278, -123.109, -8), "Vegas Golden Knights": (36.103, -115.178, -8),
    "Washington Capitals": (38.898, -77.021, -5), "Winnipeg Jets": (49.893, -97.144, -6),

    # NFL
    "Arizona Cardinals": (33.528, -112.263, -7), "Atlanta Falcons": (33.755, -84.401, -5),
    "Baltimore Ravens": (39.278, -76.623, -5), "Buffalo Bills": (42.774, -78.787, -5),
    "Carolina Panthers": (35.226, -80.853, -5), "Chicago Bears": (41.862, -87.617, -6),
    "Cincinnati Bengals": (39.095, -84.516, -5), "Cleveland Browns": (41.506, -81.700, -5),
    "Dallas Cowboys": (32.747, -97.095, -6), "Denver Broncos": (39.744, -105.020, -7),
    "Detroit Lions": (42.340, -83.046, -5), "Green Bay Packers": (44.501, -88.062, -6),
    "Houston Texans": (29.685, -95.411, -6), "Indianapolis Colts": (39.760, -86.164, -5),
    "Jacksonville Jaguars": (30.324, -81.637, -5), "Kansas City Chiefs": (39.049, -94.484, -6),
    "Las Vegas Raiders": (36.091, -115.183, -8), "Los Angeles Chargers": (33.953, -118.339, -8),
    "Los Angeles Rams": (33.953, -118.339, -8), "Miami Dolphins": (25.958, -80.239, -5),
    "Minnesota Vikings": (44.974, -93.258, -6), "New England Patriots": (42.091, -71.264, -5),
    "New Orleans Saints": (29.951, -90.081, -6), "New York Giants": (40.813, -74.074, -5),
    "New York Jets": (40.813, -74.074, -5), "Philadelphia Eagles": (39.901, -75.168, -5),
    "Pittsburgh Steelers": (40.447, -80.016, -5), "San Francisco 49ers": (37.403, -121.970, -8),
    "Seattle Seahawks": (47.595, -122.332, -8), "Tampa Bay Buccaneers": (27.976, -82.503, -5),
    "Tennessee Titans": (36.166, -86.771, -6), "Washington Commanders": (38.908, -76.865, -5)
}

SPORTS = [
    {"odds_key": "basketball_nba", "espn": "basketball/nba", "cat": "basketball"},
    {"odds_key": "icehockey_nhl", "espn": "hockey/nhl", "cat": "hockey"},
    {"odds_key": "americanfootball_nfl", "espn": "football/nfl", "cat": "football"}
]

def calc_miles(c1, c2):
    R = 3958.8
    lat1, lon1, lat2, lon2 = map(math.radians, [c1[0], c1[1], c2[0], c2[1]])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_7d_travel_and_finals(espn_path):
    history = {}
    finals = {}
    now = datetime.now(timezone.utc)
    for days_ago in range(7, -1, -1):
        dt = now - timedelta(days=days_ago)
        date_str = dt.strftime("%Y%m%d")
        url = f"https://site.api.espn.com/apis/site/v2/sports/{espn_path}/scoreboard?dates={date_str}"
        try:
            data = requests.get(url, timeout=8).json()
            for ev in data.get("events", []):
                comp = ev["competitions"][0]
                completed = comp.get("status", {}).get("type", {}).get("completed", False)
                host = None
                scores = {}
                for c in comp["competitors"]:
                    name = c["team"]["displayName"]
                    if c["homeAway"] == "home":
                        host = name
                    try:
                        scores[name] = float(c.get("score", 0))
                    except (ValueError, TypeError):
                        scores[name] = 0.0
                    if days_ago > 0:
                        history.setdefault(name, {"venues": [], "last_dt": None})
                        if host:
                            history[name]["venues"].append(host)
                        history[name]["last_dt"] = dt
                if completed and len(scores) == 2:
                    teams = list(scores.keys())
                    key = tuple(sorted(teams))
                    finals[key] = scores
        except Exception:
            continue
    return history, finals

def evaluate_team(team, host_today, history):
    rec = history.get(team, {"venues": [], "last_dt": None})
    past_venues = rec["venues"]
    full_path = past_venues + [host_today]

    miles = 0
    tz_shifts = 0
    for i in range(1, len(full_path)):
        p_coord = STADIUMS.get(full_path[i-1])
        c_coord = STADIUMS.get(full_path[i])
        if p_coord and c_coord:
            miles += calc_miles(p_coord, c_coord)
            tz_shifts += abs(c_coord[2] - p_coord[2])

    is_home_game = (host_today == team)
    if is_home_game:
        current_road_legs = 0
    else:
        current_road_legs = 1
        for i in range(len(full_path) - 2, -1, -1):
            if full_path[i] == team:
                break
            current_road_legs += 1

    home_days = 4
    if rec["last_dt"]:
        home_days = max(1, (datetime.now(timezone.utc) - rec["last_dt"]).days)

    fatigue = min(100, round((miles / 40.0) + (tz_shifts * 12) + (current_road_legs * 15)))
    return fatigue, round(miles), current_road_legs, home_days

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return []

def grade_history(history_entries, finals_by_sport):
    for entry in history_entries:
        if entry.get("status") in ("won", "lost"):
            continue
        sport_finals = finals_by_sport.get(entry.get("sport"), {})
        home = entry.get("homeTeam")
        away = entry.get("awayTeam")
        if not home or not away:
            continue
        key = tuple(sorted([home, away]))
        scores = sport_finals.get(key)
        if not scores:
            continue
        h_score = scores.get(home, 0)
        a_score = scores.get(away, 0)
        entry["finalScore"] = f"{away} {int(a_score)} - {home} {int(h_score)}"
        if h_score == a_score:
            entry["status"] = "push"
            entry["netProfit"] = 0.0
        elif h_score > a_score:
            entry["status"] = "won"
            ml = float(entry.get("happyML", -110))
            profit = 100.0 * (ml / 100.0) if ml > 0 else 100.0 * (100.0 / abs(ml))
            entry["netProfit"] = round(profit, 2)
        else:
            entry["status"] = "lost"
            entry["netProfit"] = -100.0
    return history_entries

def run():
    results = []
    history_entries = load_history()
    existing_ids = {item.get("id") for item in history_entries if item.get("id")}
    finals_by_sport = {}
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for cfg in SPORTS:
        travel_map, finals = get_7d_travel_and_finals(cfg["espn"])
        finals_by_sport[cfg["cat"]] = finals

        url = f"https://api.the-odds-api.com/v4/sports/{cfg['odds_key']}/odds/"
        params = {"apiKey": API_KEY, "regions": "us", "markets": "h2h", "oddsFormat": "american"}
        try:
            games = requests.get(url, params=params, timeout=10).json()
            if not isinstance(games, list):
                continue
            for g in games:
                home, away = g.get("home_team"), g.get("away_team")
                bms = g.get("bookmakers", [])
                if not bms:
                    continue
                outcomes = bms[0]["markets"][0]["outcomes"]
                ml_map = {o["name"]: o["price"] for o in outcomes}
                home_ml, away_ml = ml_map.get(home, -110), ml_map.get(away, -110)

                away_fat, away_mi, away_commutes, _ = evaluate_team(away, home, travel_map)
                home_fat, _, _, home_stay_days = evaluate_team(home, home, travel_map)
                gap = away_fat - home_fat

                if gap >= 20 and home_fat <= 25:
                    matchup_str = f"✈️ {away} ({'+' if away_ml > 0 else ''}{away_ml}) @ 😊 {home} ({'+' if home_ml > 0 else ''}{home_ml})"
                    item = {
                        "sport": cfg["cat"],
                        "awayTeam": away,
                        "homeTeam": home,
                        "matchup": matchup_str,
                        "routeNote": f"Road trip across {away_commutes} stops away from home",
                        "miles": away_mi,
                        "legs": away_commutes,
                        "restSummary": f"{home_stay_days} days home resting",
                        "exhaustionGap": gap,
                        "happyML": home_ml
                    }
                    results.append(item)

                    pick_id = f"{today_str}_{cfg['cat']}_{away}_{home}"
                    if pick_id not in existing_ids:
                        existing_ids.add(pick_id)
                        history_entries.append({
                            "id": pick_id,
                            "date": today_str,
                            "sport": cfg["cat"],
                            "awayTeam": away,
                            "homeTeam": home,
                            "matchup": matchup_str,
                            "legs": away_commutes,
                            "exhaustionGap": gap,
                            "happyML": home_ml,
                            "status": "pending",
                            "finalScore": "",
                            "netProfit": 0.0
                        })
        except Exception as e:
            print(f"Error {cfg['odds_key']}: {e}")

    history_entries = grade_history(history_entries, finals_by_sport)

    with open("travel_data.json", "w") as f:
        json.dump(results, f, indent=2)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history_entries, f, indent=2)

if __name__ == "__main__":
    run()
