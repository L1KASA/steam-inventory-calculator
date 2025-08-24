import json
import re
import requests


class SteamInventoryChecker:
    def __init__(self, steam_id: str, headers: dict[str, str]) -> None:
        self.steam_id = steam_id
        self.session = requests.Session()
        self.session.headers.update(headers)

    def _extract_json_from_html(self, html_content: str, pattern: str) -> dict:
        match = re.search(pattern, html_content, re.DOTALL)
        if match:
            try:
                json_data = json.loads(match.group(1))
                return json_data
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return {}
        return {}

    def get_inventory_games(self) -> dict:
        url = f"https://steamcommunity.com/id/{self.steam_id}/inventory/"
        params = {
            'l': 'russian',
            'count': 1
        }
        try:
            response = self.session.get(url, params=params, timeout=20)
            if response.status_code == 200:
                app_context_data = self._extract_json_from_html(
                    response.text, r'var g_rgAppContextData = (\{.*?\});'
                )

                games_list = {}

                for context_key, game_info in app_context_data.items():
                    game_data = {
                        'appid': game_info.get('appid', ''),
                        'name': game_info.get('name', ''),
                        'asset_count': game_info.get('asset_count', 0),
                    }
                    games_list[context_key] = game_data

                return games_list
            else:
                print(f"HTTP Error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return {}
        except Exception as e:
            print(f"Exception: {e}")
            return {}


def main():
    print("We started! Please, wait...")

    inventory = SteamInventoryChecker(
        steam_id='tempo_218',
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    )

    games = inventory.get_inventory_games()

    print('Found games:')
    for game_key, game_data in games.items():
        print(
            f"{game_data['name']} (AppID: {game_data['appid']}) - {game_data['asset_count']} items"
        )


if '__main__' == __name__:
    main()
