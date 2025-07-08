---
layout: default
title: Categories and Tags Index
---

<h1>Cross Index: Categories and Tags</h1>

{% assign cats = site.categories | sort %}
{% assign tags = site.tags | sort %}

<table>
  <thead>
    <tr>
      <th>Category</th>
      <th>Tag</th>
      <th>Posts</th>
    </tr>
  </thead>
  <tbody>
    {% for category in cats %}
      {% for tag in tags %}
        {% assign cross_posts = site.posts | where_exp: "post", "post.categories contains category[0] and post.tags contains tag[0]" %}
        {% if cross_posts.size > 0 %}
        <tr>
          <td>{{ category[0] }}</td>
          <td>{{ tag[0] }}</td>
          <td>
            {% for post in cross_posts %}
              <a href="{{ post.url }}">{{ post.title }}</a>{% unless forloop.last %}, {% endunless %}
            {% endfor %}
          </td>
        </tr>
        {% endif %}
      {% endfor %}
    {% endfor %}
  </tbody>
</table>

