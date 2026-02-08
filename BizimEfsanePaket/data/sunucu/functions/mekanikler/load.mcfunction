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
scoreboard objectives add walk_cm minecraft.custom:minecraft.walk_one_cm
scoreboard objectives add old_walk dummy
scoreboard objectives add speed_timer dummy
scoreboard objectives add speed_delta dummy
scoreboard objectives add air_time dummy
scoreboard objectives add diamond_mined minecraft.mined:minecraft.diamond_ore
scoreboard objectives add old_diamond dummy
scoreboard objectives add mining_timer dummy
scoreboard objectives add reach_damage minecraft.custom:minecraft.damage_dealt
scoreboard objectives add old_reach_damage dummy
scoreboard objectives add dost_dmg_old dummy
scoreboard objectives add verify dummy
scoreboard objectives add dogrulama dummy
scoreboard objectives add soru_a dummy
scoreboard objectives add soru_b dummy
scoreboard objectives add cevap trigger
scoreboard objectives add ping dummy
scoreboard objectives add baris_sure dummy
scoreboard objectives add bayrak_puan dummy
scoreboard objectives add savas_sure dummy
scoreboard objectives add son_direnis dummy
scoreboard objectives add use_item minecraft.used:minecraft.carrot_on_a_stick
scoreboard objectives add old_use_item dummy

team add mavi
team modify mavi color blue
team modify mavi friendlyFire false
team add kirmizi
team modify kirmizi color red
team modify kirmizi friendlyFire false

scoreboard players set $mavi krallik_puan 0
scoreboard players set $kirmizi krallik_puan 0
