from typing import Final, Callable, cast
from os import environ, makedirs
from os.path import join
from dotenv import load_dotenv  # type: ignore
from logging import getLogger, Logger
from requests import Response, get
import pathlib
import asyncio
from time import time, sleep
from threading import Lock, Thread
import json

from ._types import (
    User,
    Repository,
    RepoGist,
    RepoSlice
)

load_dotenv()

currentdir = pathlib.Path(__file__).parent.resolve()
CACHE_DIR: str = join(currentdir, "cache")
makedirs(CACHE_DIR, exist_ok=True)

REPOSITORY_JSON: str = join(CACHE_DIR, "repositories.json")
USER_JSON: str = join(CACHE_DIR, "user.json")
REPO_CACHE: RepoSlice = {}
USER_CACHE: User = {}
CACHE_LOCK: Lock = Lock()

TOKEN: Final[str] = environ.get("GITHUB_TOKEN", "")
API_VERSION: Final[str] = '2022-11-28'
API_ENDPOINT: Final[str] = 'https://api.github.com' 
LOGGER: Logger = getLogger(__name__)
LOGGER.setLevel('INFO')


def write_json(file_path: str, data: dict):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except (IOError, OSError) as e:
        print(f"WRITE JSON ::: Error writing cache: {e}")


def read_json(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading cache: {e}")

    return {}


async def req(fn: Callable, url: str, **kwargs) -> Response:
    kwargs['timeout'] = 30
    kwargs.setdefault('headers', {}).update(
        {
            'Authorization': f'Bearer {TOKEN}',
            'X-GitHub-Api-Version': API_VERSION,
            'User-Agent': 'devinci.space/1.0',
            'Accept': 'application/vnd.github.v3+json',
        })
    r = await asyncio.to_thread(fn, f'{API_ENDPOINT}{url}', **kwargs)
    await asyncio.sleep(0.1)
    return r


async def get_user() -> tuple[int, User]:
    res = await req(fn = get,
              url='/user',)
    return (res.status_code, res.json())


async def get_repos() -> tuple[int, list[Repository]]:
    res = await req(fn=get,
              url='/user/repos',
              params={
                'visibility': 'public',
                'sort': 'updated',
                'direction': 'desc',
                'per_page': 10,
              })
    return (res.status_code, res.json())


async def get_repo_languages(repo: str) -> tuple[int, dict[str, int]]:
    res = await req(
        fn=get,
        url=f'/repos/sudoDeVinci/{repo}/languages',
    )
    return (res.status_code, res.json())


async def get_repo_thumbnail(repo:str,
                     owner:str = "sudoDeVinci"
                    ) -> tuple[int, dict]:
    res = await req(
        fn=get,
        url=f'/repos/{owner}/{repo}/contents/thumbnail.png',
    )
    return (res.status_code, res.json())


async def refresh() -> None:
    """
    Refresh our user and repositories cache w/ the latest data from GitHub.
    """
    global USER_CACHE, REPO_CACHE
    try:

        with CACHE_LOCK:
            if not USER_CACHE:
                print("REFRESH ::: No in-memory user cache found, fetching disk cache ...")
                USER_CACHE = cast(User, read_json(USER_JSON))

            if not USER_CACHE:
                print("REFRESH ::: No user cache found, fetching user data from GitHub ...")
                stat, user = await get_user()
                if stat != 200:
                    raise ValueError(f"Failed to fetch user data: {stat} :: {user}")

                USER_CACHE.update(user)

        
        # Get the repos we wanna show - 10 of the most recently updated.
        print("REFRESH ::: Fetching repositories from GitHub ...")
        stat, fullrepos = await get_repos()
        if stat != 200:
            raise ValueError(f"Failed to fetch repositories: {stat} :: {fullrepos}")
        
        # Format repos into a list of RepoGist
        repos: list[RepoGist] = [RepoGist(
            name=repo['name'],
            description=cast(str, repo.get('description', '')),
            html_url=repo['html_url'],
            stars=cast(int, repo.get('stargazers_count', 0)),
            topics=cast(list[str], repo.get('topics', [])),
            thumbnail=''
        ) for repo in fullrepos]
    
        with CACHE_LOCK:
            REPO_CACHE.update(
                {
                    'count': len(repos),
                    'repos': repos,
                    'updated': int(time())
                }
            )

            langcoroutines = [get_repo_languages(repo['name']) for repo in repos]
            thumbnailcoroutines = [get_repo_thumbnail(repo['name']) for repo in repos]

            awaitables = [asyncio.gather(*langcoroutines), asyncio.gather(*thumbnailcoroutines)]
            langresponses, thumbnailresponses  = await asyncio.gather(*awaitables)

            languages = [list(langs.keys()) for _, langs in langresponses]
            thumbnails = [thumbnail.get('download_url', None) for _, thumbnail in thumbnailresponses]

            for index, repo in enumerate(repos):
                repo['languages'] = languages[index]
                repo['thumbnail'] = thumbnails[index]
        

    except Exception as e:
        LOGGER.error(f"An error occurred: {e}")



async def fetch_repositories() -> list[RepoGist]:
    global REPO_CACHE, CACHE_LOCK

    repocopy: RepoSlice | None = None

    print("FETCH REPOSITORIES ::: Checking in-memory cache ...")
    with CACHE_LOCK:
        if not REPO_CACHE:
            print("FETCH REPOSITORIES ::: No in-memory cache found, fetching disk cache ...")
            REPO_CACHE = cast(RepoSlice, read_json(REPOSITORY_JSON))

        repocopy = REPO_CACHE.copy() if REPO_CACHE else None


    if repocopy and "updated" in repocopy:
        print("FETCH REPOSITORIES ::: Cache exists, validating ...")
        diff = int(time()) - repocopy["updated"]
        if diff < 7200:
            print("FETCH REPOSITORIES ::: Cache valid, returning cached repositories ...")
            return repocopy.get("repos", [])
        

    print("FETCH REPOSITORIES ::: Cache Invalid / not found, refreshing ...")
    await refresh()

    with CACHE_LOCK:
        write_json(REPOSITORY_JSON, REPO_CACHE)  # type: ignore
        write_json(USER_JSON, USER_CACHE)        # type: ignore
        return REPO_CACHE.get("repos", []) if REPO_CACHE else []
    

def schedule_refresh() -> None:
    global CACHE_LOCK

    ttl = 3600  # 1 hour in seconds
    print("SCHEDULE REFRESH ::: Starting background refresh every hour ...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        while True:
            loop.run_until_complete(refresh())
            with CACHE_LOCK:
                write_json(REPOSITORY_JSON, REPO_CACHE)  # type: ignore
                write_json(USER_JSON, USER_CACHE)        # type: ignore
            sleep(ttl)
    except Exception as e:
        LOGGER.error(f"Background refresh error: {e}")
    finally:
        loop.close()
    
    print("")

if __name__ == "__main__": 
    Thread(target=schedule_refresh, daemon=True).start()
    while True:
        pass
