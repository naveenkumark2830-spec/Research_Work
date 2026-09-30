class DeterministicIdGenerator:
    """Generates deterministic identifiers for HDFS simulation objects."""

    @staticmethod
    def cluster_id(index: int = 1) -> str:
        return f"cluster-{index}"

    @staticmethod
    def namenode_id(index: int = 1) -> str:
        return f"namenode-{index}"

    @staticmethod
    def datanode_id(index: int) -> str:
        return f"datanode-{index}"

    @staticmethod
    def block_id(index: int) -> str:
        return f"block-{index:05d}"

    @staticmethod
    def file_id(index: int) -> str:
        return f"file-{index:05d}"
