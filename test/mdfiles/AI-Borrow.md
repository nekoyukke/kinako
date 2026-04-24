## `BorrowingChecker` の全体像
`BorrowingChecker` は、AST をたどって各 `Symbol` の借用・移動状態を追跡する仕組みです。  
主に次のデータ構造を使っています。

- `borrow_map: dict[Symbol, Borrow]`
  - 現在のシンボルごとの借用状態
- `borrow_ledger_stack: list[dict[Symbol, Symbol]]`
  - ブロックごとの借用元管理
- `lender_map: dict[Symbol, set[Symbol]]`
  - 誰に借りられているか
- `function_returns: dict[Symbol, ReturnType]`
  - 関数が返すときの Move/Copy 情報

---

## ステートメントごとの実装

### `DeclarationNode`
- 右辺の式を評価して `rab` を取得
- 変数宣言の種類に応じて状態を設定
  - `VAL` / `CONST` の場合は `ACTIVE`
  - `BORROW` の場合は右辺が `Borrow` であることを確認し、左辺に `BORROW` を設定
- `rab` が `None` のときは `ACTIVE`、未初期化なら `UNINIT`

### `ExprStmtNode`
- 単純に式を評価

### `BlockNode`
- `new_Frame()` で新しいフレームを作成
- 中身の文を順に評価
- `pop_Frame()` でフレームを破棄

### `IfStmtNode`
- 条件式を評価
- then / else 両方のスナップショットを比較して `SnapShot_Marge` で統合
- else がない場合は then と直前状態をマージ

### `WhileStmtNode`
- 条件式を評価
- 本体実行後にループ前後のスナップショットをマージ

### `ForNode`
- イテラブル式を評価
- イテレータ変数を `ACTIVE` として登録
- ループ本体評価後にスナップショットをマージ

### `FunctionDefNode`
- 関数シンボルを `ACTIVE` にセット
- current function stack に追加
- 引数をすべて `ACTIVE` にセット
- 本体を評価
- 退出時にスナップショットを元に戻す

### `ReturnStmtNode`
- 返り値式を評価
- `Borrow.MOVED` や `Borrow.UNINIT` などの異常を検出
- 関数の戻り値形式を `ReturnType` に登録

### `ImportNode`
- 現状は無視

---

## 式ごとの実装

### `VariableNode`
- `borrow_map` から状態を読み取り
- `MOVED` / `NONE` ならエラー
- 現在の借用状態を `AnalysisBorrow` で返す

### `AssignNode`
- 左辺が代入可能か `_visit_expr_can_change` で確認
- 右辺を評価
- 左辺が `CONST` / `VAL` なら変更禁止
- 左辺が `BORROW` / `BORROWED` ならエラー
- 左辺を `ACTIVE` に戻す

### `BinaryOpNode`
- 左右の式を評価して現在は `None` を返す
- つまり、二項演算自体は借用状態を変えない

### `UnaryOpNode`
- 右辺を評価して `None` を返す

### `ReferenceNode`
- 内部式を評価し、その元 `Symbol` を `POTENTIAL` として返す
- 参照操作の借用を表す

### `DereferenceNode`
- 内部式を評価し、`POTENTIAL` を返す
- デリファレンスも借用扱い

### `CallExprNode`
- 引数をすべて評価
- 呼び出し対象を `_visit_expr_can_change` で確認
- 関数の戻り値が `ReturnType.MOVE` なら `ACTIVE` を返す

### `Literal()`
- リテラルは借用状態を持たず `None`

### `MemberAccessNode`
- 左辺を評価して `None` を返す

### `IndexAccessNode`
- アドレスとインデックスを評価して `None` を返す

### `AsCastNode`
- キャスト対象を評価して `None`

### `MoveOpNode`
- 右辺を評価し、移動対象の `Symbol` を `Borrow.MOVED` に変更
- 移動の結果を `ACTIVE` として返す

### `BorrowOpNode`
- 右辺を評価
- 既に `BORROW` 状態ならエラー
- 元変数を `BORROWED` にし、戻り値として `Borrow.BORROW` を返す

---

## 補助メソッド

### `get_Snapshot()` / `set_SnapShot()`
- 現在の `borrow_map` をスナップショットとして保存・復元

### `add_SnapShot_value()`
- `borrow_map` に初期状態を挿入

### `new_Frame()` / `pop_Frame()` / `get_Frame()`
- ブロックごとの借用フレーム管理

### `get_borrow()`
- フレームを逆順に検索し、借用元シンボルを返す

### `SnapShot_Marge()`
- 2 つの借用スナップショットを統合
- 同じ `Symbol` で異なる状態ならエラー

### `get_fn_ret()` / `new_fn_ret()`
- 関数の返却方式を記録するための管理

---

## まとめ
この `BorrowingChecker` の実装は、「式をたどって変数の借用／移動状態を追跡し、矛盾や違反を検出する」仕組みです。  
特に重点が置かれているのは次の点です。

- `MoveOpNode` で移動をマーク
- `BorrowOpNode` で借用をマーク
- `DeclarationNode` で変数状態を初期化
- `If/While/For` で分岐後の状態をマージして整合性を保つ

必要なら、各ノードごとにさらに詳細な処理フローも追って説明できます。