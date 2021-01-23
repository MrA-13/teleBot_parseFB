import os
class DB:
    def __init__(self):
        self.path_to_db_file = self.__init_db_file()
        self.ids_posts = self.__read_file()

    def __init_db_file(self):
        if os.path.isfile("db") is not True:
            with open("db", 'w') as file_db:
                file_db.write('114571847179520\n')
        return "db"

    def __read_file(self):
        with open(self.path_to_db_file, 'r') as file_db:
            ids_posts = file_db.readlines()
        ids_posts = [int(i.rstrip('\n')) for i in ids_posts]
        ids_posts.sort()
        return ids_posts[-1:]

    def __append_to_file(self):
        self.ids_posts.sort()
        if len(self.ids_posts) > 1:
            with open(self.path_to_db_file, 'a') as file_db:
                for id_ in self.ids_posts[1:]:
                    file_db.write(str(id_) + '\n')
        self.ids_posts = self.ids_posts[-1:]
        return True

    def get_last_post_id(self):
        return self.ids_posts[-1]

    def __add_new_ids_to_list(self, new_posts_ids):
        for id_ in new_posts_ids:
            self.ids_posts.append(id_)
        self.__append_to_file()
        return True

    def check_new_post(self, list_of_posts_ids):
        last_post_id = self.get_last_post_id()
        new_posts_ids = list(filter(lambda id_: id_ > last_post_id, [int(id_) for id_ in list_of_posts_ids]))
        self.__add_new_ids_to_list(new_posts_ids)
        return [str(id_) for id_ in new_posts_ids]


class DB_CHENELS:
    def __init__(self):
        self.path_to_db_chennels_file = self.__init_db_file()
        self.chennels = self.__read_file()

    def __init_db_file(self):
        if os.path.isfile("db_chennels") is not True:
            with open("db_chennels", 'w') as file_db:
                file_db.write('@donbasspress\n')
        return "db_chennels"

    def __read_file(self):
        with open(self.path_to_db_chennels_file, 'r') as file_db:
            chennels = file_db.readlines()
        return [i.rstrip('\n') for i in chennels]

    def __write_to_file(self):
        self.chennels = list(set())
        with open(self.path_to_db_chennels_file, 'w') as file_db:
            for line in self.chennels:
                file_db.write(str(line) + '\n')
        return True

    def add_new_chennel_to_list(self, new_chennel):
        if new_chennel not in self.chennels:
            self.chennels.append(new_chennel)
            self.__write_to_file()
        return True

