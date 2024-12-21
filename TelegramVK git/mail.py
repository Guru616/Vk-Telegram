import os
import json
from Vk_modul import get_post_vk
from TG_modul import maintg
import asyncio
from config import  NAMES_GROUP_LIST
#Приложения для сбора постов из Вконтакте, и отправкой их в канал телеграма
# Для работы вставьте свои данные в файле Config
def main():
    for name_group in NAMES_GROUP_LIST:
        posts_from_vk = get_post_vk(name_group)
        #print(str(posts_from_vk) + '\n\n\n')

        #Запись поста в файл
        #Проверка создания папки с группами
        while os.path.exists(f"Data_group_vk/{name_group}/posts_text.json") == False:
            #Проверка существования папки для групп
            if os.path.exists(f"Data_group_vk"):
                #Проверка существования папки группы
                if os.path.exists(f"Data_group_vk/{name_group}"):
                    print(f"Data_group_vk/{name_group} уже существует")

                    #Проверка существования файла с id постов
                    if not os.path.exists(f"Data_group_vk/{name_group}/id_posts.txt"):
                        with open(f"Data_group_vk/{name_group}/id_posts.txt", "w") as file:
                            for post in posts_from_vk:
                                file.write(str(post['id']) + "\n")
                        print(f"Файла id {name_group} нет,создание...")
                    else:
                        with open(f"Data_group_vk/{name_group}/id_posts.txt", "w") as file:
                            for post in posts_from_vk:
                                file.write(str(post['id']+'') + "\n")
                        print(f'файл id {name_group} есть, запись id!')

                    #Проверка существования файла с постом
                    if not os.path.exists(f"Data_group_vk/{name_group}/posts_text.json"):
                        with open(f"Data_group_vk/{name_group}/posts_text.json", "w", encoding="utf-8") as file:
                            json.dump(posts_from_vk, file, indent=2, ensure_ascii=False)
                        print(f"Файла {name_group} нет,создание...")
                    else:
                        print(f"Запись {name_group}!")
                        with open(f"Data_group_vk/{name_group}/posts_text.json", "w", encoding="utf-8") as file:
                            json.dump(posts_from_vk, file, indent=2, ensure_ascii=False)
                else:
                    os.mkdir(f"Data_group_vk/{name_group}")
            else:
                os.mkdir(f"Data_group_vk")


if __name__ == '__main__':
    main()
    asyncio.run(maintg())