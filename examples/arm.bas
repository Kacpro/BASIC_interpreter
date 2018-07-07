10 input n
20 for i = 1 to n
30 let r = 0
40 let j = i
50 let l = 0
60 while j != 0
70 let l = l + 1
80 let j = j // 10
90 wend 
100 let j = i
110 while j != 0
120 let r = r + (( j % 10) ** l )
130 let j = j // 10
140 wend 
150 if r == i then print i
160 next