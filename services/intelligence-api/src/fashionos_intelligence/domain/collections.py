from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Label = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
Identifier = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]
Objective = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
Rules = Annotated[list[Label], Field(max_length=50)]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=False)


class CreateCollection(Input):
    collection_id: UUID = Field(alias="collectionId")
    name: Label
    objective: Objective
    hard_locks: Rules = Field(default_factory=list, alias="hardLocks")
    allowed_changes: Rules = Field(default_factory=list, alias="allowedChanges")

    @model_validator(mode="after")
    def no_conflicting_rules(self):
        if {x.casefold() for x in self.hard_locks} & {x.casefold() for x in self.allowed_changes}:
            raise ValueError("A hard lock cannot also be an allowed change")
        return self


class UpdateCollection(Input):
    expected_revision: int = Field(alias="expectedRevision", ge=1, strict=True)
    name: Label | None = None
    objective: Objective | None = None
    hard_locks: Rules | None = Field(default=None, alias="hardLocks")
    allowed_changes: Rules | None = Field(default=None, alias="allowedChanges")
    archived: bool | None = Field(default=None, strict=True)

    @model_validator(mode="after")
    def nonempty_patch(self):
        changed = self.model_fields_set - {"expected_revision"}
        if not changed or any(getattr(self, k) is None for k in changed):
            raise ValueError("Provide at least one non-null change")
        return self


class CreateLook(Input):
    look_id: UUID = Field(alias="lookId")
    expected_collection_revision: int = Field(alias="expectedCollectionRevision", ge=1, strict=True)
    name: Label
    source_asset_id: Identifier = Field(alias="sourceAssetId")
    task_id: Identifier | None = Field(default=None, alias="taskId")


class UpdateLook(Input):
    expected_revision: int = Field(alias="expectedRevision", ge=1, strict=True)
    expected_collection_revision: int = Field(alias="expectedCollectionRevision", ge=1, strict=True)
    name: Label
