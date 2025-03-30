import subprocess
import requests
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from datetime import datetime

# Initialize Rich console
console = Console()

# AniList API endpoint
API_URL = "https://graphql.anilist.co"

# GraphQL query for trending anime (currently airing, sorted by trending)
TRENDING_QUERY = """
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: ANIME, status: RELEASING, sort: TRENDING_DESC) {
      id
      title {
        english
        romaji
      }
      episodes
      popularity
      status
    }
  }
}
"""

# GraphQL query for popular this season
SEASONAL_QUERY = """
query ($page: Int, $perPage: Int, $season: MediaSeason, $seasonYear: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: ANIME, season: $season, seasonYear: $seasonYear, sort: POPULARITY_DESC) {
      id
      title {
        english
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
    """Determine the current anime season and year based on the date (March 29, 2025)."""
    current_date = datetime(2025, 3, 29)  # Updated to current date
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
        variables = {
            "page": 1,
            "perPage": 10
        }

        response = requests.post(
            API_URL,
            json={"query": TRENDING_QUERY, "variables": variables},
            headers={"Content-Type": "application/json"}
        )
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
        variables = {
            "page": 1,
            "perPage": 10,
            "season": season,
            "seasonYear": year
        }

        response = requests.post(
            API_URL,
            json={"query": SEASONAL_QUERY, "variables": variables},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            console.print(f"[red]GraphQL Error: {data['errors']}[/red]")
            return []

        return data["data"]["Page"]["media"]
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error fetching data: {e}[/red]")
        return []

def display_trending_anime(anime_list, period):
    """Display trending anime in a table and return the list with ranks."""
    if not anime_list:
        console.print(f"[yellow]No data available for {period}.[/yellow]")
        return []

    table = Table(title=f"Top 10 Trending Anime - {period.capitalize()}", show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="cyan", justify="center")
    table.add_column("Name", style="green")
    table.add_column("Episodes", style="blue")
    table.add_column("Popularity", style="yellow")

    ranked_list = []
    for rank, anime in enumerate(anime_list, start=1):
        # Use English title if available, otherwise fall back to romaji
        name = anime["title"]["english"] if anime["title"]["english"] else anime["title"]["romaji"]
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
        console.print("4. Exit")

        choice = Prompt.ask("[bold yellow]Select an option (1-4)[/bold yellow]", choices=["1", "2", "3", "4"], default="1")

        ranked_list = []
        period = ""
        if choice == "1":
            period = "day"
            ranked_list = display_trending_anime(trending_anime, period)
        elif choice == "2":
            period = "week"
            ranked_list = display_trending_anime(trending_anime, period)
        elif choice == "3":
            period = "month"
            ranked_list = display_trending_anime(seasonal_anime, period)
        elif choice == "4":
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
