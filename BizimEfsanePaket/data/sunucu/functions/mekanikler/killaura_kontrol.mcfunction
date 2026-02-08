execute as @a at @s unless entity @e[tag=killaura_test,distance=..2,limit=1] run summon armor_stand ~ ~ ~ {Tags:["killaura_test"],Invisible:1b,Marker:1b,NoGravity:1b}
execute as @e[tag=killaura_test,nbt={HurtTime:1s..}] at @s run function sunucu:mekanikler/killaura_ceza
