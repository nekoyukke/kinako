from src.utils.error.base import KinakoBaseError, KinakoRelatedInfo, KinakoHelp

class KinakoCollectError(KinakoBaseError):
    pass

if __name__ == "__main__":
    raise KinakoCollectError(
        "不明なエラー！",
        line=1,
        column=1,
        source=
"""let int a = 1;
mut int b = 4005;
{
    anchor int f@ = anchor b; // うんち！！！！！
}
shared int g = 3;
""",
        length=10,
        related=[KinakoRelatedInfo("ライフタイムエラー",6,0,17)],
        help=[KinakoHelp("もしかしたら(=^・^=)かもね")]
    )