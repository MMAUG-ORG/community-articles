# Contributing to MMAUG Community Articles

Thank you for your interest in contributing a technical article to the Malta Microsoft AI User Group (MMAUG) community!

This guide explains how to submit, review, and publish articles.

## Before You Start

- Read the [MMAUG Code of Conduct](https://maltamsaiusergroup.github.io/maltamsaiusergroup/code-of-conduct.html).
- Check [existing articles](https://maltamsaiusergroup.github.io/community-articles/) and [open issues](https://github.com/maltamsaiusergroup/community-articles/issues) to avoid duplicate topics.
- If you have an idea but are unsure, [open an Article Proposal issue](https://github.com/maltamsaiusergroup/community-articles/issues/new?template=article-proposal.yml) to get feedback first.

## Contribution Workflow

### 1. Fork and Clone

```bash
# Fork the repo on GitHub, then clone your fork
git clone https://github.com/<your-username>/community-articles.git
cd community-articles
```

### 2. Create a Branch

```bash
git checkout -b article/your-article-slug
```

### 3. Write Your Article

Create a Markdown file in `_articles/` using the naming convention:

```
_articles/YYYY-MM-DD-your-article-slug.md
```

Use the [article template](article-template.md) as a starting point. Every article **must** include the following YAML frontmatter:

```yaml
---
title: "Your Article Title"
author: "Your Full Name"
author_github: "your-github-username"
date: YYYY-MM-DD
tags: [tag1, tag2]
description: "A short summary of the article."
---
```

### 4. Add Images (Optional)

Place images in:

```
assets/images/articles/your-article-slug/
```

Reference them in your article using:

```markdown
![Description]({{ '/assets/images/articles/your-article-slug/image.png' | relative_url }})
```

### 5. Commit and Push

```bash
git add .
git commit -m "Add article: Your Article Title"
git push origin article/your-article-slug
```

### 6. Open a Pull Request

Open a PR from your fork's branch to `maltamsaiusergroup/community-articles:main`.

In the PR description, include:

- A brief summary of the article
- Target audience (beginner / intermediate / advanced)
- Any related issues (e.g., `Closes #12`)

### 7. Review Process

- A reviewer (typically the Technical Program Lead) will review your article.
- You may receive feedback as PR review comments — please address them.
- Once approved, the article will be merged and automatically published.

## Content Guidelines

### Topics We Welcome

- Microsoft Azure (AI, cloud, security, DevOps, infrastructure)
- Azure AI Foundry, Copilot, and AI agents
- Open-source tools and frameworks
- Cloud architecture and best practices
- Hands-on tutorials and walkthroughs
- Session recaps from MMAUG meetups and events

### Quality Standards

- **Original content** — your article must be your own work. Cite references properly.
- **Accurate** — verify technical claims, commands, and code samples.
- **Clear** — write for your target audience. Define acronyms on first use.
- **Structured** — use headings, code blocks, lists, and images to improve readability.
- **Respectful** — follow the [MMAUG Code of Conduct](https://maltamsaiusergroup.github.io/maltamsaiusergroup/code-of-conduct.html).

### What to Avoid

- Promotional or advertising content (see Code of Conduct §4.5)
- Confidential or proprietary information
- Unverified technical claims or misleading AI assertions
- Content that violates intellectual property rights

## Updating an Existing Article

To update a published article, follow the same fork-and-PR workflow. Update the article file and open a new PR with a clear description of what changed.

## Questions?

- Open a [GitHub Discussion](https://github.com/maltamsaiusergroup/community-articles/discussions) for general questions.
- Open an [Issue](https://github.com/maltamsaiusergroup/community-articles/issues) for bugs or suggestions.
