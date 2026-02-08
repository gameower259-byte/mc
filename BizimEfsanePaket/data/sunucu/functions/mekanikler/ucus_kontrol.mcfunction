execute as @a if data entity @s {OnGround:0b} if block ~ ~-1 ~ air run scoreboard players add @s air_time 1
execute as @a if data entity @s {OnGround:1b} run scoreboard players set @s air_time 0
execute as @a[scores={air_time=60..}] run tp @s ~ ~-2 ~
execute as @a[scores={air_time=60..}] run tellraw @s {"text":"Uçuş algılandı, yere çekildin.","color":"red"}
execute as @a[scores={air_time=60..}] run scoreboard players set @s air_time 0
