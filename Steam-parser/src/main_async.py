#!/usr/bin/env python3

import asyncio
import typer
from rich.console import Console
from rich.table import Table
from src.async_steam_parser import AsyncSteamParser
from src.filters import GameFilter
from pathlib import Path
import json

console = Console()
app = typer.Typer(help="🎮 Steam Hunter — быстрая асинхронная версия")

@app.command()
def hunt(
    discount: int = typer.Option(70, "--discount", "-d", help="Минимальная скидка в %"),
    rating: int = typer.Option(0, "--rating", "-r", help="Минимальный рейтинг"),
    max_price: int = typer.Option(None, "--max-price", "-p", help="Максимальная цена"),
    genres: str = typer.Option(None, "--genres", "-g", help="Жанры через запятую"),
    pages: int = typer.Option(3, "--pages", help="Страниц для парсинга"),
    concurrent: int = typer.Option(15, "--concurrent", "-c", help="Одновременных запросов"),
    no_details: bool = typer.Option(False, "--no-details", help="Без деталей"),
    clear_cache: bool = typer.Option(False, "--clear-cache", help="Очистить кэш"),
):
    if clear_cache:
        from diskcache import Cache
        cache = Cache("cache")
        cache.clear()
        console.print("[yellow]🗑️ Кэш очищен[/yellow]")
        cache.close()
    
    console.print("\n[bold cyan]⚡ STEAM HUNTER — АСИНХРОННАЯ ВЕРСИЯ[/bold cyan]")
    console.print(f"[dim]Одновременных запросов: {concurrent}[/dim]\n")
    
    async def run():
        async with AsyncSteamParser(max_concurrent=concurrent) as parser:
            console.print("[1/3] 📡 Быстрый сбор игр со скидками...")
            games = await parser.get_sale_games(max_pages=pages)
            
            if not games:
                console.print("[red]❌ Игры не найдены[/red]")
                return
            
            console.print(f"[green]✅ Найдено {len(games)} игр[/green]")
            
            if not no_details:
                console.print("\n[2/3] 🔄 Параллельная загрузка деталей...")
                games = await parser.enrich_games_with_details(games)
            
            console.print("\n[3/3] 🔍 Фильтрация...")
            genre_list = [g.strip() for g in genres.split(',')] if genres else []
            
            filter_engine = GameFilter(
                min_discount=discount,
                min_rating=rating,
                max_price=max_price,
                genres=genre_list
            )
            
            filtered = filter_engine.filter_batch(games)
            
            if not filtered:
                console.print("[yellow]⚠️ Нет игр подходящих под критерии[/yellow]")
                return
            
            console.print(f"\n[bold green]📊 НАЙДЕНО: {len(filtered)} ИГР[/bold green]\n")
            
            table = Table(title="🔥 Лучшие предложения")
            table.add_column("#", style="dim")
            table.add_column("Название", style="green", no_wrap=False)
            table.add_column("Скидка", style="yellow")
            table.add_column("Цена", style="white")
            table.add_column("Рейтинг", style="magenta")
            
            for idx, game in enumerate(filtered[:20], 1):
                table.add_row(
                    str(idx),
                    game.get('name', 'Unknown')[:45],
                    f"-{game.get('discount', 0)}%",
                    f"{game.get('price', 0)}₽",
                    f"{game.get('rating_percent', 0)}%"
                )
            
            console.print(table)
            
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / "steam_deals_async.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(filtered, f, ensure_ascii=False, indent=2)
            
            console.print(f"\n[green]📁 Результат: {output_file}[/green]")
            
            if filtered:
                console.print("\n[bold cyan]💎 ТОП-5 ПРЕДЛОЖЕНИЙ:[/bold cyan]")
                for idx, game in enumerate(filtered[:5], 1):
                    console.print(f"  {idx}. [green]{game.get('name')}[/green]")
                    console.print(f"     💰 -{game.get('discount')}% | {game.get('price')}₽")
                    console.print(f"     🔗 {game.get('url')}\n")
    
    asyncio.run(run())

@app.command()
def quick():
    hunt(discount=70, pages=2, concurrent=20, no_details=True, rating=0, max_price=None, genres=None, clear_cache=False)

@app.command()
def best():
    hunt(discount=80, pages=3, concurrent=15, no_details=False, rating=0, max_price=None, genres=None, clear_cache=False)

@app.command()
def cache_stats():
    from diskcache import Cache
    cache = Cache("cache")
    console.print(f"\n[cyan]📊 Статистика кэша:[/cyan]")
    console.print(f"  Размер: {len(cache)} записей")
    console.print(f"  Объём: {cache.volume() / 1024 / 1024:.2f} MB")
    cache.close()

if __name__ == "__main__":
    app()