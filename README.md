<p align=center>
    <img src="https://upload.wikimedia.org/wikipedia/fi/thumb/2/2a/Veolia-logo.svg/250px-Veolia-logo.svg.png"/>
</p>

<p align=center>
    <a href="https://pypi.org/project/pyolia/"><img src="https://img.shields.io/pypi/v/pyolia.svg"/></a>
    <a href="https://github.com/tetienne/python-veolia-api/actions"><img src="https://github.com/tetienne/python-veolia-api/workflows/CI/badge.svg"/></a>
    <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" /></a>
</p>

Small client to retrieve the water consumption from Veolia website: https://www.eau-services.com

## Remarks
Veolia publishes water consumption with a delay of 3 days. It  means if we are the 14, you will be only able to retrieve your data from the 11.
To retrieve the hourly water consumption, you have to update your preferences on this [page](https://www.eau-services.com/mon-espace-suivi-personnalise.aspx).

## Installation

```bash
pip install pyolia
```

## Getting started

```python
import asyncio
from datetime import datetime, timedelta

from pyolia.client import VeoliaClient


USERNAME = "your username"
PASSWORD = "your password"

async def main() -> None:
    async with VeoliaClient(USERNAME, PASSWORD) as client:
        now = datetime.now()
        if now.day < 4:
            now = now - timedelta(days=3)
        consumption = await client.get_consumption(now.month, now.year)
        print(consumption)
        now = now - timedelta(days=3)
        consumption = await client.get_consumption(now.month, now.year, now.day)
        print(consumption)


asyncio.run(main())
```

## Development

### Installation

- For Linux, install [pyenv](https://github.com/pyenv/pyenv) using [pyenv-installer](https://github.com/pyenv/pyenv-installer)
- For MacOS, run `brew install pyenv`
- Don't forget to update your `.bashrc` file (or similar):
  ```
  export PATH="~/.pyenv/bin:$PATH"
  eval "$(pyenv init -)"
  ```
- Install the required [dependencies](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)
- Install [poetry](https://python-poetry.org): `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python`

- Clone this repository
- `cd python-veolia-api`
- Install the required Python version: `pyenv install`
- Init the project: `poetry install`
- Run `poetry run pre-commit install`

## PyCharm

As IDE you can use [PyCharm](https://www.jetbrains.com/pycharm/).

Using snap, run `snap install pycharm --classic` to install it.

For MacOS, run `brew cask install pycharm-ce`

Once launched, don't create a new project, but open an existing one and select the **python-veolia-api** folder.

Go to _File | Settings | Project: nre-tag | Project Interpreter_. Your interpreter must look like `<whatever>/python-veolia-api/.venv/bin/python`
