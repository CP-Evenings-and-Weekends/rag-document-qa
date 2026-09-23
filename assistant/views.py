# assistant/views.py
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
    print("CONTENT:", repr(doc.content))
    print("CHUNKS:", chunks)

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

# assistant/views.py (continued)
from .rag import retrieve_relevant_chunks, generate_rag_response


@api_view(["POST"])
def ask_question(request):
    """RAG endpoint: retrieve relevant chunks, then generate an answer."""
    serializer = AskQuestionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    question = serializer.validated_data["question"]

    # Check that we have documents to search
    if not DocumentChunk.objects.exists():
        return Response({
            "answer": "No study materials have been uploaded yet. Please upload documents first.",
            "sources": [],
        })

    # Steps 1 & 2: Retrieve relevant chunks
    chunks = retrieve_relevant_chunks(question, top_k=5)

    # Step 3: Generate answer using retrieved context
    answer = generate_rag_response(question, chunks)

    return Response({
        "answer": answer,
        "sources": [
            {
                "document": chunk["document_title"],
                "text_preview": chunk["chunk_text"][:200] + "..."
                    if len(chunk["chunk_text"]) > 200
                    else chunk["chunk_text"],
                "relevance_score": round(1 - chunk["distance"], 3),
            }
            for chunk in chunks
        ],
    })