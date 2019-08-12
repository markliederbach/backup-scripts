import os
import datetime
import subprocess
import shutil
import pathlib
import tarfile
from backup_scripts import exceptions


class NextCloudClient:
    def __init__(self, config):
        nextcloud_config = config['nextcloud']
        self.user = nextcloud_config.get('user', 'abc')
        self.occ = nextcloud_config.get('occ', '/config/www/nextcloud/occ')
        self.local_backup_folder = nextcloud_config.get('local_backup_folder', '/tmp')
        self.nextcloud_folder = nextcloud_config.get('nextcloud_folder', '/config/www/nextcloud')
        self.data_folder = nextcloud_config.get('data_folder', '/data')
        self.mysql_server = nextcloud_config.get('mysql_server', '192.168.2.63:3306')
        self.mysql_user = nextcloud_config.get('mysql_user', 'nextcloud')
        self.mysql_password = nextcloud_config.get('mysql_password', 'xxxx')
        self.mysql_database = nextcloud_config.get('mysql_database', 'nextcloud')

    def maintenance_mode(self, state):
        command = ["sudo", "-u", self.user, "php", self.occ, "maintenance:mode", f"--{state}"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise exceptions.NextCloudClientException(
                f"Command [{' '.join(command)}] returned exit code {result.returncode}. Expected 0."
            )
        return result.stdout.decode('utf-8')

    def make_backup(self):
        timestamp = datetime.datetime.utcnow().isoformat()
        backup_name = f"nextcloud-backup-{timestamp}"
        backup_folder_path = os.path.join(self.local_backup_folder, backup_name)
        pathlib.Path(backup_folder_path).mkdir(parents=True, exist_ok=True)
        # backup data folder
        self.copy_to_backup_folder(self.data_folder, backup_folder_path, 'data')
        # backup nextcloud config
        self.copy_to_backup_folder(self.nextcloud_folder, backup_folder_path, 'nextcloud')
        # backup mysql
        # mysqldump
        mysql_dump_command = ['mysqldump', '--single-transaction',
                              f'-host={self.mysql_server}', f'-username={self.mysql_user}',
                              f'--password={self.mysql_password}', self.mysql_database,
                              '>', os.path.join(backup_folder_path, 'nextcloud-mysql.bak')]
        result = subprocess.run(mysql_dump_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise exceptions.NextCloudClientException(
                f"Command [{' '.join(mysql_dump_command)}] returned exit code {result.returncode}. Expected 0."
            )
        tarfile_path = f"{backup_folder_path}.tar.gz"
        self.make_tarfile(tarfile_path, backup_folder_path)
        shutil.rmtree(backup_folder_path)
        return tarfile_path

    def copy_to_backup_folder(self, source_folder, backup_folder_path, backup_subfolder):
        shutil.copytree(source_folder, os.path.join(backup_folder_path, backup_subfolder))

    def make_tarfile(self, output_filename, source_dir):
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
