# KRAL TACİ PARÇACIKLARI
execute as @a[scores={kral=1}] at @s run particle dust 1 0.84 0 1 ~ ~2.2 ~ 0.2 0.2 0.2 0.01 10 force @a

# SAVAŞ NARASI (Kral, boynuz elde)
execute as @a[scores={kral=1},nbt={SelectedItem:{id:"minecraft:goat_horn",tag:{display:{Name:'{"text":"Savaş Narası","color":"gold","italic":false}'}}}}] at @s run effect give @a[team=mavi,distance=..10] resistance 10 0 true
execute as @a[scores={kral=1},nbt={SelectedItem:{id:"minecraft:goat_horn",tag:{display:{Name:'{"text":"Savaş Narası","color":"gold","italic":false}'}}}}] at @s run effect give @a[team=kirmizi,distance=..10] resistance 10 0 true

# İHANET CEZASI
function sunucu:mekanikler/ihanet_cezasi

# SINIR MUHAFIZLARI
execute positioned 500 70 500 as @a[team=kirmizi,distance=..12] run effect give @s levitation 1 0 true
execute positioned -500 70 -500 as @a[team=mavi,distance=..12] run effect give @s levitation 1 0 true

# BAYRAK TAŞIMA
execute as @a[team=mavi,nbt={SelectedItem:{id:"minecraft:red_banner"}}] positioned 500 70 500 if entity @s[distance=..4] run function sunucu:mekanikler/bayrak_mavi
execute as @a[team=kirmizi,nbt={SelectedItem:{id:"minecraft:blue_banner"}}] positioned -500 70 -500 if entity @s[distance=..4] run function sunucu:mekanikler/bayrak_kirmizi

# CASUS MODU
execute as @a[team=mavi,nbt={SelectedItem:{tag:{display:{Name:'{"text":"Casus Maskesi","color":"gray","italic":false}'}}}}] positioned -500 70 -500 if entity @s[distance=..30] run effect give @s invisibility 5 0 true
execute as @a[team=mavi,nbt={SelectedItem:{tag:{display:{Name:'{"text":"Casus Maskesi","color":"gray","italic":false}'}}}}] positioned -500 70 -500 if entity @s[distance=..30] run effect give @s slowness 5 1 true
execute as @a[team=kirmizi,nbt={SelectedItem:{tag:{display:{Name:'{"text":"Casus Maskesi","color":"gray","italic":false}'}}}}] positioned 500 70 500 if entity @s[distance=..30] run effect give @s invisibility 5 0 true
execute as @a[team=kirmizi,nbt={SelectedItem:{tag:{display:{Name:'{"text":"Casus Maskesi","color":"gray","italic":false}'}}}}] positioned 500 70 500 if entity @s[distance=..30] run effect give @s slowness 5 1 true

# BÖLGE KONTROLÜ HAVAİ FİŞEK
execute positioned 0 80 0 as @a[distance=..5,team=mavi] run summon firework_rocket ~ ~1 ~ {LifeTime:10}
execute positioned 0 80 0 as @a[distance=..5,team=kirmizi] run summon firework_rocket ~ ~1 ~ {LifeTime:10}

# DİPLOMASİ MASASI (KRALLAR YAKINSA)
execute as @a[scores={kral=1,baris_sure=0}] if entity @a[scores={kral=1},distance=..2] run function sunucu:mekanikler/baris_baslat
execute as @a[scores={baris_sure=1..}] run scoreboard players remove @s baris_sure 1

# PARALI ASKERLER
execute as @a[nbt={SelectedItem:{id:"minecraft:gold_ingot"}}] at @s if entity @e[type=villager,distance=..2,limit=1] run summon iron_golem ~ ~ ~

# KELLE AVCISI
function sunucu:mekanikler/kelle_avcisi

# SAVAŞ TAZMİNATI
function sunucu:mekanikler/savas_tazminati

# İSTİLA UYARISI
execute positioned 500 70 500 as @a[team=kirmizi,distance=..25] run tellraw @a[scores={kral=1,team=mavi}] {"text":"İstila uyarısı: Düşman mavi üste!","color":"red"}
execute positioned -500 70 -500 as @a[team=mavi,distance=..25] run tellraw @a[scores={kral=1,team=kirmizi}] {"text":"İstila uyarısı: Düşman kırmızı üste!","color":"red"}

# KUTSAL ALAN
execute unless block 500 70 500 minecraft:blast_furnace run effect give @a[team=mavi] weakness 2 0 true
execute unless block -500 70 -500 minecraft:blast_furnace run effect give @a[team=kirmizi] weakness 2 0 true

# CESARET ÖDÜLÜ
scoreboard players add @a savas_sure 1
execute as @a[scores={savas_sure=1200..}] run function sunucu:mekanikler/cesaret_odulu

# İSİM GİZLEME
execute as @a[team=mavi] positioned -500 70 -500 if entity @s[distance=..25] run effect give @s invisibility 2 0 true
execute as @a[team=kirmizi] positioned 500 70 500 if entity @s[distance=..25] run effect give @s invisibility 2 0 true
