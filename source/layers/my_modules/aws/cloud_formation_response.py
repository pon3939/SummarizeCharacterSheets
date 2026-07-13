# -*- coding: utf-8 -*-

from typing import Any

from ..constants.aws import CLOUD_FORMATION_REQUEST_TYPE_MANUAL

"""
CloudFormationのレスポンス情報
"""


class CloudFormationResponse:
    """
    CloudFormationのレスポンス
    Attributes:
        RequestType str: リクエストタイプ
        ResponseUrl str: レスポンスURL
        PhysicalResourceId str: 物理リソースID
        StackId str: スタックID
        RequestId str: リクエストID
    """

    RequestType: str
    ResponseUrl: str = ""
    PhysicalResourceId: str = ""
    StackId: str = ""
    RequestId: str = ""
    LogicalResourceId: str = ""

    def __init__(
        self,
        event: dict[str, Any],
    ):
        """
        コンストラクタ

        Args:
            event: dict[str, Any]: Lambdaのイベント情報
        """
        self.RequestType = event["RequestType"]
        if self.RequestType == CLOUD_FORMATION_REQUEST_TYPE_MANUAL:
            # 手動実行なので他のパラメーターはない
            return

        self.ResponseUrl = event["ResponseURL"]
        self.LogicalResourceId = event["LogicalResourceId"]
        self.PhysicalResourceId = event.get(
            "PhysicalResourceId", self.LogicalResourceId
        )
        self.StackId = event["StackId"]
        self.RequestId = event["RequestId"]
