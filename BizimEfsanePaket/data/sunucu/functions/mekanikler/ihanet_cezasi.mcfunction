execute as @a[team=mavi] if score @s reach_damage > @s dost_dmg_old if entity @p[team=mavi,distance=..4.5,limit=1] run effect give @s blindness 5 0 true
execute as @a[team=kirmizi] if score @s reach_damage > @s dost_dmg_old if entity @p[team=kirmizi,distance=..4.5,limit=1] run effect give @s blindness 5 0 true
execute as @a run scoreboard players operation @s dost_dmg_old = @s reach_damage
