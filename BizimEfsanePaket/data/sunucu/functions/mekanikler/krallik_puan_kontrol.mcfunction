# ORTA NOKTA PUANLAMA
execute positioned 0 80 0 as @a[distance=..5,team=mavi] run scoreboard players add $mavi krallik_puan 1
execute positioned 0 80 0 as @a[distance=..5,team=kirmizi] run scoreboard players add $kirmizi krallik_puan 1

execute if score $mavi krallik_puan matches 90..99 run title @a title {"text":"Mavi Krallık 10'a yaklaştı!","color":"blue"}
execute if score $kirmizi krallik_puan matches 90..99 run title @a title {"text":"Kırmızı Krallık 10'a yaklaştı!","color":"red"}

execute if score $mavi krallik_puan matches 100.. run function sunucu:mekanikler/mavi_zafer
execute if score $kirmizi krallik_puan matches 100.. run function sunucu:mekanikler/kirmizi_zafer
