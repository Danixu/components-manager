# -*- coding: utf-8 -*-
from modules import compressionTools
from tempfile import _get_candidate_names, _get_default_tempdir
from os.path import isfile, isdir, basename, splitext, join
from os import makedirs, urandom, remove
from hashlib import sha256

from modules import getResourcePath


def file_add(self, fName, componentID, storage=0, datasheet=False,
             compression=compressionTools.COMPRESSION_FMT.LZMA):
    if self.templates:
        self.log.warning(
            "This function is not compatible with templates" +
            " databases"
        )
        return False

    if isfile(fName):
        filename = basename(fName)
        try:
            with open(fName, 'rb') as fIn:
                _blob = None
                if storage == 0:
                    _blob = compressionTools.compressData(fIn.read(), compression)
                else:
                    if not isdir(getResourcePath.getResourcePath("attachments", "")):
                        makedirs(getResourcePath.getResourcePath("attachments", ""))

                    new_fname = "{}.dat".format(sha256(urandom(128)).hexdigest())
                    # If file exists then generate a new name
                    while isfile(getResourcePath.getResourcePath("attachments", new_fname)):
                        new_fname = "{}.dat".format(sha256(urandom(128)).hexdigest())
                    new_path = getResourcePath.getResourcePath("attachments", new_fname)
                    with open(new_path, 'wb') as fOut:
                        fOut.write(compressionTools.compressData(fIn.read(), compression))
                        _blob = new_fname.encode('utf-8')

                file_id = self._insert(
                    "Files",
                    values=[
                        None,
                        componentID,
                        filename,
                        storage,
                        datasheet
                    ]
                )
                self._insert(
                    "Files_blob",
                    values=[
                        file_id[0],
                        self.file_to_blob(_blob),
                        int(compression)
                    ]
                )

                self.conn.commit()
                return True

        except Exception as e:
            self.log.error(
                "There was an error adding the file to database: {}".format(e)
            )
            self.conn.rollback()
            return False

    else:
        self.log.error("The file {} does not exists".format(fName))
        return False


def file_del(self, fileID):
    if self.templates:
        self.log.warning(
            "This function is not compatible with templates"
            " databases"
        )
        return False

    try:
        fData = self._select(
            "Files",
            ["Storage"],
            where=[
                {'key': 'ID', 'value': fileID}
            ]
        )
        # If Storage is filesystem, first we delete the file
        if fData[0][0] == 1:
            blob_data = self._select(
                "Files_blob",
                ["Filedata"],
                where=[
                    {'key': 'File_id', 'value': fileID}
                ]
            )
            at_file = getResourcePath.getResourcePath(
                "attachments",
                blob_data[0][0].decode()
            )
            remove(at_file)

        self._delete(
            "Files",
            where=[
                {'key': 'ID', 'value': fileID}
            ]
        )
        self.conn.commit()
        return True

    except Exception as e:
        self.log.error(
            "There was an error deleting the file from database: {}".format(e)
        )
        self.conn.rollback()
        return False


def file_export(self, fileID, fName=None):
    if self.templates:
        self.log.warning(
            "This function is not compatible with templates"
            " databases"
        )
        return False

    exists = self._select(
        "Files",
        ["Filename", "Storage"],
        where=[
            {'key': 'ID', 'value': fileID}
        ]
    )
    if len(exists) > 0:
        try:
            blob_data = self._select(
                "Files_blob",
                ["Filedata", "Filecompression"],
                where=[
                    {'key': 'File_id', 'value': fileID}
                ]
            )
            if not fName:
                tempName = next(_get_candidate_names())
                tempFolder = _get_default_tempdir()

                # La extensión la sacamos del nombre de fichero en la BBDD
                filename, extension = splitext(exists[0][0])
                fName = join(
                    tempFolder,
                    tempName +
                    extension
                )

            fData = blob_data[0][0]
            if exists[0][1] == 1:
                at_file = getResourcePath.getResourcePath(
                    "attachments",
                    blob_data[0][0].decode()
                )
                with open(at_file, 'rb') as fIn:
                    fData = fIn.read()

            with open(fName, 'wb') as fOut:
                fOut.write(
                    compressionTools.decompressData(
                        fData,
                        blob_data[0][1]
                    )
                )

            return fName
        except Exception as e:
            self.log.error(
                "There was an error writing file temporary file: {}".format(e)
            )
            return False
    else:
        return False
