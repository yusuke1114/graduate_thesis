# --- 設定 ---
set terminal pdfcairo enhanced font "Arial,10" size 6in, 5in
set output "confusion_matrix.pdf"

# タイトルと軸ラベル
set xlabel "Predicted Label"
set ylabel "Actual Label"

# 軸の範囲と目盛り設定
# ラベルの定義
array labels[5] = ["Sell Overwrite", "Buy Overwrite", "Sell Execution", "Buy Execution", "Failure"]

# 範囲設定
set xrange [-0.5 : 4.5]
set yrange [4.5 : -0.5] reverse

# 目盛りをラベルに置き換え
set xtics 0,1,4
set ytics 0,1,4
set xtics ("Sell Overwrite" 0, "Buy Overwrite" 1, "Sell Execution" 2, "Buy Execution" 3, "Failure" 4) rotate by -45
set ytics ("Sell Overwrite" 0, "Buy Overwrite" 1, "Sell Execution" 2, "Buy Execution" 3, "Failure" 4)

# ヒートマップの設定
set palette defined (0 "white", 1 "blue")
set cbrange [0:1]  # 規格化されているため0〜1に固定推奨（自動なら [0:*]）
unset key

# --- プロット ---
# ★修正箇所: sprintf("%d", $3) → sprintf("%.6f", $3) に変更
# %.2f は小数点以下6桁まで表示するという意味です。4桁で良ければ %.4f にしてください。
plot "confusion_matrix.dat" using 1:2:3 with image, \
     "confusion_matrix.dat" using 1:2:(sprintf("%.4f", $3)) with labels font ",10"