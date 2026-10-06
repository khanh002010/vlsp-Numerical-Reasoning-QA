import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from vinumqa.cv_module.chart_to_table.model_files import resolve_model_directory, snapshot_complete


class ModelFilesTests(unittest.TestCase):
    def make_snapshot(self, directory):
        root = Path(directory)
        for name in ("config.json", "preprocessor_config.json", "tokenizer_config.json",
                     "tokenizer.json", "chat_template.json"):
            (root / name).write_text("{}", encoding="utf-8")
        (root / "model.safetensors").write_bytes(b"test-weights")

    def test_complete_cache_never_requests_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.make_snapshot(tmp)
            def download(**kwargs):
                self.assertTrue(kwargs.get("local_files_only"), "Unexpected network request")
                return tmp
            self.assertEqual(resolve_model_directory("Qwen/test", download), str(Path(tmp).resolve()))

    def test_local_directory_does_not_contact_hub(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.make_snapshot(tmp)
            download = Mock(side_effect=AssertionError("Unexpected Hub call"))
            self.assertEqual(resolve_model_directory(tmp, download), str(Path(tmp).resolve()))
            download.assert_not_called()

    def test_missing_shard_triggers_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.make_snapshot(tmp)
            root = Path(tmp)
            (root / "model.safetensors.index.json").write_text(
                json.dumps({"weight_map": {"weight": "model-00001.safetensors"}}), encoding="utf-8")
            self.assertFalse(snapshot_complete(tmp))
            def download(**kwargs):
                if not kwargs.get("local_files_only"):
                    (root / "model-00001.safetensors").write_bytes(b"shard")
                return tmp
            mocked = Mock(side_effect=download)
            resolve_model_directory("Qwen/test", mocked)
            self.assertEqual(mocked.call_count, 2)
            self.assertTrue(snapshot_complete(tmp))

    def test_rate_limit_preserves_original_error_and_does_not_loop(self):
        download = Mock(side_effect=[FileNotFoundError("no cache"), RuntimeError("429 Retry after 144 seconds")])
        with self.assertRaisesRegex(RuntimeError, "429 Retry after 144 seconds"):
            resolve_model_directory("Qwen/test", download)
        self.assertEqual(download.call_count, 2)

    def test_incomplete_download_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            download = Mock(return_value=tmp)
            with self.assertRaisesRegex(RuntimeError, "missing required"):
                resolve_model_directory("Qwen/test", download)


if __name__ == "__main__":
    unittest.main()
