import requests

BASE_URL = "http://localhost:8000/api/documents/"


documents = [
    {
        "title": "Django Notes",
        "content": """Django is a Python web framework designed to help developers build web applications quickly.

Django follows the model-template-view architecture and includes many features for building web applications.

Django provides an object-relational mapper, commonly called the ORM, which allows developers to interact with a database using Python objects instead of writing every SQL query manually.

Django also provides URL routing, views, templates, forms, authentication, and an administrative interface.

A Django project can contain multiple applications, with each application organizing a specific area of functionality.

Django is commonly used to build websites, APIs, and other server-side applications."""
    },
    {
        "title": "PostgreSQL Notes",
        "content": """PostgreSQL is an open-source relational database management system.

PostgreSQL uses SQL to create, read, update, and delete data stored in tables.

It supports transactions, indexes, constraints, foreign keys, and many advanced database features.

PostgreSQL can be extended with additional functionality through extensions.

One useful extension is pgvector, which allows PostgreSQL to store vector embeddings and perform similarity searches.

Vector similarity is useful for applications involving semantic search and retrieval augmented generation.

PostgreSQL is often used as the database behind web applications and APIs."""
    },
]


for document in documents:
    print(f"Uploading: {document['title']}")

    response = requests.post(
        BASE_URL,
        json=document,
        timeout=120,
    )

    print(f"Status: {response.status_code}")

    if response.ok:
        print(response.json())
        print("Upload successful!\n")
    else:
        print(response.text)
        print("Upload failed!\n")

# {
#   "title": "Django Notes",
#   "content": "Django is a Python web framework designed to help developers build web applications quickly.\n\nDjango follows the model-template-view architecture and includes many features for building web applications.\n\nDjango provides an object-relational mapper, commonly called the ORM, which allows developers to interact with a database using Python objects instead of writing every SQL query manually.\n\nDjango also provides URL routing, views, templates, forms, authentication, and an administrative interface."
# }

# {
#   "title": "PostgreSQL Notes",
#   "content": "PostgreSQL is an open-source relational database management system.\n\nPostgreSQL uses SQL to create, read, update, and delete data stored in tables.\n\nIt supports transactions, indexes, constraints, foreign keys, and many advanced database features.\n\nPostgreSQL can be extended with additional functionality through extensions.\n\nOne useful extension is pgvector, which allows PostgreSQL to store vector embeddings and perform similarity searches."
# }