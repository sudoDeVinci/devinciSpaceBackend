from typing import Any, Dict, List, TypedDict, Final
from github import Github, Auth, Repository, ContentFile
from os import environ, getcwd
from os.path import join
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(join(getcwd(), ".env"))

class RepositoryDict(TypedDict):
    title: str
    thumbnail: str
    description: str
    tags: List[str]
    demo_url: str
    repo_url: str
    updated: str

class RepositorySlice(TypedDict):
    repos: List[RepositoryDict]
    count: int
    updated: datetime

REPOSITORIES: RepositorySlice | None = None
TOKEN: Final[str] = environ.get("GITHUB_TOKEN", "")


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
    
    # Default thumbnail
    return ""

def get_repositories() -> List[RepositoryDict]:
    global REPOSITORIES, TOKEN
    repos: List[RepositoryDict] = []

    print(f">>>> TOKEN is {TOKEN}")


    if REPOSITORIES is not None:
        diff: timedelta = datetime.now() - REPOSITORIES["updated"]
        if diff.seconds < 7200:  # 2 hours
            repos.extend(REPOSITORIES["repos"])

    else:
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
                "updated": datetime.now()
            }
            
        except Exception as e:
            print(f"Error retrieving repositories: {e}")
            return []

        finally:
            if publicGithub is not None:
                publicGithub.close()

    return repos