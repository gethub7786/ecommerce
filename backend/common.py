import uuid, time
from typing import Any, Dict, List

tasks: List[Dict[str, Any]] = []


def start_task(name: str, supplier: str) -> Dict[str, Any]:
    task = {
        'id': str(uuid.uuid4()),
        'name': name,
        'supplier': supplier,
        'status': 'running',
        'progress': 0,
        'nextRun': '',
        'started': int(time.time()),
    }
    tasks.append(task)
    return task


def finish_task(task: Dict[str, Any], ok: bool = True) -> None:
    task['status'] = 'completed' if ok else 'failed'
    task['progress'] = 100
    task['finished'] = int(time.time()) 