# =========================================================
# Gnuplot Script (Debug Mode)
# =========================================================
set terminal pdf enhanced font "Arial,12" size 6in, 4in
set datafile separator whitespace
pi = 3.141592653589793

# ループ設定
pcts = "50"  # まずは50%だけで確認

print "--- Gnuplot Debug Start ---"

do for [p in pcts] {
    
    label = p . "pct"
    print ">> Processing: " . label
    
    # ファイル名
    file_zit = "fig_ml/asset_raw_" . label . "_zit.dat"
    file_ml  = "fig_ml/asset_raw_" . label . "_ml.dat"
    
    # ★デバッグ出力: 統計量を計算して画面に表示
    stats file_zit using 1 name "Z"
    print "   [CHECK] ZIT File: ", file_zit
    print "   [CHECK] ZIT Mean: ", Z_mean, " (Should be approx 161)"
    
    stats file_ml using 1 name "M"
    print "   [CHECK] ML File:  ", file_ml
    print "   [CHECK] ML Mean:  ", M_mean, " (Should be approx 839)"

    # --- グラフ描画 ---
    output_file = "fig_ml/graph_asset_compare_" . label . ".pdf"
    set output output_file
    
    unset title
    set xlabel "Asset Value"
    set ylabel "Probability Density"
    set grid xtics ytics
    set key top right box opaque
    
    # ヒストグラム設定
    binwidth = 100.0 
    bin(x,width) = width * floor(x/width) + width/2.0
    set boxwidth binwidth absolute
    set style fill transparent solid 0.4 noborder
    
    # 密度変換
    dens_z = 1.0 / (Z_records * binwidth)
    dens_m = 1.0 / (M_records * binwidth)
    
    gauss(x, mu, sigma) = (1.0/(sigma*sqrt(2*pi))) * exp(-0.5*(((x-mu)/sigma)**2))
    
    set xrange [-4000:5000]
    set yrange [0:*]
    
    t_zit = sprintf("ZIT ({/Symbol m}=%.0f)", Z_mean)
    t_ml  = sprintf("ML ({/Symbol m}=%.0f)", M_mean)
    
    plot \
      file_zit using (bin($1,binwidth)):(dens_z) smooth frequency with boxes lc rgb "#9999ff" title "ZIT Hist", \
      file_ml  using (bin($1,binwidth)):(dens_m) smooth frequency with boxes lc rgb "#ff9999" title "ML Hist", \
      gauss(x, Z_mean, Z_stddev) with lines lw 3 dt 1 lc rgb "blue" title t_zit, \
      gauss(x, M_mean, M_stddev) with lines lw 3 dt 1 lc rgb "red"  title t_ml
         
    unset output
}

print "--- Check the terminal output for Mean values ---"