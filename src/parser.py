import re
import requests
from typing import List, Dict
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_fixed
from src.config import Config

class SteamSaleParser:
    
    def __init__(self):
        self.ua = UserAgent()
        self.base_url = Config.STEAM_SEARCH_URL
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def fetch_sale_page(self, page: int = 1) -> str:
        params = {
            'filter': 'globaltopsellers',
            'specials': '1',
            'page': page,
            'cc': 'ru',
            'l': 'russian'
        }
        
        headers = {
            'User-Agent': self.ua.random,
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8'
        }
        
        response = requests.get(
            self.base_url,
            params=params,
            headers=headers,
            timeout=Config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.text
    
    def parse_game_blocks(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'lxml')
        game_blocks = soup.select('a.search_result_row')
        
        games = []
        for block in game_blocks:
            href = block.get('href', '')
            app_id_match = re.search(r'app/(\d+)', href)
            
            if not app_id_match:
                continue
            
            app_id = int(app_id_match.group(1))
            
            title_elem = block.select_one('.title')
            name = title_elem.text.strip() if title_elem else 'Unknown'
            
            discount_elem = block.select_one('.discount_pct')
            discount = 0
            if discount_elem:
                discount_text = discount_elem.text.strip()
                discount_match = re.search(r'(\d+)', discount_text)
                if discount_match:
                    discount = int(discount_match.group(1))
            
            price_elem = block.select_one('.discount_final_price')
            price = 0
            if price_elem:
                price_text = price_elem.text.strip()
                price_text = price_text.replace(' ', '').replace('р.', '').replace('руб.', '')
                price_match = re.search(r'(\d+)', price_text)
                if price_match:
                    price = int(price_match.group(1))
            
            original_elem = block.select_one('.discount_original_price')
            original_price = 0
            if original_elem:
                orig_text = original_elem.text.strip().replace(' ', '').replace('р.', '')
                orig_match = re.search(r'(\d+)', orig_text)
                if orig_match:
                    original_price = int(orig_match.group(1))
            
            games.append({
                'app_id': app_id,
                'name': name,
                'discount': discount,
                'price': price,
                'original_price': original_price
            })
        
        return games
    
    def get_all_sale_games(self, max_pages: int = None) -> List[Dict]:
        if max_pages is None:
            max_pages = Config.DEFAULT_PAGES
        
        all_games = []
        
        for page in range(1, max_pages + 1):
            print(f"  📄 Парсинг страницы {page}/{max_pages}...")
            
            try:
                html = self.fetch_sale_page(page)
                games = self.parse_game_blocks(html)
                
                if not games:
                    print(f"  ℹ️ Страница {page} пуста, остановка")
                    break
                
                all_games.extend(games)
                print(f"     Найдено {len(games)} игр")
                
            except Exception as e:
                print(f"  ⚠️ Ошибка на странице {page}: {e}")
                continue
        
        return all_games