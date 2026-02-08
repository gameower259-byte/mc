execute as @a[scores={verify=0,dogrulama=0}] run scoreboard players random @s soru_a 1 9
execute as @a[scores={verify=0,dogrulama=0}] run scoreboard players random @s soru_b 1 9
execute as @a[scores={verify=0,dogrulama=0}] run scoreboard players operation @s dogrulama = @s soru_a
execute as @a[scores={verify=0,dogrulama=0}] run scoreboard players operation @s dogrulama += @s soru_b
execute as @a[scores={verify=0,dogrulama=0}] run tellraw @s {"text":"Doğrulama: ","color":"yellow","extra":[{"score":{"name":"@s","objective":"soru_a"}},{"text":" + ","color":"white"},{"score":{"name":"@s","objective":"soru_b"}},{"text":" = ? /trigger cevap set <sonuc>","color":"white"}]}

execute as @a[scores={verify=0}] if score @s cevap = @s dogrulama run function sunucu:mekanikler/dogrulama_basarili
execute as @a[scores={verify=0}] run effect give @s slowness 2 2 true
