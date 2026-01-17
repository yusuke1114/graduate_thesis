# =========================================================
# Gnuplot Script (Modified)
# =========================================================
# ★変更点1: PNG出力用に変更し、全体のフォントサイズを14→18に拡大
# size はピクセル指定 (800x600推奨)
set terminal pngcairo enhanced font "Helvetica,18" size 800, 600
set output "asset_ml10zit.png"

# データファイルの指定
file_ml  = "asset_ml10.dat"
file_zit = "asset_ml10zit.dat"

# --- 統計量の計算 ---
stats file_ml  using 1 name "M" nooutput
stats file_zit using 1 name "Z" nooutput

print sprintf("ML  Mean: %.2f, StdDev: %.2f, N: %d", M_mean, M_stddev, M_records)
print sprintf("ZIT Mean: %.2f, StdDev: %.2f, N: %d", Z_mean, Z_stddev, Z_records)

# --- グラフ設定 ---

# ★変更点2: 軸ラベル（X, Yのタイトル）をさらに大きく強調する場合
set xlabel "Asset Value" font "Helvetica,22"
set ylabel "Probability Density" font "Helvetica,22"

# ★変更点3: X軸の目盛りを2000刻みに設定
# set xtics <間隔>
set xtics 2000 font "Helvetica,16"  # 目盛りの数字自体のフォントサイズも指定可能

# Y軸の設定（必要なら）
set yrange [0:*]
set grid xtics ytics

set xtics font ",22"
set ytics font ",22"

# 凡例の設定
set key box opaque width -2 height 0 samplen 1 spacing 1.1 font ",18"
set key nobox

# --- ヒストグラム・分布の設定 ---
binwidth = 100.0
bin(x,width) = width * floor(x/width) + width/2.0
set boxwidth binwidth absolute
set style fill transparent solid 0.5 noborder

pi = 3.141592653589793
gauss(x, mu, sigma) = (1.0/(sigma*sqrt(2*pi))) * exp(-0.5*(((x-mu)/sigma)**2))

set xrange [-4000:5000]

t_zit = sprintf("ZIT Fit ({/Symbol m}=%.0f)", Z_mean)
t_ml  = sprintf("ML Fit ({/Symbol m}=%.0f)", M_mean)

# --- プロット実行 ---
plot \
    file_zit using (bin($1,binwidth)):(1.0/(Z_records*binwidth)) smooth frequency with boxes lc rgb "#9999ff" title "ZIT Hist", \
    file_ml  using (bin($1,binwidth)):(1.0/(M_records*binwidth)) smooth frequency with boxes lc rgb "#ff9999" title "ML Hist", \
    gauss(x, Z_mean, Z_stddev) with lines lw 3 lc rgb "blue" title t_zit, \
    gauss(x, M_mean, M_stddev) with lines lw 3 lc rgb "red"  title t_ml

unset output