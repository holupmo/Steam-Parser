import csv
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from src.config import Config

console = Console()

class GameReporter:
    
    def __init__(self, games: List[Dict]):
        self.games = games
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def to_console(self):
        if not self.games:
            console.print(Panel(
                "[red]😢 Игр по заданным критериям не найдено[/red]\n"
                "Попробуй снизить требования к скидке или рейтингу.",
                title="Результаты поиска",
                border_style="red"
            ))
            return
        
        total_savings = sum(g.get('original_price', 0) - g.get('price_final', 0) 
                           for g in self.games if g.get('original_price'))
        
        header = Panel(
            f"[bold cyan]🎮 Найдено игр: {len(self.games)}[/bold cyan]\n"
            f"[green]💰 Экономия: {total_savings}₽[/green]\n"
            f"[yellow]📊 Средняя скидка: {sum(g.get('discount',0) for g in self.games)//len(self.games)}%[/yellow]",
            title="STEAM HUNTER REPORT",
            border_style="green"
        )
        console.print(header)
        
        table = Table(title="🔥 Лучшие предложения", style="cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Название", style="green", no_wrap=False)
        table.add_column("Скидка", style="yellow", justify="right")
        table.add_column("Цена", style="white", justify="right")
        table.add_column("Рейтинг", style="magenta", justify="right")
        table.add_column("Жанры", style="blue", max_width=30)
        
        for idx, game in enumerate(self.games[:20], 1):
            discount = game.get('discount', 0)
            discount_style = "bright_green" if discount >= 80 else "yellow" if discount >= 70 else "white"
            
            rating = game.get('rating_percent', 0)
            rating_style = "bright_green" if rating >= 90 else "green" if rating >= 80 else "yellow"
            
            genres = game.get('genres', [])
            genre_str = ', '.join([g.get('description', '')[:15] for g in genres[:2]])
            
            table.add_row(
                str(idx),
                game.get('name', 'Unknown')[:50],
                f"[{discount_style}]-{discount}%[/{discount_style}]",
                f"{game.get('price_final', 0)}₽",
                f"[{rating_style}]{rating}%[/{rating_style}]",
                genre_str
            )
        
        console.print(table)
        
        if len(self.games) > 20:
            console.print(f"\n[dim]... и ещё {len(self.games) - 20} игр (смотри CSV для полного списка)[/dim]")
    
    def to_csv(self, filename: str = None) -> Path:
        if not self.games:
            return None
        
        if filename is None:
            filename = f"steam_hunt_{self.timestamp}.csv"
        
        output_path = Config.ensure_output_dir() / filename
        
        rows = []
        for game in self.games:
            rows.append({
                'Название': game.get('name', ''),
                'Steam ID': game.get('app_id', ''),
                'Скидка %': game.get('discount', 0),
                'Цена со скидкой': game.get('price_final', 0),
                'Оригинальная цена': game.get('original_price', 0),
                'Рейтинг Metacritic': game.get('rating_percent', 0),
                'Разработчики': ', '.join(game.get('developers', [])),
                'Издатели': ', '.join(game.get('publishers', [])),
                'Жанры': ', '.join([g.get('description', '') for g in game.get('genres', [])]),
                'Дата релиза': game.get('release_date', {}).get('date', ''),
                'Ссылка на изображение': game.get('header_image', '')
            })
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        
        console.print(f"[green]📁 CSV сохранён: {output_path}[/green]")
        return output_path
    
    def to_json(self, filename: str = None) -> Path:
        if not self.games:
            return None
        
        if filename is None:
            filename = f"steam_hunt_{self.timestamp}.json"
        
        output_path = Config.ensure_output_dir() / filename
        
        clean_games = []
        for game in self.games:
            clean_game = game.copy()
            if 'release_date' in clean_game and hasattr(clean_game['release_date'], 'isoformat'):
                clean_game['release_date'] = clean_game['release_date'].isoformat()
            clean_games.append(clean_game)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': self.timestamp,
                'total_games': len(self.games),
                'games': clean_games
            }, f, ensure_ascii=False, indent=2)
        
        console.print(f"[green]📁 JSON сохранён: {output_path}[/green]")
        return output_path
    
    def to_markdown(self, filename: str = None) -> Path:
        if not self.games:
            return None
        
        if filename is None:
            filename = f"steam_hunt_{self.timestamp}.md"
        
        output_path = Config.ensure_output_dir() / filename
        
        lines = [
            f"# Steam Hunter Report - {self.timestamp}",
            "",
            f"## Статистика",
            f"- **Найдено игр:** {len(self.games)}",
            f"- **Средняя скидка:** {sum(g.get('discount',0) for g in self.games)//len(self.games)}%",
            "",
            "## Топ 10 предложений",
            "",
            "| # | Название | Скидка | Цена | Рейтинг |",
            "|---|----------|--------|------|---------|"
        ]
        
        for idx, game in enumerate(self.games[:10], 1):
            lines.append(
                f"| {idx} | {game.get('name', 'Unknown')[:40]} | "
                f"-{game.get('discount', 0)}% | "
                f"{game.get('price_final', 0)}₽ | "
                f"{game.get('rating_percent', 0)}% |"
            )
        
        lines.extend(["", "---", "*Отчёт сгенерирован Steam Hunter*"])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        console.print(f"[green]📁 Markdown сохранён: {output_path}[/green]")
        return output_path