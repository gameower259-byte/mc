execute as @a if score @s use_item > @s old_use_item run function sunucu:mekanikler/use_item_tetik
execute as @a run scoreboard players operation @s old_use_item = @s use_item
