from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


class ProfileRow(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    raw_text: Mapped[str] = mapped_column(Text, default="")
    data: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class JobRow(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    company: Mapped[str] = mapped_column(String)
    location: Mapped[str | None] = mapped_column(String, default=None)
    description: Mapped[str] = mapped_column(Text, default="")
    data: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ApplicationRow(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    company: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String, default=None)
    match_score: Mapped[float] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="saved")
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resume_version: Mapped[str] = mapped_column(String, default="")


class Storage:
    """Thin SQLAlchemy repository over SQLite."""

    def __init__(self, database_url: str | None = None):
        settings = get_settings()
        url = database_url or settings.database_url
        self.engine = create_engine(url, connect_args={"check_same_thread": False})
        self.session_factory = sessionmaker(
            bind=self.engine, autoflush=False, expire_on_commit=False
        )
        Base.metadata.create_all(self.engine)

    def session(self) -> Session:
        return self.session_factory()

    # -- profiles --
    def save_profile(self, profile_id: str, raw_text: str, data: dict) -> None:
        with self.session() as sess:
            row = sess.get(ProfileRow, profile_id)
            if row is None:
                row = ProfileRow(id=profile_id, raw_text=raw_text, data=data)
                sess.add(row)
            else:
                row.raw_text = raw_text
                row.data = data
            sess.commit()

    def get_profile(self, profile_id: str) -> dict | None:
        with self.session() as sess:
            row = sess.get(ProfileRow, profile_id)
            if row is None:
                return None
            return {"id": row.id, "raw_text": row.raw_text, "data": row.data}

    # -- jobs --
    def save_jobs(self, jobs: list[dict]) -> None:
        with self.session() as sess:
            for job in jobs:
                row = sess.get(JobRow, job["id"])
                if row is None:
                    row = JobRow(
                        id=job["id"],
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

    def list_jobs(self) -> list[dict]:
        with self.session() as sess:
            rows = sess.query(JobRow).all()
            return [{"id": r.id, **r.data} for r in rows]

    def get_job(self, job_id: str) -> dict | None:
        with self.session() as sess:
            row = sess.get(JobRow, job_id)
            if row is None:
                return None
            return {"id": row.id, **row.data}

    # -- applications --
    def save_application(self, record: dict) -> None:
        with self.session() as sess:
            row = sess.get(ApplicationRow, record["id"])
            if row is None:
                row = ApplicationRow(
                    id=record["id"],
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
                row.company = record["company"]
                row.role = record["role"]
                row.url = record.get("url")
                row.match_score = int(record.get("match_score", 0))
                row.status = record.get("status", "saved")
                row.resume_version = record.get("resume_version", "")
            sess.commit()

    def list_applications(self, status: str | None = None) -> list[dict]:
        with self.session() as sess:
            query = sess.query(ApplicationRow)
            if status:
                query = query.filter(ApplicationRow.status == status)
            rows = query.all()
            return [
                {
                    "id": r.id,
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

    def get_application(self, record_id: str) -> dict | None:
        with self.session() as sess:
            row = sess.get(ApplicationRow, record_id)
            if row is None:
                return None
            return {
                "id": row.id,
                "company": row.company,
                "role": row.role,
                "url": row.url,
                "match_score": float(row.match_score),
                "status": row.status,
                "date": row.date.isoformat(),
                "resume_version": row.resume_version,
            }

    def delete_application(self, record_id: str) -> bool:
        with self.session() as sess:
            row = sess.get(ApplicationRow, record_id)
            if row is None:
                return False
            sess.delete(row)
            sess.commit()
            return True

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
