# -*- coding: utf-8 -*-
"""Smoke test: the benchmark scoring (combined accuracy + false positives)
on a 26-pair fixture (18 positive executor/regulator pairs + 8 form-mismatch negatives).
Locks in the exact scoring rule used in cot_benchmark_v11.py / consensus_benchmark_v7."""


def combined_correct(true_role, pred_role, pred_mech):
    """Same rule as the production benchmark scripts."""
    return ((true_role in ('EXECUTOR', 'REGULATOR') and pred_role == true_role) or
            (true_role == 'NEGATIVE' and pred_role == 'UNCERTAIN' and pred_mech == 'NO'))


def test_perfect_run_scores_100_percent():
    pairs = []
    for role in ['EXECUTOR'] * 10 + ['REGULATOR'] * 8:
        pairs.append((role, role, 'YES'))           # correctly classified positive
    for _ in range(8):
        pairs.append(('NEGATIVE', 'UNCERTAIN', 'NO'))  # correctly rejected negative

    correct = sum(combined_correct(tr, pr, pm) for tr, pr, pm in pairs)
    false_positives = sum(1 for tr, pr, pm in pairs
                          if tr == 'NEGATIVE' and not (pr == 'UNCERTAIN' and pm == 'NO'))

    assert len(pairs) == 26
    assert correct == 26
    assert false_positives == 0
    assert correct / 26 == 1.0
    assert false_positives / 8 == 0.0


def test_one_false_positive_is_detected():
    pairs = []
    for role in ['EXECUTOR'] * 10 + ['REGULATOR'] * 8:
        pairs.append((role, role, 'YES'))
    pairs.append(('NEGATIVE', 'EXECUTOR', 'YES'))  # one negative wrongly called positive
    for _ in range(7):
        pairs.append(('NEGATIVE', 'UNCERTAIN', 'NO'))

    correct = sum(combined_correct(tr, pr, pm) for tr, pr, pm in pairs)
    false_positives = sum(1 for tr, pr, pm in pairs
                          if tr == 'NEGATIVE' and not (pr == 'UNCERTAIN' and pm == 'NO'))

    assert correct == 25
    assert false_positives == 1
    assert false_positives / 8 == 0.125


if __name__ == '__main__':
    test_perfect_run_scores_100_percent()
    test_one_false_positive_is_detected()
    print('test_benchmark_scoring.py: OK')
