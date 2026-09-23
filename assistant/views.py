from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Document, DocumentChunk
from .serializers import (
    DocumentSerializer,
    DocumentCreateSerializer,
    AskQuestionSerializer,
)
from .chunking import chunk_text
from .embeddings import generate_embeddings_batch


@api_view(["GET", "POST"])
def document_list(request):
    """List all documents or upload a new one."""
    if request.method == "GET":
        documents = Document.objects.all().order_by("-created_at")
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

    # POST: Create a new document, chunk it, and generate embeddings
    serializer = DocumentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Save the document
    doc = serializer.save()

    # Chunk the content
    chunks = chunk_text(doc.content)

    if not chunks:
        return Response(
            DocumentSerializer(doc).data,
            status=status.HTTP_201_CREATED,
        )

    # Generate embeddings for all chunks in one batch call
    embeddings = generate_embeddings_batch(chunks)

    # Create chunk objects
    chunk_objects = [
        DocumentChunk(
            document=doc,
            chunk_text=text,
            chunk_index=idx,
            embedding=emb,
        )
        for idx, (text, emb) in enumerate(zip(chunks, embeddings))
    ]
    DocumentChunk.objects.bulk_create(chunk_objects)

    return Response(
        DocumentSerializer(doc).data,
        status=status.HTTP_201_CREATED,
    )