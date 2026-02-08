execute as @a[team=mavi] at @s if block -500 70 -500 minecraft:furnace run setblock -500 70 -500 air
execute as @a[team=kirmizi] at @s if block 500 70 500 minecraft:furnace run setblock 500 70 500 air
playsound minecraft:entity.generic.explode master @s ~ ~ ~ 1 1
