# -*- coding: utf-8 -*-
"""Smoke test: the chain-of-thought governance rules (check_rules)."""
import importlib.util, os, sys

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m = _load('cot_rules', os.path.join(BASE, 'code', 'validation', 'consensus_cot_full.py'))


def test_executor_promotes_is_consistent():
    r = m.check_rules({'role': 'EXECUTOR', 'mechanistic': 'YES', 'direction': 'PROMOTES',
                       'role_form': 'Apoptosis'}, form='Apoptosis')
    assert r['status'] == 'consistent'


def test_executor_protects_is_inconsistent():
    r = m.check_rules({'role': 'EXECUTOR', 'mechanistic': 'YES', 'direction': 'PROTECTS',
                       'role_form': 'Apoptosis'}, form='Apoptosis')
    assert r['status'] == 'inconsistent'
    assert any('EXECUTOR' in i for i in r['issues'])


def test_mech_no_should_not_have_confident_role():
    r = m.check_rules({'role': 'REGULATOR', 'mechanistic': 'NO', 'direction': 'PROMOTES',
                       'role_form': 'Apoptosis'}, form='Apoptosis')
    assert r['status'] == 'inconsistent'


def test_mech_yes_needs_confident_role():
    r = m.check_rules({'role': 'UNCERTAIN', 'mechanistic': 'YES', 'direction': 'UNCLEAR',
                       'role_form': ''}, form='Apoptosis')
    assert r['status'] == 'inconsistent'


if __name__ == '__main__':
    test_executor_promotes_is_consistent()
    test_executor_protects_is_inconsistent()
    test_mech_no_should_not_have_confident_role()
    test_mech_yes_needs_confident_role()
    print('test_governance_rules.py: OK')
