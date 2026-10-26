from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.core.storage import get_storage
from app.models.schemas import Job
from app.services.chunker import ProfileChunker
from app.services.faithfulness import FaithfulnessService
from app.services.job_sources import ADAPTERS
from app.services.matcher import Matcher
from app.services.parser import ResumeParser
from app.services.retriever import HybridRetriever
from app.services.tailor import TailorService


class PipelineState(TypedDict, total=False):
    content: bytes
    profile_id: str
    filename: str
    raw_text: str
    user_id: str | None
    filters: dict[str, Any]
    profile: Any
    jobs: list[dict]
    matches: list[dict]
    selected_job: Job | dict | None
    retrieved_chunks: list[dict]
    tailored: Any
    faithfulness: Any
    status: str


def build_graph(
    parser: ResumeParser | None = None,
    matcher: Matcher | None = None,
    tailor: TailorService | None = None,
    verifier: FaithfulnessService | None = None,
    chunker: ProfileChunker | None = None,
    retriever: HybridRetriever | None = None,
):
    parser = parser or ResumeParser()
    matcher = matcher or Matcher()
    chunker = chunker or ProfileChunker()
    tailor = tailor or TailorService(chunker=chunker)
    verifier = verifier or FaithfulnessService(chunker=chunker)
    retriever = retriever or HybridRetriever()
    storage = get_storage()

    async def node_parse(state: PipelineState) -> PipelineState:
        content = state.get("content", b"")
        filename = state.get("filename", "resume.pdf")
        user_id = state.get("user_id")
        profile, raw_text = parser.parse(filename, content)
        profile_id = profile.id
        storage.save_profile(profile_id, raw_text, profile.model_dump(), user_id=user_id)
        return {
            "profile_id": profile_id,
            "user_id": user_id,
            "raw_text": raw_text,
            "profile": profile.model_dump(),
            "status": "parsed",
        }

    async def node_fetch_jobs(state: PipelineState) -> PipelineState:
        filters: dict[str, Any] = dict(state.get("filters", {}))
        profile = state.get("profile")
        user_id = state.get("user_id")
        if profile and not filters.get("query"):
            try:
                from app.models.schemas import Profile as ProfileSchema

                prof = ProfileSchema(**profile)
                skills = prof.skills or []
                if skills:
                    filters["query"] = " ".join(skills[:5])
            except Exception:
                pass
        fetched: list[dict] = []
        for adapter in ADAPTERS.values():
            jobs = await adapter.fetch(filters)
            fetched.extend([j.model_dump() for j in jobs])
        storage.save_jobs(fetched, user_id=user_id)
        return {"jobs": fetched, "user_id": user_id, "status": "jobs_fetched"}

    async def node_match(state: PipelineState) -> PipelineState:
        profile = state.get("profile")
        jobs = state.get("jobs", [])
        user_id = state.get("user_id")
        if not profile:
            return {"matches": [], "user_id": user_id, "status": "no_profile"}
        from app.models.schemas import Profile as ProfileSchema

        prof = ProfileSchema(**profile)
        job_objs = [Job(**j) for j in jobs]
        results = await matcher.match(prof, job_objs)
        out = [r.model_dump() for r in results]
        return {"matches": out, "user_id": user_id, "status": "matched"}

    async def node_retrieve_context(state: PipelineState) -> PipelineState:
        profile = state.get("profile")
        job = state.get("selected_job") or (state.get("jobs") or [{}])[0]
        user_id = state.get("user_id")
        if not profile or not job:
            return {"retrieved_chunks": [], "user_id": user_id, "status": "nothing_to_retrieve"}
        from app.models.schemas import Profile as ProfileSchema

        prof = ProfileSchema(**profile)
        job_obj = Job(**job) if isinstance(job, dict) else job
        chunks = chunker.chunk(prof)
        retriever.build_index([(c["id"], c["text"]) for c in chunks])
        results = retriever.search_hybrid(job_obj.description, top_k=20)
        chunk_map = {c["id"]: c for c in chunks}
        retrieved = [chunk_map[cid] for cid, _ in results if cid in chunk_map]
        return {"retrieved_chunks": retrieved, "user_id": user_id, "status": "context_retrieved"}

    async def node_tailor(state: PipelineState) -> PipelineState:
        profile = state.get("profile")
        jobs = state.get("jobs", [])
        user_id = state.get("user_id")
        job = state.get("selected_job") or (jobs[0] if jobs else None)
        if not profile or job is None:
            return {"tailored": None, "user_id": user_id, "status": "no_jobs"}
        from app.models.schemas import Profile as ProfileSchema

        prof = ProfileSchema(**profile)
        job_obj = Job(**job) if isinstance(job, dict) else job
        chunks = state.get("retrieved_chunks") or chunker.chunk(prof)
        tailored = await tailor.tailor(prof, job_obj, chunks)
        return {"tailored": tailored.model_dump(), "user_id": user_id, "status": "tailored"}

    async def node_verify(state: PipelineState) -> PipelineState:
        profile = state.get("profile")
        tailored = state.get("tailored")
        user_id = state.get("user_id")
        if not profile or not tailored:
            return {"faithfulness": None, "user_id": user_id, "status": "nothing_to_verify"}
        from app.models.schemas import Profile as ProfileSchema
        from app.models.schemas import TailoredResume

        prof = ProfileSchema(**profile)
        resume = TailoredResume(**tailored)
        report = await verifier.verify(prof, resume)
        return {"faithfulness": report.model_dump(), "user_id": user_id, "status": "verified"}

    graph = StateGraph(PipelineState)
    graph.add_node("parse", node_parse)
    graph.add_node("fetch_jobs", node_fetch_jobs)
    graph.add_node("match", node_match)
    graph.add_node("retrieve_context", node_retrieve_context)
    graph.add_node("tailor", node_tailor)
    graph.add_node("verify", node_verify)
    graph.add_edge("parse", "fetch_jobs")
    graph.add_edge("fetch_jobs", "match")
    graph.add_edge("match", "retrieve_context")
    graph.add_edge("retrieve_context", "tailor")
    graph.add_edge("tailor", "verify")
    graph.add_edge("verify", END)
    graph.set_entry_point("parse")
    return graph.compile()
