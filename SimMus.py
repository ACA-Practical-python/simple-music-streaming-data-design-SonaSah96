import string
import datetime
import uuid
import os
import time


class Methods:
    FILE_PATH = os.path.normpath("./data/{}.txt")
    NAME = "{}"
    META_INFO = {}

    @property
    def path(self):
        return self.FILE_PATH.format(self.__class__.__name__)

    @property
    def names(self):
        return self.NAME.format(self.__class__.__name__)

    def find(self):
        user_dict = self.__dict__
        with open(self.path, "r") as df:
            line = df.readline()
            while line:
                if str(user_dict["id"]) in line:
                    return True
                line = df.readline()
            return False

    def save(self):
        user_dict = self.__dict__
        with open(self.path, "a") as df:
            if not self.find():
                df.write(f"{user_dict}\n")

    def delete(self):
        user_dict = self.__dict__
        with open(self.path, "r") as df:
            lines = df.readlines()
        if self.find():
            with open(self.path, "w") as df:
                for line in lines:
                    if str(user_dict["id"]) not in line:
                        df.write(line)
        else:
            raise Exception(f"No {self.names} objects founded")

    @classmethod
    def __get_rec(cls, kwargs):
        for key, val in kwargs.items():
            if isinstance(val, dict):
                value = list(val.values())
                if all(not isinstance(item, dict) for item in value):
                    cr_by_ins = cls.META_INFO.get(key)(**val)
                    kwargs[key] = cr_by_ins
                else:
                    cls.__get_rec(val)
        return kwargs

    @classmethod
    def get(cls, **kwargs):
        value = list(kwargs.values())
        new_val = [item1.__dict__["id"] if isinstance(item1, (Artist, Song, User, Playlist, Album)) else item1 for
                   item1 in value]
        stack_for_line = []
        with open(cls.FILE_PATH.format(cls.__name__), "r") as df:
            line = df.readline()
            while line:
                if all(item in line for item in new_val):
                    new_line = eval(line[:-1])
                    num = cls.__get_rec(new_line)
                    final_num = cls.__get_rec(num)
                    stack_for_line.append(cls(**final_num))
                line = df.readline()
        if len(stack_for_line) > 1:
            raise Exception(f"Multiple {cls.__name__} objects founded")
        elif len(stack_for_line) == 0:
            raise Exception(f"No {cls.__name__} objects founded")
        else:
            return stack_for_line[0]

    @classmethod
    def filter(cls, **kwargs):
        value = kwargs.values()
        new_val = [item1.__dict__["id"] if isinstance(item1, (Artist, User, Song, Playlist, Album)) else item1 for
                   item1 in value]
        stack_for_line = []
        with open(cls.FILE_PATH.format(cls.__name__), "r") as df:
            line = df.readline()
            while line:
                if all(item in line for item in new_val):
                    new_line = eval(line[:-1])
                    num = cls.__get_rec(new_line)
                    final_num = cls.__get_rec(num)
                    stack_for_line.append(cls(**final_num))
                line = df.readline()
        if len(stack_for_line) == 0:
            raise Exception(f"No {cls.__name__} objects founded")
        return stack_for_line  # returns the list of objects

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                self.delete()
                self.save()
            else:
                raise Exception(f"{self.names} does't have {key} field")


class User(Methods):

    def __init__(self, first_name, last_name, email, password, stage_name=None, listeners_count=0, about=None, id=None, profile_pic=None, birth_date=None, level=0):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.stage_name = stage_name
        self.listeners_count = listeners_count
        self.about = about
        self.profile_pic = profile_pic
        self.birth_date = birth_date
        self.level = level
        self.id = str(uuid.uuid3(uuid.NAMESPACE_DNS, self.email))

        self.validate_user()
        self.save()

    def validate_user(self):
        ans_tuple = (self.first_name, self.last_name, self.email, self.password)
        if not all(ans_tuple):
            raise Exception("All required fields should be filled out")
        if "@" not in self.email:
            raise Exception("Invalid email")
        self.valid_pass()

    def valid_pass(self):
        num = string.digits
        up_let = string.ascii_uppercase
        low_let = string.ascii_lowercase
        sym = string.punctuation
        if len(self.password) < 8 or not any(item in num for item in self.password) or not any(
            item in up_let for item in self.password) or not any(item in low_let for item in self.password) or not any(
            item in sym for item in self.password):
            raise Exception("Invalid password")

    def create_playlist(self, name):
        return Playlist(name=name, created_by=self)

    def delete_playlist(self, name):
        get_pl = Playlist.get(name=name, created_by=self)
        get_pl.delete()


class Artist(User):
    FILE_PATH = os.path.normpath("./data/User.txt")

    def __init__(self, first_name, last_name, email, password, stage_name=None, listeners_count=0, about=None, id=None, profile_pic=None, birth_date=None, level=0):
        super().__init__(first_name, last_name, email, password, stage_name, listeners_count, about, id, profile_pic, birth_date, level)

        self.save()

    def add_song(self, title, duration, genre, year):
        return Song(title=title, duration=duration, genre=genre, year=year, s_created_by=self)

    def delete_song(self, title):
        try:
            get_song = Song.get(title=title, artist=self.stage_name)
            get_song.delete()
        except Exception as e:
            print("There is no such a song created by the artist")

    def create_album(self, title, year, label, list_of_song_url=()):
        return Album(name=title, created_by=self, year=year, label=label)

    def delete_album(self, title):
        try:
            get_album = Album.get(name=title, created_by=self)
            get_album.delete()
        except Exception as e:
            print("There is no such an album created by the artist")


class Song(Methods):
    META_INFO = {"s_created_by": Artist}

    def __init__(self, title, duration, genre, year, s_created_by, artist=None, id=None, album_name=None, streams_count=0):
        if not isinstance(s_created_by, Artist):
            raise Exception("Access denied")

        self.title = title
        self.artist = s_created_by.stage_name
        self.duration = duration
        self.genre = genre
        self.year = year
        self.s_created_by = s_created_by.__dict__
        self.streams_count = streams_count
        if album_name is None:
            self.album_name = Album(name=self.title, created_by=s_created_by, year=self.year).name
        else:
            alb = Album.get(name=album_name)
            self.album_name = alb.name
        self.id = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{self.title}-{self.artist}"))

        self.save()

    def add_to_playlist(self, playlist_name, user):
        try:
            get_pl = Playlist.get(name=playlist_name, s_created_by=user)
            PlaylistSong(playlist=get_pl, song=self)
        except Exception as e:
            print("There is no playlist with this name created by the user")

    def remove_from_playlist(self, playlist_name, user):
        get_pl = Playlist.get(name=playlist_name, s_created_by=user)
        try:
            get_pl_song = PlaylistSong.get(id=get_pl, song=self)
            get_pl_song.delete()
        except Exception as e:
            print("There is no such a song in the playlist")

    def play(self, user):
        try:
            result = SongPlays.filter(user=user)
            for item in result:
                search_id = item.song["id"]
                search_song = Song.get(id=search_id)
                search_song.stop(user=user)
            SongPlays(user=user, song=self)
        except Exception as e:
            SongPlays(user=user, song=self)

    def stop(self, user, end_time=time.time()):
        try:
            search_sp = SongPlays.get(user=user, song=self)
            start = search_sp.__dict__["start_timestamp"]
            song_stream = end_time - start
            if song_stream >= 30:
                # because in __init__ streams_count by deafult is 0
                song = Song.get(id=self.id)
                str_count = song.streams_count + 1
                self.update(streams_count=str_count)
                artist_id = self.s_created_by["id"]
                artist = Artist.get(id=artist_id)
                lis_count = artist.listeners_count + 1
                artist.update(listeners_count=lis_count)
            search_sp.delete()
        except Exception as e:
            print("There is no such a song playing now")

    def download(self):
        print(self.path)


class Playlist(Methods):
    META_INFO = {"created_by": User}

    def __init__(self, name, created_by, date_added=str(datetime.datetime.now()), id=None, picture_url=None):
        if not isinstance(created_by, User):
            raise Exception("Access denied")

        self.name = name
        self.created_by = created_by.__dict__
        self.date_added = date_added
        self.id = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{self.name}{self.created_by.get('first_name')}"))
        self.picture_url = picture_url

        self.save()

    @property
    def count_of_songs(self):
        pl_songs = PlaylistSong.filter(playlist=self)
        count = len(pl_songs)
        return count

    @property
    def duration_of_playlist(self):
        pl_dur = 0
        pl_songs = PlaylistSong.filter(playlist=self)
        for song in pl_songs:
            song_dur = song.__dict__["song"]["duration"]
            pl_dur += song_dur
        return pl_dur

    @property
    def genre_list(self):
        all_genre = set()
        pl_songs = PlaylistSong.filter(playlist=self)
        for song in pl_songs:
            song_genre = song.__dict__["song"]["genre"]
            all_genre.add(song_genre)
        return all_genre

    def __play_help(self, user):
        all_songs = PlaylistSong.filter(playlist=self)
        length = len(all_songs)
        stack_for_sd = []
        stack_for_stt = []
        for item in range(length):
            song_id = all_songs[item].__dict__["song"]["id"]
            search_song = Song.get(id=song_id)
            stack_for_sd.append(search_song.duration)
            if item == 0:
                sp = SongPlays(user=user, song=search_song, start_timestamp=time.time())
                stack_for_stt.append(sp.start_timestamp)
            else:
                st_time = stack_for_sd[item - 1] + stack_for_stt[item - 1]
                stack_for_stt.append(st_time)
                SongPlays(user=user, song=search_song, start_timestamp=st_time)
        stack_for_sd.clear()
        stack_for_stt.clear()

    def play(self, user):
        e_t = time.time()
        try:
            pl_list = SongPlays.filter(user=user)
            for item1 in pl_list:
                sng_id = item1.song["id"]
                sr_song = Song.get(id=sng_id)
                sr_song.stop(user=user, end_time=e_t)
            self.__play_help(user=user)
        except Exception as e:
            self.__play_help(user=user)

    @staticmethod
    def stop(user, end_t=time.time()):
        try:
            pl_list = SongPlays.filter(user=user)
            for item in pl_list:
                song_id = item.song["id"]
                search_song = Song.get(id=song_id)
                search_song.stop(user=user, end_time=end_t)
        except Exception as e:
            print("There is no song turned on by the user")


class Album(Playlist):
    META_INFO = {"created_by": Artist}

    def __init__(self, name, year, created_by, label=None, date_added=str(datetime.datetime.now()), id=None, picture_url=None):
        if not isinstance(created_by, Artist):
            raise Exception("Access denied")

        self.year = year
        self.label = label
        super().__init__(name, created_by, date_added, id, picture_url)
        self.id = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{self.name}{self.created_by.get('first_name')}"))

        self.save()


class PlaylistSong(Methods):
    META_INFO = {"playlist": Playlist, "song": Song, "s_created_by": Artist,
                 "created_by": User}
    FILE_PATH = os.path.normpath("./data/PlaylistSong.txt")

    def __init__(self, playlist, song, date_added=str(datetime.datetime.now()), id=None):
        if not isinstance(playlist, Playlist) and not isinstance(song, Song):
            raise Exception("Access denied")

        self.playlist = playlist.__dict__
        self.song = song.__dict__
        self.date_added = date_added
        self.id = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{song.__dict__['title']}{playlist.__dict__['name']}"))

        self.save()


class SongPlays(Methods):
    META_INFO = {"song": Song, "s_created_by": Artist, "user": User}

    def __init__(self, user, song, start_timestamp=time.time(), id=None):
        if not isinstance(user, User) and not isinstance(song, Song):
            raise Exception("Access denied")
        self.user = user.__dict__
        self.song = song.__dict__
        self.start_timestamp = start_timestamp
        self.id = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{user.__dict__['id']}{song.__dict__['id']}"))

        self.save()
