import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os
import re


SAVE_TEAMS_TO_CSV =False
SAVE_ALL_TO_CSV = False

def scrape_website(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve data, status code: {response.status_code}")
        return None

def parse_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id='ratings-table')
    
    data = []
    
    # Extract the table body rows
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    
    for row in rows:
        cols = row.find_all('td')
        if cols:
            rk = cols[0].text.strip()
            team = cols[1].text.strip()
            conf = cols[2].text.strip()
            wl = cols[3].text.strip()
            adjEM = cols[4].text.strip()
            adjO = cols[5].text.strip() # spacing between adjO and adjD, etc bc rankings
            adjD = cols[7].text.strip()  
            adjT = cols[9].text.strip() 
            luck = cols[11].text.strip() 
            data.append([rk, team, conf, wl, adjEM, adjO, adjD, adjT, luck])
    
    # Create df with specified column names
    columns = ['Rk', 'Team', 'Conf', 'W-L', 'AdjEM', 'AdjO', 'AdjD', 'AdjT', 'Luck']
    df = pd.DataFrame(data, columns=columns)
    return df

def normalize_team_name(name):
    name = name.lower()
    # Replace 'st.' with 'state'
    name = re.sub(r'\bst\.?\b', 'state', name)
    name = name.replace('.', '')
    name = name.replace("'", "")
    return name

def filter_by_teams_ordered(df, team_names):
    ordered_df = pd.DataFrame()

    # Normalize input team names for easier user input
    normalized_team_names = [normalize_team_name(name) for name in team_names]

    for name in normalized_team_names:
        # Filter the DataFrame for each team name, using the .apply() method to normalize names in the DataFrame for comparison
        match = df[df['Team'].apply(normalize_team_name) == name]

        if not match.empty:
            ordered_df = pd.concat([ordered_df, match])

    return ordered_df.reset_index(drop=True)


def filter_by_teams(df, team_names):
    # Normalize input team names
    normalized_team_names = [normalize_team_name(name) for name in team_names]
    
    # Create a temporary column for normalized team names in the DataFrame
    df['Normalized_Team'] = df['Team'].apply(normalize_team_name)
    
    # Apply normalization to the 'Team' column and filter the DataFrame using the temporary column
    filtered_df = df[df['Normalized_Team'].isin(normalized_team_names)]
    
    # Drop the temporary normalized column if you don't want it in the output
    filtered_df = filtered_df.drop(columns=['Normalized_Team'])
    
    return filter_by_teams_ordered(filtered_df, team_names)

def get_data_for_teams(df):
    # Input for team names
    team_names = []
    team_names.append(input("Away Team: "))
    team_names.append(input("Home Team: "))
    
    specific_teams_df = filter_by_teams(df, team_names)
    
    return specific_teams_df

def save_to_csv(df, team_names=[]):
    today = datetime.date.today()
    date_str = today.strftime('%Y-%m-%d')

    if (len(team_names) == 2):
        filename = f'kenpom_data_{team_names[0]}_at_{team_names[1]}__{date_str}.csv'
    else:
        filename = f'kenpom_data_ALL__{date_str}.csv'
    
    folder_name = "kenpom_data"
    folder_path = os.path.join('.', folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    full_path = os.path.join(folder_path, filename) 
    df.to_csv(full_path, index=False)
    print(f"Kenpom data saved to '{full_path}'.")
    

def main():
    url = 'https://kenpom.com/index.php#'
    html_content = scrape_website(url)
    
    if html_content:
        df = parse_data(html_content)
       
        while True:
            try:
                team_df = get_data_for_teams(df)
                print(team_df)
                print('\n')

                if SAVE_TEAMS_TO_CSV:
                    save_to_csv(team_df)
            except KeyboardInterrupt:
                print("\nExiting...")
                break  
    
    if SAVE_ALL_TO_CSV:
        save_to_csv(df)

if __name__ == "__main__":
    main()
