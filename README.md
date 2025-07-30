# My Personal Blog

A personal blog and portfolio website built with [Zola](https://www.getzola.org/), a fast static site generator written in Rust. This site showcases my projects and experience.

## Features

- 📝 Technical blog posts and articles
- 🚀 Project portfolio with detailed descriptions
- 🎨 Clean, responsive design using the Linkita theme
- 🔍 Search functionality (when enabled)
- ⚡ Fast loading times with static generation

## Tech Stack

- **Static Site Generator**: [Zola](https://www.getzola.org/)
- **Theme**: [Linkita](https://github.com/Diegomangasco/linkita)
- **Deployment**: Ready for Netlify, Vercel, or GitHub Pages

## Quick Start

### Prerequisites

- [Zola](https://www.getzola.org/documentation/getting-started/installation/) installed on your system

### Local Development

1. Clone the repository:
```bash
git clone <your-repo-url>
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

## Project Structure

```
zola-blog/
├── content/          # Markdown content files
│   ├── blog/         # Blog posts
│   ├── pages/        # Static pages (about, projects)
│   └── _index.md     # Homepage content
├── static/           # Static assets (images, files)
├── sass/             # Custom Sass styles
├── themes/           # Theme files (git submodule)
├── public/           # Generated site (ignored by git)
├── config.toml       # Site configuration
└── README.md         # This file
```

## Content Management

### Adding Blog Posts

Create new markdown files in the `content/blog/` directory:

```markdown
+++
title = "Your Post Title"
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

## Deployment

This site is ready to deploy on various platforms:

### Netlify
1. Connect your GitHub repository
2. Set build command to `zola build`
3. Set publish directory to `public`

### Vercel
1. Import your GitHub repository
2. Vercel will auto-detect Zola and configure the build

### GitHub Pages
Use the [Zola GitHub Action](https://github.com/shalzz/zola-deploy-action) for automatic deployment.

## Customization

### Theme Customization
The Linkita theme can be customized through the `config.toml` file. Refer to the [theme documentation](https://github.com/Diegomangasco/linkita) for available options.

### Custom Styles
Add custom CSS in the `sass/` directory. Files will be automatically compiled during build.

## Contributing

This is a personal blog, but if you spot any issues or have suggestions, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
