# KILLSTREAK TAKİBİ
execute as @a if score @s player_kills > @s old_kills run scoreboard players add @s killstreak 1
execute as @a if score @s player_kills > @s old_kills run scoreboard players operation @s old_kills = @s player_kills

# ÖDÜL EŞİKLERİ
execute as @a[scores={killstreak=3}] run effect give @s speed 10 0 true
execute as @a[scores={killstreak=5}] run effect give @s strength 10 0 true
execute as @a[scores={killstreak=10}] run tellraw @a {"text":"[!] EFSANE SERİ: ","color":"gold","extra":[{"selector":"@s","color":"yellow"}]}
