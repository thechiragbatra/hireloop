from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.core.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    pass


class ProfileRow(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String, index=True, default=None)
    raw_text: Mapped[str] = mapped_column(Text, default="")
    data: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class JobRow(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String, index=True, default=None)
    title: Mapped[str] = mapped_column(String)
    company: Mapped[str] = mapped_column(String)
    location: Mapped[str | None] = mapped_column(String, default=None)
    description: Mapped[str] = mapped_column(Text, default="")
    data: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ApplicationRow(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String, index=True, default=None)
    company: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String, default=None)
    match_score: Mapped[float] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="saved")
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resume_version: Mapped[str] = mapped_column(String, default="")


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


class Storage:
    """Async SQLAlchemy repository over Postgres (Supabase) with SQLite fallback for tests."""

    def __init__(self, database_url: str | None = None, database_url_async: str | None = None):
        self.settings = get_settings()
        self.url = database_url or self.settings.database_url
        self.url_async = database_url_async or self.settings.database_url_async
        self._is_sqlite = _is_sqlite(self.url)

        if self._is_sqlite:
            self.engine = create_engine(self.url, connect_args={"check_same_thread": False})
            self.async_engine = create_async_engine(self.url_async)
        else:
            self.engine = create_engine(self.url)
            self.async_engine = create_async_engine(self.url_async)

        self.session_factory = sessionmaker(
            bind=self.engine, autoflush=False, expire_on_commit=False
        )
        self.async_session_factory = async_sessionmaker(
            bind=self.async_engine, autoflush=False, expire_on_commit=False
        )
        self.create_all()

    def create_all(self) -> None:
        Base.metadata.create_all(self.engine)

    def session(self):
        return self.session_factory()

    async def async_session(self) -> AsyncSession:
        return self.async_session_factory()

    # -- helpers --

    def _current_user_id(self) -> str | None:
        # In async contexts, the user_id is passed explicitly.
        return None

    # -- profiles --
    def save_profile(
        self, profile_id: str, raw_text: str, data: dict, user_id: str | None = None
    ) -> None:
        with self.session() as sess:
            row = sess.get(ProfileRow, profile_id)
            if row is None:
                row = ProfileRow(id=profile_id, user_id=user_id, raw_text=raw_text, data=data)
                sess.add(row)
            else:
                row.user_id = user_id or row.user_id
                row.raw_text = raw_text
                row.data = data
            sess.commit()

    def get_profile(self, profile_id: str, user_id: str | None = None) -> dict | None:
        with self.session() as sess:
            row = sess.get(ProfileRow, profile_id)
            if row is None:
                return None
            if user_id is not None and row.user_id is not None and row.user_id != user_id:
                return None
            return {
                "id": row.id,
                "user_id": row.user_id,
                "raw_text": row.raw_text,
                "data": row.data,
            }

    def list_profiles(self, user_id: str | None = None) -> list[dict]:
        with self.session() as sess:
            query = sess.query(ProfileRow)
            if user_id is not None:
                query = query.filter(ProfileRow.user_id == user_id)
            rows = query.all()
            return [
                {"id": r.id, "user_id": r.user_id, "raw_text": r.raw_text, "data": r.data}
                for r in rows
            ]

    # -- jobs --
    def save_jobs(self, jobs: list[dict], user_id: str | None = None) -> None:
        with self.session() as sess:
            for job in jobs:
                row = sess.get(JobRow, job["id"])
                if row is None:
                    row = JobRow(
                        id=job["id"],
                        user_id=user_id,
                        title=job.get("title", ""),
                        company=job.get("company", ""),
                        location=job.get("location"),
                        description=job.get("description", ""),
                        data=job,
                    )
                    sess.add(row)
                else:
                    row.title = job.get("title", row.title)
                    row.company = job.get("company", row.company)
                    row.description = job.get("description", row.description)
                    row.data = job
            sess.commit()

    def list_jobs(self, user_id: str | None = None) -> list[dict]:
        with self.session() as sess:
            query = sess.query(JobRow)
            if user_id is not None:
                query = query.filter(JobRow.user_id == user_id)
            rows = query.all()
            return [{"id": r.id, "user_id": r.user_id, **r.data} for r in rows]

    def get_job(self, job_id: str, user_id: str | None = None) -> dict | None:
        with self.session() as sess:
            row = sess.get(JobRow, job_id)
            if row is None:
                return None
            if user_id is not None and row.user_id is not None and row.user_id != user_id:
                return None
            return {"id": row.id, "user_id": row.user_id, **row.data}

    # -- applications --
    def save_application(self, record: dict, user_id: str | None = None) -> None:
        with self.session() as sess:
            row = sess.get(ApplicationRow, record["id"])
            if row is None:
                row = ApplicationRow(
                    id=record["id"],
                    user_id=user_id,
                    company=record["company"],
                    role=record["role"],
                    url=record.get("url"),
                    match_score=int(record.get("match_score", 0)),
                    status=record.get("status", "saved"),
                    resume_version=record.get("resume_version", ""),
                    date=record.get("date", datetime.utcnow()),
                )
                sess.add(row)
            else:
                row.user_id = user_id or row.user_id
                row.company = record["company"]
                row.role = record["role"]
                row.url = record.get("url")
                row.match_score = int(record.get("match_score", 0))
                row.status = record.get("status", "saved")
                row.resume_version = record.get("resume_version", "")
            sess.commit()

    def list_applications(
        self, user_id: str | None = None, status: str | None = None
    ) -> list[dict]:
        with self.session() as sess:
            query = sess.query(ApplicationRow)
            if user_id is not None:
                query = query.filter(ApplicationRow.user_id == user_id)
            if status:
                query = query.filter(ApplicationRow.status == status)
            rows = query.all()
            return [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "company": r.company,
                    "role": r.role,
                    "url": r.url,
                    "match_score": float(r.match_score),
                    "status": r.status,
                    "date": r.date.isoformat(),
                    "resume_version": r.resume_version,
                }
                for r in rows
            ]

    def get_application(self, record_id: str, user_id: str | None = None) -> dict | None:
        with self.session() as sess:
            row = sess.get(ApplicationRow, record_id)
            if row is None:
                return None
            if user_id is not None and row.user_id is not None and row.user_id != user_id:
                return None
            return {
                "id": row.id,
                "user_id": row.user_id,
                "company": row.company,
                "role": row.role,
                "url": row.url,
                "match_score": float(row.match_score),
                "status": row.status,
                "date": row.date.isoformat(),
                "resume_version": row.resume_version,
            }

    def delete_application(self, record_id: str, user_id: str | None = None) -> bool:
        with self.session() as sess:
            row = sess.get(ApplicationRow, record_id)
            if row is None:
                return False
            if user_id is not None and row.user_id is not None and row.user_id != user_id:
                return False
            sess.delete(row)
            sess.commit()
            return True

    def delete_user_data(self, user_id: str) -> None:
        """Delete all data for a user (GDPR / 'delete my account')."""
        with self.session() as sess:
            sess.query(ApplicationRow).filter(ApplicationRow.user_id == user_id).delete()
            sess.query(JobRow).filter(JobRow.user_id == user_id).delete()
            sess.query(ProfileRow).filter(ProfileRow.user_id == user_id).delete()
            sess.commit()

    def clear(self) -> None:
        with self.session() as sess:
            sess.query(ApplicationRow).delete()
            sess.query(JobRow).delete()
            sess.query(ProfileRow).delete()
            sess.commit()


_storage: Storage | None = None


def get_storage() -> Storage:
    global _storage
    if _storage is None:
        _storage = Storage()
    return _storage
