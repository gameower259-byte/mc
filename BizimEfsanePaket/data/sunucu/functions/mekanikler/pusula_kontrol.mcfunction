# KRALLIK PUSULASI - ÜSSE DÖNÜŞ
execute as @a[scores={horn_cooldown=1..}] run scoreboard players remove @s horn_cooldown 1

execute as @a[team=mavi,nbt={SelectedItem:{id:"minecraft:compass",tag:{display:{Name:'{"text":"Krallık Pusulası","color":"gold","italic":false}'}}}},scores={horn_cooldown=0}] run function sunucu:mekanikler/pusula_mavi
execute as @a[team=kirmizi,nbt={SelectedItem:{id:"minecraft:compass",tag:{display:{Name:'{"text":"Krallık Pusulası","color":"gold","italic":false}'}}}},scores={horn_cooldown=0}] run function sunucu:mekanikler/pusula_kirmizi
