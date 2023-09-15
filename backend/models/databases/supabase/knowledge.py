from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from models.databases.repository import Repository
from models.knowledge import Knowledge
from pydantic import BaseModel


class CreateKnowledgeProperties(BaseModel):
    """Properties that can be received on notification creation"""

    name: Optional[str] = None
    file_id: Optional[UUID] = None
    url: Optional[str] = None
    content_sha1: Optional[str] = None
    owner_id: Optional[UUID] = None
    summary: Optional[str] = None
    extension: str = "txt"

    def dict(self, *args, **kwargs):
        knowledge_dict = super().dict(*args, **kwargs)
        knowledge_dict["owner_id"] = str(knowledge_dict.get("owner_id"))
        if knowledge_dict.get("file_id"):
            knowledge_dict["file_id"] = str(knowledge_dict.get("file_id"))
        return knowledge_dict


class DeleteKnowledgeResponse(BaseModel):
    """Response when deleting a prompt"""

    status: str = "delete"
    knowledge_id: UUID


class Knowledges(Repository):
    def __init__(self, supabase_client):
        self.db = supabase_client

    def insert_knowledge(self, knowledge: CreateKnowledgeProperties) -> Knowledge:
        """
        Add a knowledge
        """
        response = (self.db.from_("knowledge").insert(knowledge.dict()).execute()).data
        return Knowledge(**response[0])

    def remove_knowledge_by_id(
        # todo: remove brain
        self,
        knowledge_id: UUID,
    ) -> DeleteKnowledgeResponse:
        """
        Args:
            knowledge_id (UUID): The id of the knowledge

        Returns:
            str: Status message
        """
        response = (
            self.db.from_("knowledge")
            .delete()
            .filter("id", "eq", knowledge_id)
            .execute()
            .data
        )

        if response == []:
            raise HTTPException(404, "Knowledge not found")

        return DeleteKnowledgeResponse(
            # change to response[0].brain_id and knowledge_id[0].brain_id
            status="deleted",
            knowledge_id=knowledge_id,
        )

    def get_knowledge_by_id(self, knowledge_id: UUID) -> Knowledge:
        """
        Get all the knowledge from a brain
        Args:
            brain_id (UUID): The id of the brain
        """
        knowledge = (
            self.db.from_("knowledge")
            .select("*")
            .filter("knowledge_id", "eq", str(knowledge_id))
            .execute()
        ).data

        return Knowledge(**knowledge[0])
