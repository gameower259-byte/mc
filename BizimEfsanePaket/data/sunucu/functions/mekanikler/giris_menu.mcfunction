# GİRİŞ MENÜSÜ (Dinamik)
execute as @a[scores={secim=0,giris=0}] run tellraw @s ["",{"text":"HOŞ GELDİN! BİR TARAF SEÇ:\n\n","color":"gold","bold":true},{"text":"[ MAVİ KRALLIK ]","color":"blue","clickEvent":{"action":"run_command","value":"/function sunucu:mekanikler/mavi_ol"}},{"text":"  "},{"text":"[ KIRMIZI KRALLIK ]","color":"red","clickEvent":{"action":"run_command","value":"/function sunucu:mekanikler/kirmizi_ol"}}]
execute as @a[scores={secim=0,giris=0}] run scoreboard players set @s giris 1
execute as @a[scores={secim=0}] run title @s actionbar {"text":"Bir krallık seçmeden savaşamazsın!","color":"yellow"}
