import copy
import json
from pathlib import Path
import tempfile
import unittest

from demo import SCENARIOS, load
from gate import evaluate

ROOT = Path(__file__).resolve().parents[1]


class GateTests(unittest.TestCase):
    def setUp(self):
        self.report = load(ROOT / 'examples/evidence/matched-commit.json')

    def assert_stop(self):
        decision = evaluate(self.report)
        self.assertEqual((decision.verdict, decision.next_action), ('ESCALATE', 'STOP'))

    def test_scenarios(self):
        for name, expected in SCENARIOS.items():
            with self.subTest(name=name):
                result = evaluate(load(ROOT / 'examples/evidence' / name))
                self.assertEqual((result.verdict, result.next_action), expected)

    def test_stale_passing_review_cannot_accept_new_commit(self):
        self.report['reviews'][0]['commit_sha'] = 'b' * 40
        self.assert_stop()

    def test_implementation_agent_cannot_review_itself(self):
        self.report['reviews'][0]['agent_id'] = self.report['implementation']['agent_id']
        self.assert_stop()

    def test_one_identity_cannot_fill_multiple_review_roles(self):
        self.report['reviews'][1]['agent_id'] = self.report['reviews'][0]['agent_id']
        self.assert_stop()

    def test_missing_ci_is_not_success(self):
        self.report['ci_checks'].pop()
        self.assert_stop()

    def test_duplicate_role_does_not_replace_missing_role(self):
        self.report['reviews'][1]['role'] = self.report['reviews'][0]['role']
        self.assert_stop()

    def test_passing_label_with_unresolved_findings_is_contradictory(self):
        self.report['reviews'][0]['findings'] = ['Boundary case still fails.']
        self.assert_stop()

    def test_pending_ci_is_not_success(self):
        self.report['ci_checks'][0]['result'] = 'pending'
        self.assert_stop()

    def test_failed_ci_can_be_remediated_but_not_accepted(self):
        self.report['ci_checks'][0]['result'] = 'failure'
        decision = evaluate(self.report)
        self.assertEqual((decision.verdict, decision.next_action), ('FAIL', 'REMEDIATE'))

    def test_repaired_change_can_pass_at_second_cycle(self):
        self.report['remediation_cycles'] = 2
        self.assertEqual(evaluate(self.report).verdict, 'PASS')

    def test_unresolved_failure_at_second_cycle_stops(self):
        self.report['remediation_cycles'] = 2
        self.report['ci_checks'][0]['result'] = 'failure'
        self.assert_stop()

    def test_exceeded_cycle_limit_stops_even_with_passing_records(self):
        self.report['remediation_cycles'] = 3
        self.assert_stop()

    def test_boolean_cycle_count_is_not_an_integer(self):
        self.report['remediation_cycles'] = True
        self.assert_stop()

    def test_missing_human_scope_approval_stops(self):
        self.report['task']['human_scope_approved'] = False
        self.assert_stop()

    def test_release_request_is_outside_demo_authority(self):
        self.report['task']['requested_action'] = 'deploy'
        self.assert_stop()

    def test_high_risk_task_requires_human_attention(self):
        self.report['task']['risk'] = 'high'
        self.assert_stop()

    def test_malformed_nested_fields_fail_closed(self):
        for section, key in [('reviews', 'role'), ('reviews', 'verdict'), ('ci_checks', 'name'), ('ci_checks', 'result')]:
            for value in [None, [], {}, False, 42]:
                with self.subTest(section=section, key=key, value=value):
                    report = copy.deepcopy(self.report)
                    report[section][0][key] = value
                    self.assertEqual(evaluate(report).verdict, 'ESCALATE')

    def test_input_is_not_modified(self):
        original = copy.deepcopy(self.report)
        evaluate(self.report)
        self.assertEqual(original, self.report)

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'duplicate.json'
            path.write_text('{"synthetic": true, "synthetic": false}')
            with self.assertRaises(ValueError):
                load(path)

    def test_not_an_object_stops(self):
        for value in [None, [], 'PASS', 1, True]:
            with self.subTest(value=value):
                self.assertEqual(evaluate(value).verdict, 'ESCALATE')


if __name__ == '__main__':
    unittest.main()
