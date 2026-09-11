"""
Realistic Multi-Season Historical IPL Sample Dataset Generator.
Generates comprehensive historical data across multiple seasons (2018-2024),
10 franchise teams, real marquee players, ball-by-ball events, wickets,
toss decisions, and match results.
Ensures zero runtime dependency on external downloads for local college evaluations.
"""

import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

TEAMS = [
    "Chennai Super Kings",
    "Mumbai Indians",
    "Royal Challengers Bengaluru",
    "Kolkata Knight Riders",
    "Delhi Capitals",
    "Punjab Kings",
    "Rajasthan Royals",
    "Sunrisers Hyderabad",
    "Gujarat Titans",
    "Lucknow Super Giants"
]

VENUES = {
    "Wankhede Stadium, Mumbai": "Mumbai",
    "M Chinnaswamy Stadium, Bengaluru": "Bengaluru",
    "MA Chidambaram Stadium, Chepauk, Chennai": "Chennai",
    "Eden Gardens, Kolkata": "Kolkata",
    "Arun Jaitley Stadium, Delhi": "Delhi",
    "Narendra Modi Stadium, Ahmedabad": "Ahmedabad",
    "Rajiv Gandhi International Stadium, Hyderabad": "Hyderabad",
    "Sawai Mansingh Stadium, Jaipur": "Jaipur",
    "Punjab Cricket Association IS Bindra Stadium, Mohali": "Mohali",
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow": "Lucknow"
}

ROSTERS = {
    "Chennai Super Kings": {
        "batsmen": ["MS Dhoni", "Ruturaj Gaikwad", "Devon Conway", "Shivam Dube", "Ajinkya Rahane"],
        "bowlers": ["Ravindra Jadeja", "Deepak Chahar", "Matheesha Pathirana", "Shardul Thakur", "Maheesh Theekshana"]
    },
    "Mumbai Indians": {
        "batsmen": ["Rohit Sharma", "Suryakumar Yadav", "Ishan Kishan", "Tilak Varma", "Hardik Pandya"],
        "bowlers": ["Jasprit Bumrah", "Piyush Chawla", "Gerald Coetzee", "Jason Behrendorff", "Hardik Pandya"]
    },
    "Royal Challengers Bengaluru": {
        "batsmen": ["Virat Kohli", "Faf du Plessis", "Glenn Maxwell", "Rajat Patidar", "Dinesh Karthik"],
        "bowlers": ["Mohammed Siraj", "Yuzvendra Chahal", "Wanindu Hasaranga", "Harshal Patel", "Glenn Maxwell"]
    },
    "Kolkata Knight Riders": {
        "batsmen": ["Shreyas Iyer", "Rinku Singh", "Andre Russell", "Venkatesh Iyer", "Nitish Rana"],
        "bowlers": ["Sunil Narine", "Varun Chakravarthy", "Mitchell Starc", "Harshit Rana", "Andre Russell"]
    },
    "Delhi Capitals": {
        "batsmen": ["Rishabh Pant", "David Warner", "Prithvi Shaw", "Mitchell Marsh", "Axar Patel"],
        "bowlers": ["Kuldeep Yadav", "Anrich Nortje", "Khaleel Ahmed", "Axar Patel", "Ishant Sharma"]
    },
    "Punjab Kings": {
        "batsmen": ["Shikhar Dhawan", "Jonny Bairstow", "Liam Livingstone", "Jitesh Sharma", "Sam Curran"],
        "bowlers": ["Kagiso Rabada", "Arshdeep Singh", "Rahul Chahar", "Sam Curran", "Harpreet Brar"]
    },
    "Rajasthan Royals": {
        "batsmen": ["Sanju Samson", "Jos Buttler", "Yashasvi Jaiswal", "Shimron Hetmyer", "Riyan Parag"],
        "bowlers": ["Trent Boult", "Yuzvendra Chahal", "Ravichandran Ashwin", "Sandeep Sharma", "Avesh Khan"]
    },
    "Sunrisers Hyderabad": {
        "batsmen": ["Heinrich Klaasen", "Travis Head", "Abhishek Sharma", "Aiden Markram", "Rahul Tripathi"],
        "bowlers": ["Pat Cummins", "Bhuvneshwar Kumar", "T Natarajan", "Mayank Markande", "Umran Malik"]
    },
    "Gujarat Titans": {
        "batsmen": ["Shubman Gill", "David Miller", "Sai Sudharsan", "Matthew Wade", "Rahul Tewatia"],
        "bowlers": ["Rashid Khan", "Mohammed Shami", "Mohit Sharma", "Noor Ahmad", "Joshua Little"]
    },
    "Lucknow Super Giants": {
        "batsmen": ["KL Rahul", "Quinton de Kock", "Nicholas Pooran", "Marcus Stoinis", "Ayush Badoni"],
        "bowlers": ["Ravi Bishnoi", "Mohsin Khan", "Naveen-ul-Haq", "Mayank Yadav", "Krunal Pandya"]
    }
}

SEASONS = [2018, 2019, 2020, 2021, 2022, 2023, 2024]

def generate_historical_ipl_data(num_matches: int = 150, seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    random.seed(seed)
    np.random.seed(seed)

    matches = []
    deliveries = []
    
    match_id_counter = 1
    base_date = datetime(2018, 4, 7)

    for i in range(num_matches):
        match_id = match_id_counter
        match_id_counter += 1

        season = random.choice(SEASONS)
        team1, team2 = random.sample(TEAMS, 2)
        venue, city = random.choice(list(VENUES.items()))
        toss_winner = random.choice([team1, team2])
        toss_decision = random.choice(["bat", "field"])
        match_date = base_date + timedelta(days=i*14 + random.randint(0, 5))

        if toss_decision == "bat":
            batting_first = toss_winner
            batting_second = team2 if toss_winner == team1 else team1
        else:
            batting_second = toss_winner
            batting_first = team2 if toss_winner == team1 else team1

        # Simulate Innings 1
        t1_roster = ROSTERS[batting_first]
        t2_roster = ROSTERS[batting_second]
        
        inn1_runs, inn1_wickets, inn1_balls, inn1_player_runs = simulate_innings(
            match_id=match_id,
            inning_num=1,
            batting_team=batting_first,
            bowling_team=batting_second,
            batsmen=t1_roster["batsmen"],
            bowlers=t2_roster["bowlers"],
            target_runs=None
        )
        deliveries.extend(inn1_balls)

        # Simulate Innings 2
        target = inn1_runs + 1
        inn2_runs, inn2_wickets, inn2_balls, inn2_player_runs = simulate_innings(
            match_id=match_id,
            inning_num=2,
            batting_team=batting_second,
            bowling_team=batting_first,
            batsmen=t2_roster["batsmen"],
            bowlers=t1_roster["bowlers"],
            target_runs=target
        )
        deliveries.extend(inn2_balls)

        # Determine Winner and Margin
        if inn2_runs >= target:
            winner = batting_second
            win_by_wickets = 10 - inn2_wickets
            win_by_runs = 0
            result = "wickets"
        elif inn1_runs > inn2_runs:
            winner = batting_first
            win_by_runs = inn1_runs - inn2_runs
            win_by_wickets = 0
            result = "runs"
        else:
            winner = random.choice([batting_first, batting_second])
            win_by_runs = 0
            win_by_wickets = 0
            result = "tie"

        # Marquee player of the match selection based on top innings runs
        all_players = {**inn1_player_runs, **inn2_player_runs}
        if all_players:
            player_of_match = max(all_players.items(), key=lambda x: x[1])[0]
        else:
            player_of_match = random.choice(t1_roster["batsmen"] + t2_roster["bowlers"])

        matches.append({
            "match_id": match_id,
            "season": str(season),
            "city": city,
            "date": match_date.strftime("%Y-%m-%d"),
            "team1": team1,
            "team2": team2,
            "toss_winner": toss_winner,
            "toss_decision": toss_decision,
            "result": result,
            "dl_applied": 0,
            "winner": winner,
            "win_by_runs": win_by_runs,
            "win_by_wickets": win_by_wickets,
            "player_of_match": player_of_match,
            "venue": venue,
            "umpire1": "C Shamshuddin",
            "umpire2": "KN Ananthapadmanabhan"
        })

    df_matches = pd.DataFrame(matches)
    df_deliveries = pd.DataFrame(deliveries)
    return df_matches, df_deliveries

def simulate_innings(match_id, inning_num, batting_team, bowling_team, batsmen, bowlers, target_runs=None):
    balls_list = []
    total_runs = 0
    total_wickets = 0
    player_runs = {}

    striker_idx = 0
    non_striker_idx = 1
    striker = batsmen[striker_idx]
    non_striker = batsmen[non_striker_idx]

    runs_distribution = [0, 0, 0, 1, 1, 1, 2, 4, 6]
    dismissal_types = ["caught", "bowled", "lbw", "run out", "stumped"]

    for over in range(1, 21):
        bowler = bowlers[(over - 1) % len(bowlers)]
        for ball in range(1, 7):
            if total_wickets >= 10:
                break
            if target_runs is not None and total_runs >= target_runs:
                break

            # Outcome probabilities
            is_wicket_ball = random.random() < 0.05
            is_extra = random.random() < 0.04
            
            extra_runs = 0
            wide_runs = 0
            noball_runs = 0
            legbye_runs = 0

            if is_extra:
                extra_type = random.choice(["wide", "legbye", "noball"])
                if extra_type == "wide":
                    wide_runs = 1
                    extra_runs = 1
                    batsman_runs = 0
                elif extra_type == "noball":
                    noball_runs = 1
                    extra_runs = 1
                    batsman_runs = random.choice([0, 1, 2, 4])
                else:
                    legbye_runs = 1
                    extra_runs = 1
                    batsman_runs = 0
            else:
                batsman_runs = random.choice(runs_distribution)

            player_dismissed = None
            dismissal_kind = None
            fielder = None

            if is_wicket_ball:
                total_wickets += 1
                player_dismissed = striker
                dismissal_kind = random.choice(dismissal_types)
                if dismissal_kind in ["caught", "run out", "stumped"]:
                    fielder = random.choice(bowlers)
                batsman_runs = 0
                ball_total = extra_runs
            else:
                ball_total = batsman_runs + extra_runs

            total_runs += ball_total
            player_runs[striker] = player_runs.get(striker, 0) + batsman_runs

            balls_list.append({
                "match_id": match_id,
                "inning": inning_num,
                "batting_team": batting_team,
                "bowling_team": bowling_team,
                "over": over,
                "ball": ball,
                "batsman": striker,
                "non_striker": non_striker,
                "bowler": bowler,
                "is_super_over": 0,
                "wide_runs": wide_runs,
                "bye_runs": 0,
                "legbye_runs": legbye_runs,
                "noball_runs": noball_runs,
                "penalty_runs": 0,
                "batsman_runs": batsman_runs,
                "extra_runs": extra_runs,
                "total_runs": ball_total,
                "player_dismissed": player_dismissed,
                "dismissal_kind": dismissal_kind,
                "fielder": fielder,
                "is_wicket": 1 if is_wicket_ball else 0
            })

            if is_wicket_ball:
                striker_idx = max(striker_idx, non_striker_idx) + 1
                if striker_idx < len(batsmen):
                    striker = batsmen[striker_idx]
                else:
                    striker = "Tailender " + str(striker_idx)
            else:
                if batsman_runs in [1, 3]:
                    striker, non_striker = non_striker, striker

        # Rotate strike at end of over
        striker, non_striker = non_striker, striker
        if total_wickets >= 10:
            break
        if target_runs is not None and total_runs >= target_runs:
            break

    return total_runs, total_wickets, balls_list, player_runs

def build_starter_data_files(data_dir: str):
    raw_dir = os.path.join(data_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    matches_file = os.path.join(raw_dir, "matches.csv")
    deliveries_file = os.path.join(raw_dir, "deliveries.csv")

    print("Generating comprehensive multi-season historical IPL starter dataset...")
    df_matches, df_deliveries = generate_historical_ipl_data(num_matches=180, seed=101)
    df_matches.to_csv(matches_file, index=False)
    df_deliveries.to_csv(deliveries_file, index=False)
    print(f"Starter data successfully created: {len(df_matches)} matches, {len(df_deliveries)} deliveries.")

if __name__ == "__main__":
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    data_path = os.path.join(base, "data")
    build_starter_data_files(data_path)
