scoreboard players set @a speed_timer 0
execute as @a run scoreboard players operation @s speed_delta = @s walk_cm
execute as @a run scoreboard players operation @s speed_delta -= @s old_walk
execute as @a[scores={speed_delta=1501..}] run tp @s 0 80 0
execute as @a[scores={speed_delta=1501..}] run tellraw @s {"text":"Hız sınırı aşıldı, başlangıca çekildin.","color":"red"}
execute as @a run scoreboard players operation @s old_walk = @s walk_cm
