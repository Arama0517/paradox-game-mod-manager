from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from steam import webapi
from steam.client.cdn import CDNDepotManifest
from steam.exceptions import SteamError

from src.steam_clients import cdn_client, login


class CDNWorkShopDepotManifest(CDNDepotManifest):
    item_info: dict = None


def get_manifest(app_id, depot_id, manifest_gid, decrypt=True, manifest_request_code=0):
    """Download a manifest file

    :param app_id: App ID
    :type  app_id: int
    :param depot_id: Depot ID
    :type  depot_id: int
    :param manifest_gid: Manifest gid
    :type  manifest_gid: int
    :param decrypt: Decrypt manifest filenames
    :type  decrypt: bool
    :param manifest_request_code: Manifest request code, authenticates the download
    :type  manifest_request_code: int
    :returns: manifest instance
    :rtype: :class:`.CDNDepotManifest`
    """
    if (app_id, depot_id, manifest_gid) not in cdn_client.manifests:
        if manifest_request_code:
            resp = cdn_client.cdn_cmd(
                'depot',
                f'{depot_id}/manifest/{manifest_gid}/5/{manifest_request_code}',
                app_id,
                depot_id,
            )
        else:
            resp = cdn_client.cdn_cmd(
                'depot', f'{depot_id}/manifest/{manifest_gid}/5', app_id, depot_id
            )

        if not resp:
            raise SteamError('get response failed.')

        if resp.ok:
            manifest = CDNDepotManifest(cdn_client, app_id, resp.content)
            if decrypt:
                manifest.decrypt_filenames(cdn_client.get_depot_key(app_id, depot_id))
            cdn_client.manifests[(app_id, depot_id, manifest_gid)] = manifest

    return cdn_client.manifests[(app_id, depot_id, manifest_gid)]


def get_manifests_for_workshop_item(
    items_id: list[str],
) -> list[CDNWorkShopDepotManifest]:
    manifests = []

    retry_login = False
    items_info = webapi.post(
        'ISteamRemoteStorage',
        'GetPublishedFileDetails',
        params={
            'itemcount': len(items_id),
            'publishedfileids': items_id,
        },
    )['response']['publishedfiledetails']

    with Progress(
        SpinnerColumn(),
        TextColumn('[progress.description]{task.description}'),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        task_id = progress.add_task('[bold dim]正在获取清单中...', total=len(items_id))

        for item_info in items_info:
            progress.update(
                task_id,
                description=f'[bold dim]正在获取清单: {item_info["title"]}',
            )
            app_id = depot_id = item_info['consumer_app_id']
            manifest_gid = item_info['hcontent_file']

            while True:
                need_retry = False
                try:
                    manifest_code = cdn_client.get_manifest_request_code(
                        app_id,
                        depot_id,
                        manifest_gid,
                    )
                    if not manifest_code:
                        need_retry = True
                    manifest: CDNWorkShopDepotManifest = get_manifest(
                        app_id,
                        depot_id,
                        manifest_gid,
                        manifest_request_code=manifest_code,
                    )
                except SteamError:
                    need_retry = True

                if need_retry:
                    if not retry_login and login():
                        retry_login = True
                        continue
                    else:
                        return []
                break

            manifest.name = item_info['title']
            manifest.item_info = item_info
            manifests += [manifest]
            progress.update(task_id, advance=1, refresh=True)
        progress.update(task_id, description='[bold dim]清单获取完成', refresh=True)
    return manifests


__all__ = ['get_manifests_for_workshop_item']
