# Kinako

Pythonで実装されたRustとCのハイブリッド言語！！！

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\
kinakoは、C言語は型付けで素早いが安全性に欠ける点、C++のユニークポインタやRustの借用などは強力ですが、型という枠組みにとらわれ過ぎている点から開発されました。

~~作者があれなので構造があれかもしれません。ご了承お願いします。~~

## ✨ 特徴 (Features)

- **特徴1**: 強力な静的型付け。同じIntでもbit数が違えば演算ができません
- **特徴2**: 元祖オブジェクト指向。カプセル化、メソッドのみ。継承はありません
- **特徴3**: ユニークポインタは存在せず、すべて束縛になりました。

## 🚀 クイックスタート (Quick Start)

### 1. 前提条件 (Prerequisites)
この言語をビルド・実行するには以下が必要です。
- Python 3.12~

### 2. インストール (Installation)
```bash
git clone https://github.com/nekoyukke/kinako.git
cd kinako
```

## 📄 テストコード 
### Hello World
```
import std.io;
fn int main() {
    io.print("Hello World");
    return 0;
}
```

## その他
コミュニティ規約については[ここ](docs/CONTRIBUTING.md)を参照してください。\
また言語仕様については[こちら](docs/spec.md)を参照してください。

つくってるひと:[ねこゆっけ](https://github.com/nekoyukke) ※つくってるひとがボケをかましまくるのでとてもめんどくさいです

てつだってるひと:**なし！！！！**