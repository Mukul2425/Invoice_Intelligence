import os
import tempfile
import time
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.db import Base
from database.processing_state import mark_file_processed, should_process_file


class TestProcessingState(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        self.test_session_local = sessionmaker(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_should_process_new_then_skip_unchanged(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"first")
            temp_path = tmp.name

        try:
            with patch("database.processing_state.SessionLocal", self.test_session_local):
                self.assertTrue(should_process_file(temp_path))

                mark_file_processed(temp_path, "stored")

                self.assertFalse(should_process_file(temp_path))
        finally:
            os.unlink(temp_path)

    def test_should_process_when_file_changes(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"first")
            temp_path = tmp.name

        try:
            with patch("database.processing_state.SessionLocal", self.test_session_local):
                mark_file_processed(temp_path, "stored")
                self.assertFalse(should_process_file(temp_path))

                time.sleep(1)
                with open(temp_path, "wb") as handle:
                    handle.write(b"updated content")

                self.assertTrue(should_process_file(temp_path))
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
