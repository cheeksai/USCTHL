from flask import Flask, request, render_template_string, url_for
import pandas as pd
import numpy as np
import random
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

roster_csv = os.path.join(BASE_DIR, "rosters.csv")
df = pd.read_csv(roster_csv)
df.drop(['Pos'], axis=1, inplace=True)
inf = df.dropna()
info = inf.drop([12, 19, 22])

official_roster = os.path.join(BASE_DIR, "roster_official.tsv")
dataframe = pd.read_csv(official_roster, sep='\t', header=None)
dataframe.columns = ['Player', 'Position', 'Team', 'Number']

assist_matrix = os.path.join(BASE_DIR, "assists")
df1 = pd.read_csv(assist_matrix, sep='\t', index_col=0)
df1 = df1.drop(index=df1.index[-1], columns='assister')



print(info.columns.tolist())

clean_cols = []
for i in range(0, len(info.columns), 2):
    team_raw = info.columns[i]
    team_name = team_raw.split(" - ")[0]
    clean_cols.append(team_name)
    clean_cols.append(f"{team_name}_OVR")

info.columns = clean_cols
print(info)

place_abbreviations = {
    "Arizona": "ARI",
    "Atlanta": "ATL",
    "Baltimore": "BAL",
    "Boise": "BOI",
    "Charleston": "CHA",
    "Chicago": "CHI",
    "Cincinnati": "CIN",
    "Cleveland": "CLE",
    "Delaware": "DEL",
    "Denver": "DEN",
    "Detroit": "DET",
    "Florida": "FLA",
    "Honolulu": "HON",
    "Houston": "HOU",
    "Indianapolis": "IND",
    "Iowa": "IOA",
    "Jacksonville": "JAX",
    "Kansas City": "KC",
    "Las Vegas": "LV",
    "Lincoln": "LIN",
    "Long Island": "LI",
    "Madison": "MAD",
    "Memphis": "MEM",
    "Mississippi": "MIS",
    "Montana": "MON",
    "New York": "NY",
    "North Dakota": "ND",
    "Oklahoma": "OKL",
    "Philadelphia": "PHI",
    "Portland": "POR",
    "Puerto Rico": "PR",
    "Raleigh": "RAL",
    "Rapid City": "RC",
    "Richmond": "RCH",
    "San Antonio": "SAN",
    "Seattle": "SEA",
    "South Dakota": "SD",
    "St. Louis": "STL",
    "Tennessee": "TEN",
    "Washington": "WSH"
}
    
team_names = {
    "Arizona": "Heat",
    "Atlanta": "Cobalts",
    "Baltimore": "Oceanics",
    "Boise": "Grinders",
    "Charleston": "Tsunami",
    "Chicago": "Rockets",
    "Cincinnati": "Thunderbolts",
    "Cleveland": "Demons",
    "Delaware": "Pilots",
    "Denver": "Mountain Lions",
    "Detroit": "Motors",
    "Florida": "Sunshine",
    "Honolulu": "Hawks",
    "Houston": "Hammerheads",
    "Indianapolis": "Ghosts",
    "Iowa": "Rebels",
    "Jacksonville": "Blood Hounds",
    "Kansas City": "Metrostars",
    "Las Vegas": "Vipers",
    "Lincoln": "Lumberjacks",
    "Long Island": "Blizzards",
    "Madison": "Supernovas",
    "Memphis": "Cannons",
    "Mississippi": "Blue Jays",
    "Montana": "Miners",
    "New York": "Steam Rollers",
    "North Dakota": "Bison",
    "Oklahoma": "Twisters",
    "Philadelphia": "Destroyers",
    "Portland": "Sea Lions",
    "Puerto Rico": "Toros",
    "Raleigh": "Wildcats",
    "Rapid City": "Gladiators",
    "Richmond": "Robbers",
    "San Antonio": "Bandits",
    "Seattle": "Dragons",
    "South Dakota": "Spartans",
    "St. Louis": "Leopards",
    "Tennessee": "Wolverines",
    "Washington": "Admirals"
}

ALL_VALID_INPUTS = {}

for city, abbr in place_abbreviations.items():
    ALL_VALID_INPUTS[abbr.lower()] = city
    ALL_VALID_INPUTS[city.lower()] = city

for city, team in team_names.items():
    ALL_VALID_INPUTS[team.lower()] = city

def normalize_team_input(raw_input):
    key = raw_input.strip().lower()
    return ALL_VALID_INPUTS.get(key)


def expected_goals(x, idx,randomnum):
    goals = 0
    periods = [1,2,3]
    minutes = range(0,19)
    seconds = range(0,59)

    if 0 <= idx < 11:
        xgpg = (1/40)*x - (15/8)
    elif 12 <= idx < 18:
        xgpg = (1/100)*x - (3/4)
    else:
        xgpg = 0

    while randomnum < xgpg:
        randomnum = random.uniform(0.01, 1)/2
        goals += 1
        xgpg = xgpg / 4

    score_times = []
    
    for _ in range(goals):
        random_period = random.choice(periods)
        random_minute = random.randint(0,19)
        random_second = random.randint(0,59)
        score_times.append((random_period,random_minute,random_second))

    if goals > 0:
        sorted_score_times = [
            (p * 1200 + m * 60 + s, (p, m, s)) for p, m, s in score_times
        ]
        sorted_score_times.sort()
        sorted_score_times_actual = [
            (p, m, s, f'{19 - m}:{59 - s:02}') for _, (p, m, s) in sorted_score_times
        ]
    else:
        sorted_score_times_actual = []
        


               
    return goals, (score_times, sorted_score_times_actual)
    
def generate_assists(scorer_name, dataframe, df1):
    assisters = []
    assists = []
    final_assisters = []

    scorer_name = scorer_name

    idx = dataframe[dataframe['Player'] == scorer_name].index[0]
    player = dataframe['Player'].iloc[idx]
    position = dataframe['Position'].iloc[idx]
    team = dataframe['Team'].iloc[idx]
    number = dataframe['Number'].iloc[idx]

    if position.startswith('G'):
        return [('Unassisted', '')]

    percentages = df1.loc[position]
    for i, _ in percentages.items():
        assisters.append(i)

    idx1 = df1.index.get_indexer([position])[0]
    one = 0
    for i in df1.iloc[idx1]:
        one += i
        assists.append(f'{one:.3f}')

    full = [(i, a, b) for i, (a, b) in enumerate(zip(assisters, assists))]
    dictionary = { (a, b): (i, a, b) for i, a, b in full }

    assists_number = {0.06: 0, 0.22: 1, 1: 2}
    number_assists = random.uniform(0, 1)
    for key, value in assists_number.items():
        if number_assists <= key:
            assist_number = value
            break

    if assist_number > 0:
        full = [item for item in full if item[1] != position]

        for _ in range(assist_number):
            assister_num = random.uniform(0, 1.000)
            assister = None
            for i in range(0, len(full) - 1):
                ranger = round(float(full[i][2]), 3)
                if assister_num >= ranger:
                    assister = full[i + 1][1]
            if assister is None:
                assister = full[0][1]

            for idx, row in dataframe[dataframe['Team'] == team].iterrows():
                if row['Position'] == assister:
                    final_assisters.append((row['Player'], row['Number']))
                    break

            full = [item for item in full if item[1] != assister]
    else:
        final_assisters.append(('Unassisted', ''))


    return final_assisters


def simulate_game(team1, team2):
    score_tracker = {team1: 0, team2: 0}
    if team1 not in info.columns or team2 not in info.columns:
        return {"error": "Please enter valid team names, bub"}

    players1 = info[team1]
    players2 = info[team2]
    ovrs1 = team1 + '_OVR'
    ovrs2 = team2 + '_OVR'
    overalls1 = info[ovrs1]
    overalls2 = info[ovrs2]
    starter_goalie1 = players1.iloc[-2]
    backup_goalie1 = players1.iloc[-1]
    starter_goalie2 = players2.iloc[-2]
    backup_goalie2 = players2.iloc[-1]
   
    goalie_num = random.randint(1,100)

    if goalie_num > 35:
        goalie1 = starter_goalie1
    else:
        goalie1 = backup_goalie1

    goalie_num1 = random.randint(1,100)

    if goalie_num1 > 35:
        goalie2 = starter_goalie2
    else:
        goalie2 = backup_goalie2

    goalie1_ovr = info[team1 + '_OVR'].iloc[-2] if goalie1 == starter_goalie1 else info[team1 + '_OVR'].iloc[-1]
    goalie2_ovr = info[team2 + '_OVR'].iloc[-2] if goalie2 == starter_goalie2 else info[team2 + '_OVR'].iloc[-1]

    all_goals = []
    player_goal_counter = {}
    score_tracker = {team1: 0, team2: 0}
    period_events = {1: [], 2: [], 3: []}

    print(f'{team1} goalie: {goalie1}\n{team2} goalie: {goalie2}')


    def simulate_team(players, overalls, goalies, team_name, score_tracker):
        lines = []
        total_goals = 0
        scores1 = 0
        scores2 = 0
        player_goal_counter = {}
        all_sorted_score_times = []


        for idx, (x, player) in enumerate(zip(overalls, players)):
            goals, (_, sorted_score_times_actual) = expected_goals(
                x, idx, randomnum=(goalies / 84) * random.uniform(0.01, 1)
            )
            if goals > 0:
                total_goals += goals
                all_sorted_score_times.extend(sorted_score_times_actual)

                for p, m, s, formatted_time in sorted_score_times_actual:
                    
                    count = player_goal_counter.get(player, 0)
                    score_tracker[team_name] += 1
                    if score_tracker[team1] > score_tracker[team2]:
                        score_live = f"{score_tracker[team1]}–{score_tracker[team2]}"
                    else:
                        score_live = f"{score_tracker[team2]}-{score_tracker[team1]}"
                    lines.append((p, m, s, f"{team_name}: {player} ({count}) - {formatted_time}  {score_live}"))

        period_goals = {1: 0, 2: 0, 3: 0}
        for p, m, s, formatted_time in all_sorted_score_times:
            period_goals[p] += 1

        hat_trick_scorer = next((p for p, c in player_goal_counter.items() if c >= 3), None)

        def extract_time_seconds(line):
            try:
                time_str = line.split(" - ")[-1].split()[0]
                minutes, seconds = map(int, time_str.split(":"))
                return minutes * 60 + seconds
            except:
                return 9999

        lines.sort(key=lambda x: (x[0], x[1]*60 + x[2]))
    
        
        return lines, total_goals, period_goals, hat_trick_scorer

    for idx, (x, player) in enumerate(zip(overalls1, players1)):
        goals, (_, sorted_times) = expected_goals(x, idx, randomnum=(goalie2_ovr / 84) * random.uniform(0.01, 1))
        for p, m, s, formatted_time in sorted_times:
            all_goals.append((p, m, s, team1, player, formatted_time))
            player_goal_counter[player] = player_goal_counter.get(player, 0) + 1

    for idx, (x, player) in enumerate(zip(overalls2, players2)):
        goals, (_, sorted_times) = expected_goals(x, idx, randomnum=(goalie1_ovr / 84) * random.uniform(0.01, 1))
        for p, m, s, formatted_time in sorted_times:
            all_goals.append((p, m, s, team2, player, formatted_time))
            player_goal_counter[player] = player_goal_counter.get(player, 0) + 1

    all_goals.sort(key=lambda x: (x[0], x[1]*60 + x[2]))

    player_goal_sequence = {}
    player_assist_counter = {}
    
    for p, m, s, team, player, formatted_time in all_goals:
        score_tracker[team] += 1

        player_goal_sequence[player] = player_goal_sequence.get(player, 0) + 1
        goal_number = player_goal_sequence[player]

        if score_tracker[team1] > score_tracker[team2]:
            score_live = f"{score_tracker[team1]}–{score_tracker[team2]}"
        else:
            score_live = f"{score_tracker[team2]}–{score_tracker[team1]}"

        assists = generate_assists(player, dataframe, df1)
        
        for name, num in assists:
            if name != 'Unassisted':
                player_assist_counter[name] = player_assist_counter.get(name, 0) + 1

        valid_assists = [(name, num) for name, num in assists if name != 'Unassisted']

        if valid_assists:
            assist_text = ", ".join([
                f"#{num} {name} ({player_assist_counter.get(name, 0)})"
                for name, num in valid_assists
            ])
        else:
            assist_text = "Unassisted"

        idx = dataframe[dataframe['Player'] == player].index[0]
        number = dataframe['Number'].iloc[idx]

        winning = 'Tie'
        if score_tracker[team1] > score_tracker[team2]:
            winning = team1
        elif score_tracker[team2] > score_tracker[team1]:
            winning = team2
        else:
            winning = 'Tie'
            
        player = player
        
        line = f"{place_abbreviations[team]} Goal: #{number} {player} ({goal_number})\nAssists: {assist_text}\nTime: {formatted_time}\nScore: {score_live} {winning}"
        period_events[p].append(line)
        
    periods = []
    thigns = ['1st','2nd','3rd']
    
    for i in range(3):
        periods.append({
            "label": f"{thigns[i]} Period",
            "events": period_events[i+1]
        })
    
    hat_trick_scorer = next((p for p, c in player_goal_counter.items() if c >= 3), None)
    
    team1_period1 = sum(1 for line in period_events[1] if line.startswith(team1))
    team1_period2 = sum(1 for line in period_events[2] if line.startswith(team1))
    team1_period3 = sum(1 for line in period_events[3] if line.startswith(team1))

    team2_period1 = sum(1 for line in period_events[1] if line.startswith(team2))
    team2_period2 = sum(1 for line in period_events[2] if line.startswith(team2))
    team2_period3 = sum(1 for line in period_events[3] if line.startswith(team2))

    overtime = "No"
    ot_winner = None
    ot_scorers = []
    #shootout = "No"

    score1 = score_tracker[team1]
    score2 = score_tracker[team2]

    if score1 > score2:
        winner = team1
    elif score2 > score1:
        winner = team2
    else:
        #overtime_or_shootout = random.uniform(0,100)
        #if overtime_or_shootout > 7.9:
        overtime = "Yes"
        difference = 0
        while difference == 0:
            ot_scorers_team1 = []
            ot_scorers_team2 = []

            for idx, (x, player) in enumerate(zip(overalls1, players1)):
                goals, (raw_times, sorted_score_times_actual) = expected_goals(x, idx, randomnum=(goalie2_ovr / 84) * random.uniform(0.01, 1))
                if goals > 0:
                    ot_scorers_team1.append(player)

            for idx, (x, player) in enumerate(zip(overalls2, players2)):
                goals, (raw_times, sorted_score_times_actual) = expected_goals(x, idx, randomnum=(goalie1_ovr / 84) * random.uniform(0.01, 1))
                if goals > 0:
                    ot_scorers_team2.append(player)

            difference = len(ot_scorers_team1) - len(ot_scorers_team2)

        if difference > 0:
            ot_winner = team1
            winner = f"{team1} "
            score1 += 1
            ot_scorers = ot_scorers_team1
        else:
            ot_winner = team2
            winner = f"{team2} "
            score2 += 1
            ot_scorers = ot_scorers_team2
        #else:
            #ot_scorers = ['N/A']
            #shootout = "Yes"
            #winner = random.choice([team1, team2])
            #lose = team1 if winner == team2 else team2
            #avg = .342
            #shootout_chance = avg * player_ovr/85
            #for idx, (x, player) in enumerate(zip(overalls, players)):
            #goals, (_, sorted_score_times_actual) = expected_goals(
                #x, idx, randomnum=(goalies / 84) * random.uniform(0.00000001, 1)
            #)
            #print(winner+'working on it still ')
                

    
    if ot_scorers:
        scorer_name = random.choice(ot_scorers)
        player_goal_counter[scorer_name] = player_goal_counter.get(scorer_name, 0) + 1
        player_goal_sequence[scorer_name] = player_goal_sequence.get(scorer_name, 0) + 1
        ot_goal_number = player_goal_sequence[scorer_name]

        minute = 5 - random.randint(1, 5)
        second = 59 - random.randint(0, 59)
        time = f'{minute}:{second:02}'
        
        team = ot_winner
        team_abbr = place_abbreviations.get(team, 'N/A')

        assists = generate_assists(scorer_name, dataframe, df1)
        
        for name, num in assists:
            if name != 'Unassisted':
                player_assist_counter[name] = player_assist_counter.get(name, 0) + 1
        
        valid_assists = [(name, num) for name, num in assists if name != 'Unassisted']

        if valid_assists:
            assist_text = ", ".join([
                f"#{num} {name} ({player_assist_counter.get(name, 0)})"
                for name, num in valid_assists
            ])
        else:
            assist_text = "Unassisted"

        idx = dataframe[dataframe['Player'] == scorer_name].index[0]
        number = dataframe['Number'].iloc[idx]

        if team == team1:
            score_tracker[team1] += 1
            score_live = f'{score_tracker[team1]} - {score_tracker[team2]}' 
        else:
            score_tracker[team2] += 1
            score_live = f'{score_tracker[team2]} - {score_tracker[team1]}'

        if score_tracker[team1] > score_tracker[team2]:
            winning = team1
        elif score_tracker[team2] > score_tracker[team1]:
            winning = team2

        ot_scorers = [
            f'{team_abbr} Goal: #{number} {scorer_name} ({ot_goal_number})\nAssists: {assist_text}\nTime: {time}\nScore: {score_live} {winning}'
        ]

        all_goals.append((4, minute, second, team, scorer_name, time))

        raw = ot_scorers[0].split(" - ")[0]
        ot_scorers_name = raw.split("#")[1].split("(")[0].strip()
        ot_scorers_name = ot_scorers_name[2:]
    else:
        ot_scorers = ['N/A']
        ot_scorers_name = 'N/A'

    ot1_score = score1
    ot2_score = score2
    
    scorers_team1 = [f"{player} - {formatted_time}" for p, m, s, team, player, formatted_time in all_goals if team == team1]
    scorers_team2 = [f"{player} - {formatted_time}" for p, m, s, team, player, formatted_time in all_goals if team == team2]

    team1_data = {
        "name": team1,
        "goalie": goalie1,
        "scorers": scorers_team1,
        "total_goals": score1
    }
    team2_data = {
        "name": team2,
        "goalie": goalie2,
        "scorers": scorers_team2,
        "total_goals": score2
    }
        


    periods = []
    thigns = ['1st','2nd','3rd']
    
    for i in range(3):
        periods.append({
            "label": f"{thigns[i]} Period",
            "events": period_events[i+1]
        })

    
    return {
        "periods": periods,
        "hat_trick_scorer": hat_trick_scorer,
        "team1": team1_data,
        "team2": team2_data,
        "period_events": period_events,
        "winner": winner,
        "ot_winner": ot_winner,
        "overtime": overtime,
        "ot_scorers": ot_scorers,
        "ot_scorers_name": ot_scorers_name,
        "ot1_score": ot1_score,
        "ot2_score": ot2_score,
        "score1": score1,
        "score2": score2,
        "team1_periods": [team1_period1, team1_period2, team1_period3],
        "team2_periods": [team2_period1, team2_period2, team2_period3],
        "hat_trick_scorer": hat_trick_scorer,

        "error": None
    }


headline_choices = {
"close_team1_win": [
    "{team1} edges out {team2} in a {score1}-{score2} nailbiter",
    "Late goal seals it as {team1} narrowly tops {team2} {score1}-{score2}",
    "One-goal game ends with {team1} surviving {team2}'s final push",
    "{team1} squeaks past {team2} in razor-thin {score1}-{score2} battle",
    "Photo finish for {team1} as they defeat {team2} in a tight contest",
    "{team2} kept it neck and neck, but {team1} held on {score1}-{score2}",
    "Down to the wire: {team1} escapes with tense win over {team2}"
],
"close_team1_loss": [
    "{team1} falls just short in {score2}-{score1} thriller vs {team2}",
    "Final push from {team1} denied as {team2} escapes with tight win",
    "Heartbreaking end for {team1} in one-goal loss to {team2}",
    "{team2} fends off last-minute surge from {team1} to seal win",
    "{team1} kept it close, but couldn't finish against {team2}",
    "Close contest slips away from {team1} as {team2} clinches it",
    "One-goal difference sinks {team1} in dramatic finish vs {team2}"
],
"close_team2_win": [
    "{team2} edges out {team1} in a {score2}-{score1} nailbiter",
    "Late goal seals it as {team2} narrowly tops {team1} {score2}-{score1}",
    "One-goal game ends with {team2} surviving {team1}'s final push",
    "{team2} squeaks past {team1} in razor-thin {score2}-{score1} battle",
    "Photo finish for {team2} as they defeat {team1} in a tight contest",
    "{team1} kept it neck and neck, but {team2} held on {score2}-{score1}",
    "Down to the wire: {team2} escapes with tense win over {team1}"
],
"close_team2_loss": [
    "{team2} falls just short in {score1}-{score2} thriller vs {team1}",
    "Final push from {team2} denied as {team1} escapes with tight win",
    "Heartbreaking end for {team2} in one-goal loss to {team1}",
    "{team1} fends off last-minute surge from {team2} to seal win",
    "{team2} kept it close, but couldn't finish against {team1}",
    "Close contest slips away from {team2} as {team1} clinches it",
    "One-goal difference sinks {team2} in dramatic finish vs {team1}"
],

"blowout_team1_win": [
    "{team1} steamrolls {team2} in a {score1}-{score2} drubbing",
    "No contest as {team1} demolishes {team2} with dominant {score1}-{score2} display",
    "{team2} suffers crushing defeat, falling {score2}-{score1} to {team1}",
    "Thumping from start to finish: {team1} routs {team2}",
    "Lopsided affair sees {team1} light the lamp in blowout win over {team2}",
    "Domination by {team1} leads to emphatic {score1}-{score2} result",
    "Wall-to-wall scoring as {team1} overwhelms {team2} in thumping victory"
],
"blowout_team1_loss": [
    "{team1} outmatched in {score2}-{score1} blowout by {team2}",
    "Defensive collapse dooms {team1} in runaway loss",
    "Rough night for {team1} as {team2} rolls to easy win",
    "Nothing clicking for {team1} in lopsided defeat",
    "Offense sputters as {team1} gets blown out",
    "{team1} routed with little resistance against {team2}",
    "Unanswered goals pile up in crushing defeat for {team1}"
],
"blowout_team2_win": [
    "{team2} steamrolls {team1} in a {score2}-{score1} drubbing",
    "No contest as {team2} demolishes {team1} with dominant {score2}-{score1} display",
    "{team1} suffers crushing defeat, falling {score1}-{score2} to {team2}",
    "Thumping from start to finish: {team2} routs {team1}",
    "Lopsided affair sees {team2} light the lamp in blowout win over {team1}",
    "Domination by {team2} leads to emphatic {score2}-{score1} result",
    "Wall-to-wall scoring as {team2} overwhelms {team1} in thumping victory"
],
"blowout_team2_loss": [
    "{team2} outmatched in {score1}-{score2} blowout by {team1}",
    "Defensive collapse dooms {team2} in runaway loss",
    "Rough night for {team2} as {team1} rolls to easy win",
    "Nothing clicking for {team2} in lopsided defeat",
    "Offense sputters as {team2} gets blown out",
    "{team2} routed with little resistance against {team1}",
    "Unanswered goals pile up in crushing defeat for {team2}"
],
"overtime_team1_win": [
    "{team1} triumphs in sudden death thanks to {ot_scorers_name}'s overtime winner",
    "OT drama ends with {team1} grinding out win over {team2} {ot1_score}-{ot2_score}",
    "Bonus hockey sees {team1} prevail on {ot_scorers_name}'s walk-off goal",
    "Extended play pays off as {team1} clinches victory in {ot1_score}-{ot2_score} thriller",
    "{team2} can't hold on in extra time as {team1} steals the game",
    "Overtime thriller ends with {ot_scorers_name} lighting the lamp for {team1}",
    "Sudden death sealed by {ot_scorers_name}'s clutch tally as {team1} defeats {team2}"
],
"overtime_team1_loss": [
    "{team1} falls in overtime as {team2} secures narrow victory",
    "Sudden death disappointment for {team1} in extended {ot2_score}-{ot1_score} battle",
    "{team2} wins OT thriller as {team1} can't convert chances",
    "Extra time ends with {team1} on wrong side of momentum",
    "OT stings for {team1} as {team2} capitalizes late",
    "Bonus hockey ends in heartbreak for {team1}",
    "Late winner from {ot_scorers_name} sinks {team1} in sudden death"
],
"overtime_team2_win": [
    "{team2} triumphs in sudden death thanks to {ot_scorers_name}'s overtime winner",
    "OT drama ends with {team2} grinding out win over {team1} {ot2_score}-{ot1_score}",
    "Bonus hockey sees {team2} prevail on {ot_scorers_name}'s walk-off goal",
    "Extended play pays off as {team2} clinches victory in {ot2_score}-{ot1_score} thriller",
    "{team1} can't hold on in extra time as {team2} steals the game",
    "Overtime thriller ends with {ot_scorers_name} lighting the lamp for {team2}",
    "Sudden death sealed by {ot_scorers_name}'s clutch tally as {team2} defeats {team1}"
],
"overtime_team2_loss": [
    "{team2} falls in overtime as {team1} secures narrow victory",
    "Sudden death disappointment for {team2} in extended {ot1_score}-{ot2_score} battle",
    "{team1} wins OT thriller as {team2} can't convert chances",
    "Extra time ends with {team2} on wrong side of momentum",
    "OT stings for {team2} as {team1} capitalizes late",
    "Bonus hockey ends in heartbreak for {team2}",
    "Late winner from {ot_scorers_name} sinks {team2} in sudden death"
],
#"shootout_team1_win": [
 #   "{team1} emerges in shootout duel, defeating {team2} {score1}-{score2}",
  #  "Shootout win secured by {shootout_scorer}, lifting {team1} past {team2}",
   # "Goalie showdown ends with {team1} prevailing in penalty shot battle",
    #"Sharp-shooting {team1} claims extra point in shootout thriller",
    #"{team2} falls short as {team1} converts clutch chances",
    #"Shootout magic from {shootout_scorer} seals {team1} victory",
    #"Skills competition favors {team1} in dramatic finish vs {team2}"
#],
#"shootout_team1_loss": [
 #   "{team1} edged in shootout after tense battle with {team2}",
  #  "Shootout stumble costs {team1} a valuable point",
   # "{team2} wins duel as {team1} falters in final round",
    #"Clutch stops from {goalie2} deny {team1} in shootout finish",
    #"{team1} comes up empty in penalty shot showdown",
    #"Shootout heroics go to {team2}, defeating {team1}",
    #"Post-regulation loss for {team1} as {team2} clinches it"
#],
#"shootout_team2_win": [
 #   "{team2} emerges in shootout duel, defeating {team1} {score2}-{score1}",
  #  "Shootout win secured by {shootout_scorer}, lifting {team2} past {team1}",
   # "Goalie showdown ends with {team2} prevailing in penalty shot battle",
    #"Sharp-shooting {team2} claims extra point in shootout thriller",
    #"{team1} falls short as {team2} converts clutch chances",
    #"Shootout magic from {shootout_scorer} seals {team2} victory",
    #"Skills competition favors {team2} in dramatic finish vs {team1}"
#],
#"shootout_team2_loss": [
 #   "{team2} edged in shootout after tense battle with {team1}",
  #  "Shootout stumble costs {team2} a valuable point",
   # "{team1} wins duel as {team2} falters in final round",
    #"Clutch stops from {goalie1} deny {team2} in shootout finish",
    #"{team2} comes up empty in penalty shot showdown",
    #"Shootout heroics go to {team1}, defeating {team2}",
    #"Post-regulation loss for {team2} as {team1} clinches it"
#],
"shutout_team1_win": [
    "{team1}'s {goalie1} posts clean sheet with stops",
    "{team2} blanked in {score1}-{score2} shutout loss to {team1}",
    "Lights-out goaltending: {team1}'s {goalie1} shuts the door on {team2}",
    "{team1} records shutout as {team2} fails to generate offense",
    "{team2} silenced for full 60 minutes as {team1} cruises",
    "Goose egg handed to {team2} in dominant win by {team1}",
    "{team1} wins behind flawless netminding from {goalie1}"
],
"shutout_team1_loss": [
    "{team1} blanked in {score2}-{score1} shutout loss to {team2}",
    "Offensive drought costs {team1} in scoreless defeat",
    "Nothing doing for {team1} against locked-in {goalie2}",
    "Goose egg handed to {team1} as {team2} rolls",
    "{team1} held off the board by stellar {goalie2} play",
    "Clean sheet against {team1} gives {team2} all the momentum",
    "{team1} can't solve {team2}'s defense, loses in shutout"
],
"shutout_team2_win": [
    "{team2}'s {goalie2} posts clean sheet with stops",
    "{team1} blanked in {score2}-{score1} shutout loss to {team2}",
    "Lights-out goaltending: {team2}'s {goalie2} shuts the door on {team1}",
    "{team2} records shutout as {team1} fails to generate offense",
    "{team1} silenced for full 60 minutes as {team2} cruises",
    "Goose egg handed to {team1} in dominant win by {team2}",
    "{team2} wins behind flawless netminding from {goalie2}"
],
"shutout_team2_loss": [
    "{team2} blanked in {score1}-{score2} shutout loss to {team1}",
    "Offensive drought costs {team2} in scoreless defeat",
    "Nothing doing for {team2} against locked-in {goalie1}",
    "Goose egg handed to {team2} as {team1} rolls",
    "{team2} held off the board by stellar {goalie1} play",
    "Clean sheet against {team2} gives {team1} all the momentum",
    "{team2} can't solve {team1}'s defense, loses in shutout"
],
"back_and_forth_team1_win": [
    "Seesaw battle ends with {team1} edging {team2} {score1}-{score2}",
    "Momentum swings wildly before {team1} breaks through for win",
    "Back-and-forth affair sees {team1} finally pull away",
    "{team2} rallies then falters as {team1} turns tide in tense finish",
    "Lead changes all night as {team1} escapes with victory",
    "Wild exchanges give way to {team1}'s late surge",
    "Trading goals ends with {team1} snagging the last word"
],
"back_and_forth_team1_loss": [
    "{team1} loses thriller after trading blows with {team2}",
    "Momentum slips from {team1} in wild lead-changing defeat",
    "Seesaw matchup tilts toward {team2} late",
    "{team1} can't hold final lead in back-and-forth battle",
    "Trading goals ends with {team2} having the last word",
    "Lead changes aplenty, but {team1} falls at the finish",
    "Chaotic contest ends in disappointment for {team1}"
],
"back_and_forth_team2_win": [
    "Seesaw battle ends with {team2} edging {team1} {score2}-{score1}",
    "Momentum swings wildly before {team2} breaks through for win",
    "Back-and-forth affair sees {team2} finally pull away",
    "{team1} rallies then falters as {team2} turns tide in tense finish",
    "Lead changes all night as {team2} escapes with victory",
    "Wild exchanges give way to {team2}'s late surge",
    "Trading goals ends with {team2} snagging the last word"
],
"back_and_forth_team2_loss": [
    "{team2} loses thriller after trading blows with {team1}",
    "Momentum slips from {team2} in wild lead-changing defeat",
    "Seesaw matchup tilts toward {team1} late",
    "{team2} can't hold final lead in back-and-forth battle",
    "Trading goals ends with {team1} having the last word",
    "Lead changes aplenty, but {team2} falls at the finish",
    "Chaotic contest ends in disappointment for {team2}"
],
"low_score_team1_win": [
    "Defensive grind ends with {team1} edging {team2} {score1}-{score2}",
    "{team1} survives low-event affair thanks to stingy defense",
    "Goalie duel favors {team1} in quiet night",
    "Tight-checking contest sees {team1} hold on late",
    "{team2} can't crack {team1}'s system in low-output match",
    "Chess match ends with {team1} getting the only breakthrough",
    "Low-scoring slugfest tips toward {team1}"
],
"low_score_team1_loss": [
    "{team1} can't solve goalie in {score2}-{score1} defensive defeat",
    "Offense dries up as {team1} drops tight-checking tilt",
    "Low-event battle favors {team2}, frustrating {team1}",
    "Chances minimal as {team1} falls in grind-it-out affair",
    "Defensive showdown ends in {team1}'s narrow loss",
    "Goaltending trumps firepower as {team1} falters",
    "Quiet night ends in bitter defeat for {team1}"
],
"low_score_team2_win": [
    "Defensive grind ends with {team2} edging {team1} {score2}-{score1}",
    "{team2} survives low-event affair thanks to stingy defense",
    "Goalie duel favors {team2} in quiet night",
    "Tight-checking contest sees {team2} hold on late",
    "{team1} can't crack {team2}'s system in low-output match",
    "Chess match ends with {team2} getting the only breakthrough",
    "Low-scoring slugfest tips toward {team2}"
],
"low_score_team2_loss": [
    "{team2} can't solve goalie in {score1}-{score2} defensive defeat",
    "Offense dries up as {team2} drops tight-checking tilt",
    "Low-event battle favors {team1}, frustrating {team2}",
    "Chances minimal as {team2} falls in grind-it-out affair",
    "Defensive showdown ends in {team2}'s narrow loss",
    "Goaltending trumps firepower as {team2} falters",
    "Quiet night ends in bitter defeat for {team2}"
],

"high_score_team1_win": [
    "{team1} offense explodes in {score1}-{score2} goal fest over {team2}",
    "Goals galore as {team1} overwhelms {team2}",
    "{team1} turns scoring frenzy into convincing win",
    "{team2} can't keep pace as {team1} lights the lamp repeatedly",
    "{team1} runs wild in offensive showcase vs {team2}",
    "{team1} overcomes {team2} with timely goals and relentless pressure",
    "Fireworks fly in {team1}'s high-octane victory"
],
"high_score_team1_loss": [
    "{team1} can't match {team2}'s offensive pace, falls {score2}-{score1}",
    "Goal fest turns against {team1} late",
    "{team2} erupts, outdueling {team1} in goal-scoring game",
    "Scoring surge from {team2} proves too much for {team1}",
    "Defensive gaps doom {team1} in wild affair",
    "{team1} contributes to fireworks but ends up on wrong side",
    "Despite offensive push, {team1} loses high-scoring thriller"
],
"high_score_team2_win": [
    "{team2} offense explodes in {score2}-{score1} goal fest over {team1}",
    "Goals galore as {team2} overwhelms {team1}",
    "{team2} turns scoring frenzy into convincing win",
    "{team1} can't keep pace as {team2} lights the lamp repeatedly",
    "{team2} runs wild in offensive showcase vs {team1}",
    "{team2} overcomes {team1} with timely goals and relentless pressure",
    "Fireworks fly in {team2}'s high-octane victory"
],
"high_score_team2_loss": [
    "{team2} can't match {team1}'s offensive pace, falls {score1}-{score2}",
    "Goal fest turns against {team2} late",
    "{team1} erupts, outdueling {team2} in goal-scoring game",
    "Scoring surge from {team1} proves too much for {team2}",
    "Defensive gaps doom {team2} in wild affair",
    "{team2} contributes to fireworks but ends up on wrong side",
    "Despite offensive push, {team2} loses high-scoring thriller"
],
"team1_win": [
    "{team1} opens strong and never looks back in {score1}-{score2} win over {team2}",
    "Efficient, disciplined effort lifts {team1} past {team2} in regulation",
    "Momentum tilts early as {team1} controls flow in clean victory",
    "{team1} methodically dismantles {team2} with consistent pressure",
    "Scoring touch and steady defense combine in {team1}'s composed win",
    "{team1} stays ahead wire-to-wire to close out {team2}",
    "Quiet dominance as {team1} wraps up routine regulation win"
],
"team1_loss": [
    "Sluggish start buries {team1} in {score2}-{score1} defeat to {team2}",
    "Late push not enough as {team1} drops regulation contest",
    "No spark for {team1} in frustrating loss to {team2}",
    "{team2} controls tempo, leaving {team1} chasing from puck drop",
    "{team1} struggles to generate chances, falls without a fight",
    "Defensive miscues haunt {team1} throughout composed loss",
    "Regulation effort fizzles as {team2} outmatches {team1}"
],
"team2_win": [
    "{team2} executes game plan flawlessly in {score2}-{score1} win over {team1}",
    "Clinical passing and net-front pressure drive {team2}'s strong result",
    "Measured approach pays off as {team2} picks apart {team1}",
    "Clean transition play helps {team2} earn full points in regulation",
    "From forecheck to finish, {team2} sets the tone in win vs {team1}",
    "Efficiency and poise guide {team2} past {team1} in no-nonsense victory",
    "{team2} leaves little doubt in one-sided outcome over {team1}"
],
"team2_loss": [
    "{team2} shows flashes but can’t hold on vs steady {team1}",
    "Momentum stalls as {team2} fades late against {team1}",
    "Scoring chances wasted as {team2} drops regulation contest",
    "Offensive rhythm elusive for {team2} in controlled loss to {team1}",
    "{team1} applies pressure and {team2} never settles in",
    "Disjointed play leads to empty result for {team2}",
    "{team2} undone by missed assignments and slow recovery"
],
"comeback_team1_win": [
    "{team1} rallies from behind to stun {team2} {score1}-{score2}",
    "Comeback complete: {team1} flips deficit into win",
    "Trailing early, {team1} surges late to defeat {team2}",
    "{team2} can't hold lead as {team1} storms back",
    "Momentum shift favors {team1} in dramatic turnaround",
    "Down but not out: {team1} claws back for victory",
    "{team1} erases deficit and finishes strong"
],
"comeback_team1_loss": [
    "{team1} rallies but falls short against {team2}",
    "Late push from {team1} can't overcome early hole",
    "Comeback fizzles as {team2} holds on",
    "{team1} erases deficit but can't finish the job",
    "Momentum shifts, but {team1} can't seal the deal",
    "Valiant effort from {team1} ends in defeat",
    "Lead slips away again as {team1} drops tight one"
],
"comeback_team2_win": [
    "{team2} rallies from behind to stun {team1} {score2}-{score1}",
    "Comeback complete: {team2} flips deficit into win",
    "Trailing early, {team2} surges late to defeat {team1}",
    "{team1} can't hold lead as {team2} storms back",
    "Momentum shift favors {team2} in dramatic turnaround",
    "Down but not out: {team2} claws back for victory",
    "{team2} erases deficit and finishes strong"
],
"comeback_team2_loss": [
    "{team2} rallies but falls short against {team1}",
    "Late push from {team2} can't overcome early hole",
    "Comeback fizzles as {team1} holds on",
    "{team2} erases deficit but can't finish the job",
    "Momentum shifts, but {team2} can't seal the deal",
    "Valiant effort from {team2} ends in defeat",
    "Lead slips away again as {team2} drops tight one"
],
"collapse_team1_win": [
    "{team1} storms back from multi-goal hole to stun {team2}",
    "Collapse by {team2} opens door for {team1}'s comeback win",
    "Momentum flips as {team1} erases early deficit",
    "From trailing to triumph: {team1} completes dramatic turnaround",
    "{team2} can't hold lead as {team1} roars back",
    "Early struggles forgotten as {team1} flips the script",
    "Comeback complete: {team1} capitalizes on {team2}'s collapse"
],
"collapse_team1_loss": [
    "{team1} squanders multi-goal lead in stunning loss to {team2}",
    "Collapse complete: {team2} flips script on {team1}",
    "Early dominance undone as {team1} falls apart late",
    "Momentum vanishes as {team1} lets game slip away",
    "Lead evaporates in brutal defeat for {team1}",
    "{team2} capitalizes on {team1}'s breakdown",
    "From control to chaos: {team1} can't close it out"
],
"collapse_team2_win": [
    "{team2} storms back from multi-goal hole to stun {team1}",
    "Collapse by {team1} opens door for {team2}'s comeback win",
    "Momentum flips as {team2} erases early deficit",
    "From trailing to triumph: {team2} completes dramatic turnaround",
    "{team1} can't hold lead as {team2} roars back",
    "Early struggles forgotten as {team2} flips the script",
    "Comeback complete: {team2} capitalizes on {team1}'s collapse"
],
"collapse_team2_loss": [
    "{team2} squanders multi-goal lead in stunning loss to {team1}",
    "Collapse complete: {team1} flips script on {team2}",
    "Early dominance undone as {team2} falls apart late",
    "Momentum vanishes as {team2} lets game slip away",
    "Lead evaporates in brutal defeat for {team2}",
    "{team1} capitalizes on {team2}'s breakdown",
    "From control to chaos: {team2} can't close it out"
],
"strong_start_team1_win": [
    "{team1} sets tone early, cruises past {team2}",
    "Fast start fuels {team1}'s wire-to-wire win",
    "Opening blitz from {team1} buries {team2}",
    "First-period fireworks spark {team1}'s victory",
    "{team1} jumps ahead early and never looks back",
    "Quick strike offense leads {team1} to win",
    "Early goals give {team1} control from the outset"
],
"strong_start_team1_loss": [
    "{team1} fades after hot start, falls to {team2}",
    "Early lead squandered as {team2} rallies past {team1}",
    "Momentum stalls after first as {team1} drops contest",
    "{team1} can't hold early edge in tough loss",
    "Fast start undone by slow finish for {team1}",
    "Lead evaporates as {team2} flips script",
    "Promising start ends in disappointment for {team1}"
],
"strong_start_team2_win": [
    "{team2} sets tone early, cruises past {team1}",
    "Fast start fuels {team2}'s wire-to-wire win",
    "Opening blitz from {team2} buries {team1}",
    "First-period fireworks spark {team2}'s victory",
    "{team2} jumps ahead early and never looks back",
    "Quick strike offense leads {team2} to win",
    "Early goals give {team2} control from the outset"
],
"strong_start_team2_loss": [
    "{team2} fades after hot start, falls to {team1}",
    "Early lead squandered as {team1} rallies past {team2}",
    "Momentum stalls after first as {team2} drops contest",
    "{team2} can't hold early edge in tough loss",
    "Fast start undone by slow finish for {team2}",
    "Lead evaporates as {team1} flips script",
    "Promising start ends in disappointment for {team2}"
],
"hat_trick_team1_win": [
    "{team1}'s {hat_trick_scorer} nets three in statement win",
    "Hat trick hero {hat_trick_scorer} powers {team1} past {team2}",
    "Three-goal night from {hat_trick_scorer} lifts {team1}",
    "{team1} rides {hat_trick_scorer}'s offensive outburst to victory",
    "Scoring clinic from {hat_trick_scorer} headlines {team1}'s win",
    "Hat trick and hustle: {team1} overwhelms {team2}",
    "{hat_trick_scorer} steals the show in {team1}'s triumph"
],
"hat_trick_team1_loss": [
    "{hat_trick_scorer}'s hat trick not enough as {team1} falls",
    "Three goals wasted in {team1}'s tough loss to {team2}",
    "{team1}'s {hat_trick_scorer} shines, but result slips away",
    "Offensive fireworks from {hat_trick_scorer} can't save {team1}",
    "Hat trick in vain as {team2} outlasts {team1}",
    "{team1} drops high-scoring affair despite {hat_trick_scorer}'s heroics",
    "Individual brilliance undone by team breakdown"
],
"hat_trick_team2_win": [
    "{team2}'s {hat_trick_scorer} nets three in statement win",
    "Hat trick hero {hat_trick_scorer} powers {team2} past {team1}",
    "Three-goal night from {hat_trick_scorer} lifts {team2}",
    "{team2} rides {hat_trick_scorer}'s offensive outburst to victory",
    "Scoring clinic from {hat_trick_scorer} headlines {team2}'s win",
    "Hat trick and hustle: {team2} overwhelms {team1}",
    "{hat_trick_scorer} steals the show in {team2}'s triumph"
],
"hat_trick_team2_loss": [
    "{hat_trick_scorer}'s hat trick not enough as {team2} falls",
    "Three goals wasted in {team2}'s tough loss to {team1}",
    "{team2}'s {hat_trick_scorer} shines, but result slips away",
    "Offensive fireworks from {hat_trick_scorer} can't save {team2}",
    "Hat trick in vain as {team1} outlasts {team2}",
    "{team2} drops high-scoring affair despite {hat_trick_scorer}'s heroics",
    "Individual brilliance undone by team breakdown"
],
"late_surge_team1_win": [
    "{team1} erupts late to take down {team2}",
    "Third-period push lifts {team1} to victory",
    "Late goals flip script as {team1} defeats {team2}",
    "Final frame belongs to {team1} in comeback win",
    "{team1} surges past {team2} with clutch finish",
    "Strong close seals win for {team1}",
    "Late rally from {team1} stuns {team2}"
],
"late_surge_team1_loss": [
    "Late push from {team1} falls short against {team2}",
    "{team1} scores late but can't complete comeback",
    "Final frame flurry not enough for {team1}",
    "{team2} withstands late surge from {team1}",
    "Momentum shift denied as {team1} drops contest",
    "Third-period effort wasted in {team1}'s loss",
    "Clutch chances missed as {team1} falls"
],
"late_surge_team2_win": [
    "{team2} erupts late to take down {team1}",
    "Third-period push lifts {team2} to victory",
    "Late goals flip script as {team2} defeats {team1}",
    "Final frame belongs to {team2} in comeback win",
    "{team2} surges past {team1} with clutch finish",
    "Strong close seals win for {team2}",
    "Late rally from {team2} stuns {team1}"
],
"late_surge_team2_loss": [
    "Late push from {team2} falls short against {team1}",
    "{team2} scores late but can't complete comeback",
    "Final frame flurry not enough for {team2}",
    "{team1} withstands late surge from {team2}",
    "Momentum shift denied as {team2} drops contest",
    "Third-period effort wasted in {team2}'s loss",
    "Clutch chances missed as {team2} falls"
],
"scoreless_period_team1_win": [
    "{team1} goes quiet for a bit but still tops {team2}",
    "Despite scoreless stretch, {team1} finds enough to win",
    "Offensive lull doesn’t stop {team1} from beating {team2}",
    "{team1} rebounds after dry spell to secure victory",
    "Some moments of cold, but {team1} heats up when it counts",
    "Scoreless stretch shrugged off in {team1}'s win",
    "{team1} finds rhythm late to overcome early silence"
],
"scoreless_period_team1_loss": [
    "Scoreless stretch costs {team1} in loss to {team2}",
    "{team1} can't recover from offensive drought",
    "Momentum lost during scoreless frame for {team1}",
    "Dry spell proves costly as {team1} falls",
    "{team2} capitalizes on {team1}'s quiet period",
    "One bad frame dooms {team1}",
    "Offensive gap leaves {team1} chasing all night"
],
"scoreless_period_team2_win": [
    "{team2} goes quiet for a bit but still tops {team1}",
    "Despite scoreless stretch, {team2} finds enough to win",
    "Offensive lull doesn’t stop {team2} from beating {team1}",
    "{team2} rebounds after dry spell to secure victory",
    "Some moments of cold, but {team2} heats up when it counts",
    "Scoreless stretch shrugged off in {team2}'s win",
    "{team2} finds rhythm late to overcome early silence"
],
"scoreless_period_team2_loss": [
    "Scoreless stretch costs {team2} in loss to {team1}",
    "{team2} can't recover from offensive drought",
    "Momentum lost during scoreless frame for {team2}",
    "Dry spell proves costly as {team2} falls",
    "{team1} capitalizes on {team2}'s quiet period",
    "One bad frame dooms {team2}",
    "Offensive gap leaves {team2} chasing all night"
],
"goalie_performance_team1_win": [
    "{goalie1} anchors {team1}'s win with key saves",
    "Solid outing from {goalie1} helps {team1} top {team2}",
    "{goalie1} holds firm in high-pressure moments",
    "{team1} wins despite shaky night from {goalie1}",
    "Few big stops from {goalie1}, but offense carries the load",
    "{goalie1} rebounds after early goals to secure win",
    "Mixed performance from {goalie1} in {team1}'s victory"
],
"goalie_performance_team1_loss": [
    "{goalie1} struggles as {team1} falls to {team2}",
    "Strong effort from {goalie1} wasted in defeat",
    "{goalie1} keeps it close, but can't steal the win",
    "Soft goals hurt {team1} in loss despite {goalie1}'s effort",
    "Busy night for {goalie1}, but result slips away",
    "{goalie1} flashes brilliance, but breakdowns prove costly",
    "Late goals undo solid outing from {goalie1}"
],
"goalie_performance_team2_win": [
    "{goalie2} anchors {team2}'s win with key saves",
    "Solid outing from {goalie2} helps {team2} top {team1}",
    "{goalie2} holds firm in high-pressure moments",
    "{team2} wins despite shaky night from {goalie2}",
    "Few big stops from {goalie2}, but offense carries the load",
    "{goalie2} rebounds after early goals to secure win",
    "Mixed performance from {goalie2} in {team2}'s victory"
],
"goalie_performance_team2_loss": [
    "{goalie2} struggles as {team2} falls to {team1}",
    "Strong effort from {goalie2} wasted in defeat",
    "{goalie2} keeps it close, but can't steal the win",
    "Soft goals hurt {team2} in loss despite {goalie2}'s effort",
    "Busy night for {goalie2}, but result slips away",
    "{goalie2} flashes brilliance, but breakdowns prove costly",
    "Late goals undo solid outing from {goalie2}"
],
}

def headline_generator(**kwargs):
    team1 = kwargs.get("team1", "")
    team2 = kwargs.get("team2", "")
    score1 = kwargs.get("score1", 0)
    score2 = kwargs.get("score2", 0)
    winner = kwargs.get("winner", "")
    ot_winner = kwargs.get("ot_winner", "")
    overtime = kwargs.get("overtime", "No")
    ot_scorers = kwargs.get("ot_scorers", ["N/A"])
    ot_scorers_name = kwargs.get("ot_scorers_name", "N/A")
    ot1_score = kwargs.get("ot1_score", score1)
    ot2_score = kwargs.get("ot2_score", score2)
    hat_trick_scorer = kwargs.get("hat_trick_scorer", None)
    all_goals = kwargs.get("all_goals", [])

    team1_period1 = kwargs.get("team1_period1", 0)
    team1_period2 = kwargs.get("team1_period2", 0)
    team1_period3 = kwargs.get("team1_period3", 0)

    team2_period1 = kwargs.get("team2_period1", 0)
    team2_period2 = kwargs.get("team2_period2", 0)
    team2_period3 = kwargs.get("team2_period3", 0)
                               
    hrs = random.randint(0, 6)
    goal_difference = abs(score1 - score2)

    team1_win_options = ['_team1_win', '_team2_loss']
    team2_win_options = ['_team2_win', '_team1_loss']

    team1_win = random.choice(team1_win_options)
    team2_win = random.choice(team2_win_options)

    shutout = score2 == 0 if winner == team1 else score1 == 0

    tag_base = 'None'
    
    if overtime == 'Yes':
        if ot_winner == team1:
            tag_base = 'team1_win'
        elif ot_winner == team2:
            tag_base = 'team2_win'
        key = 'overtime_' + tag_base
    
    else:
        raw_winner = team1 if score1 > score2 else team2

        either = ['collapse','late_surge']
        either1 = ['shutout_win','shutout_win','shutout_win','goalie_performance']
        
        if winner == team1:
            tag_base = team1_win
        else:
            tag_base = team2_win

        if overtime == 'Yes':
            key = 'overtime' + tag_base
        elif hat_trick_scorer:
            hat_trick_team = next(
                (team for _, _, _, team, player, _ in all_goals if player == hat_trick_scorer),
                None
            )
            hat_trick_team_won = hat_trick_team == winner

            if hat_trick_team == team1:
                tag_base = "team1_win" if hat_trick_team_won else "team1_loss"
            elif hat_trick_team == team2:
                tag_base = "team2_win" if hat_trick_team_won else "team2_loss"
            key = 'hat_trick' + tag_base
        elif shutout:
            key = random.choice(either1) + tag_base
        elif (team1_period1 > team2_period1 and winner == team2) or (team2_period1 > team1_period1 and winner == team1):
            key = 'comeback' + tag_base
        elif (team1_period1 + team1_period2 > team2_period1 + team2_period2 and winner == team2) or (team2_period1 + team2_period2 > team1_period1 + team1_period2 and winner == team1):
            key = random.choice(either) + tag_base
        elif goal_difference == 1:
            key = 'close' + tag_base
        elif (team1_period1 >= 3 and winner == team1) or (team2_period1 >=3 and winner == team2):
            key = 'strong_start' + tag_base
        elif goal_difference >= 4:
            key = 'blowout' + tag_base
        elif score1 + score2 <= 3:
            key = 'low_score' + tag_base
        elif score1 + score2 >= 7:
            key = 'high_score' + tag_base
        elif (raw_winner == team1 and (team1_period1 == 0 or team1_period2 == 0 or team1_period3 == 0)) or (raw_winner == team2 and (team2_period1 == 0 or team2_period2 == 0 or team2_period3 == 0)):
            key = 'scoreless_period' + tag_base
        else:
            key = tag_base.strip('_')
        
    headline_list = headline_choices.get(key)

    if not headline_list:
        fallback_key = tag_base.strip("_")
        headline_list = headline_choices.get(fallback_key, [""] * 7)

    template = headline_list[hrs] if hrs < len(headline_list) else ""
    safe_kwargs = {k: (v if v is not None else "") for k, v in kwargs.items()}
    headline = template.format(**safe_kwargs)

    return headline


    #elif shootout = 'Yes' then headline = shootout

team_colors = {
    "Arizona": ["rgb(242,12,23)", "rgb(255,245,0)"],
    "Atlanta": ["rgb(4,0,74)", "rgb(236,121,1)"],
    "Baltimore": ["rgb(4,0,74)", "rgb(7,178,239)"],
    "Boise": ["rgb(73,31,33)", "rgb(232,213,177)"],
    "Charleston": ["rgb(0,118,195)", "rgb(4,4,4)"],
    "Chicago": ["rgb(242,0,145)", "rgb(4,4,4)"],
    "Cincinnati": ["rgb(42,41,152)", "rgb(253,247,1)"],
    "Cleveland": ["rgb(235,121,2)", "rgb(4,4,4)"],
    "Delaware": ["rgb(242,12,23)", "rgb(255,244,0)"],
    "Denver": ["rgb(242,207,4)", "rgb(4,4,4)"],
    "Detroit": ["rgb(160,2,3)", "rgb(252,252,252)"],
    "Florida": ["rgb(210,245,4)", "rgb(4,4,4)"],
    "Honolulu": ["rgb(254,244,0)", "rgb(4,4,4)"],
    "Houston": ["rgb(9,25,138)", "rgb(102,95,101)"],
    "Indianapolis": ["rgb(2,245,202)", "rgb(4,4,4)"],
    "Iowa": ["rgb(161,2,3)", "rgb(225,86,52)"],
    "Jacksonville": ["rgb(241,19,5)", "rgb(4,4,4)"],
    "Kansas City": ["rgb(1,90,33)", "rgb(4,4,4)"],
    "Las Vegas": ["rgb(242,230,7)", "rgb(4,4,4)"],
    "Lincoln": ["rgb(202,96,0)", "rgb(4,4,4)"],
    "Long Island": ["rgb(21,188,219)", "rgb(10,4,241)"],
    "Madison": ["rgb(64,1,102)", "rgb(252,252,252)"],
    "Memphis": ["rgb(4,4,4)", "rgb(242,4,3)"],
    "Mississippi": ["rgb(84,4,241)", "rgb(0,230,242)"],
    "Montana": ["rgb(241,191,0)", "rgb(4,4,4)"],
    "New York": ["rgb(40,40,40)", "rgb(241,13,23)"],
    "North Dakota": ["rgb(2,117,54)", "rgb(252,252,252)"],
    "Oklahoma": ["rgb(74,37,31)", "rgb(252,252,252)"],
    "Philadelphia": ["rgb(127,0,0)", "rgb(201,96,0)"],
    "Portland": ["rgb(42,41,152)", "rgb(252,252,252)"],
    "Puerto Rico": ["rgb(241,180,6)", "rgb(4,4,4)"],
    "Raleigh": ["rgb(0,246,43)", "rgb(4,4,4)"],
    "Rapid City": ["rgb(119,121,119)", "rgb(127,0,0)"],
    "Richmond": ["rgb(242,12,23)", "rgb(4,4,4)"],
    "San Antonio": ["rgb(127,0,0)", "rgb(252,252,252)"],
    "Seattle": ["rgb(53,187,73)", "rgb(243,13,25)"],
    "South Dakota": ["rgb(161,2,3)", "rgb(217,159,20)"],
    "St. Louis": ["rgb(241,104,21)", "rgb(4,4,4)"],
    "Tennessee": ["rgb(73,73,73)", "rgb(4,4,4)"],
    "Washington": ["rgb(4,0,74)", "rgb(254,244,0)"]
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>USCTHL Simulator</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 30px;
      background-color: rgb(222,227,237);
      color: black;
    }
    .form-section {
      margin-bottom: 30px;
    }
    .team-row {
      display: flex;
      justify-content: space-between;
      align-items: stretch;
      margin-bottom: 20px;
    }
    .team-box {
      width: 45%;
      display: flex;
      flex-direction: column;
      border: 4px solid;
      padding: 0;
    }
    .team-label {
      text-align: center;
      font-weight: bold;
      padding: 8px;
      background-color: #f0f0f0;
      border-bottom: 2px solid #ccc;
    }
    .team-content {
      display: flex;
      flex: 1;
    }
    .score-line {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-weight: bold;
    }
    .team-info {
      flex: 2;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
      padding: 15px;
    }
    .team-logo {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: inherit;
    }
    .team-logo img {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      padding: 10px;
    }
    .final-score-label {
      font-weight: bold;
      margin-top: 10px;
      margin-bottom: 6px;
    }
    .vs-box {
      width: 10%;
      text-align: center;
      font-size: 1.5em;
      font-weight: bold;
      color: #101010;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .period-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-top: 30px;
    }
    .period-box {
      width: 60%;
      background-color: #FFFFFF;
      border: 1px solid #000000;
      border-radius: 0;
      padding: 15px 20px;
      margin-bottom: 20px;
      text-align: left;
    }
    .period-box h4 {
      margin-top: -5px;
      margin-bottom: 10px;
      color: black;
      text-align: center;
    }
    .period-box p {
      margin: 5px 0;
      font-size: 0.95em;
    }
    .winner-box {
      width: 60%;
      margin: 40px auto 20px auto;
      padding: 15px 20px;
      border: 2px solid #000000;
      border-radius: 0px;
      text-align: center;
    }
    .winner-label {
      font-size: 1.1em;
      font-weight: bold;
      margin-bottom: 10px;
    }
    .winner-name {
      font-size: 1.25em;
      font-weight: bold;
    }
    .score-text {
      font-weight: bold;
    }
    .headline-box {
      width: 60%;
      background-color: white;
      text-align: center;
      padding: 10px 0;
      margin-top: 60px;
      border: 2px solid #000000;
      border-radius: 0px;
    }
    .headline-label {
      font-size: 1.1em;
      font-weight: bold;
      margin-bottom: 10px;
      color: black;
    }
    .headline {
      font-size: 1.6em;
      font-weight: bold;
      margin-bottom: 5px;
      color: black;
    }
  </style>
</head>
<body>

  <h1>USCTHL Game Simulator</h1>

  <form method="POST" class="form-section">
    <label for="team1">Home:</label>
    <input type="text" name="team1" id="team1" required>
    &nbsp;&nbsp;
    <label for="team2">Away:</label>
    <input type="text" name="team2" id="team2" required>
    &nbsp;&nbsp;
    <button type="submit">Simulate</button>
  </form>

  {% if result %}
    {% if result["error"] %}
      <p style="color:red;">Error: {{ result["error"] }}</p>
    {% else %}

      <div class="team-row">
        <div class="team-box" style="border-color: {{ team_colors[result["team1"]["name"]][1] }};">
          <div class="team-content"
               style="background-color: {{ team_colors[result["team1"]["name"]][0] }};
                      color: {{ team_colors[result["team1"]["name"]][1] }};">
            <div class="team-info">
              <div style="font-weight: bold; margin-bottom: 10px;">Home</div>
              <h3 style="color: {{ team_colors[result["team1"]["name"]][1] }};">
                {{ result["team1"]["place"] }} {{ team_names[result["team1"]["place"]]}}
              </h3>
              <p><strong>Goalie:</strong> {{ result["team1"]["goalie"] }}</p>
            </div>
            <div class="team-logo"
                 style="border-left: 4px solid {{ team_colors[result["team1"]["name"]][1] }};">
              <img src="{{ logo1 }}" alt="{{ result["team1"]["name"] }} logo">
            </div>
          </div>
        </div>

        <div class="vs-box">VS</div>

        <div class="team-box" style="border-color: {{ team_colors[result["team2"]["name"]][1] }};">
          <div class="team-content"
               style="background-color: {{ team_colors[result["team2"]["name"]][0] }};
                      color: {{ team_colors[result["team2"]["name"]][1] }};">
            <div class="team-logo"
                 style="border-right: 4px solid {{ team_colors[result["team2"]["name"]][1] }};">
              <img src="{{ logo2 }}" alt="{{ result["team2"]["name"] }} logo">
            </div>
            <div class="team-info">
              <div style="font-weight: bold; margin-bottom: 10px;">Away</div>
              <h3 style="color: {{ team_colors[result["team2"]["name"]][1] }};">
                {{ result["team2"]["place"] }} {{ team_names[result["team2"]["place"]]}}
              </h3>
              <p><strong>Goalie:</strong> {{ result["team2"]["goalie"] }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="period-container">
        {% for period in result["periods"] %}
          <div class="period-box">
            <h4>{{ period["label"] }}</h4>
            {% if period["events"] %}
              {% for event in period["events"] %}
                <p style="white-space: pre-line; margin-bottom: 12px;">{{ event }}</p>
              {% endfor %}
            {% else %}
              <p>No Scoring</p>
            {% endif %}
          </div>
        {% endfor %}

        {% if result["overtime"] == "Yes" and result["ot_scorers_name"] %}
          <div class="period-box">
            <h4>Overtime</h4>
            <p style="white-space: pre-line;">{{ result["ot_scorers"][0] }}</p>
          </div>
        {% endif %}
      </div>
    {% endif %}
  {% endif %}

  {% if result and not result.get("error") %}
    {% set winner_key = result["winner"] %}
    <div class="winner-box" style="background-color: {{ team_colors[winner_key][0] }};">
      <div class="winner-label" style="color: {{ team_colors[winner_key][1] }}">
        Winner:
        <span class="winner-name">
          {% if result["winner"] == result["team1"]["name"] %}
            {{ result["team1"]["place"] }} {{ team_names[result["team1"]["place"]] }}
          {% elif result["winner"] == result["team2"]["name"] %}
            {{ result["team2"]["place"] }} {{ team_names[result["team2"]["place"]] }}
          {% else %}
            {{ result["winner"] }}
          {% endif %}
        </span>
      </div>

      <div class="final-score-label" style="color: {{ team_colors[winner_key][1] if winner_key in team_colors else 'black' }};">
        Final Score:
      </div>

      <div class="score-line">
        <span style="color: {{ team_colors[winner_key][1] if winner_key in team_colors else 'black' }};">
          {% if result["ot1_score"] > result["ot2_score"] %}
            {{ result["ot1_score"] }} - {{ result["ot2_score"] }}
          {% else %}
            {{ result["ot2_score"] }} - {{ result["ot1_score"] }}
          {% endif %}
          {% if result["overtime"] == "Yes" %} (OT){% endif %}
        </span>
      </div>
    </div>
  {% endif %}

  {% if headline %}
    <div class="headline-box">
      <div class="headline-label">Headline</div>
      <p class="headline">{{ headline }}</p>
    </div>
  {% endif %}

</body>
</html>"""

from flask import request, render_template_string

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    headline = None

    if request.method == 'POST':
        raw_team1 = request.form.get('team1')
        raw_team2 = request.form.get('team2')

        team_thing1 = normalize_team_input(raw_team1).strip()
        team_thing2 = normalize_team_input(raw_team2).strip()


        if team_thing1 and team_thing2:
            result = simulate_game(team_thing1, team_thing2)
            result["team1"]["place"] = result["team1"].get("place", team_thing1).strip()
            result["team2"]["place"] = result["team2"].get("place", team_thing2).strip()
        
            result["team1"]["name"] = result["team1"]["name"].strip()
            result["team2"]["name"] = result["team2"]["name"].strip()
            result["winner"] = result["winner"].strip()

            if result and not result.get("error"):
                team1_period1, team1_period2, team1_period3 = result.get("team1_periods", [0, 0, 0])
                team2_period1, team2_period2, team2_period3 = result.get("team2_periods", [0, 0, 0])
                result["team1"]["place"] = team_thing1
                result["team2"]["place"] = team_thing2
                result["team1"]["place"] = result["team1"]["place"].strip()
                result["team2"]["place"] = result["team2"]["place"].strip()

                headline = headline_generator(
                    team1 = result["team1"]["name"],
                    team2 = result["team2"]["name"],
                    score1 = result["ot1_score"],
                    score2 = result["ot2_score"],
                    winner = result["winner"],
                    overtime = result["overtime"],
                    ot_winner = result.get("ot_winner", ""),
                    ot_scorers = result.get("ot_scorers", ["N/A"]),
                    ot_scorers_name = result["ot_scorers_name"] if result.get("ot_scorers") else "N/A",
                    ot1_score = result.get("ot1_score", result["team1"]["total_goals"]),
                    ot2_score = result.get("ot2_score", result["team2"]["total_goals"]),
                    goalie1 = result["team1"]["goalie"],
                    goalie2 = result["team2"]["goalie"],
                    period_events = result["period_events"],
                    hat_trick_scorer = result.get("hat_trick_scorer"),
                    team1_period1 = result["team1_periods"][0],
                    team1_period2 = result["team1_periods"][1],
                    team1_period3 = result["team1_periods"][2],
                    team2_period1 = result["team2_periods"][0],
                    team2_period2 = result["team2_periods"][1],
                    team2_period3 = result["team2_periods"][2],
                    all_goals = result.get("all_goals", [])
                )
            else:
                result = {"error": "Invalid team thing there, bub"}
        else:
            result = {"error": "please enter a valid input bub"}
            

    winner_key = None
    if result and isinstance(result, dict) and "winner" in result and not result.get("error"):
        winner_key = result["winner"].split(" (")[0].strip()

    def get_logo(team_name):
        logo_dir = os.path.join(app.static_folder, "logos")
        prefix = team_name + " "
        suffix = "Logo.jpg"
    
        for file in os.listdir(logo_dir):
            if file.startswith(prefix) and file.endswith(suffix):
                return url_for('static', filename=f'logos/{file}')
        return None

    logo1 = get_logo(result["team1"]["name"]) if result else None
    logo2 = get_logo(result["team2"]["name"]) if result else None

    team_colors.setdefault("overtime", ["#000000", "#000000"])

    return render_template_string(
        HTML_TEMPLATE,
        result=result,
        headline=headline,
        team_colors=team_colors,
        team_names=team_names,
        winner_key=winner_key,
        logo1=logo1,
        logo2=logo2
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
