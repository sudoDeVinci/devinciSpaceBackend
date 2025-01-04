from server import Manager, create_app
from server import PostService, Post, TagManager

if __name__ == "__main__":
    Manager.connect()
    PostService.insert(
        post=Post(
            uid="1",
            title="Hello",
            content="World",
            tags=TagManager.encode_tags(["python", "software"]),
            comments=[],
        )
    )
    app = create_app()
    app.run(debug=True)
