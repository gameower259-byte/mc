execute as @a if score @s reach_damage > @s old_reach_damage unless entity @p[distance=..4.5,limit=1] run effect give @s weakness 3 1 true
execute as @a if score @s reach_damage > @s old_reach_damage unless entity @p[distance=..4.5,limit=1] run tellraw @s {"text":"Şüpheli uzak vuruş tespit edildi.","color":"yellow"}
execute as @a run scoreboard players operation @s old_reach_damage = @s reach_damage
