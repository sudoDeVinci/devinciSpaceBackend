from server import Manager, create_app
from server import PostService, Post, TagManager, Comment

if __name__ == "__main__":
    Manager.connect()
    comments = []
    comments.append(
        Comment(author="John Doe", title="Great post!", content="Great post!")
    )
    comments.append(
        Comment(author="Jane Doe", title="Awesome post!", content="Awesome post!")
    )
    PostService.insert(
        post=Post(
            title="Lorem Ipsum",
            content="""
                    <p>Lorem ipsum dolor sit amet, <strong>consectetur adipiscing elit</strong>. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
                    <img src="/api/placeholder/640/360" alt="Vintage Computer Setup" />                    
                    <h3>The Golden Age of Computing</h3>
                    <p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
                    <ul>
                        <li>Commodore 64</li>
                        <li>Apple II</li>
                        <li>IBM PC</li>
                    </ul>
                    <img src="/api/placeholder/480/320" alt="Retro Programming Interface" />
                    <p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.</p>
                    <blockquote>
                        "The computer was born to solve problems that did not exist before." 
                        — Bill Gates
                    </blockquote>
                    <p>Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.</p>
                    """,
            tags=TagManager.encode_tags(["python", "software"]),
            comments=[],
        )
    )
    app = create_app()
    app.run(debug=True)
