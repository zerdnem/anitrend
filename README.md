# Trending Anime Console App with AniList and ani-cli

A Python-based console application that fetches trending anime from the AniList API and allows users to play their selected anime using `ani-cli`. The app provides a user-friendly interface with tabulated output using the `rich` library, enabling users to browse trending anime by day, week, or month and stream them directly from the terminal.

## Features
- **Fetch Trending Anime**: Uses the AniList GraphQL API to retrieve currently airing anime (sorted by trending activity) and popular anime for the current season (e.g., Winter 2025).
- **Interactive Console UI**: Displays anime lists in a colorful, tabulated format using the `rich` library.
- **Time-Based Categories**: View trending anime for "Today," "This Week," or "This Month" (seasonal popularity).
- **Play Anime with `ani-cli`**: Select an anime from the list and stream it using `ani-cli`, a command-line tool for watching anime.
- **Error Handling**: Includes basic error handling for API requests and `ani-cli` execution.

## Prerequisites
Before running the application, ensure you have the following installed:

### System Requirements
- **Python 3.7+**: The script is written in Python and requires a compatible version.
- **Node.js and npm** (optional, if you want to host the original Anime-API locally as an alternative).
- **Git**: To clone repositories (e.g., `ani-cli`).
- **A Media Player**: `mpv` (recommended), `vlc`, or `iina` (for macOS) to play anime via `ani-cli`.
- **fzf**: For interactive menus in `ani-cli`.

### Python Dependencies
- **requests**: For making HTTP requests to the AniList API.
- **rich**: For creating a beautiful console UI with tables and prompts.

Install them using pip:
```bash
pip install requests rich
