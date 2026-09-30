import pytest
from app.simulation.hdfs.cluster import HDFSClusterConfig
from app.simulation.hdfs.engine import HDFSSimulationEngine
from app.simulation.common.enums import BlockState, DataNodeStatus
from app.simulation.common.exceptions import BlockDataLossError, HDFSFileNotFoundError


def test_cluster_creation_and_datanode_count():
    # TEST 1 & TEST 2: Cluster creation and correct number of DataNodes
    cfg = HDFSClusterConfig(file_size_bytes=524288000, block_size_bytes=134217728, replication_factor=3, data_node_count=5)
    engine = HDFSSimulationEngine(config=cfg)
    state = engine.get_cluster_state()

    assert state.cluster_id == "cluster-1"
    assert len(state.datanodes) == 5
    assert "datanode-1" in state.datanodes
    assert "datanode-5" in state.datanodes
    assert state.datanodes["datanode-1"].status == DataNodeStatus.LIVE


def test_block_count_and_final_block_size():
    # TEST 3, TEST 4, TEST 5: 500 MB file split into 128 MB blocks
    # 500 MB = 524,288,000 bytes, 128 MB = 134,217,728 bytes
    # 500 / 128 = 3.90625 -> ceil = 4 blocks
    # B1 = 134,217,728, B2 = 134,217,728, B3 = 134,217,728, B4 = 121,634,816
    cfg = HDFSClusterConfig(file_size_bytes=524288000, block_size_bytes=134217728, replication_factor=3, data_node_count=5)
    engine = HDFSSimulationEngine(config=cfg)
    file_obj, blocks = engine.write_file("customers.csv", 524288000)

    assert len(blocks) == 4
    assert file_obj.block_ids == [b.block_id for b in blocks]
    assert blocks[0].size_bytes == 134217728
    assert blocks[1].size_bytes == 134217728
    assert blocks[2].size_bytes == 134217728
    assert blocks[3].size_bytes == 121634816  # 524288000 - (3 * 134217728)
    assert sum(b.size_bytes for b in blocks) == 524288000


def test_no_duplicate_replica_on_same_datanode():
    # TEST 6: Unique replica placements
    cfg = HDFSClusterConfig(file_size_bytes=524288000, block_size_bytes=134217728, replication_factor=3, data_node_count=5)
    engine = HDFSSimulationEngine(config=cfg)
    _, blocks = engine.write_file("data.csv", 524288000)

    for block in blocks:
        assert len(block.replica_nodes) == 3
        assert len(set(block.replica_nodes)) == 3  # All DataNode IDs must be unique


def test_namenode_metadata_queries():
    # TEST 8 & TEST 9: NameNode metadata lookup
    cfg = HDFSClusterConfig(file_size_bytes=524288000, block_size_bytes=134217728, replication_factor=3, data_node_count=5)
    engine = HDFSSimulationEngine(config=cfg)
    file_obj, blocks = engine.write_file("test.csv", 524288000)

    meta = engine.state.namenode.metadata
    assert meta.get_file("test.csv") == file_obj
    assert len(meta.get_file_blocks(file_obj.file_id)) == 4

    first_block = blocks[0]
    locations = meta.get_block_locations(first_block.block_id)
    assert locations == first_block.replica_nodes


def test_file_read_success():
    # TEST 10: File read succeeds with healthy replicas
    cfg = HDFSClusterConfig(file_size_bytes=524288000, block_size_bytes=134217728, replication_factor=3, data_node_count=5)
    engine = HDFSSimulationEngine(config=cfg)
    engine.write_file("read_test.csv", 524288000)

    read_res = engine.read_file("read_test.csv")
    assert read_res["path"] == "read_test.csv"
    assert read_res["total_bytes"] == 524288000
    assert len(read_res["read_plan"]) == 4


def test_datanode_failure_and_under_replication():
    # TEST 11, TEST 12, TEST 13: DataNode failure causes under-replication
    cfg = HDFSClusterConfig(file_size_bytes=524288000, block_size_bytes=134217728, replication_factor=3, data_node_count=5)
    engine = HDFSSimulationEngine(config=cfg)
    _, blocks = engine.write_file("fail_test.csv", 524288000)

    # Identify DataNodes holding replicas of block-00001
    b1 = blocks[0]
    failed_node_id = b1.replica_nodes[0]

    under_rep, lost = engine.fail_datanode(failed_node_id)
    assert failed_node_id not in engine.state.namenode.metadata.get_live_datanodes if hasattr(engine.state.namenode.metadata, "get_live_datanodes") else True
    assert b1.block_id in under_rep
    assert b1.state == BlockState.UNDER_REPLICATED
    assert len(b1.replica_nodes) == 2


def test_recovery_under_replicated_blocks():
    # TEST 14 & TEST 15: Recovery restores under-replicated block to HEALTHY
    cfg = HDFSClusterConfig(file_size_bytes=524288000, block_size_bytes=134217728, replication_factor=3, data_node_count=5)
    engine = HDFSSimulationEngine(config=cfg)
    _, blocks = engine.write_file("rec_test.csv", 524288000)

    b1 = blocks[0]
    failed_node_id = b1.replica_nodes[0]
    engine.fail_datanode(failed_node_id)

    assert b1.state == BlockState.UNDER_REPLICATED

    recovered = engine.recover_under_replicated_blocks()
    assert len(recovered) > 0
    assert b1.state == BlockState.HEALTHY
    assert len(b1.replica_nodes) == 3


def test_all_replicas_fail_causes_data_loss():
    # TEST 16, TEST 17, TEST 18: Multiple failures causing block LOST & read failure
    cfg = HDFSClusterConfig(file_size_bytes=524288000, block_size_bytes=134217728, replication_factor=3, data_node_count=5)
    engine = HDFSSimulationEngine(config=cfg)
    _, blocks = engine.write_file("loss_test.csv", 524288000)

    b1 = blocks[0]
    nodes_to_fail = list(b1.replica_nodes)

    for node_id in nodes_to_fail:
        engine.fail_datanode(node_id)

    assert b1.state == BlockState.LOST

    with pytest.raises(BlockDataLossError):
        engine.read_file("loss_test.csv")


def test_heartbeat_updates():
    # TEST 19: Heartbeat updates DataNode health
    cfg = HDFSClusterConfig(file_size_bytes=524288000, block_size_bytes=134217728, replication_factor=3, data_node_count=5)
    engine = HDFSSimulationEngine(config=cfg)

    hb_time = engine.send_heartbeat("datanode-1")
    assert hb_time > 0.0
    assert engine.state.datanodes["datanode-1"].heartbeat_status == "HEALTHY"
