# -*- coding: utf-8 -*-

from os import getenv

from boto3 import client
from mypy_boto3_sns.client import SNSClient

from .constants.env_keys import MY_AWS_REGION, MY_SNS_TOPIC_ARN

"""
SNSClient拡張クラス
"""


class MySNSClient:
    """
    SNSClient拡張クラス
    """

    def __init__(self):
        """
        コンストラクタ
        """

        self.Client: SNSClient = client(
            "sns", region_name=getenv(MY_AWS_REGION, "")
        )

    def Publish(
        self,
        message: str,
        subject: str,
    ) -> None:
        """

        SNSトピックにメッセージを送信

        Args:
            message (str): メッセージ
            subject (str): 件名
        """

        self.Client.publish(
            TopicArn=getenv(MY_SNS_TOPIC_ARN, ""),
            Message=message,
            Subject=subject,
        )
