# =========================================================
# Gnuplot Script: Asset Transition (PNG, Helvetica 18, No Title)
# =========================================================
# 基本フォント設定: Helvetica, サイズ18
set terminal pngcairo enhanced font "Helvetica,18" size 800, 600
set output "transition_sqrt_sigma.png"

# タイトルなし
unset title

# --- 変更点: ここで個別にフォントサイズを指定します ---
# ",24" とすることで、フォント種類は継承し、サイズだけ24にします
set xlabel "ML Trader Ratio (%)" font ",24"
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

# --- データ定義 ---
$Data << EOD
10   460.8   27.1   852.7   31.7
20   419.7   27.7   821.3   33.6
30   349.1   27.9   852.0   33.1
40   279.5   27.6   830.7   32.0
50   160.9   28.5   839.1   30.7
EOD

# --- プロット ---
shift = 0.5

plot \
    $Data using ($1-shift):2:3 with yerrorbars lw 1.5 lc rgb "blue" pt 7 ps 1.2 title "ZIT Mean +/- {/Symbol s}", \
    $Data using ($1-shift):2 with lines lw 2 lc rgb "blue" notitle, \
    $Data using ($1+shift):4:5 with yerrorbars lw 1.5 lc rgb "red" pt 7 ps 1.2 title "ML Mean +/- {/Symbol s}", \
    $Data using ($1+shift):4 with lines lw 2 lc rgb "red" notitle

unset output