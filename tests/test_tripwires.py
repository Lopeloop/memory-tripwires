import copy
import json
import unittest
from tripwires import DEFAULT_DATA, build_probe, validate


class ProbeIsolation(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(DEFAULT_DATA.read_text())

    def test_pre_update_probe_cannot_see_later_preference(self):
        result = build_probe(self.data, 'preference-update', 'p1')
        self.assertEqual(len(result['turns']), 1)
        self.assertNotIn('dairy', json.dumps(result))

    def test_probe_export_excludes_oracles_and_limit_metadata(self):
        for case in self.data['cases']:
            for probe in case['probes']:
                result = build_probe(self.data, case['id'], probe['id'])
                self.assertEqual(set(result), {'case_id', 'probe_id', 'turns', 'question'})
                self.assertEqual(result['turns'][-1]['id'], probe['after_turn'])
                for turn in result['turns']:
                    self.assertEqual(set(turn), {'id', 'at', 'role', 'text'})

    def test_unknown_boundary_is_rejected_instead_of_using_all_turns(self):
        self.data['cases'][0]['probes'][0]['after_turn'] = 'missing'
        with self.assertRaises(ValueError):
            build_probe(self.data, 'preference-update', 'p1')

    def test_duplicate_turn_id_is_rejected_instead_of_ambiguous_boundary(self):
        self.data['cases'][0]['turns'][1]['id'] = 't1'
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_report_order_cannot_silently_change(self):
        self.data['cases'][0]['turns'].reverse()
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_export_does_not_mutate_fixture(self):
        original = copy.deepcopy(self.data)
        result = build_probe(self.data, 'selective-forgetting', 'p1')
        result['turns'][0]['text'] = 'changed by consumer'
        self.assertEqual(self.data, original)

    def test_unknown_probe_is_rejected(self):
        with self.assertRaises(ValueError):
            build_probe(self.data, 'preference-update', 'missing')


if __name__ == '__main__':
    unittest.main()
