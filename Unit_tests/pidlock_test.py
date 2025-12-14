# tests/test_pid_lock.py
import os
import pytest
from pathlib import Path
from dataclasses import dataclass


@dataclass
class LockState:
    pid: int
    lockfile_path: Path
    acquired: bool = False


class PIDLockFile:
    def __init__(self, lockfile_path="app.lock"):
        self.state = LockState(
            pid=os.getpid(),
            lockfile_path=Path(lockfile_path)
        )

    def __enter__(self):
        if self.state.lockfile_path.exists():
            try:
                with open(self.state.lockfile_path, 'r') as f:
                    existing_pid = int(f.read().strip())

                if self._is_process_alive(existing_pid):
                    raise RuntimeError(f"Процесс {existing_pid} ещё запущен")
                else:
                    print(f"Удаление битого файла с PID {existing_pid}")
                    self.state.lockfile_path.unlink()
            except (ValueError, IOError) as e:
                print(f"Удаление нечитаемого файл: {e}")
                self.state.lockfile_path.unlink()

        with open(self.state.lockfile_path, 'w') as f:
            f.write(str(self.state.pid))

        self.state.acquired = True
        print(f"Получен захват PID {self.state.pid}")
        return self.state

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.state.acquired and self.state.lockfile_path.exists():
            try:
                with open(self.state.lockfile_path, 'r') as f:
                    if int(f.read().strip()) == self.state.pid:
                        self.state.lockfile_path.unlink()
                        print(f"Lock released for PID {self.state.pid}")
            except (ValueError, IOError) as e:
                print(f"Ошибка при снятии захвата: {e}")

        self.state.acquired = False

    def _is_process_alive(self, pid):
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False


def test_normal_creation_and_removal():
    lock_path = Path("test1.lock")
    pid = os.getpid()

    with PIDLockFile(lock_path) as state:
        assert lock_path.exists()
        assert state.acquired is True
        assert state.pid == pid

        with open(lock_path, 'r') as f:
            file_pid = int(f.read().strip())
            assert file_pid == pid

    assert not lock_path.exists()


def test_stale_lockfile_removal():
    lock_path = Path("test2.lock")
    fake_pid = 999999

    with open(lock_path, "w") as f:
        f.write(str(fake_pid))

    with PIDLockFile(lock_path) as state:
        assert state.acquired is True
        assert lock_path.exists()

        with open(lock_path, 'r') as f:
            file_pid = int(f.read().strip())
            assert file_pid == state.pid

    assert not lock_path.exists()


def test_double_entry_protection():
    lock_path = Path("test3.lock")

    with PIDLockFile(lock_path) as state1:
        assert state1.acquired is True

        with pytest.raises(RuntimeError, match=r"Процесс.*ещё запущен"):
            with PIDLockFile(lock_path) as state2:
                pass


def test_corrupted_lockfile_handling():
    lock_path = Path("test4.lock")

    with open(lock_path, "w") as f:
        f.write("not_a_number")

    with PIDLockFile(lock_path) as state:
        assert state.acquired is True
        assert lock_path.exists()

        with open(lock_path, 'r') as f:
            file_pid = int(f.read().strip())
            assert file_pid == state.pid

    assert not lock_path.exists()
