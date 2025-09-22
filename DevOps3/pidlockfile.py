import os
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


# Тесты
if __name__ == "__main__":
    # Тест 1: нормальное создание и удаление
    print("Тест 1")
    with PIDLockFile("test1.lock") as state:
        assert state.lockfile_path.exists()
        assert state.acquired == True
        print(f"PID в файле: {state.pid}")
        Path("test1.lock").unlink()
    # Тест 2: обработка битого lockfile
    print("Тест 2")
    with open("test2.lock", "w") as f:
        f.write("999999")  # Несуществующий PID

    with PIDLockFile("test2.lock") as state:
        assert state.acquired == True

        Path("test2.lock").unlink()


    # Тест 3: защита от двойного входа
    print("Тест 3")
    # Создаем первый lock
    lock1 = PIDLockFile("test3.lock")
    lock2 = PIDLockFile("test3.lock")

    with lock1 as state1:
        assert state1.acquired == True

        try:
            with lock2 as state2:
                assert False
        except RuntimeError as e:
            print(f"Ошибка поймана: {e}")

            Path("test3.lock").unlink()

    # Тест 4: проверка содержимого lockfile
    print("\n=== Тест 4: проверка содержимого ===")
    with PIDLockFile("test4.lock") as state:
        with open("test4.lock", "r") as f:
            content = f.read().strip()

    # Очистка
    for f in ["test1.lock", "test2.lock", "test3.lock", "test4.lock"]:
        if Path(f).exists():
            Path(f).unlink()
