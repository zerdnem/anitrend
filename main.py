import requests
import subprocess
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from datetime import datetime

# Initialize Rich console
console = Console()

# AniList API endpoint
API_URL = "https://graphql.anilist.co"

# GraphQL query for trending anime
TRENDING_QUERY = """
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: ANIME, status: RELEASING, sort: TRENDING_DESC) {
      id
      title {
        romaji
      }
      episodes
      popularity
      status
    }
  }
}
"""

# GraphQL query for seasonal anime
SEASONAL_QUERY = """
query ($page: Int, $perPage: Int, $season: MediaSeason, $seasonYear: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: ANIME, season: $season, seasonYear: $seasonYear, sort: POPULARITY_DESC) {
      id
      title {
        romaji
      }
      episodes
      popularity
      status
    }
  }
}
"""

# New GraphQL query for searching anime
SEARCH_QUERY = """
query ($page: Int, $perPage: Int, $search: String) {
  Page(page: $page, perPage: $perPage) {
    media(type: ANIME, search: $search, sort: POPULARITY_DESC) {
      id
      title {
        romaji
      }
      episodes
      popularity
      status
    }
  }
}
"""

def get_current_season_and_year():
    """Determine the current anime season and year based on the date."""
    current_date = datetime(2025, 3, 22)  # Using March 22, 2025 as per your code
    month = current_date.month

    if 1 <= month <= 3:
        season = "WINTER"
        year = current_date.year
    elif 4 <= month <= 6:
        season = "SPRING"
        year = current_date.year
    elif 7 <= month <= 9:
        season = "SUMMER"
        year = current_date.year
    else:
        season = "FALL"
        year = current_date.year

    return season, year

def fetch_trending_anime():
    """Fetch currently airing anime sorted by trending."""
    try:
        variables = {"page": 1, "perPage": 10}
        response = requests.post(API_URL, json={"query": TRENDING_QUERY, "variables": variables}, 
                              headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            console.print(f"[red]GraphQL Error: {data['errors']}[/red]")
            return []
        return data["data"]["Page"]["media"]
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error fetching data: {e}[/red]")
        return []

def fetch_seasonal_anime():
    """Fetch popular anime for the current season."""
    try:
        season, year = get_current_season_and_year()
        variables = {"page": 1, "perPage": 10, "season": season, "seasonYear": year}
        response = requests.post(API_URL, json={"query": SEASONAL_QUERY, "variables": variables},
                              headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            console.print(f"[red]GraphQL Error: {data['errors']}[/red]")
            return []
        return data["data"]["Page"]["media"]
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error fetching data: {e}[/red]")
        return []

def search_anime(search_term):
    """Search for anime by title."""
    try:
        variables = {"page": 1, "perPage": 10, "search": search_term}
        response = requests.post(API_URL, json={"query": SEARCH_QUERY, "variables": variables},
                              headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            console.print(f"[red]GraphQL Error: {data['errors']}[/red]")
            return []
        return data["data"]["Page"]["media"]
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error fetching data: {e}[/red]")
        return []

def display_anime_list(anime_list, title):
    """Display anime list in a table and return the list with ranks."""
    if not anime_list:
        console.print(f"[yellow]No data available for {title}.[/yellow]")
        return []

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="cyan", justify="center")
    table.add_column("Name", style="green")
    table.add_column("Episodes", style="blue")
    table.add_column("Popularity", style="yellow")

    ranked_list = []
    for rank, anime in enumerate(anime_list, start=1):
        name = anime["title"]["romaji"]
        episodes = str(anime["episodes"] if anime["episodes"] else "N/A")
        popularity = str(anime["popularity"])
        table.add_row(str(rank), name, episodes, popularity)
        ranked_list.append((rank, name, anime))

    console.print(table)
    return ranked_list

def play_with_ani_cli(anime_title):
    """Play the selected anime using ani-cli."""
    try:
        console.print(f"[bold cyan]Launching ani-cli for '{anime_title}'...[/bold cyan]")
        subprocess.run(["ani-cli", anime_title], check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running ani-cli: {e}[/red]")
    except FileNotFoundError:
        console.print("[red]ani-cli not found. Please ensure it is installed and in your PATH.[/red]")

def main_menu():
    """Display the main menu and handle user input."""
    trending_anime = fetch_trending_anime()
    seasonal_anime = fetch_seasonal_anime()

    console.print("[bold yellow]Note:[/bold yellow] 'Today' and 'This Week' show currently airing anime by trending activity. 'This Month' shows popular anime from the current season.")

    while True:
        console.print("\n[bold cyan]=== Trending Anime Menu ===[/bold cyan]")
        console.print("1. Top 10 Anime Today")
        console.print("2. Top 10 Anime This Week")
        console.print("3. Top 10 Anime This Month")
        console.print("4. Search Anime")
        console.print("5. Exit")

        choice = Prompt.ask("[bold yellow]Select an option (1-5)[/bold yellow]", 
                          choices=["1", "2", "3", "4", "5"], default="1")

        ranked_list = []
        if choice == "1":
            ranked_list = display_anime_list(trending_anime, "Top 10 Trending Anime - Day")
        elif choice == "2":
            ranked_list = display_anime_list(trending_anime, "Top 10 Trending Anime - Week")
        elif choice == "3":
            ranked_list = display_anime_list(seasonal_anime, "Top 10 Anime This Month")
        elif choice == "4":
            search_term = Prompt.ask("[bold yellow]Enter anime title to search[/bold yellow]")
            search_results = search_anime(search_term)
            ranked_list = display_anime_list(search_results, f"Search Results for '{search_term}'")
        elif choice == "5":
            console.print("[green]Goodbye![/green]")
            break

        if ranked_list:
            selection = Prompt.ask(
                f"[bold yellow]Enter the rank of the anime to play (1-{len(ranked_list)}) or 0 to go back[/bold yellow]",
                choices=[str(i) for i in range(len(ranked_list) + 1)],
                default="0"
            )
            if selection != "0":
                selected_rank = int(selection)
                selected_anime = next((item for item in ranked_list if item[0] == selected_rank), None)
                if selected_anime:
                    anime_title = selected_anime[1]
                    play_with_ani_cli(anime_title)

if __name__ == "__main__":
    console.print("[bold green]Welcome to the Trending Anime Console App (Powered by AniList)![/bold green]")
    main_menu()
