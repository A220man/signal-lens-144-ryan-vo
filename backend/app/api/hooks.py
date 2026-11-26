from fastapi import APIRouter, File, HTTPException, UploadFile
from typing import List, Optional
from pydantic import BaseModel, Field


# Transcript JSONL entry model
class TranscriptEntry(BaseModel):
    """A single entry from a transcript JSONL log."""
    prompt_id: str = Field(..., description="Unique identifier for the prompt session")
    session_type: str = Field(..., description="Either 'main' or 'subagent'")
    event_type: str = Field(..., description="Event type: 'open', 'router', 'playbook', 'principle'")
    timestamp: Optional[float] = Field(None, description="Unix timestamp of the event")
    prompt_text: Optional[str] = Field(None, description="The prompt text")
    model_name: Optional[str] = Field(None, description="The model name used")
    metadata: Optional[dict] = Field(None, description="Additional metadata")


# Aggregated metrics for effectiveness analysis
class OpensMetrics(BaseModel):
    """Per-session-type opens metrics per 100 prompts."""
    session_type: str = Field(..., description="'main' or 'subagent'")
    total_prompts: int = Field(..., description="Total number of prompts")
    open_count: int = Field(..., description="Number of 'open' events")
    opens_per_100: float = Field(..., description="Open rate per 100 prompts")
    router_count: int = Field(0, description="Number of 'router' events")
    playbook_count: int = Field(0, description="Number of 'playbook' events")
    principle_count: int = Field(0, description="Number of 'principle' events")


# In-memory store for transcript data and computed metrics
_transcript_store: List[TranscriptEntry] = []
_metrics_store: List[OpensMetrics] = []


def reset_hook_store():
    """Reset the in-memory hook transcript and metrics stores.
    
    Useful for test isolation.
    """
    global _transcript_store, _metrics_store
    _transcript_store = []
    _metrics_store = []


def compare_metrics(
    before: List[OpensMetrics], after: List[OpensMetrics]
) -> dict:
    """Compute before/after delta for hook effectiveness metrics.
    
    Returns dict mapping session_type to dict of field deltas.
    Only includes fields that changed (non-zero delta).
    Numeric fields: total_prompts, open_count, opens_per_100, router_count,
    playbook_count, principle_count. session_type is excluded from delta.
    """
    numeric_fields = ["total_prompts", "open_count", "opens_per_100",
                      "router_count", "playbook_count", "principle_count"]
    
    delta: dict[str, dict[str, float | int]] = {}
    
    # Track which session types appear in before
    before_types = {m.session_type for m in before}
    
    # Build a lookup from after by session_type
    after_by_type: dict[str, OpensMetrics] = {}
    for m in after:
        after_by_type[m.session_type] = m
    
    # Process each session type that appears in either before or after
    all_types = before_types | {m.session_type for m in after}
    
    for st in all_types:
        changes: dict[str, float | int] = {}
        
        before_m = next((m for m in before if m.session_type == st), None)
        after_m = after_by_type.get(st)
        
        if before_m is None:
            # Session type is new (only in after) - diff = after - 0 = after values
            for field in numeric_fields:
                if field in after_m.model_fields:
                    changes[field] = getattr(after_m, field)
        elif after_m is None:
            # Session type disappeared (only in before) - diff = 0 - before = -before values
            for field in numeric_fields:
                if field in before_m.model_fields:
                    changes[field] = -getattr(before_m, field)
        else:
            # Session type in both before and after - compute diffs
            for field in numeric_fields:
                if field in before_m.model_fields and field in after_m.model_fields:
                    before_val = getattr(before_m, field)
                    after_val = getattr(after_m, field)
                    diff = after_val - before_val
                    if diff != 0:
                        changes[field] = diff
        
        if changes:
            delta[st] = changes
    
    return delta


router = APIRouter(prefix="/hooks", tags=["hooks"])


@router.post("/ingest-file", status_code=202, summary="Ingest local transcript JSONL files")
async def ingest_transcript_file(file: UploadFile = File(...)):
    """Accept a local transcript JSONL upload, ignoring blank lines."""
    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="Transcript file must be UTF-8") from exc

    entries: List[TranscriptEntry] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entries.append(TranscriptEntry.model_validate_json(line))
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid JSONL entry on line {line_number}",
            ) from exc

    global _transcript_store
    _transcript_store.extend(entries)
    await compute_metrics()
    return {"status": "accepted", "entries_ingested": len(entries)}


@router.post("/ingest", status_code=202, summary="Ingest transcript logs (JSONL)")
async def ingest_transcript(entries: List[TranscriptEntry]):
    """Accept a batch of transcript JSONL entries and store them for analysis.
    
    Each entry should have:
    - prompt_id: unique session identifier
    - session_type: 'main' or 'subagent'  
    - event_type: 'open', 'router', 'playbook', or 'principle'
    - optional: timestamp, prompt_text, model_name, metadata
    """
    global _transcript_store
    _transcript_store.extend(entries)
    
    # Recompute metrics after ingesting new data
    await compute_metrics()
    
    return {"status": "accepted", "entries_ingested": len(entries)}


@router.get("/effectiveness", response_model=List[OpensMetrics], summary="Get hook effectiveness metrics")
async def get_effectiveness_metrics():
    """Compute and return opens-per-100-prompts for main vs subagent sessions.
    
    Metrics include:
    - opens per 100 prompts by session type
    - counts of router, playbook, principle events by session type
    - total prompt counts for normalization
    """
    global _metrics_store
    if not _metrics_store:
        await compute_metrics()
    return _metrics_store


async def compute_metrics():
    """Compute opens-per-100-prompts metrics from the transcript store."""
    global _metrics_store, _transcript_store
    
    # Group by session_type
    by_session: dict[str, list[TranscriptEntry]] = {}
    for entry in _transcript_store:
        st = entry.session_type
        if st not in by_session:
            by_session[st] = []
        by_session[st].append(entry)
    
    results: list[OpensMetrics] = []
    
    for session_type, entries in by_session.items():
        total_prompts = len(entries)
        open_count = sum(1 for e in entries if e.event_type == "open")
        opens_per_100 = (open_count / total_prompts * 100) if total_prompts > 0 else 0.0
        
        router_count = sum(1 for e in entries if e.event_type == "router")
        playbook_count = sum(1 for e in entries if e.event_type == "playbook")
        principle_count = sum(1 for e in entries if e.event_type == "principle")
        
        results.append(OpensMetrics(
            session_type=session_type,
            total_prompts=total_prompts,
            open_count=open_count,
            opens_per_100=round(opens_per_100, 2),
            router_count=router_count,
            playbook_count=playbook_count,
            principle_count=principle_count,
        ))
    
    _metrics_store = results


