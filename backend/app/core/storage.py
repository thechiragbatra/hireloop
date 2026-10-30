"""Small durable SQLAlchemy store for profiles, public jobs and applications."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import JSON, String, create_engine, delete, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class StoredRecord(Base):
    __tablename__ = "hireloop_records"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    kind: Mapped[str] = mapped_column(String(32), index=True)
    owner_id: Mapped[str] = mapped_column(String(255), default="local", index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)


class Storage:
    """Persistent owner-scoped records; SQLite for local runs, Postgres in production."""

    def __init__(self, database_url: str | None = None):
        if database_url is None:
            from app.core.config import get_settings

            database_url = get_settings().database_url
        database_url = database_url or "sqlite:///./data/hireloop.db"
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        if database_url.startswith("sqlite:///") and ":memory:" not in database_url:
            Path(database_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        options: dict[str, Any] = {}
        if database_url.startswith("sqlite"):
            options["connect_args"] = {"check_same_thread": False}
            if database_url.endswith(":memory:"):
                options["poolclass"] = StaticPool
        self.engine = create_engine(database_url, **options)
        self._sessions = sessionmaker(self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)

    def create_all(self) -> None:
        Base.metadata.create_all(self.engine)

    def _put(self, kind: str, record_id: str, payload: dict[str, Any], owner_id: str | None):
        owner = owner_id or "local"
        payload = jsonable_encoder(payload)
        with self._sessions() as session:
            row = session.get(StoredRecord, record_id)
            if row and (row.kind != kind or row.owner_id != owner):
                raise ValueError("Record ID is already in use")
            if row:
                row.payload = payload
            else:
                session.add(StoredRecord(id=record_id, kind=kind, owner_id=owner, payload=payload))
            session.commit()
        return payload

    def _get(self, kind: str, record_id: str, owner_id: str | None = None):
        with self._sessions() as session:
            row = session.get(StoredRecord, record_id)
            if (
                not row
                or row.kind != kind
                or (owner_id is not None and row.owner_id not in {owner_id, "*"})
            ):
                return None
            return dict(row.payload)

    def save_profile(self, profile_id, raw_text=None, profile_data=None, user_id=None):
        data = profile_data or {}
        self._put("profile", profile_id, {"id": profile_id, "data": data}, user_id)
        return {"profile_id": profile_id}

    def get_profile(self, profile_id, user_id=None):
        return self._get("profile", profile_id, user_id)

    def save_job(self, job_id, job_data, user_id=None):
        self._put("job", job_id, dict(job_data), "*")
        return job_data

    def save_jobs(self, jobs, user_id=None):
        for job in jobs:
            data = dict(job) if isinstance(job, dict) else job.model_dump(mode="json")
            if data.get("id"):
                self.save_job(data["id"], data, user_id)
        return jobs

    def get_job(self, job_id, user_id=None):
        return self._get("job", job_id, user_id)

    def list_jobs(self, user_id=None):
        with self._sessions() as session:
            query = select(StoredRecord).where(StoredRecord.kind == "job")
            if user_id is not None:
                query = query.where(StoredRecord.owner_id.in_([user_id, "*"]))
            return [dict(row.payload) for row in session.scalars(query)]

    def save_application(self, record, user_id=None):
        data = dict(record) if isinstance(record, dict) else record.model_dump(mode="json")
        self._put("application", data["id"], data, user_id)
        return data

    def list_applications(self, user_id=None, status=None):
        with self._sessions() as session:
            query = select(StoredRecord).where(StoredRecord.kind == "application")
            if user_id is not None:
                query = query.where(StoredRecord.owner_id == user_id)
            rows = [dict(row.payload) for row in session.scalars(query)]
            return [row for row in rows if status is None or row.get("status") == status]

    def get_application(self, record_id, user_id=None):
        return self._get("application", record_id, user_id)

    def delete_application(self, record_id: str, user_id: str | None = None) -> bool:
        with self._sessions() as session:
            row = session.get(StoredRecord, record_id)
            if (
                not row
                or row.kind != "application"
                or (user_id is not None and row.owner_id != user_id)
            ):
                return False
            session.delete(row)
            session.commit()
            return True

    def delete_profile(self, profile_id: str, user_id: str | None = None) -> bool:
        with self._sessions() as session:
            row = session.get(StoredRecord, profile_id)
            if (
                not row
                or row.kind != "profile"
                or (user_id is not None and row.owner_id != user_id)
            ):
                return False
            session.delete(row)
            session.commit()
            return True

    def delete_user_data(self, user_id: str) -> int:
        with self._sessions() as session:
            rows = list(
                session.scalars(
                    select(StoredRecord).where(
                        StoredRecord.owner_id == user_id,
                        StoredRecord.kind.in_(["profile", "application"]),
                    )
                )
            )
            for row in rows:
                session.delete(row)
            session.commit()
            return len(rows)

    def clear(self):
        Base.metadata.create_all(self.engine)
        with self._sessions() as session:
            session.execute(delete(StoredRecord))
            session.commit()


_storage: Storage | None = None


def get_storage() -> Storage:
    global _storage
    if _storage is None:
        _storage = Storage()
    return _storage
