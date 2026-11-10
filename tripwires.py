"""Validate fixtures or emit one probe without future turns or grading criteria."""
import argparse
from datetime import datetime
import json
from pathlib import Path

DEFAULT_DATA = Path(__file__).parent / 'cases' / 'scenarios.json'


def validate(data):
    if data.get('schema_version') != 1 or type(data.get('schema_version')) is not int:
        raise ValueError('schema_version must be integer 1')
    cases = data.get('cases')
    if not isinstance(cases, list) or not cases:
        raise ValueError('cases must be a non-empty list')
    ids = set()
    for case in cases:
        identifier = case.get('id')
        if not isinstance(identifier, str) or not identifier or identifier in ids:
            raise ValueError('missing or duplicate case id')
        ids.add(identifier)
        for field in ('category', 'limit'):
            if not isinstance(case.get(field), str) or not case[field].strip():
                raise ValueError(f'{identifier}: missing {field}')
        if not isinstance(case.get('turns'), list) or not case['turns']:
            raise ValueError(f'{identifier}: empty turns')
        turn_ids = set()
        previous = None
        for turn in case['turns']:
            tid = turn.get('id')
            if not isinstance(tid, str) or not tid or tid in turn_ids:
                raise ValueError(f'{identifier}: missing or duplicate turn id')
            turn_ids.add(tid)
            if turn.get('role') != 'user' or not isinstance(turn.get('text'), str) or not turn['text'].strip():
                raise ValueError(f'{identifier}: invalid turn')
            if not isinstance(turn.get('at'), str) or not turn['at'].endswith('Z'):
                raise ValueError(f'{identifier}: UTC timestamp required')
            stamp = datetime.fromisoformat(turn['at'].replace('Z', '+00:00'))
            if previous is not None and stamp < previous:
                raise ValueError(f'{identifier}: report timestamps out of order')
            previous = stamp
        if not isinstance(case.get('probes'), list) or not case['probes']:
            raise ValueError(f'{identifier}: empty probes')
        probe_ids = set()
        for probe in case['probes']:
            pid = probe.get('id')
            if not isinstance(pid, str) or not pid or pid in probe_ids:
                raise ValueError(f'{identifier}: missing or duplicate probe id')
            probe_ids.add(pid)
            if probe.get('after_turn') not in turn_ids:
                raise ValueError(f'{identifier}: unknown probe boundary')
            if not isinstance(probe.get('question'), str) or not probe['question'].strip():
                raise ValueError(f'{identifier}: missing question')
            for field in ('must', 'must_not'):
                values = probe.get(field)
                if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v.strip() for v in values):
                    raise ValueError(f'{identifier}: invalid {field}')
    return data


def build_probe(data, case_id, probe_id):
    """Independent probe: fresh state, ingest the prefix, then ask the question."""
    validate(data)
    case = next((c for c in data['cases'] if c['id'] == case_id), None)
    if case is None:
        raise ValueError('unknown case')
    probe = next((p for p in case['probes'] if p['id'] == probe_id), None)
    if probe is None:
        raise ValueError('unknown probe')
    stop = next(i for i, turn in enumerate(case['turns']) if turn['id'] == probe['after_turn'])
    return {'case_id': case_id, 'probe_id': probe_id,
            'turns': [dict(t) for t in case['turns'][:stop + 1]],
            'question': probe['question']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=DEFAULT_DATA)
    parser.add_argument('--case')
    parser.add_argument('--probe')
    args = parser.parse_args()
    if bool(args.case) != bool(args.probe):
        parser.error('--case and --probe must be supplied together')
    try:
        data = validate(json.loads(args.data.read_text()))
        result = build_probe(data, args.case, args.probe) if args.case else {
            'valid': True, 'cases': len(data['cases']),
            'probes': sum(len(c['probes']) for c in data['cases'])}
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f'Invalid fixture or selection: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
