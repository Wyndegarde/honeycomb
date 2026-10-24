# Honeycomb

A personal catalogue of media (books, films, games, etc.) where items are connected to each other by shared themes, forming a graph.

## Language

**Media**:
A single piece of media in the catalogue, such as a book, film, TV show, game or podcast.
_Avoid_: Item, entry, work

**Link**:
An undirected connection between exactly two Media, explaining why they belong together through one or more Themes. A pair of Media has at most one Link, and a Media cannot link to itself.
_Avoid_: Edge, relation, connection

**Theme**:
A named idea or subject that can describe a Media or justify a Link. Names are unique regardless of case.
_Avoid_: Tag, topic, category

**Connecting Theme**:
A Theme attached to a Link. Every Link has at least one.
_Avoid_: Link tag, shared theme

**Review**:
The single rating and optional write-up attached to a Media.
