#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path


def mask_secret(value: str) -> str:
    if len(value) <= 6:
        return '*' * len(value)
    return f'{value[:3]}{"*" * (len(value) - 5)}{value[-2:]}'


def parse_args():
    parser = argparse.ArgumentParser(
        description='Write Aliyun SMS AccessKey credentials to Config table.',
    )
    parser.add_argument(
        '--access-key-id',
        dest='access_key_id',
        default=None,
        help='Aliyun AccessKey ID. Fallback: env ALI_SMS_ACCESS_KEY_ID',
    )
    parser.add_argument(
        '--access-key-secret',
        dest='access_key_secret',
        default=None,
        help='Aliyun AccessKey Secret. Fallback: env ALI_SMS_ACCESS_KEY_SECRET',
    )
    parser.add_argument(
        '--settings',
        dest='settings_module',
        default='NotificatorX.settings',
        help='Django settings module (default: NotificatorX.settings)',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    access_key_id = (args.access_key_id or os.getenv('ALI_SMS_ACCESS_KEY_ID') or '').strip()
    access_key_secret = (args.access_key_secret or os.getenv('ALI_SMS_ACCESS_KEY_SECRET') or '').strip()

    if not access_key_id or not access_key_secret:
        print('ERROR: missing AccessKey ID or AccessKey Secret.')
        print('Pass via args or env:')
        print('  --access-key-id / --access-key-secret')
        print('  ALI_SMS_ACCESS_KEY_ID / ALI_SMS_ACCESS_KEY_SECRET')
        return 1

    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', args.settings_module)

    import django

    django.setup()

    from Config.models import Config, CI

    Config.update_value(CI.ALI_SMS_ACCESS_KEY_ID, access_key_id)
    Config.update_value(CI.ALI_SMS_ACCESS_KEY_SECRET, access_key_secret)

    print('Aliyun SMS credentials updated in Config table:')
    print(f'  {CI.ALI_SMS_ACCESS_KEY_ID}={mask_secret(access_key_id)}')
    print(f'  {CI.ALI_SMS_ACCESS_KEY_SECRET}={mask_secret(access_key_secret)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
