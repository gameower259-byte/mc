scoreboard players set @a mining_timer 0
execute as @a run scoreboard players operation @s speed_delta = @s diamond_mined
execute as @a run scoreboard players operation @s speed_delta -= @s old_diamond
execute as @a[scores={speed_delta=11..}] run tag @s add supheli_maden
execute as @a[scores={speed_delta=11..}] run tellraw @a {"text":"[Anti-Hile] Şüpheli maden: ","color":"red","extra":[{"selector":"@s","color":"yellow"}]}
execute as @a run scoreboard players operation @s old_diamond = @s diamond_mined
