scoreboard players set @s odul 0
item replace entity @s hotbar.8 with minecraft:emerald 2
playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 1
tellraw @s {"text":"Sadakat ödülü kazandın!","color":"green"}
