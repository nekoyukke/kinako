from dataclasses import dataclass

from src.utils.error.base import KinakoBaseError

@dataclass
class ErrorLists():
    errs: list[KinakoBaseError]

    # クラス表示の共通部分
    def display(self, is_tb:bool=False) -> str:
        if is_tb:
            result_stirng = ""
            result_stirng += "\n\n\n".join([er.__str__(False) for er in self.errs])
            return result_stirng
        
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


    def __str__(self, is_tb:bool=False) -> str:
        return self.display(is_tb)

    def __repr__(self, is_tb:bool=False) -> str:
        return self.display(is_tb)