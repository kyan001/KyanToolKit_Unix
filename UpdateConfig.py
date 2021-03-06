#!/usr/bin/env python3
import os
import shutil
import getpass
import consoleiotools as cit
import consolecmdtools as cct


@cit.as_session('Generate Filepath')
def generate_filepath(filename):
    home_dir = os.path.expanduser('~')
    cit.info("Home Dir\t: {}".format(home_dir))
    if not os.path.isdir(home_dir):
        cit.warn('Home Dir does not exist, creating it')
        os.makedirs(home_dir)
    new_file = os.path.join(home_dir, filename)
    cit.info("Target File\t: {}".format(new_file))
    return new_file


@cit.as_session('Copying my file')
def copy(from_path: str, to_path: str) -> bool:
    # deal from
    if not os.path.isabs(from_path):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        from_path = os.path.join(current_dir, from_path)
    cit.info('From\t: {}'.format(from_path))
    if not os.path.isfile(from_path):
        cit.err("config file does not exists, copy cancelled")
        return False
    # deal to
    cit.info('To\t: {}'.format(to_path))
    if os.path.isfile(to_path):
        cit.err('target file exists, copy cancelled')
        return False
    cit.info('Copying file ...')
    shutil.copyfile(from_path, to_path)
    cit.info('Changing file owner ...')
    current_user = getpass.getuser()
    shutil.chown(to_path, user=current_user)
    return True


@cit.as_session('Menu')
def menu():
    def config_filenames() -> list:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        all_files = os.listdir(current_dir)
        return [filename for filename in all_files if filename.startswith('config.')]
    confs = [filename.replace("config", "") for filename in config_filenames()]
    cit.ask('Which config file to update:')
    choice = cit.get_choice(['** ALL **'] + sorted(confs) + ['** EXIT **'])
    if choice == '** ALL **':
        for conf in confs:
            apply_config(conf)
        cit.info('Done')
        cit.bye()
    elif choice == '** EXIT **':
        cit.bye()
    else:
        return choice


@cit.as_session('Configing')
def apply_config(config_name):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    new_conf = os.path.join(current_dir, "config" + config_name)
    target_conf = generate_filepath(config_name)
    if os.path.exists(target_conf):
        cit.warn("Target file is already exist.")
        diffs = cct.diff(target_conf, new_conf)
        if not diffs:
            cit.warn("Files are same, stop configing.")
            return True
        cit.warn("Diffs found:\n" + "\n".join(diffs))
        backup = '{}.old'.format(target_conf)
        os.rename(target_conf, backup)
        cit.warn("Old config file renamed as {}".format(backup))
    return copy(new_conf, target_conf)


def main():
    while True:
        conf = menu()
        if not apply_config(conf):
            cit.bye()


if __name__ == '__main__':
    main()
