from app.services.tracker import TrackerService
from app.models.schemas import TrackerItem
from datetime import datetime

def test_tracker_crud_export():
    t = TrackerService()
    item = TrackerItem(tracker_id='1', profile_id='p1', job_id='j1', company='Acme', role='Eng')
    t.upsert(item)
    items = t.list(profile_id='p1')
    assert len(items) == 1
    csv = t.export_csv(items)
    assert b'tracker_id' in csv
