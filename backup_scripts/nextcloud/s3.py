import configparser
import click

from backup_scripts.nextcloud.nextcloud_client import NextCloudClient


@click.command()
@click.option('--config-file', '-c', required=True,
              type=click.Path(exists=True, file_okay=True, dir_okay=False),
              help='INI file containing script parameters', )
def main(config_file):

    config = get_config(config_file)
    nextcloud = NextCloudClient(config)

    # Turn on maintenance mode
    nextcloud.maintenance_mode("on")
    # Copy directories to backup location
    archive_path = nextcloud.make_backup()
    nextcloud.maintenance_mode("off")
    # TODO: Copy backup location to S3


def get_config(config_file):
    config = configparser.ConfigParser()

    with open(config_file, 'r') as f:
        config.read_file(f)

    return config


if __name__ == '__main__':
    main()
