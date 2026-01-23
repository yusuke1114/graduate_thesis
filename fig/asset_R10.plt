# =========================================================
# Gnuplot Script (Rule Trader Version)
# =========================================================
# ★変更点1: PNG出力、フォントサイズ18
set terminal pngcairo enhanced font "Helvetica,18" size 800, 600
set output "asset_Rule10_dist.png"

# データファイルの指定
# ※ファイル名はご提示いただいたRule用のものを維持
file_rule = "asset_Rule10.dat"
file_zit  = "asset_Rule10zit.dat"

# --- 統計量の計算 ---
# 変数名を M (ML) から R (Rule) に変更
stats file_rule using 1 name "R" nooutput
stats file_zit  using 1 name "Z" nooutput

print sprintf("Rule Mean: %.2f, StdDev: %.2f, N: %d", R_mean, R_stddev, R_records)
print sprintf("ZIT  Mean: %.2f, StdDev: %.2f, N: %d", Z_mean, Z_stddev, Z_records)

# --- グラフ設定 ---

set xlabel "Asset Value" font "Helvetica,22"
set ylabel "Probability Density" font "Helvetica,22"

# ★変更点3: X軸の目盛りを2000刻み
set xtics 2000 font "Helvetica,16"

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

# ラベルを Rule に変更
t_zit  = sprintf("ZIT Fit ({/Symbol m}=%.0f)", Z_mean)
t_rule = sprintf("Rule Fit ({/Symbol m}=%.0f)", R_mean)

# --- プロット実行 ---
# Ruleの色を赤(#ff9999)から緑(#99ff99 / forest-green)に変更して区別しやすくしています
plot \
    file_zit  using (bin($1,binwidth)):(1.0/(Z_records*binwidth)) smooth frequency with boxes lc rgb "#9999ff" title "ZIT Hist", \
    file_rule using (bin($1,binwidth)):(1.0/(R_records*binwidth)) smooth frequency with boxes lc rgb "#99ff99" title "Rule Hist", \
    gauss(x, Z_mean, Z_stddev) with lines lw 3 lc rgb "blue" title t_zit, \
    gauss(x, R_mean, R_stddev) with lines lw 3 lc rgb "forest-green" title t_rule

unset output