# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

import hashlib
from fastapi import APIRouter, HTTPException
from time import time

from api.models.run import HashParams
from api.models.send_newsletter import SendNewsletterParams, ListmonkReturnDataList
from api.models.exceptions import CredentialsInvalid
from api.factory.runs import get_hash_runs
from source.database import get_db_handler
from common.misc import php_deserialize, grab
from common.log import get_logger
from listmonk.handler import get_listmonk_handler


log = get_logger()

newsletter = APIRouter(
    prefix="/send-newsletter",
    tags=["newsletter"]
)


# noinspection PyShadowingBuiltins
@newsletter.post("/{post_id}", response_model=ListmonkReturnDataList, summary="post run",
                 description="post run via newsletter")
async def get_run(post_id: int, params: SendNewsletterParams):
    """
        To post/update a run to listmonk

        - **id**: The integer id of the desired run
    """

    db_handler = get_db_handler()

    # query user metadata from database
    user_params = db_handler.get_usermeta(params.user)
    session_tokens = None
    for item in user_params:
        if item.get("meta_key") == "session_tokens":
            session_tokens = item.get("meta_value")

    if session_tokens is None:
        log.debug(f"No session_tokens metadata found in wordpress DB for user id {params.user}")
        raise CredentialsInvalid

    # use hashed session token to find session in database
    hashed_token_sha256 = hashlib.sha256(params.token.encode()).hexdigest()
    hashed_token_sha1 = hashlib.sha1(params.token.encode()).hexdigest()

    session_data = None
    try:
        session_data = php_deserialize(session_tokens).get(hashed_token_sha256)
        if session_data is None:
            session_data = php_deserialize(session_tokens).get(hashed_token_sha1)
    except Exception as e:
        log.debug(f"PHP deserialization of 'session_tokens' failed: {e}")

    if session_data is None:
        log.debug(f"No session data found in wordpress DB for user id {params.user}")
        raise CredentialsInvalid

    # check if session has not expired
    expiration_ts = session_data.get("expiration")
    if not isinstance(expiration_ts, int):
        log.debug(f"session data expiration is not an int: {session_data}")
        raise CredentialsInvalid

    if expiration_ts < int(time()):
        log.debug(f"session already expired")
        raise CredentialsInvalid

    # all checks passed and user presented a valid session

    # fetch post
    # noinspection PyArgumentList
    result = get_hash_runs(HashParams(id=post_id))

    if result is None or len(result) == 0:
        raise HTTPException(status_code=404, detail="Run not found")

    event = result[0]

    # fetch template from listmonk
    listmonk_handler = get_listmonk_handler()
    listmonk_template = listmonk_handler.get_template(listmonk_handler.config.body_template_id)

    if listmonk_template is None:
        raise HTTPException(status_code=404,
                            detail=f"Listmonk template {listmonk_handler.config.body_template_id} not found")

    template_body = grab(listmonk_template, "data.body")

    if template_body is None:
        template_body = event.event_description

    # set all paragraph text to center
    event.event_description = event.event_description.replace('<p>', '<p style="text-align: center;">')

    # use data from post and apply to template
    try:
        campaign_body = template_body.format(**event.__dict__)
    except Exception as e:
        log.error(f"Failed to format template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to format template: {e}")

    # fetch post metadata to check if newsletter has already been sent before
    post_meta_data = db_handler.get_posts_meta([post_id])
    post_campaign_id = None
    subject_prefix = ""
    for post_meta in post_meta_data:
        if post_meta.get("meta_key") == "listmonk_campaign_id":
            post_campaign_id = post_meta.get("meta_value")

    if post_campaign_id is not None:
        subject_prefix = "UPDATE: "

    # prepare campaign data
    campaign_data = {
        "name": f"{subject_prefix}{event.event_name}",
        "subject": f"{subject_prefix}[{event.kennel_name}] Run #{event.run_number}, "
                   f"{event.start_date:%A %d %B %Y, %H:%M} @ {event.location_name}",
        "lists": listmonk_handler.config.list_ids,
        "type": "regular",
        "content_type": "html",
        "body": campaign_body
    }

    if listmonk_handler.config.campaign_template_id is not None:
        campaign_data["template_id"] = listmonk_handler.config.campaign_template_id

    # create listmonk campaign
    campaign_result = listmonk_handler.add_campaign(campaign_data)

    if campaign_result is None:
        raise HTTPException(status_code=503, detail=f"Upstream request failed")

    campaign_id = grab(campaign_result, "data.id")

    # send campaign
    if listmonk_handler.config.send_campaign is True:
        campaign_result = listmonk_handler.set_campaign_status(campaign_id, "running")

        if campaign_result is None:
            raise HTTPException(status_code=503, detail=f"Upstream request failed, unable to start campaign")

    # write campaign id to WP database
    if post_campaign_id is not None:
        db_handler.update_post_meta(post_id, "listmonk_campaign_id", campaign_id)
    else:
        db_handler.add_post_meta(post_id, "listmonk_campaign_id", campaign_id)

    return ListmonkReturnDataList(**campaign_result)

# EOF
