# -*- coding: utf-8 -*-


from json import dumps

from aws_lambda_powertools.utilities.typing import LambdaContext
from my_modules.cloud_formation_response import CloudFormationResponse
from my_modules.common_functions import (
    InitDb,
    InitS3,
    putCloudFormationResponse,
)
from my_modules.constants.aws import (
    CLOUD_FORMATION_REQUEST_TYPE_DELETE,
    CLOUD_FORMATION_REQUEST_TYPE_MANUAL,
    CLOUD_FORMATION_STATUS_FAILED,
)
from mypy_boto3_dynamodb.client import DynamoDBClient
from mypy_boto3_dynamodb.type_defs import ScanOutputTypeDef
from mypy_boto3_s3.client import S3Client

"""
Dynamo DBをバックアップ
"""


def lambda_handler(event: dict, context: LambdaContext):
    """

    メイン処理

    Args:
        event dict: イベント
        context LambdaContext: コンテキスト
    """
    cloudFormationResponse: CloudFormationResponse = CloudFormationResponse(
        event
    )

    try:
        if cloudFormationResponse.RequestType not in (
            CLOUD_FORMATION_REQUEST_TYPE_DELETE,
            CLOUD_FORMATION_REQUEST_TYPE_MANUAL,
        ):
            # 削除時以外はスキップする
            putCloudFormationResponse(cloudFormationResponse)
            return

        tableNames: list[str] = event["ResourceProperties"]["TableNames"]
        bucketName: str = event["ResourceProperties"]["BucketName"]
        backupDynamoDb(tableNames, bucketName)
        putCloudFormationResponse(cloudFormationResponse)
    except Exception as e:
        putCloudFormationResponse(
            cloudFormationResponse,
            CLOUD_FORMATION_STATUS_FAILED,
            str(e),
        )


def backupDynamoDb(tableNames: list[str], bucketName: str):
    """Dynamo DBをバックアップする

    Args:
        tableNames: list[str]: バックアップ対象のテーブル名
        bucketName: str: バックアップ先のバケット名
    """
    dynamodb: DynamoDBClient = InitDb()
    s3: S3Client = InitS3()
    for tableName in tableNames:
        # 全件取得
        response: ScanOutputTypeDef = dynamodb.scan(
            TableName=tableName,
        )

        # ページ分割分を取得
        items: list[dict] = []
        while "LastEvaluatedKey" in response:
            items += response["Items"]
            response = dynamodb.scan(
                TableName=tableName,
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )

        items += response["Items"]

        # S3に保存
        s3.put_object(
            Bucket=bucketName,
            Key=f"{tableName}.json",
            Body=dumps({"data": items}, ensure_ascii=False),
        )
