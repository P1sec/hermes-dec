#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from appdirs import user_data_dir
from unidecode import unidecode
from datetime import datetime
from os.path import join
from os import makedirs
from re import sub

class ProjectSubdirManager:

    @classmethod
    def new_with_name(cls, name : str):

        self = cls()
        dirname = self.gen_unique_dirname(name)
        self.subdir_path = join(user_data_dir('HermesDec', 'P1Security'), dirname)

        makedirs(self.subdir_path, exist_ok = True)

        self.file_buffer = open(self.subdir_path + '/index.android.bundle', 'wb+')

        return self
    
    def gen_unique_dirname(self, orig_name : str):

        return '-'.join(filter(None, [
            datetime.now().isoformat().split('.')[0],
            sub('[^a-z0-9\-]', '', sub('\s+', '-', unidecode(orig_name).lower().strip()))
        ]))



