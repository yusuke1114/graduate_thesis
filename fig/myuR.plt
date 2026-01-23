# =========================================================
# Gnuplot Script: Asset Transition (Rule Trader Version)
# =========================================================
# 基本フォント設定: Helvetica, サイズ18
set terminal pngcairo enhanced font "Helvetica,18" size 800, 600
set output "transition_sqrt_sigma_rule.png"

# タイトルなし
unset title

# --- 軸ラベル設定 ---
# Rule Trader用に変更
set xlabel "Rule Trader Ratio (%)" font ",24"
set ylabel "Mean Asset Value ({/Symbol m})" font ",24" offset -1,0

set grid xtics ytics

# 凡例の設定 (枠なし)
set key top right nobox font",20"

# X軸の設定
set xrange [5:55]
set xtics 10

# Y軸の設定
set yrange [0:1000]

set xtics font ",20"
set ytics font ",20"

# --- データ定義 (Rule Traderデータ) ---
# Column 1: Ratio
# Column 2: ZIT Mean
# Column 3: ZIT Sigma
# Column 4: Rule Mean
# Column 5: Rule Sigma
$Data << EOD
10   523.4   27.0   289.6   33.1
20   531.1   27.8   375.6   33.2
30   536.8   28.1   414.1   33.1
40   600.6   28.8   349.1   33.0
50   635.6   29.3   364.4   34.1
EOD

# --- プロット ---
shift = 0.5

plot \
    $Data using ($1-shift):2:3 with yerrorbars lw 1.5 lc rgb "blue" pt 7 ps 1.2 title "ZIT Mean +/- {/Symbol s}", \
    $Data using ($1-shift):2 with lines lw 2 lc rgb "blue" notitle, \
    $Data using ($1+shift):4:5 with yerrorbars lw 1.5 lc rgb "red" pt 7 ps 1.2 title "Rule Mean +/- {/Symbol s}", \
    $Data using ($1+shift):4 with lines lw 2 lc rgb "red" notitle

unset output