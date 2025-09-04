# Google Drive to Blog Markdown Guide

This guide documents how to structure Markdown content in Google Drive documents for optimal html rendering on your blog.
The blog engine converts these Drive documents into HTML using Python-Markdown with carefully selected extensions for technical writing.

## Purpose
- Serves as a quick reference for writing blog posts in Google Drive
- Documents supported Markdown features and their HTML output
- Ensures consistent rendering of technical content
- Details special features and extensions available

## Key Features
- Syntax highlighting for code blocks
- Technical writing elements (tables, footnotes)
- Blog-specific formatting
- Automatic line breaks handling
- Table of contents generation
- Definition lists support

---

## Table of Contents
1. [Blockquotes](#blockquotes)
2. [Code Blocks](#code-blocks) (to be added)
3. [Tables](#tables) (to be added)
4. [Lists](#lists) (to be added)
5. [Links and Images](#links-and-images) (to be added)
6. [Advanced Features](#advanced-features) (to be added)

---

## Blockquotes

Blockquotes are used for highlighting quoted text, important notes, or creating callouts in your content. They are created using the `>` character at the start of a line.

***

### Basic Syntax
```
markdown
> This is a blockquote
```
Renders as:
> This is a blockquote

***

### Multiline Blockquotes

You can create multiline blockquotes in several ways:

1. Using `>` on each line:
```
markdown
> Line one of the quote
> Line two of the quote
```
2. Continuation (without `>`):
```
markdown
> First line
This line continues the quote
```
Both methods produce the same HTML output:
```
html
<blockquote><p>Line one of the quote<br>Line two of the quote</p></blockquote>
```

***

### Multiple Blockquotes

To create separate blockquotes, use blank lines between them:
```
markdown
> First blockquote

> Second blockquote
```
Renders as:
> First blockquote

> Second blockquote

***

### Technical Notes

- The HTML output uses `<blockquote>` tags with nested `<p>` tags
- Line breaks within blockquotes are rendered as `<br>` tags due to the `nl2br` extension
- Content following a blockquote line without a blank line is included in the blockquote
- Blank lines are required to end a blockquote and start regular text

[Next sections to be added...]