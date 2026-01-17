set terminal pdfcairo font "Helvetica,14"
set output "ccdf_20.pdf"
set xrange [1e-2:10]
set yrange [1e-3:1]
set key at 0.2,0.003
set log xy
set xlabel "Normalized Asset"
set ylabel "CCDF"
p "ccdf_20.dat" ps 0.5 pt 6 lc "blue" t "Simulation Data (All)"\
,1-erf(x/sqrt(2.0)) lt 1 lc "black" t "Standard Normal"
