#!/bin/bash
#
#Remove header
cat plot_data_mem_comp_size.tsv | tail -n +2 > aux.tsv
#
gnuplot << EOF
    reset
    set terminal pdfcairo enhanced color font 'Verdade,9'
    set output "ram_data.pdf"
    set datafile separator "\t"
    
    set style data histogram
    set style histogram cluster
    
    set boxwidth 0.25
    
    set autoscale y
    set xrange [-1:12]
   
    set ytics auto
    set xtics rotate by 45 right
    set ylabel "Memory used"
    set xlabel "Compression Tools"

    set rmargin 5

    plot 'aux.tsv' using (column(0)):0.0:xtic(1) with boxes lc rgb "#ffffff" fill solid 0.5 notitle, \
    'aux.tsv' using (column(0)-0.13):2 with boxes lc rgb "#d3804a" fill solid 0.5 notitle, \
    'aux.tsv' using (column(0)+0.13):3 with boxes lc rgb "#067188" fill solid 0.5 notitle,
    

EOF
#
gnuplot << EOF
    reset
    set terminal pdfcairo enhanced color font 'Verdade,9'
    set output "sum_comp_size.pdf"
    set datafile separator "\t"
    set boxwidth 0.5
    
    spacing_x = 30
    set yrange [:]
    set xrange [-1:12]
   
    set ytics auto
    set xtics rotate by 45 right
    set ylabel "Size of the compressed files"
    set xlabel "Compression Tools"
    set multiplot layout 1,1
    set rmargin 5
    set key at screen 1, graph 1 

    plot "aux.tsv" using 0:4:xtic(1) with boxes lc rgb "#067188" fill solid 0.5 notitle

EOF
