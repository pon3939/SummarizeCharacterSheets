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
