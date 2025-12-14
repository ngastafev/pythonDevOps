# tests/test_timestamp_sync.py
import os
import time
import tempfile
import pytest
from datetime import datetime
from pathlib import Path


def sync_timestamps(source_path, target_path):
    stat_info = os.stat(source_path)
    os.utime(target_path, (stat_info.st_atime, stat_info.st_mtime))
    print(f"Timestamps copied from '{source_path}' to '{target_path}'")


def set_timestamp_manually(file_path, timestamp_str, attr='both'):
    dt = datetime.fromisoformat(timestamp_str.replace(' ', 'T'))
    timestamp = dt.timestamp()

    stat_info = os.stat(file_path)
    if attr == 'both':
        os.utime(file_path, (timestamp, timestamp))
    elif attr == 'mtime':
        os.utime(file_path, (stat_info.st_atime, timestamp))
    elif attr == 'atime':
        os.utime(file_path, (timestamp, stat_info.st_mtime))

    print(f"Set timestamp(s) on '{file_path}' to {dt.isoformat()}")


def test_sync_timestamps():
    with tempfile.NamedTemporaryFile(delete=False) as src, \
            tempfile.NamedTemporaryFile(delete=False) as tgt:
        source_path = Path(src.name)
        target_path = Path(tgt.name)

        fixed_time = 1000000000.0
        os.utime(source_path, (fixed_time, fixed_time))

        sync_timestamps(source_path, target_path)

        target_stat = os.stat(target_path)
        assert target_stat.st_atime == fixed_time
        assert target_stat.st_mtime == fixed_time
    os.unlink(source_path)
    os.unlink(target_path)


def test_set_timestamp_manually_both():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        file_path = Path(f.name)

    timestamp_str = "2023-10-20 15:30:00"
    set_timestamp_manually(file_path, timestamp_str, 'both')

    expected_ts = datetime.fromisoformat(timestamp_str.replace(' ', 'T')).timestamp()
    stat = os.stat(file_path)
    assert stat.st_atime == pytest.approx(expected_ts, abs=1)
    assert stat.st_mtime == pytest.approx(expected_ts, abs=1)

    os.unlink(file_path)


def test_set_timestamp_manually_mtime():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        file_path = Path(f.name)

    initial_time = 1000000000.0
    os.utime(file_path, (initial_time, initial_time))

    new_timestamp_str = "2024-01-01 12:00:00"
    set_timestamp_manually(file_path, new_timestamp_str, 'mtime')

    expected_ts = datetime.fromisoformat(new_timestamp_str.replace(' ', 'T')).timestamp()
    stat = os.stat(file_path)
    assert stat.st_atime == pytest.approx(initial_time, abs=1)
    assert stat.st_mtime == pytest.approx(expected_ts, abs=1)

    os.unlink(file_path)


def test_set_timestamp_manually_atime():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        file_path = Path(f.name)
    initial_time = 1000000000.0
    os.utime(file_path, (initial_time, initial_time))

    new_timestamp_str = "2024-01-01 12:00:00"
    set_timestamp_manually(file_path, new_timestamp_str, 'atime')

    expected_ts = datetime.fromisoformat(new_timestamp_str.replace(' ', 'T')).timestamp()
    stat = os.stat(file_path)
    assert stat.st_mtime == pytest.approx(initial_time, abs=1)
    assert stat.st_atime == pytest.approx(expected_ts, abs=1)

    os.unlink(file_path)


def test_main_touch():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        target_path = Path(f.name)
    import sys
    original_argv = sys.argv
    sys.argv = ["script", "--target", str(target_path)]

    main_implementation()

    assert target_path.exists()

    time_before = time.time()
    main_implementation()
    time_after = time.time()

    stat = os.stat(target_path)
    assert time_before <= stat.st_mtime <= time_after

    sys.argv = original_argv
    os.unlink(target_path)


def test_main_sync():
    with tempfile.NamedTemporaryFile(delete=False) as src, \
            tempfile.NamedTemporaryFile(delete=False) as tgt:
        source_path = Path(src.name)
        target_path = Path(tgt.name)

    fixed_time = 1000000000.0
    os.utime(source_path, (fixed_time, fixed_time))

    import sys
    original_argv = sys.argv
    sys.argv = ["script", "--source", str(source_path), "--target", str(target_path)]

    main_implementation()

    stat = os.stat(target_path)
    assert stat.st_mtime == fixed_time
    assert stat.st_atime == fixed_time

    sys.argv = original_argv
    os.unlink(source_path)
    os.unlink(target_path)


def test_main_set_time():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        target_path = Path(f.name)

    import sys
    original_argv = sys.argv
    sys.argv = ["script", "--target", str(target_path), "--set-time", "2023-06-15 10:00:00"]

    main_implementation()

    expected_ts = datetime.fromisoformat("2023-06-15T10:00:00").timestamp()
    stat = os.stat(target_path)
    assert stat.st_mtime == pytest.approx(expected_ts, abs=1)
    assert stat.st_atime == pytest.approx(expected_ts, abs=1)

    sys.argv = original_argv
    os.unlink(target_path)
