# -*- coding: utf-8 -*-
import argparse
import os
import eyed3
from os.path import join

MAX_DEPTH = 0  # глубина обхода поддиректорий


def move_file(src_path, dst_path):
    """
    Перемещает файл из src_path в dst_path.
    Если папки в dst_path не существуют, то они создаются, файл перезаписывается.

    :param src_path: Исходная директория
    :param dst_path: Директория куда переместить файл
    :return:
    """

    try:
        # Если файл существует, сначала удаляем
        if os.path.exists(dst_path):
            if os.access(dst_path, os.W_OK):
                os.remove(dst_path)
            else:
                print(f'  Не хватает прав доступа: {dst_path}')
                return
        os.renames(src_path, dst_path)
        print(f'{src_path} -> {dst_path}')
    except Exception as e:
        print(e)
    return


def sort_mp3_files(src_dir, dst_dir):
    """Сортирует mp3 файлы.
    Ищет mp3 файлы в src_dir, и перемещает их в dst_dir по пакам на основе аналза id3 заголовков.

    :param src_dir: директория откуда брать mp3 файлы
    :param dst_dir: директория куда переместить файлы
    :return:
    """

    if not all((os.path.isdir(src_dir), os.path.isdir(dst_dir))):
        print(f'  Указанная(ые) папка(и) не найдена(ы)!\n  {src_dir}\n  {dst_dir}')
        return

    for root, dirs, files in os.walk(args.src_dir):
        # прерываемся если зашли глубже чем надо
        if root.count(os.sep) - args.src_dir.count(os.sep) != MAX_DEPTH:
            continue
        for src_name in (x for x in files if x.endswith('.mp3')):
            src_path = join(root, src_name)
            try:
                mf = eyed3.load(src_path)
            except PermissionError:
                print(f'  Не хватает прав доступа: {src_path}')
                continue

            if not mf:  # Ошибка при файле mp3 0 байт
                print(f'  Ошибка загрузки файла для анализа: {src_path}')
                continue

            if not mf.tag:  # Ошибка при пустых заголовках
                print(f'  Пропускаем, пустые заголовки: {src_path}')
                continue

            title, artist, album = mf.tag.title.strip(), mf.tag.artist.strip(), mf.tag.album.strip()
            if artist and album:
                dst_name = f'{title} - {artist} - {album}.mp3' if title else src_name
                dst_path = join(args.dst_dir, artist.capitalize(), album.capitalize(), dst_name)
                if src_path == dst_path:
                    continue
                move_file(src_path, dst_path)
    return


if __name__ == '__main__':
    current_path = os.getcwd()

    parser = argparse.ArgumentParser(description='Sorting mp3 files')
    parser.add_argument('-s', '--src-dir', default='.', type=str,
                        help='Input dir for mp3 files (default: current directory)')
    parser.add_argument('-d', '--dst-dir', default='.', type=str,
                        help='Output dir for mp3 files  (default: current directory)')
    args = parser.parse_args()

    print('...')
    if not os.path.exists(args.dst_dir):
        try:
            os.makedirs(args.dst_dir)
        except Exception as e:
            print(f'Ошибка при создании {args.dst_dir} {e}')

    sort_mp3_files(args.src_dir, args.dst_dir)
    print('...\nDone')
