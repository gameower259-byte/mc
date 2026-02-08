team join mavi @s
scoreboard players set @s secim 1
scoreboard players set @s giris 1
spawnpoint @s 500 70 500
tp @s 500 70 500
clear @s minecraft:stone_sword
clear @s minecraft:bread
item replace entity @s weapon.mainhand with minecraft:stone_sword
item replace entity @s hotbar.1 with minecraft:bread 16
tellraw @s {"text":"Mavi Krallığa katıldın!","color":"blue"}
