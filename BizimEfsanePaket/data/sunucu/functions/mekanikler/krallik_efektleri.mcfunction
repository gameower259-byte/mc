# ÜS BÖLGESİ BUFFLARI
execute positioned 500 70 500 as @a[distance=..20,team=mavi] run effect give @s regeneration 3 0 true
execute positioned -500 70 -500 as @a[distance=..20,team=kirmizi] run effect give @s regeneration 3 0 true

# KRAL GÜÇLENDİRME
execute as @a[scores={kral=1}] run effect give @s resistance 5 0 true
execute as @a[scores={kral=1}] run effect give @s glowing 5 0 true
