# tests/test_basic.py
from serial_monitor.data_processing import DataProcessor, parse_status_line


def test_parse_ok():
    assert parse_status_line("Status:0\n")["status"] == 0
    assert parse_status_line("Status:1")["status"] == 1


def test_parse_bad():
    assert parse_status_line("foo:bar") is None
    assert parse_status_line("") is None


def test_processor():
    p = DataProcessor(window_size=5)
    for v in [1, 0, 1, 1, 0]:
        p.push(v)
    assert p.counts() == (2, 3)
    assert 0.4 <= p.moving_average() <= 0.6
