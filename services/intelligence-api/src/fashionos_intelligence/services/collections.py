"""Workspace-scoped draft organization. No approval or source mutation occurs here."""
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from fashionos_intelligence.domain.collections import CreateCollection, CreateLook, UpdateCollection, UpdateLook
from fashionos_intelligence.persistence.db import (
    AssetRow, CollectionEventRow, CollectionRow, LookRow, TaskRow, WorkspaceMemberRow,
)


class CollectionError(Exception):
    def __init__(self, code: str, status: int = 409):
        self.code, self.status = code, status
        super().__init__(code)


def collection_data(row):
    return {"collectionId": row.collection_id, "workspaceId": row.workspace_id,
            "name": row.name, "objective": row.objective, "hardLocks": list(row.hard_locks),
            "allowedChanges": list(row.allowed_changes), "revision": row.revision, "archived": row.archived}


def look_data(row):
    return {"lookId": row.look_id, "collectionId": row.collection_id, "workspaceId": row.workspace_id,
            "name": row.name, "sourceAssetId": row.source_asset_id, "taskId": row.task_id, "revision": row.revision}


class CollectionService:
    def __init__(self, sessions):
        self.sessions = sessions

    def provision_member(self, workspace_id, actor_id, role):
        """Trusted deployment operation; never exposed as a customer endpoint."""
        if role not in {"viewer", "contributor", "approver", "admin"}:
            raise ValueError("Invalid workspace role")
        with self.sessions.begin() as s:
            s.merge(WorkspaceMemberRow(workspace_id=workspace_id, actor_id=actor_id, role=role))

    def _authorize(self, s, workspace, actor, *, write=False):
        member = s.get(WorkspaceMemberRow, (workspace, actor))
        if not member:
            raise CollectionError("WORKSPACE_ACCESS_DENIED", 403)
        if member.role not in {"viewer", "contributor", "approver", "admin"}:
            raise CollectionError("FORBIDDEN", 403)
        if write and member.role == "viewer":
            raise CollectionError("FORBIDDEN", 403)
        return member.role

    def _collection(self, s, workspace, collection_id):
        row = s.get(CollectionRow, collection_id)
        if row is None or row.workspace_id != workspace:
            raise CollectionError("COLLECTION_NOT_FOUND", 404)
        return row

    def _event(self, s, workspace, collection_id, actor, kind, subject, revision):
        s.add(CollectionEventRow(event_id=str(uuid4()), workspace_id=workspace,
                                collection_id=collection_id, actor_id=actor, event_type=kind,
                                subject_id=subject, revision=revision))

    def _advance_parent(self, s, row, expected, *, require_active=True):
        conditions = [CollectionRow.collection_id == row.collection_id,
                      CollectionRow.workspace_id == row.workspace_id, CollectionRow.revision == expected]
        if require_active:
            conditions.append(CollectionRow.archived.is_(False))
        result = s.execute(update(CollectionRow).where(*conditions).values(revision=expected + 1),
                           execution_options={"synchronize_session": False})
        if result.rowcount != 1:
            raise CollectionError("STATE_CONFLICT")
        s.refresh(row)

    def create(self, workspace, actor, payload: CreateCollection):
        collection_id = str(payload.collection_id)
        values = dict(workspace_id=workspace, name=payload.name, objective=payload.objective,
                      hard_locks=payload.hard_locks, allowed_changes=payload.allowed_changes)
        try:
            with self.sessions.begin() as s:
                self._authorize(s, workspace, actor, write=True)
                existing = s.get(CollectionRow, collection_id)
                if existing:
                    if existing.revision == 1 and all(getattr(existing, k) == v for k, v in values.items()):
                        return collection_data(existing)
                    raise CollectionError("STATE_CONFLICT")
                row = CollectionRow(collection_id=collection_id, revision=1, archived=False, **values)
                s.add(row)
                self._event(s, workspace, collection_id, actor, "collection.created", collection_id, 1)
                s.flush()
                return collection_data(row)
        except IntegrityError as exc:
            raise CollectionError("STATE_CONFLICT") from exc

    def list(self, workspace, actor, *, cursor=None, limit=50):
        if not 1 <= limit <= 100:
            raise CollectionError("INVALID_REQUEST", 422)
        with self.sessions() as s:
            if self._authorize(s, workspace, actor) == "viewer":
                return {"items": [], "nextCursor": None}
            q = select(CollectionRow).where(CollectionRow.workspace_id == workspace)
            if cursor:
                q = q.where(CollectionRow.collection_id > cursor)
            rows = s.scalars(q.order_by(CollectionRow.collection_id).limit(limit + 1)).all()
            return {"items": [collection_data(r) for r in rows[:limit]],
                    "nextCursor": rows[limit - 1].collection_id if len(rows) > limit else None}

    def get(self, workspace, actor, collection_id):
        with self.sessions() as s:
            if self._authorize(s, workspace, actor) == "viewer":
                raise CollectionError("COLLECTION_NOT_FOUND", 404)
            return collection_data(self._collection(s, workspace, collection_id))

    def update(self, workspace, actor, collection_id, payload: UpdateCollection):
        with self.sessions.begin() as s:
            self._authorize(s, workspace, actor, write=True)
            row = self._collection(s, workspace, collection_id)
            values = payload.model_dump(exclude_unset=True, exclude={"expected_revision"})
            locks = values.get("hard_locks", row.hard_locks)
            changes = values.get("allowed_changes", row.allowed_changes)
            if {x.casefold() for x in locks} & {x.casefold() for x in changes}:
                raise CollectionError("INVALID_LOCK_CONFIGURATION", 422)
            self._advance_parent(s, row, payload.expected_revision, require_active=False)
            for k, v in values.items():
                setattr(row, k, v)
            self._event(s, workspace, collection_id, actor, "collection.updated", collection_id, row.revision)
            s.flush()
            return collection_data(row)

    def _source_and_task(self, s, workspace, source_id, task_id):
        source = s.get(AssetRow, source_id)
        if source is None or source.workspace_id != workspace:
            raise CollectionError("SOURCE_NOT_FOUND", 404)
        if source.rights_status != "authorized":
            raise CollectionError("SOURCE_RIGHTS_UNKNOWN" if source.rights_status == "unknown" else "SOURCE_REFERENCE_ONLY", 409)
        if source.role not in {"primary", "production"}:
            raise CollectionError("SOURCE_REFERENCE_ONLY")
        if task_id:
            task = s.get(TaskRow, task_id)
            if task is None or task.workspace_id != workspace:
                raise CollectionError("TASK_NOT_FOUND", 404)

    def create_look(self, workspace, actor, collection_id, payload: CreateLook):
        look_id = str(payload.look_id)
        values = dict(workspace_id=workspace, collection_id=collection_id, name=payload.name,
                      source_asset_id=payload.source_asset_id, task_id=payload.task_id)
        try:
            with self.sessions.begin() as s:
                self._authorize(s, workspace, actor, write=True)
                parent = self._collection(s, workspace, collection_id)
                self._source_and_task(s, workspace, payload.source_asset_id, payload.task_id)
                existing = s.get(LookRow, look_id)
                if existing:
                    if existing.revision == 1 and all(getattr(existing, k) == v for k, v in values.items()):
                        return look_data(existing)
                    raise CollectionError("STATE_CONFLICT")
                self._advance_parent(s, parent, payload.expected_collection_revision)
                row = LookRow(look_id=look_id, revision=1, **values)
                s.add(row)
                self._event(s, workspace, collection_id, actor, "look.created", look_id, parent.revision)
                s.flush()
                return look_data(row)
        except IntegrityError as exc:
            raise CollectionError("STATE_CONFLICT") from exc

    def looks(self, workspace, actor, collection_id, *, cursor=None, limit=50):
        if not 1 <= limit <= 100:
            raise CollectionError("INVALID_REQUEST", 422)
        with self.sessions() as s:
            if self._authorize(s, workspace, actor) == "viewer":
                raise CollectionError("COLLECTION_NOT_FOUND", 404)
            self._collection(s, workspace, collection_id)
            q = select(LookRow).where(LookRow.workspace_id == workspace, LookRow.collection_id == collection_id)
            if cursor:
                q = q.where(LookRow.look_id > cursor)
            rows = s.scalars(q.order_by(LookRow.look_id).limit(limit + 1)).all()
            return {"items": [look_data(r) for r in rows[:limit]],
                    "nextCursor": rows[limit - 1].look_id if len(rows) > limit else None}

    def get_look(self, workspace, actor, collection_id, look_id):
        with self.sessions() as s:
            if self._authorize(s, workspace, actor) == "viewer":
                raise CollectionError("LOOK_NOT_FOUND", 404)
            self._collection(s, workspace, collection_id)
            row = self._look(s, workspace, collection_id, look_id)
            return look_data(row)

    def _look(self, s, workspace, collection_id, look_id):
        row = s.get(LookRow, look_id)
        if row is None or row.workspace_id != workspace or row.collection_id != collection_id:
            raise CollectionError("LOOK_NOT_FOUND", 404)
        return row

    def update_look(self, workspace, actor, collection_id, look_id, payload: UpdateLook):
        with self.sessions.begin() as s:
            self._authorize(s, workspace, actor, write=True)
            parent = self._collection(s, workspace, collection_id)
            row = self._look(s, workspace, collection_id, look_id)
            self._advance_parent(s, parent, payload.expected_collection_revision)
            result = s.execute(update(LookRow).where(LookRow.look_id == look_id,
                               LookRow.workspace_id == workspace, LookRow.collection_id == collection_id,
                               LookRow.revision == payload.expected_revision).values(
                                   name=payload.name, revision=payload.expected_revision + 1),
                               execution_options={"synchronize_session": False})
            if result.rowcount != 1:
                raise CollectionError("STATE_CONFLICT")
            s.refresh(row)
            self._event(s, workspace, collection_id, actor, "look.updated", look_id, parent.revision)
            return look_data(row)
