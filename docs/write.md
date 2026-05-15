# kinakoの書き方

## 改行

グローバルでの`class`, `def`との間は`2個`。\
ローカルでは`1個`

基本`79文字以内`に収め、もし文法的に開業が難しいところで超えるようなら`\`を使うこと。

## string

基本的に`"`を使い、`r`などの場合は`'`を。ただし`f`の時は例外的に`"`を使うこと

## import
`__**__`は基本的に最初で
次に標準ライブラリ、次に他人のライブラリ、最後に自分のライブラリ
基本的に改行する。

# 思想概要
```
Type       → 構造
Ownership  → 扱い
Group      → 分類
Interface  → 能力
```
これなこれ分離しよって話

ゴミみたいな構造なので
`state`, 
`onwer`, 
`value`, 
`type`, 
`context`,
`Possession`を持つ


`state`は変数の状態（有効、ロックされている等）
`onwer`は変数を誰が持っているか
`context`は上二つmix
`value`はマジ値
`type`は型
`possession`は`state` / `onwer`の初期値の取り方と変数の触り方

# パイプライン的な話

基本的に
1. `src/frontend`
2. `src/middleend`
3. `src/backend`
基本的にオニオンアーキテクチャ採用し、coreは純粋なロジックと抽象基底クラスのみ。
## frontend
1. `src/frontend/lexer`
2. `src/frontend/parser`
3. `src/frontend/collector`
4. `src/frontend/resolver`
5. `src/frontend/ownerchecker`
6. `src/frontend/typechecker`
の順





# 好きな曲/動画とか
よかったら増やして

## nekoyukke

[【UTAU＆SVカバー】驫麤～とりぷるばか～【とりぷるテト】](https://www.youtube.com/watch?v=i3xXxfamJYk)

[言葉遊び / feat.Yi Xi](https://www.youtube.com/watch?v=eGS-IjCUEzA)

[一龠 / feat.flower](https://www.youtube.com/watch?v=iWzUxFQQAKY)

[誰もここから出ることはできません ⛔️ | Your New Home - アメイジング・デジタル・サーカス (弦楽四重奏カバー)](https://www.youtube.com/watch?v=SJSJh7D_HiI)

[少女A (arrange) / 黒うさぎ](https://www.youtube.com/watch?v=9I4oOz6SZPo&)

[【Lyric Movie】Ex-Otogibanashi – ryo (supercell) / かぐや(cv.夏吉ゆうこ) & 月見ヤチヨ(cv.早見沙織) from 超かぐや姫！](https://www.youtube.com/watch?v=owEBHHZg38s)

[ハングリーニコル を歌ってみた / 黒うさぎ](https://www.youtube.com/watch?v=plmgnGEWb7o)

[いますぐ輪廻 を歌ってみた / 黒うさぎ](https://www.youtube.com/watch?v=8whiaarnvCY)

[ヨルシカ - あぶく（OFFICIAL VIDEO](https://www.youtube.com/watch?v=OHAjc-ayhus)

### AI-note

> ここまでの設計を、次にそのまま続きができるレベルで整理します。
> 
> ---
> 
> # ■ 言語設計まとめ（現時点の確定版）
> 
> ---
> 
> # ① 全体レイヤ構造
> 
> ```text id="layer"
> Type       = データ構造（list[int] など）
> Ownership  = mut / let（変数の所有・可変性の初期状態）
> Possession = 型構造に1対1対応するアクセス制約
> Runtime Access = hold / grab（参照操作）
> anchor     = possessionの一時切替
> ```
> 
> ---
> 
> # ② 基本構文
> 
> ```text id="syntax"
> <占有権タイプ> <型> <変数>;
> ```
> 
> 例：
> 
> ```text id="ex1"
> mut int a;
> let int a;
> mut[const] list[int] b;
> ```
> 
> ---
> 
> # ③ mut / let の意味
> 
> ## ✔ mut
> 
> * 変数自体が可変
> * 代入可能（a = 3）
> * mutableなpossessionを持つ
> 
> ## ✔ let
> 
> * 変数は不変
> * 再代入不可
> * read-only扱い
> 
> ---
> 
> # ④ possession（重要）
> 
> ## ✔ 定義
> 
> > possessionは「型構造に1対1で対応するアクセス制約」
> 
> ---
> 
> ## ✔ 例
> 
> ```text id="p1"
> mut[const] list[int]
> ```
> 
> 意味：
> 
> * list（外側）＝ mut（可変）
> * int（要素）＝ const（不変）
> 
> ---
> 
> ## ✔ 重要ルール
> 
> ```text id="rule1"
> possessionは型構造と同一構造で対応する
> ネストしない（再帰しない）
> ```
> 
> ---
> 
> ## ❌ 禁止
> 
> ```text id="bad"
> mut[const[mut]] list[int]
> ```
> 
> ---
> 
> # ⑤ hold / grab（実行時アクセス）
> 
> ## ✔ hold
> 
> ```text id="hold"
> hold x { ... }
> ```
> 
> * 不変参照（read）
> 
> ## ✔ grab
> 
> ```text id="grab"
> grab x { ... }
> ```
> 
> * 可変参照（write）
> * 排他アクセス
> 
> ---
> 
> # ⑥ anchor（重要）
> 
> ```text id="anchor"
> anchor x { ... }
> ```
> 
> ## ✔ 役割
> 
> * possessionの一時的切替
> * スコープ限定
> * ownershipは変更しない
> 
> ---
> 
> ## ✔ 本質
> 
> > 「その場だけアクセスルールを上書きする」
> 
> ---
> 
> # ⑦ 全体構造図
> 
> ```text id="model"
> Type
>   ↓
> mut/let（Ownership初期状態）
>   ↓
> possession（型構造に1対1対応）
>   ↓
> hold / grab（実行時アクセス）
>   ↓
> anchor（possessionの一時切替）
> ```
> 
> ---
> 
> # ⑧ 設計の特徴
> 
> ## ✔ 良い点
> 
> * 型と権限が分離されている
> * possessionが再帰しないため単純
> * Rustより軽量な所有モデル
> * Cに近い直感性
> 
> ---
> 
> ## ⚠ 制約（意図的）
> 
> * possessionは型構造に完全従属
> * ネストpossession禁止
> * anchorは一時スコープ限定
> 
> ---
> 
> # ⑨ 設計思想の核
> 
> > **Typeは構造、Ownershipは状態、Possessionは構造に従属する制約、Accessは実行時操作**
> 
> ---
> 
> # ⑩ 一言まとめ
> 
> > **この言語は「型構造に従うフラットなpossessionモデル＋明示的な参照操作」を持つ設計**
> 
> ---
> 
> 必要なら次はかなり重要で：
> 
> 👉 **「AST表現（Typeノードにpossessionを埋めるか分離するか）」**
> 
> ここでコンパイラ設計の形がほぼ確定します。
> 