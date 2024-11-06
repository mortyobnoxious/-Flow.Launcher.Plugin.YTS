# -*- coding: utf-8 -*-

import sys,os
parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, 'lib'))
sys.path.append(os.path.join(parent_folder_path, 'plugin'))

from flowlauncher import FlowLauncher
import webbrowser
import json
import requests
import pyperclip


class YtsFlow(FlowLauncher):
    API_URL = 'https://yts.mx/api/v2/list_movies.json?query_term='

    def query(self, query):
        if not query:
            return [{
                "Title": "YTS Plugin",
                "SubTitle": "Search for torrents on YTS",
                "IcoPath": "Images/film.png"
            }]
        
        suggestions = self.get_query_results(query)
        return suggestions if suggestions else [{
            "Title": "No results found",
            "SubTitle": "Try a different term",
            "IcoPath": "Images/film.png"
        }]

    def context_menu(self, data):
        menu_items = [{
            "Title": "YTS",
            "SubTitle": "Open on YTS",
            "IcoPath": "Images/yts.png",
            "JsonRPCAction": {"method": "open_url", "parameters": [f"{data['url']}"]}
        },
        {
            "Title": "IMDb",
            "SubTitle": "Open on IMDb",
            "IcoPath": "Images/imdb.png",
            "JsonRPCAction": {"method": "open_url", "parameters": [f"https://www.imdb.com/title/{data['imdb_code']}"]}
        },
        {
            "Title": "Vidsrc",
            "SubTitle": "Open on vidsrc",
            "IcoPath": "Images/vidsrc.png",
            "JsonRPCAction": {"method": "open_url", "parameters": [f"https://vidsrc.net/embed/{data['imdb_code']}"]}
        }]
        
        for torrent in data.get('torrents', []):
            magnet_link = f"magnet:?xt=urn:btih:{torrent['hash']}"
            quality = torrent.get('quality', 'N/A')
            subtitle = f"{torrent['size']}, {torrent['quality']}, {torrent['type']}, {torrent['video_codec']}, {torrent['bit_depth']}, {torrent['seeds']}/{torrent['peers']}"

            menu_items.append({
                "Title": f"Copy {quality}",
                "SubTitle": subtitle,
                "IcoPath": "Images/magnet.png",
                "JsonRPCAction": {
                    "method": "set_clipboard",
                    "parameters": [magnet_link]
                }
            })
        
        return menu_items

    def get_query_results(self, input_text):
        response = requests.get(f"{self.API_URL}{input_text}")
        response.raise_for_status()
        movies = response.json().get('data', {}).get('movies', [])

        results = []
        for movie in movies:
            title = movie.get('title_long', 'Unknown title')
            rating = f"★ {movie.get('rating', 'N/A')}"
            runtime = f"🕛 {movie.get('runtime', 'N/A')} min"
            torrent = movie.get("torrents", [-1])[-1]
            size = torrent.get("size", "N/A")
            typ = torrent.get("type", "N/A")
            quality = torrent.get("quality", "N/A")
            genres = ', '.join(movie.get('genres', []))
            subtitle = f"{rating}, {runtime}, {genres}, {size}, {typ}, {quality}"
            magnet_link = f"magnet:?xt=urn:btih:{torrent.get('hash', '')}"

            results.append({
                "Title": title,
                "SubTitle": subtitle,
                "IcoPath": f"{movie.get('medium_cover_image', 'Images/magnet.png')}",
                "JsonRPCAction": {
                    "method": "set_clipboard",
                    "parameters": [magnet_link]
                },
                "contextData": movie,
            })
        return results

    def set_clipboard(self, magnet_link):
        pyperclip.copy(magnet_link)

    def open_url(self, url):
        webbrowser.open(url)

if __name__ == "__main__":
    YtsFlow()
