# Kinako

<img src="logo.png" alt="logo" width="120">

`kinako` は `Python` で実装された `C` like な言語です。

`kinako` は、`C`や`Rust`, `Go` などから影響を受けつつ、概念をできるだけ増やさず、一貫した規則で設計することを目標に作成されました。

## ✨ 特徴 (Features)

- **特徴1**: C likeなシンプルな構文
- **特徴2**: 明示的な挙動
- **特徴3**: 可能な限りのコンパイル時検知

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
fn main() -> int {
    io.print("Hello World");
    return 0;
}
```

<!-->
ここにほかの例（`kinako`がつよつよ（笑）である理由とか）
`kinako`がわかりやすい例とか。
1. Rust比較するわかりやすい（？？？？）所有権
2. newとか
3. allocator
4. implとか
<!-->

## その他
コミュニティ規約については[ここ](docs/CONTRIBUTING.md)を参照してください。\
また言語仕様については[こちら](docs/spec.md)を参照してください。

つくってるひと:[ねこゆっけ](https://github.com/nekoyukke) ※つくってるひとがボケをかましまくるのでとてもめんどくさいです

てつだってるひと:**なし！！！！**

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/nekoyukke/kinako)こんなのがありますのでよかったら。
