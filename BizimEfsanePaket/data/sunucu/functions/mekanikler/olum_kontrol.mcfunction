# ÖLÜM VE BAN SİSTEMİ
execute as @a[nbt={Health:0.0f}] run tellraw @a {"text":"[!] BİR KRAL ELENDİ: ","color":"red","extra":[{"selector":"@s","color":"gold"}]}
execute as @a[nbt={Health:0.0f}] run summon lightning_bolt ~ ~ ~
execute as @a[nbt={Health:0.0f}] run ban-ip @s "Krallığın düştü, savaş bitti!"
execute as @a[nbt={Health:0.0f},scores={kral=1}] run summon chest_minecart ~ ~ ~ {CustomName:'{\"text\":\"Kral Ganimeti\"}',LootTable:\"minecraft:chests/end_city_treasure\"}

# Ölümde seri sıfırlama
execute as @a[nbt={Health:0.0f}] run scoreboard players set @s killstreak 0
