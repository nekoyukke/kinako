from dataclasses import dataclass

from src.utils.error.base import KinakoBaseError

@dataclass
class ErrorLists():
    errs: list[KinakoBaseError]

    # クラス表示の共通部分
    def display(self) -> str:
        file_eq_id:dict[str, list[KinakoBaseError]] = {}
        for err in self.errs:
            ffo = err.format_file_only()
            if ffo in file_eq_id:
                file_eq_id[ffo] += [err]
                continue
            file_eq_id[ffo] = [err]
            continue
        # string
        result_stirng = ""
        for k, v in file_eq_id.items():
            result_stirng += "Traceback (most recent call last):\n" + k + "\n"
            result_stirng += "\n\n\n".join([er.__str__(False) for er in v])
        return result_stirng


    def __str__(self) -> str:
        return self.display()

    def __repr__(self) -> str:
        return self.display()