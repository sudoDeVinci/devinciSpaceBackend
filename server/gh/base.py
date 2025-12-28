from asyncio import Lock, gather, new_event_loop, set_event_loop
from logging import INFO
from os import environ, makedirs
from pathlib import Path
from threading import Thread
from time import sleep, time
from typing import cast

from asyncPyGithub import (
    GitHubPortal,
    GitHubRepositoryPortal,
    GitHubUserPortal,
    PrivateUser,
    read_json,
    write_json,
)
from asyncPyGithub._types import FullRepository
from asyncPyGithub.base import LOGGER
from dotenv import load_dotenv  # type: ignore

from ._types import RepoGist, RepoSlice

CACHE_LOCK: Lock = Lock()
BASE_DIR: Path = Path(__file__).parent.resolve()
CACHE_DIR: Path = BASE_DIR / "cache"
makedirs(CACHE_DIR, exist_ok=True)
REPO_JSON: Path = CACHE_DIR / "repositories.json"
REPO_CACHE: RepoSlice | None = None
LOGGER.setLevel(INFO)

try:
    assert load_dotenv(verbose=True), (
        "Failed to load environment variables from .env file."
    )
    TOKEN = environ.get("GITHUB_TOKEN", environ.get("TOKEN", None))

    assert TOKEN is not None, "GITHUB_TOKEN must be set in environment variables."
except (AssertionError, AttributeError, OSError) as err:
    LOGGER.error(f"Error during global configuration:::{err}")


async def refresh_cache() -> RepoSlice | None:
    global CACHE_LOCK, REPO_CACHE

    try:
        # On auth, the User is stored in GitHubPortal.user on a class level
        status, user = await GitHubPortal.authenticate(TOKEN)  # type: ignore
        if status != 200:
            raise Exception(
                f"Authentication failed with status code: {status} :: {user}"
            )

        user = cast(PrivateUser, user)

        # Get the 10 most recently updated repositories
        status, repos = await GitHubUserPortal.repositories(
            visibility="public", sort="updated", direction="desc", per_page=10, page=1
        )
        if status != 200:
            raise Exception(
                f"Failed to fetch repositories with status code: {status} :: {repos}"
            )

        repos = cast(list[FullRepository], repos)

        langroutines = [
            GitHubRepositoryPortal.list_repository_languages(
                user.login,
                repo.name,
            )
            for repo in repos
        ]

        thumbnailroutines = [
            GitHubRepositoryPortal.get_repo_content(
                user.login,
                repo.name,
                "thumbnail.png",
            )
            for repo in repos
        ]

        await GitHubPortal.close()

        langresults, thumbnailresults = await gather(
            *[
                gather(*langroutines),
                gather(*thumbnailroutines),
            ]
        )

        languages = [
            list(langs.keys()) if stat == 200 else None for stat, langs in langresults
        ]

        thumbnails = [
            thumbnail.download_url
            if stat == 200 and thumbnail is not None
            else "/images/0.png"
            for stat, thumbnail in thumbnailresults
        ]

        async with CACHE_LOCK:
            REPO_CACHE = {
                "count": len(repos),
                "updated": int(time()),
                "repos": [
                    RepoGist(  # type: ignore
                        name=repo.name,
                        html_url=str(repo.html_url),
                        description=repo.description,
                        stars=repo.stargazers_count,
                        topics=repo.topics,
                        languages=languages[i],
                        thumbnail_url=str(thumbnails[i]),
                    )
                    for i, repo in enumerate(repos)
                ],
            }

        return REPO_CACHE

    except Exception as e:
        LOGGER.error(f"An error occurred: {e}")


async def fetch_repositories() -> list[RepoGist] | None:
    global REPO_CACHE, CACHE_LOCK

    repocopy: RepoSlice | None = None

    async with CACHE_LOCK:
        if not REPO_CACHE:
            LOGGER.info(
                "fetch_repositories :: No in-memory cache, fetching cache on disk."
            )
            REPO_CACHE = cast(RepoSlice | None, read_json(REPO_JSON))

        repocopy = REPO_CACHE.copy() if REPO_CACHE else None

    if repocopy and "updated" in repocopy:
        LOGGER.info("fetch_repositories :: In-memory cache found - validating")
        diff = int(time()) - repocopy["updated"]
        if diff < 7200:
            LOGGER.info("fetch_repositories :: Cache is valid, returning cached data.")
            return REPO_CACHE["repos"] if REPO_CACHE else None

    LOGGER.info("fetch_repositories :: Cache is invalid, refreshing cache.")
    _ = await refresh_cache()

    LOGGER.info("fetch_repositories :: Writing refreshed cache to disk.")
    _ = write_json(REPO_JSON, REPO_CACHE)  # type: ignore
    LOGGER.info("fetch_repositories :: Cache written to disk.")
    return REPO_CACHE["repos"] if REPO_CACHE else None


def schedule_refresh() -> None:
    global LOGGER
    ttl = 3600  # 1 hour
    LOGGER.info("schedule_refresh :: Starting cache refresh scheduler.")
    loop = new_event_loop()
    set_event_loop(loop)

    try:
        while True:
            loop.run_until_complete(fetch_repositories())
            sleep(ttl)
    except Exception as e:
        LOGGER.error(f"An error occurred in the scheduler: {e}")
    finally:
        loop.close()


if __name__ == "__main__":
    Thread(target=schedule_refresh, daemon=True).start()
    while True:
        pass
