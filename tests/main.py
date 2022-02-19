from py4mc import api

mojang = api.MojangApi()

profiles = [
    "Notch",
    "ez",
    "1234567890qwertyuiopasdfg",
    "capslock321",
    "dog",
    "bob",
    "MojangSucksDick",
    "dog_man_epic",
    "codertim",
    "Steve",
    "ec561538f3fd461daff5086b22154bce",
    "7d043c7389524696bfba571c05b6aec0",
    "cf7e569c-6e99-11ec-90d6-0242ac120003",
    "e2c16de7-6bab-47b1-beaa-85f8c8c54971",
    "dfasfdasfdasfdasfa",
    "dsioafjaiosdjfioa",
    "Alex",
]

invalid_names = [
    "d664f4b4d6884d289fbd3d58ef2844b4",
    "8667ba71b85a4004af54457a9734eed7",
    "069a79f444e94726a5befca90e38aaf5",
    "d664f4b4d6884d289fbd3d58ef2844b4",
    "Æthelstan",
    "fdadfdassasdfghjkkkkkkkkkk",
    "fjiodasjfiojasdiojfioa",
]

"""profiles = mojang.get_user(profiles)

for profile in profiles:
    print(f"UUID: {profile.uuid} | Name: {profile.username}")
    print(f"Name History:\n {profile.name_history()}")"""

print(mojang.get_user("dasfdasfasdasfasdgad"))

print(mojang.get_user("capslock321"))

print(mojang.get_user("Hypermnesia").default_skin())

print(mojang.get_blocked_servers())

print(mojang.get_statistics(["item_sold_minecraft", "prepaid_card_redeemed_minecraft"]))
