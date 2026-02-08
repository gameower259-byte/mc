# DÜŞMAN ÜS İHLALİ UYARISI
execute positioned 500 70 500 as @a[distance=..25,team=kirmizi] run effect give @s slowness 2 1 true
execute positioned 500 70 500 as @a[distance=..25,team=kirmizi] run title @s actionbar {"text":"Mavi üssüne çok yaklaştın!","color":"blue"}
execute positioned -500 70 -500 as @a[distance=..25,team=mavi] run effect give @s slowness 2 1 true
execute positioned -500 70 -500 as @a[distance=..25,team=mavi] run title @s actionbar {"text":"Kırmızı üssüne çok yaklaştın!","color":"red"}
