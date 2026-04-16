---
layout: default
title: MMAUG Community Articles
hide_tagline: false
---

Welcome to the **Malta Microsoft AI User Group** community articles platform. Here you will find technical articles written by MMAUG community members.

Want to contribute? Read the [Contributing Guide](https://github.com/maltamsaiusergroup/community-articles/blob/main/CONTRIBUTING.md) or [propose an article](https://github.com/maltamsaiusergroup/community-articles/issues/new?template=article-proposal.yml).

---

{% assign sorted_articles = site.articles | sort: "date" | reverse %}

{% if sorted_articles.size > 0 %}
<ul class="article-list">
  {% for article in sorted_articles %}
  <li class="article-card">
    <h3><a href="{{ article.url | relative_url }}">{{ article.title }}</a></h3>
    <p class="article-meta">
      By <strong>
        {% if article.author_github %}
          <a href="https://github.com/{{ article.author_github }}">{{ article.author }}</a>
        {% else %}
          {{ article.author }}
        {% endif %}
      </strong>
      &middot; {{ article.date | date: "%B %d, %Y" }}
    </p>
    {% if article.tags %}
      <p class="article-tags">
        {% for tag in article.tags %}
          <span class="tag">{{ tag }}</span>
        {% endfor %}
      </p>
    {% endif %}
    {% if article.description %}
      <p>{{ article.description }}</p>
    {% endif %}
  </li>
  {% endfor %}
</ul>
{% else %}
<p>No articles published yet. Be the first to <a href="https://github.com/maltamsaiusergroup/community-articles/blob/main/CONTRIBUTING.md">contribute</a>!</p>
{% endif %}
