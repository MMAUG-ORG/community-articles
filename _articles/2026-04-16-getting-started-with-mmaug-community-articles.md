---
title: "Getting Started with the MMAUG Community Articles Platform"
author: "Imoh Etuk"
author_github: "imohweb"
date: 2026-04-16
tags: [community, getting-started, open-source]
description: "Learn how to contribute technical articles to the Malta Microsoft AI User Group community on GitHub."
---

## Introduction

The Malta Microsoft AI User Group (MMAUG) is launching a community-driven technical articles platform. This platform is built on GitHub and powered by GitHub Pages, making it easy for anyone in the community to contribute, review, and publish technical content.

This article explains what the platform is, how it works, and how you can submit your first article.

## Why GitHub for Community Articles?

Using GitHub as our articles platform provides several benefits:

- **Open contribution** — anyone can propose and submit articles via Pull Requests.
- **Transparent review** — the Technical Program Lead and community reviewers can provide feedback directly on the PR.
- **Version history** — every change is tracked, so articles can be updated over time.
- **Automatic publishing** — once an article is merged, GitHub Pages publishes it instantly.
- **Contribution credit** — your GitHub profile shows your contributions to the community.

## How to Submit an Article

### Step 1: Fork the Repository

Go to [maltamsaiusergroup/community-articles](https://github.com/maltamsaiusergroup/community-articles) and click **Fork** to create a copy under your personal GitHub account.

### Step 2: Create Your Article

Clone your fork locally and create a new Markdown file in the `_articles/` directory. Use the naming convention:

```
YYYY-MM-DD-your-article-slug.md
```

For example: `2026-04-16-getting-started-with-azure-ai-foundry.md`

Copy the [article template](https://github.com/maltamsaiusergroup/community-articles/blob/main/article-template.md) and fill in your content.

### Step 3: Add the Frontmatter

Every article needs YAML frontmatter at the top:

```yaml
---
title: "Your Article Title"
author: "Your Name"
author_github: "your-github-username"
date: 2026-04-16
tags: [azure, ai, tutorial]
description: "A short description of your article."
---
```

### Step 4: Open a Pull Request

Push your changes to your fork and open a Pull Request against the `main` branch of `maltamsaiusergroup/community-articles`.

In the PR description, include:

- A brief summary of the article
- The target audience (beginner, intermediate, advanced)
- Any related issues or event sessions

### Step 5: Review and Publish

A reviewer will provide feedback on your article. Once approved and merged, your article will be automatically published on the MMAUG community articles site.

## Topics We Welcome

We welcome articles on a wide range of technical topics, including but not limited to:

- Microsoft Azure (AI, cloud infrastructure, security, DevOps)
- Azure AI Foundry and AI agents
- GitHub Copilot and developer productivity
- Open-source tools and frameworks
- Cloud architecture and best practices
- Hands-on tutorials and walkthroughs
- Conference and meetup session recaps

## Summary

Contributing an article is a great way to share your knowledge, build your public profile, and help grow the MMAUG community. We look forward to your contributions!

## References

- [MMAUG Community Governance](https://maltamsaiusergroup.github.io/maltamsaiusergroup/)
- [MMAUG on Meetup](https://www.meetup.com/malta-microsoft-ai-user-group)
- [MMAUG on LinkedIn](https://www.linkedin.com/company/malta-microsoft-ai-user-group)
