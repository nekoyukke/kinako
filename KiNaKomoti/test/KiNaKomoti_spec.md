# KiNaKomoti 言語仕様メモ

## 所有権と参照のルール

### 値型

-   `Int`, `Bool`, `Str`, `Struct`, `Tuple`, `Array`, `Map`
-   `&copy` → ディープコピー（全フィールドコピー）
-   `&move` → 実体を移動（元は無効化）

### 参照型

-   `&mut`
    -   強い可変更借用
    -   `&copy` → ポインタコピー（元は無効）
    -   `&move` → ポインタ所有権を移動（元は無
-   `ref`
    -   弱い可変更借用
    -   `&mut`・`&borrow`と共存可
    -   `&copy` → ポインタコピー（元は無効）
    -   `&move` → ポインタ所有権を移動（元は無効化）
-   `&borrow`
    -   `&mut`と共存不可
    -   不変更借用
    -   `&copy` → ポインタコピー（元も有効）
    -   `&move` → **`&borrow`
        と同値**（所有権がないため移動しても意味なし）

## 返り値のルール

-   返せるのは **値型** のみ。
    -   `&copy` → ディープコピーを返す
    -   `&move` → 所有権を移動して返す
-   **参照型 (`&mut`, `ref`, `&borrow`) は返せない**
    -   スコープ終了時に破棄されるため参照切れになる

## 使用例

### 値のコピーとムーブ

``` c
define clone_array:Array<Int>(a:Array<Int>) {
    return &copy a; // ディープコピー
}

define take_array:Array<Int>(a:Array<Int>) {
    return &move a; // 所有権移動
}
```

### 参照のコピーとムーブ

``` c
let arr:Array<Int> = [1,2,3];

// &mut の move
val p:&mut<Array<Int>> = &mut arr;
val q:&move<&mut<Array<Int>>> = &move p;
p[0] = 10;   // エラー: p は無効
q[0] = 20;   // OK

// &borrow の move
let b:&borrow<Array<Int>> = &borrow arr;
let c:&move<&borrow<Array<Int>>> = &move b; // 実際は &borrow と同じ
b[0]; // OK
c[0]; // OK
```

## ポイント整理

-   `&mut` / `ref` → 「所有権を持つ参照」なので move で無効化される
-   `&borrow` → 「所有権を持たない参照」なので move
    しても意味が変わらない
-   関数から返せるのは **コピーかムーブされた実体のみ**
-   借用は必ず関数スコープ内で完結する
