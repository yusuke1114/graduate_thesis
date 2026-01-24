# =========================================================
# Gnuplot Script (PNG & PDF Output)
# =========================================================

# データファイルの指定
file_ml  = "asset_ml20.dat"
file_zit = "asset_ml20zit.dat"

# --- 統計量の計算 ---
stats file_ml  using 1 name "M" nooutput
stats file_zit using 1 name "Z" nooutput

print sprintf("ML  Mean: %.2f, StdDev: %.2f, N: %d", M_mean, M_stddev, M_records)
print sprintf("ZIT Mean: %.2f, StdDev: %.2f, N: %d", Z_mean, Z_stddev, Z_records)

# --- 共通のグラフ設定 ---
set xlabel "Asset Value" font "Helvetica,22"
set ylabel "Probability Density" font "Helvetica,22"

# X軸の目盛り
set xtics 2000 font "Helvetica,16"

# Y軸の設定
set yrange [0:*]
set grid xtics ytics

set xtics font ",22"
set ytics font ",22"

# 凡例の設定
set key box opaque width -2 height 0 samplen 1 spacing 1.1 font ",18"
set key nobox

# --- ヒストグラム・分布の設定 ---
binwidth = 250.0

bin(x,width) = width * floor(x/width) + width/2.0
set boxwidth binwidth absolute
set style fill transparent solid 0.5 noborder

pi = 3.141592653589793
gauss(x, mu, sigma) = (1.0/(sigma*sqrt(2*pi))) * exp(-0.5*(((x-mu)/sigma)**2))

set xrange [-4000:5000]

t_zit = sprintf("ZIT Fit ({/Symbol m}=%.0f)", Z_mean)
t_ml  = sprintf("ML Fit ({/Symbol m}=%.0f)", M_mean)


# =========================================================
# 1. PNG 出力
# =========================================================
set terminal pngcairo enhanced font "Helvetica,18" size 800, 600
set output "asset_ml20zit.png"

# プロット実行
plot \
    file_zit using (bin($1,binwidth)):(1.0/(Z_records*binwidth)) smooth frequency with boxes lc rgb "#9999ff" title "ZIT Hist", \
    file_ml  using (bin($1,binwidth)):(1.0/(M_records*binwidth)) smooth frequency with boxes lc rgb "#ff9999" title "ML Hist", \
    gauss(x, Z_mean, Z_stddev) with lines lw 3 lc rgb "blue" title t_zit, \
    gauss(x, M_mean, M_stddev) with lines lw 3 lc rgb "red"  title t_ml


# =========================================================
# 2. PDF 出力 (追加部分)
# =========================================================
# size はインチ指定 (800x600pxに近い比率として 8インチx6インチ を指定)
set terminal pdfcairo enhanced font "Helvetica,18" size 8.0, 6.0
set output "asset_ml20zit.pdf"

# 直前のplotコマンドを再実行
replot

# 出力ファイルを閉じる
unset output