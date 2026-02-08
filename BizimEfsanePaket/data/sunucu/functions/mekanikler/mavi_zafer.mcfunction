scoreboard players set $mavi krallik_puan 0
scoreboard players set $kirmizi krallik_puan 0
playsound minecraft:ui.toast.challenge_complete master @a ~ ~ ~ 1 1
tellraw @a {"text":"Mavi Krallık orta nokta zaferini kazandı!","color":"blue"}
