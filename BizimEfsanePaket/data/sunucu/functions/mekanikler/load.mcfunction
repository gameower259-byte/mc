scoreboard objectives add secim dummy
scoreboard objectives add killstreak dummy
scoreboard objectives add krallik_puan dummy
scoreboard objectives add kral dummy
scoreboard objectives add giris dummy
scoreboard objectives add base_sure dummy
scoreboard objectives add odul dummy
scoreboard objectives add horn_cooldown dummy
scoreboard objectives add player_kills minecraft.custom:minecraft.player_kills
scoreboard objectives add old_kills dummy

team add mavi
team modify mavi color blue
team modify mavi friendlyFire false
team add kirmizi
team modify kirmizi color red
team modify kirmizi friendlyFire false

scoreboard players set $mavi krallik_puan 0
scoreboard players set $kirmizi krallik_puan 0
