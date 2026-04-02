from setuptools import setup, find_packages

setup(
    name="steam-hunter",
    version="2.0.0",
    description="Асинхронный охотник за скидками в Steam",
    author="Your Name",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "aiohttp>=3.9.0",
        "aiofiles>=23.2.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "fake-useragent>=1.4.0",
        "rich>=13.7.0",
        "typer>=0.9.0",
        "diskcache>=5.6.0",
    ],
    entry_points={
        "console_scripts": [
            "steam-hunter=src.main_async:app",
        ],
    },
)