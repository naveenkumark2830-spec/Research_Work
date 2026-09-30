from app.jarvis.visualization_animation import (
    VisualizationAnimationBuilder,
)


def test_write_file_animation():

    before = {
        "nodes": [
            {"id": "namenode", "type": "namenode", "status": "active"},
            {"id": "dn-1", "type": "datanode", "status": "active"},
        ],
        "blocks": [],
    }

    after = {
        "nodes": [
            {"id": "namenode", "type": "namenode", "status": "active"},
            {"id": "dn-1", "type": "datanode", "status": "active"},
        ],
        "blocks": [
            {
                "id": "blk-1",
                "replicas": ["dn-1"],
            }
        ],
    }

    result = VisualizationAnimationBuilder().build_animation(
        "write_file",
        before,
        after,
    )

    assert result["animation_type"] == "hdfs"
    assert result["metadata"]["animation_count"] > 0

    types = [
        animation["type"]
        for animation in result["animations"]
    ]

    assert "block_created" in types
    assert "replication" in types
    assert "operation_complete" in types


def test_datanode_failure_animation():

    before = {
        "nodes": [
            {
                "id": "dn-1",
                "type": "datanode",
                "status": "active",
            }
        ],
        "blocks": [],
    }

    after = {
        "nodes": [
            {
                "id": "dn-1",
                "type": "datanode",
                "status": "failed",
            }
        ],
        "blocks": [],
    }

    result = VisualizationAnimationBuilder().build_animation(
        "kill_datanode",
        before,
        after,
    )

    assert result["metadata"]["animation_count"] == 1
    assert result["animations"][0]["type"] == "datanode_failure"
    assert result["animations"][0]["target"] == "dn-1"


def test_datanode_recovery_animation():

    before = {
        "nodes": [
            {
                "id": "dn-1",
                "type": "datanode",
                "status": "failed",
            }
        ],
        "blocks": [],
    }

    after = {
        "nodes": [
            {
                "id": "dn-1",
                "type": "datanode",
                "status": "active",
            }
        ],
        "blocks": [],
    }

    result = VisualizationAnimationBuilder().build_animation(
        "recover_datanode",
        before,
        after,
    )

    assert result["metadata"]["animation_count"] == 1
    assert result["animations"][0]["type"] == "datanode_recovery"


def test_replication_recovery_animation():

    before = {
        "nodes": [],
        "blocks": [
            {
                "id": "blk-1",
                "replicas": ["dn-1"],
            }
        ],
    }

    after = {
        "nodes": [],
        "blocks": [
            {
                "id": "blk-1",
                "replicas": ["dn-1", "dn-2"],
            }
        ],
    }

    result = VisualizationAnimationBuilder().build_animation(
        "recover_under_replicated_blocks",
        before,
        after,
    )

    assert result["metadata"]["animation_count"] == 1
    assert (
        result["animations"][0]["type"]
        == "block_replication_recovery"
    )
    assert result["animations"][0]["target"] == "dn-2"
