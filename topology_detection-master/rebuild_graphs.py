import draw_topology

uid_list=[
    "5e57e3f9e2524d19193ea4bd",
    "5e57e409e2524d19193ea4be",
    "5e57e41fe2524d19193ea4bf",
    "5ea00c0309003408280a6c1c",
    "5eedc687b8d222311a2ebc92",
    "5f0ac15d08e1491af858bf33",
    "5f0ac25708e1491af858bf34",
    "5f12844e178008235d0f196c",
    "5f4cb42dcea52208fd3b5663",
    "5f5c9115cea52208fd42d79a",
    "5f5c9139cea52208fd42d7af",
    "5f8ead8ae43c6383f1116065",
    "5f8ee64fe43c6383f11160a4",
    "5f8fdeeae43c6383f11161d0",
    "5f8fdef8e43c6383f11161d1",
    "5fed846762b96ba7cf97f3cc",
    "60165f78301eb82b5fdb782a",
    "608065a49a11510cb282f23a",
    "609663119ecd7c4460c7c7c7",
    "60c1dc1f652e21df2dc79021",
    "60c8d937c062e32ac539ef9d",
    "60f41b367b849521350189f9",
    "6180e69b684254f2e6c44339",
    "6180e6ab684254f2e6c4433a",
    "61c89a2b6b915eca053df4bd",
    "61cfe5409d9b8c5e8ab0a5cd",
    "61e27ac30dc90294533847fa",
    "61e7fb10c6baf7aaf288328e",
    "61ee938a261b640a7fba5a8b",
    "61f3728475c280b7177e876e"
]


def rebuild():
    for uid in uid_list:
        draw_topology.draw_with_uid(uid)