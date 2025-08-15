# My Personal Blog

A personal blog and portfolio website built with [Zola](https://www.getzola.org/), a fast static site generator written in Rust. This site showcases my projects and experience.

## Features

- Technical blog posts and articles
- Project portfolio with detailed descriptions
- Clean, responsive design using the Linkita theme
- Search functionality (when enabled)
- Very fast static generation
- Tiny page size

## Tech Stack

- **Static Site Generator**: [Zola](https://www.getzola.org/)
- **Theme**: [Linkita](https://github.com/Diegomangasco/linkita)
- **Build**: Github Actions
- **Deployment**: Cloudflare Pages

## Local Development

1. Clone the repository:
```bash
git clone <repo-url>
cd zola-blog
```

2. Initialize the theme submodule:
```bash
git submodule update --init --recursive
```

3. Start the development server:
```bash
zola serve
```

4. Open your browser and navigate to `http://127.0.0.1:1111`

The site will automatically reload when you make changes to the content or templates.

### Adding Blog Posts

Create new markdown files in the `content/blog/` directory:

```markdown
+++
title = "Post Title"
date = 2024-01-01
description = "Brief description of the post"
[taxonomies]
tags = ["tag1", "tag2"]
+++

Your post content here...
```

### Updating Pages

Edit the markdown files in `content/pages/` to update the About and Projects pages.

### Configuration

Modify `config.toml` to customize:
- Site title and description
- Base URL for deployment
- Menu items
- Theme settings

## Building for Production

To build the site for deployment:

```bash
zola build
```

The generated site will be in the `public/` directory.
