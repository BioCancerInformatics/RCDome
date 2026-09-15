# -*- coding: utf-8 -*-
"""Smoke test: the 7-class mechanistic mapping (assign_mechanistic_class)."""
import importlib.util, os, sys

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m = _load('assign_mc', os.path.join(BASE, 'code', 'validation', 'channel_c_evidence_tier.py'))


def test_assign_mechanistic_class():
    assert m.assign_mechanistic_class('CONFIRMED', 100) == 'MECHANISTIC'
    assert m.assign_mechanistic_class('NEEDS_LITERATURE', 1) == 'LITERATURE_GAP'
    assert m.assign_mechanistic_class('NEEDS_CONTEXT', 1) == 'CONTEXT_GAP'
    assert m.assign_mechanistic_class('ERROR', 0) == 'TECHNICAL_FAILURE'
    assert m.assign_mechanistic_class('UNCLEAR', 26) == 'CO_OCCURRENCE'
    assert m.assign_mechanistic_class('UNCLEAR', 5) == 'INSUFFICIENT_DATA'
    assert m.assign_mechanistic_class('UNCLEAR', 0) == 'DATABASE_ONLY'


if __name__ == '__main__':
    test_assign_mechanistic_class()
    print('test_mechanistic_class.py: OK')
