# assistant/models.py
from django.db import models
from pgvector.django import VectorField

# You will write the Document and DocumentChunk models here during the lesson.

class Document(models.Model):
    """A study document uploaded by the user."""
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class DocumentChunk(models.Model):
    """A chunk of a document with its embedding for vector search."""
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="chunks"
    )
    chunk_text = models.TextField() # equivalent of content in Document
    chunk_index = models.IntegerField() # helps us keep track of chunk ordering
    embedding = VectorField(dimensions=768)

    class Meta:
        ordering = ["document", "chunk_index"]

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"