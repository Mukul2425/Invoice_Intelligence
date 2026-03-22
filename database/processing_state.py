import os
from datetime import datetime, timezone

from database.db import SessionLocal
from database.models import ProcessedFile


def _fingerprint(file_path):
    stat = os.stat(file_path)
    return f"{int(stat.st_mtime)}:{stat.st_size}"


def should_process_file(file_path):
    if not os.path.isfile(file_path):
        return False

    current_fp = _fingerprint(file_path)

    session = SessionLocal()
    try:
        row = session.query(ProcessedFile).filter_by(file_path=file_path).first()
        if not row:
            return True
        return row.fingerprint != current_fp
    finally:
        session.close()


def mark_file_processed(file_path, status):
    if not os.path.isfile(file_path):
        return

    current_fp = _fingerprint(file_path)

    session = SessionLocal()
    try:
        row = session.query(ProcessedFile).filter_by(file_path=file_path).first()
        if row:
            row.fingerprint = current_fp
            row.last_status = status
            row.processed_at = datetime.now(timezone.utc).isoformat()
        else:
            row = ProcessedFile(
                file_path=file_path,
                fingerprint=current_fp,
                last_status=status,
                processed_at=datetime.now(timezone.utc).isoformat(),
            )
            session.add(row)

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
