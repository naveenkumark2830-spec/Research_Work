class HDFSBaseException(Exception):
    """Base class for HDFS simulation domain exceptions."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InvalidClusterConfigurationError(HDFSBaseException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=400)


class DataNodeNotFoundError(HDFSBaseException):
    def __init__(self, node_id: str):
        super().__init__(message=f"DataNode '{node_id}' was not found in cluster metadata.", status_code=404)


class DataNodeUnavailableError(HDFSBaseException):
    def __init__(self, node_id: str, reason: str = "FAILED"):
        super().__init__(message=f"DataNode '{node_id}' is unavailable (status: {reason}).", status_code=400)


class HDFSFileNotFoundError(HDFSBaseException):
    def __init__(self, path: str):
        super().__init__(message=f"File '{path}' was not found in HDFS NameNode metadata.", status_code=404)


class BlockNotFoundError(HDFSBaseException):
    def __init__(self, block_id: str):
        super().__init__(message=f"Block '{block_id}' was not found in NameNode metadata.", status_code=404)


class InsufficientDataNodesError(HDFSBaseException):
    def __init__(self, required: int, available: int):
        super().__init__(
            message=f"Insufficient LIVE DataNodes: required {required}, available {available}.",
            status_code=400
        )


class BlockDataLossError(HDFSBaseException):
    def __init__(self, block_id: str, file_path: str):
        super().__init__(
            message=f"Critical Data Loss: Block '{block_id}' for file '{file_path}' has 0 healthy replicas.",
            status_code=500
        )


class InvalidSimulationStateError(HDFSBaseException):
    def __init__(self, message: str, status_code: int = 409):
        super().__init__(message=message, status_code=status_code)
