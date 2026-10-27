import json
import unittest
from unittest.mock import Mock, patch

from worker import worker


class TestWorkerCleanup(unittest.TestCase):

    def test_cleanup_failure_preserves_completion(self):

        job_json = json.dumps({
            "job_id": "test-job-001",
            "features": [5.1, 3.5, 1.4, 0.2]
        })

        fake_redis = Mock()

        # First call returns a job.
        # Second call stops the infinite worker loop.
        fake_redis.blmove.side_effect = [
            job_json,
            KeyboardInterrupt()
        ]

        fake_redis.llen.return_value = 1

        # Simulate Redis LREM failure
        fake_redis.lrem.side_effect = RuntimeError(
            "Simulated LREM failure"
        )

        fake_model = Mock()
        fake_model.predict.return_value = 0

        with (
            patch.object(worker, "redis_client", fake_redis),
            patch.object(worker, "model_service", fake_model)
        ):
            with self.assertRaises(KeyboardInterrupt):
                worker.process_jobs()

        statuses = [
            json.loads(call.args[1])["status"]
            for call in fake_redis.set.call_args_list
        ]

        self.assertEqual(
            statuses,
            ["processing", "completed"]
        )

        fake_redis.lrem.assert_called_once()


if __name__ == "__main__":
    unittest.main()