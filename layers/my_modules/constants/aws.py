# -*- coding: utf-8 -*-

"""
AWS関係の定数
"""


# CloudFormationに渡すステータス
CLOUD_FORMATION_STATUS_SUCCESS: str = "SUCCESS"
CLOUD_FORMATION_STATUS_FAILED: str = "FAILED"

# CloudFormationのリクエストタイプ
CLOUD_FORMATION_REQUEST_TYPE_CREATE: str = "Create"
CLOUD_FORMATION_REQUEST_TYPE_DELETE: str = "Delete"
CLOUD_FORMATION_REQUEST_TYPE_MANUAL: str = "Manual"

# S3のエラーコード
S3_ERROR_CODE_NOT_FOUND: str = "NoSuchKey"

# DynamoDBのバッチ書き込み最大数
DYNAMO_DB_MAX_BATCH_WRITE_ITEM: int = 25
