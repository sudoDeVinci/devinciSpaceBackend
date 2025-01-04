/**
 * @typedef {Object} Comment
 * @property {string} uid
 * @property {string} author
 * @property {string} title
 * @property {string} content
 * @property {string} created
 * @property {string} edited
 */

/**
 * @typedef {Object} Blogpost
 * @property {string} uid
 * @property {string} title
 * @property {string} content
 * @property {string} [tags]
 * @property {string} created
 * @property {string} edited
 * @property {Comment} [comments]
 */
class Page {
    /**
     * Render a blog post as an HTML element.
     * This render will be returned to a parent window.
     * @param {Blogpost} blogpost 
     * @returns {HTMLElement}
     */
    static blogpost(blogpost) {
        // Create main container with retro styling
        const blogpostElement = document.createElement('article');
        blogpostElement.classList.add('blogpost');
        blogpostElement.setAttribute('data-uid', blogpost.uid);
        
        // Add base styles
        blogpostElement.style.cssText = `
            font-family: "MS Sans Serif", "Segoe UI", Tahoma, sans-serif;
            background: #fff;
            border: 2px solid #808080;
            box-shadow: inset -1px -1px #0a0a0a, inset 1px 1px #dfdfdf;
            padding: 1rem;
            margin-bottom: 1.5rem;
            max-width: 800px;
        `;

        // Add header with title and metadata
        const header = document.createElement('header');
        header.style.cssText = `
            border-bottom: 2px solid #808080;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
        `;

        const title = document.createElement('h2');
        title.textContent = blogpost.title;
        title.style.cssText = `
            margin: 0 0 0.5rem 0;
            font-size: 1.25rem;
            font-weight: bold;
            color: #000;
        `;

        const metadata = document.createElement('div');
        metadata.style.cssText = `
            font-size: 0.875rem;
            color: #666;
            display: flex;
            gap: 1rem;
        `;

        // Format dates
        const created = new Date(blogpost.created);
        const edited = new Date(blogpost.edited);
        
        metadata.innerHTML = `
            <time datetime="${blogpost.created}">Posted: ${created.toLocaleDateString()}</time>
            ${created.getTime() !== edited.getTime() ? 
                `<time datetime="${blogpost.edited}">Edited: ${edited.toLocaleDateString()}</time>` : 
                ''
            }
            ${blogpost.tags ? `<div class="tags">Tags: ${blogpost.tags}</div>` : ''}
        `;

        header.appendChild(title);
        header.appendChild(metadata);
        blogpostElement.appendChild(header);

        // Process content to handle code blocks
        const content = document.createElement('div');
        content.classList.add('blogpost-content');
        content.style.cssText = `
            line-height: 1.6;
            margin-bottom: 1.5rem;
        `;

        // Process content for code blocks
        const processedContent = Page.processContentWithCodeBlocks(blogpost.content);
        content.innerHTML = processedContent;

        // Style images within content
        const images = content.getElementsByTagName('img');
        for (const img of images) {
            img.style.cssText = `
                max-width: 100%;
                height: auto;
                border: 1px solid #808080;
                padding: 2px;
                background: #fff;
                margin: 0.5rem 0;
            `;
        }

        blogpostElement.appendChild(content);

        // Comments section if present
        if (blogpost.comments && blogpost.comments.length > 0) {
            const commentsSection = document.createElement('section');
            commentsSection.classList.add('comments');
            commentsSection.style.cssText = `
                margin-top: 2rem;
                padding-top: 1rem;
                border-top: 2px solid #808080;
            `;

            const commentsTitle = document.createElement('h3');
            commentsTitle.textContent = 'Comments';
            commentsTitle.style.cssText = `
                font-size: 1rem;
                margin: 0 0 1rem 0;
                font-weight: bold;
            `;
            commentsSection.appendChild(commentsTitle);

            blogpost.comments.forEach(comment => {
                const commentElement = document.createElement('div');
                commentElement.classList.add('comment');
                commentElement.setAttribute('data-uid', comment.uid);
                commentElement.style.cssText = `
                    background: #f0f0f0;
                    border: 1px solid #808080;
                    box-shadow: inset -1px -1px #0a0a0a, inset 1px 1px #dfdfdf;
                    padding: 0.75rem;
                    margin-bottom: 1rem;
                `;

                // Comment header with author and title
                const commentHeader = document.createElement('div');
                commentHeader.style.cssText = `
                    margin-bottom: 0.5rem;
                    border-bottom: 1px solid #808080;
                    padding-bottom: 0.25rem;
                `;

                const commentTitle = document.createElement('h4');
                commentTitle.textContent = comment.title;
                commentTitle.style.cssText = `
                    margin: 0 0 0.25rem 0;
                    font-size: 0.875rem;
                    font-weight: bold;
                `;

                const commentAuthor = document.createElement('div');
                commentAuthor.textContent = `By: ${comment.author}`;
                commentAuthor.style.cssText = `
                    font-size: 0.75rem;
                    color: #666;
                `;

                commentHeader.appendChild(commentTitle);
                commentHeader.appendChild(commentAuthor);
                commentElement.appendChild(commentHeader);

                // Comment content - escaped as plaintext
                const commentContent = document.createElement('div');
                commentContent.style.cssText = `
                    font-size: 0.875rem;
                    line-height: 1.4;
                    white-space: pre-wrap;
                `;
                commentContent.textContent = comment.content;
                commentElement.appendChild(commentContent);

                // Comment footer with timestamps
                const commentFooter = document.createElement('footer');
                commentFooter.style.cssText = `
                    margin-top: 0.5rem;
                    font-size: 0.75rem;
                    color: #666;
                    border-top: 1px solid #808080;
                    padding-top: 0.25rem;
                `;

                const commentCreated = new Date(comment.created);
                const commentEdited = new Date(comment.edited);

                commentFooter.innerHTML = `
                    <time datetime="${comment.created}">Posted: ${commentCreated.toLocaleDateString()}</time>
                    ${commentCreated.getTime() !== commentEdited.getTime() ? 
                        `<time datetime="${comment.edited}"> (Edited: ${commentEdited.toLocaleDateString()})</time>` : 
                        ''
                    }
                `;

                commentElement.appendChild(commentFooter);
                commentsSection.appendChild(commentElement);
            });

            blogpostElement.appendChild(commentsSection);
        }

        return blogpostElement;
    }

    /**
     * Process content to handle code blocks with the same styling as chat
     * @param {string} content - The HTML content to process
     * @returns {string} - Processed HTML content with styled code blocks
     */
    static processContentWithCodeBlocks(content) {
        // Regular expression to match content between triple backticks
        const codeBlockRegex = /```([\s\S]*?)```/g;
        
        // Replace code blocks with styled pre elements
        return content.replace(codeBlockRegex, (match, code) => {
            const styledCode = `<pre style="
                font-family: 'Fira Code', monospace;
                font-size: 0.95em;
                line-height: 1.4;
                white-space: pre-wrap;
                background: #1e1e1e;
                color: #d4d4d4;
                padding: 12px;
                border-radius: 6px;
                margin: 8px 0;
                border-left: 4px solid #007acc;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                tab-size: 2;
                -moz-tab-size: 2;
                overflow-x: auto;
            ">${code.trim()}</pre>`;
            return styledCode;
        });
    }
}