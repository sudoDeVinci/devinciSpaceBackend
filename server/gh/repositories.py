from typing import Any, Dict, List, TypedDict, Final
from github import Github, Auth, Repository, ContentFile
from os import environ, getcwd
from os.path import join, exists
from datetime import datetime, timedelta
from dotenv import load_dotenv
from json import dump, load
import pathlib
from time import time
from functools import lru_cache

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

REPOSITORIES: RepositorySlice | None = None
currentdir = pathlib.Path(__file__).parent.resolve()
REPOSITORY_JSON: str = join(currentdir, "repositories.json")
TOKEN: Final[str] = environ.get("GITHUB_TOKEN", "")


lru_cache(maxsize=20)
def get_project_thumbnail(repo: Repository.Repository, paths: List[str] = ["thumbnail.png", ".github/thumbnail.png", "logo.png"]) -> str:
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
    global REPOSITORIES
    publicGithub: Github | None = None
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
        REPOSITORIES = {
            "repos": repos,
            "count": len(repos),
            "updated": int(time())
        }

        print(REPOSITORIES['updated'])
        
    except Exception as e:
        print(f"Error retrieving repositories: {e}")
        return []

    finally:
        if publicGithub is not None:
            publicGithub.close()


def write_repositories() -> None:
    with open(REPOSITORY_JSON, "w+") as f:
        dump(REPOSITORIES, f, indent=4, default=str)


def fetch_repositories() -> List[RepositoryDict]:
    global REPOSITORIES

    if REPOSITORIES is not None:
        diff = int(time()) - REPOSITORIES["updated"]
        if diff < 7200:  # 2 hours
            return REPOSITORIES["repos"]

    if exists(REPOSITORY_JSON):
        with open(REPOSITORY_JSON, "r") as f:
            REPOSITORIES = load(f)
            diff: int = int(time()) - REPOSITORIES["updated"]
            if diff < 7200:
                return REPOSITORIES["repos"]


    # If no repositories are cached or the cache is outdated, fetch and write to cache
    refresh_repositories()    
    write_repositories()

    return REPOSITORIES["repos"] if REPOSITORIES else []
