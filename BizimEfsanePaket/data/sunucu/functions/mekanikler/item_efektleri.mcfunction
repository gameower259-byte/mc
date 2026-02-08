# ZIRH VE EŞYA BUFFLARI
execute as @a[nbt={Inventory:[{Slot:103b,tag:{display:{Name:'{"text":"Madenci Kaskı","color":"yellow","italic":false}'}}}]}] run effect give @s night_vision 5 0 true
execute as @a[nbt={Inventory:[{Slot:100b,tag:{display:{Name:'{"text":"Hafif Ayakkabılar","color":"white","italic":false}'}}}]}] run effect give @s jump_boost 5 1 true
execute as @a[nbt={Inventory:[{Slot:100b,tag:{display:{Name:'{"text":"Hız İksiri Botları","color":"aqua","italic":false}'}}}]}] run effect give @s speed 5 0 true
execute as @a[nbt={Inventory:[{Slot:100b,tag:{display:{Name:'{"text":"Ağırlık Çizmesi","color":"dark_purple","italic":false}'}}}]}] run effect give @s resistance 5 0 true
execute as @a[nbt={Inventory:[{Slot:100b,tag:{display:{Name:'{"text":"Su Yürüyüşçüsü","color":"blue","italic":false}'}}}]}] run effect give @s dolphins_grace 5 0 true

execute as @a[nbt={SelectedItem:{tag:{display:{Name:'{"text":"Yakut Kazma","color":"red","italic":false}'}}}}] run effect give @s haste 5 1 true
execute as @a[nbt={SelectedItem:{tag:{display:{Name:'{"text":"Otomatik Eriten Kazma","color":"gold","italic":false}'}}}}] run effect give @s haste 5 2 true
execute as @a[nbt={SelectedItem:{tag:{display:{Name:'{"text":"Can Çalan Kılıç","color":"dark_red","italic":false}'}}}}] run effect give @s regeneration 5 0 true
execute as @a[nbt={SelectedItem:{tag:{display:{Name:'{"text":"Büyülü Ekmek","color":"gold","italic":false}'}}}}] run effect give @s saturation 2 1 true

# ALEVLİ PELERİN
execute as @a[team=mavi,nbt={Inventory:[{Slot:102b,tag:{display:{Name:'{"text":"Alevli Pelerin","color":"gold","italic":false}'}}}]}] at @s run damage @a[team=kirmizi,distance=..3] 1 minecraft:on_fire
execute as @a[team=kirmizi,nbt={Inventory:[{Slot:102b,tag:{display:{Name:'{"text":"Alevli Pelerin","color":"gold","italic":false}'}}}]}] at @s run damage @a[team=mavi,distance=..3] 1 minecraft:on_fire

# EJDERHA ZIRHI
execute as @a[nbt={Inventory:[{Slot:102b,tag:{display:{Name:'{"text":"Ejderha Zırhı","color":"dark_purple","italic":false}'}}}]}] run effect give @s slow_falling 5 0 true

# VAMPİR DİŞİ
execute as @a[nbt={SelectedItem:{tag:{display:{Name:'{"text":"Vampir Dişi","color":"dark_red","italic":false}'}}}}] if data entity @s {Time:13000L..} run effect give @s strength 5 0 true

# KULLANIM ETKİLERİ
function sunucu:mekanikler/use_item_kontrol
