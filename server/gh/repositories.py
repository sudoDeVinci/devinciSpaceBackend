from typing import Any, Dict, List, TypedDict, Final
from github import Github, Auth, Repository, ContentFile
from os import environ, getcwd
from os.path import join, exists
from datetime import datetime, timedelta
from dotenv import load_dotenv
from json import dump, load, JSONDecodeError
import pathlib
from time import time
from functools import lru_cache
from threading import Timer, Lock
from logging import getLogger

LOG = getLogger(__name__)
load_dotenv(join(getcwd(), ".env"))

class RepositoryDict(TypedDict):
    title: str
    thumbnail: str
    description: str
    demo_url: str
    repo_url: str
    updated: str
    tags: List[str]

class RepositorySlice(TypedDict):
    count: int
    updated: int
    repos: List[RepositoryDict]

CACHE_LOCK: Lock = Lock()
REPOSITORIES: RepositorySlice | None = None
REFRESH_TIMER: Timer | None = None
currentdir = pathlib.Path(__file__).parent.resolve()
REPOSITORY_JSON: str = join(currentdir, "repositories.json")
TOKEN: Final[str] = environ.get("GITHUB_TOKEN", "")


@lru_cache(maxsize=20)
def get_project_thumbnail(
    repo: Repository.Repository,
    paths: List[str] = ["thumbnail.png", ".github/thumbnail.png", "logo.png"]
) -> str:
    """
    Try to find a thumbnail image in the repository by checking multiple paths.
    Returns the download URL of the first image found, or an empty string if none is found.
    """
    for path in paths:
        try:
            file = repo.get_contents(path)
            if file and hasattr(file, "download_url"):
                return file.download_url
        except Exception:
            continue

    return ""


def refresh_repositories() -> None:
    """
    Fetch and cache the top 10 public repositories from GitHub.
    """
    global REPOSITORIES
    global CACHE_LOCK

    publicGithub: Github | None = None
    print("REFRESH REPOSITORIES ::: Fetching repositories from GitHub...")
    try:
        auth = Auth.Token(TOKEN)
        publicGithub = Github(auth = auth)
        user = publicGithub.get_user()
        
        # Get the past 10 public repos that I've worked on
        repositories:List[Repository.Repository ] = list(user.get_repos())
        repositories.sort(key = lambda repo: repo.updated_at, reverse = True)
        repositories = repositories[:10]
        repos = [{
                "title": repo.name,
                "thumbnail": get_project_thumbnail(repo),
                "description": repo.description,
                "tags": [lang for lang in repo.get_languages()],
                "demo_url": "",
                "repo_url": repo.html_url,
                "updated": repo.updated_at
            } for repo in repositories if not repo.private]
        
        # Cache the repositories
        with CACHE_LOCK:
            print(f"REFRESH REPOSITORIES ::: Found {len(repos)} public repositories.")
            REPOSITORIES = {
                "repos": repos,
                "count": len(repos),
                "updated": int(time())
            }

            print(REPOSITORIES['updated'])
        
    except Exception as e:
        print(f"Error retrieving repositories: {e}")

    finally:
        if publicGithub is not None:
            publicGithub.close()

def read_repositories() -> None:
    """
    Read the cached repositories from the JSON file.
    """
    global REPOSITORIES
    global CACHE_LOCK

    print(f"READ REPOSITORIES ::: Reading cache from {REPOSITORY_JSON} ...")
    with CACHE_LOCK:
        if exists(REPOSITORY_JSON):
            try:  # Still missing this
                with open(REPOSITORY_JSON, "r") as f:
                    REPOSITORIES = load(f)
            except (JSONDecodeError, IOError) as e:
                print(f"Error reading cache: {e}")
                REPOSITORIES = None
        else:
            print(f"Cache file {REPOSITORY_JSON} does not exist, initializing empty cache.")
            REPOSITORIES = None


def write_repositories() -> None:
    """
    Write the cached repositories to the JSON file.
    """
    global CACHE_LOCK

    print(f"WRITE REPOSITORIES ::: Writing cache to {REPOSITORY_JSON} ...")
    with CACHE_LOCK:
        try:
            with open(REPOSITORY_JSON, "w+") as f:
                dump(REPOSITORIES, f, indent=4, default=str)
        except (IOError, OSError) as e:
            print(f"Error writing cache: {e}")


def schedule_repository_refresh() -> None:
    global CACHE_LOCK
    global REFRESH_TIMER

    repocopy: RepositorySlice | None = None
    with CACHE_LOCK:
        repocopy = REPOSITORIES.copy() if REPOSITORIES is not None else None

    if repocopy is None or int(time()) - repocopy.get("updated", 0) > 3600:
        print("SCHEDULED THREAD ::: Starting repository refresh...")
        refresh_repositories()
        write_repositories()
        print("SCHEDULED THREAD ::: Repository refresh completed.")
    else:
        print("SCHEDULED THREAD ::: Repositories cache is up-to-date, skipping refresh.")

    # Cancel existing timer before creating new one
    if REFRESH_TIMER is not None:
        REFRESH_TIMER.cancel()
        del REFRESH_TIMER

    
    print(f"SCHEDULED THREAD ::: Scheduling next repository refresh...")
    REFRESH_TIMER = Timer(3600, schedule_repository_refresh)
    REFRESH_TIMER.start()


def fetch_repositories() -> List[RepositoryDict]:
    global REPOSITORIES
    global CACHE_LOCK

    repocopy: RepositorySlice | None = None
    with CACHE_LOCK:
        repocopy = REPOSITORIES.copy() if REPOSITORIES is not None else None

    if repocopy is not None and "updated" in repocopy:
        print("FETCH REPOSITORIES ::: Checking cache ...")
        diff = int(time()) - repocopy["updated"]
        if diff < 7200:
            print("FETCH REPOSITORIES ::: Cache is valid, returning cached repositories.")
            return repocopy.get("repos", [])

    read_repositories()
    with CACHE_LOCK:
        repocopy = REPOSITORIES.copy() if REPOSITORIES is not None else None

    if repocopy is not None and "updated" in repocopy:
        # Check if the cache is still valid (less than 2 hours old)
        print("FETCH REPOSITORIES ::: Cache read, checking validity ...")
        diff: int = int(time()) - repocopy["updated"]
        if diff < 7200:
            print("FETCH REPOSITORIES ::: Cache is valid, returning cached repositories.")
            return repocopy.get("repos", [])


    # If no repositories are cached or the cache is outdated, fetch and write to cache
    print("FETCH REPOSITORIES ::: Cache is invalid or not found, refreshing repositories ...")
    refresh_repositories()    
    write_repositories()

    with CACHE_LOCK:
        return REPOSITORIES["repos"] if REPOSITORIES else []
