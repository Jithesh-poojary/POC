"""Vector DB Service - Handles course catalog search using embeddings."""

import json
import os
from models.learning import Course, CourseLevel
from config import settings


class VectorDBService:
    """Service for vector-based course search using ChromaDB."""

    def __init__(self):
        self._collection = None
        self._courses_loaded = False

    async def initialize(self):
        """Initialize the vector database with course catalog."""
        # Using keyword-based search (ChromaDB removed to avoid C++ build dependency)
        self._courses_loaded = False

    async def _load_course_catalog(self):
        """Load course catalog into vector DB."""
        catalog_path = os.path.join(os.path.dirname(__file__), "..", "data", "courses.json")
        
        if not os.path.exists(catalog_path):
            return
        
        with open(catalog_path, "r") as f:
            courses = json.load(f)
        
        documents = []
        metadatas = []
        ids = []
        
        for course in courses:
            doc = f"{course['title']} {course['description']} {' '.join(course['skills_covered'])}"
            documents.append(doc)
            metadatas.append({
                "id": course["id"],
                "title": course["title"],
                "level": course["level"],
                "provider": course["provider"],
                "duration_hours": course["duration_hours"],
            })
            ids.append(course["id"])
        
        if documents:
            self._collection.add(documents=documents, metadatas=metadatas, ids=ids)

    async def search_courses(self, query: str, top_k: int = 5) -> list[Course]:
        """Search for courses matching a query."""
        
        if not self._courses_loaded or not self._collection:
            return await self._fallback_search(query, top_k)
        
        results = self._collection.query(query_texts=[query], n_results=top_k)
        
        courses = []
        if results and results["metadatas"]:
            for metadata in results["metadatas"][0]:
                courses.append(Course(
                    id=metadata["id"],
                    title=metadata["title"],
                    description=f"Course on {metadata['title']}",
                    skills_covered=[query.split()[0]],
                    level=CourseLevel(metadata.get("level", "intermediate")),
                    duration_hours=metadata.get("duration_hours", 10.0),
                    provider=metadata.get("provider", "Unknown"),
                ))
        
        return courses

    async def _fallback_search(self, query: str, top_k: int) -> list[Course]:
        """Fallback search using keyword matching when vector DB unavailable."""
        
        catalog_path = os.path.join(os.path.dirname(__file__), "..", "data", "courses.json")
        
        if not os.path.exists(catalog_path):
            return []
        
        with open(catalog_path, "r") as f:
            courses_data = json.load(f)
        
        query_lower = query.lower()
        matches = []
        
        for course_data in courses_data:
            text = f"{course_data['title']} {course_data['description']} {' '.join(course_data['skills_covered'])}".lower()
            if any(word in text for word in query_lower.split()):
                matches.append(Course(
                    id=course_data["id"],
                    title=course_data["title"],
                    description=course_data["description"],
                    skills_covered=course_data["skills_covered"],
                    level=CourseLevel(course_data["level"]),
                    duration_hours=course_data["duration_hours"],
                    provider=course_data["provider"],
                    url=course_data.get("url"),
                ))
        
        return matches[:top_k]
