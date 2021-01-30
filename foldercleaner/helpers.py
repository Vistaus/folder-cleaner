from typing import Tuple, List, Optional
from gi.repository import Gio, GLib


def get_files_and_folders(folder, absolute_folders_paths=True) -> Tuple[List[str], List[str]]:
    folder_list: List[str] = []
    files_list: List[str] = []

    path: Gio.File = Gio.File.new_for_path(folder)
    enumerator: Optional[Gio.FileEnumerator] = path.enumerate_children(Gio.FILE_ATTRIBUTE_STANDARD_NAME,
                                                                       Gio.FileQueryInfoFlags.NONE)
    info: Optional[Gio.FileInfo] = enumerator.next_file()
    while info is not None:
        if info.get_file_type() == Gio.FileType.DIRECTORY:
            if absolute_folders_paths:
                folder_path: str = GLib.build_pathv(GLib.DIR_SEPARATOR_S, [path.get_path(), info.get_name()])
            else:
                folder_path: str = info.get_name()
            folder_list.append(folder_path)
            info: Optional[Gio.FileInfo] = enumerator.next_file()
        else:
            abs_path: str = GLib.build_pathv(GLib.DIR_SEPARATOR_S, [path.get_path(), info.get_name()])
            files_list.append(abs_path)
            info: Optional[Gio.FileInfo] = enumerator.next_file()

    return folder_list, files_list
