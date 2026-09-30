from app.jarvis.visualization_scene import VisualizationSceneBuilder


def test_empty_hdfs_scene():
    builder = VisualizationSceneBuilder()

    scene = builder.build_scene(
        None,
        question="What does the NameNode do?"
    )

    assert scene["scene_type"] == "hdfs"
    assert scene["metadata"]["state_available"] is False
    assert scene["nodes"] == []


def test_basic_hdfs_scene():

    state = {
        "cluster": {
            "data_nodes": [
                {
                    "node_id": "dn-1",
                    "status": "active",
                },
                {
                    "node_id": "dn-2",
                    "status": "active",
                },
            ],
            "files": [
                {
                    "path": "/teddy/demo-file",
                    "blocks": [
                        {
                            "block_id": "blk-1",
                            "replicas": ["dn-1", "dn-2"],
                        }
                    ],
                }
            ],
        }
    }

    builder = VisualizationSceneBuilder()

    scene = builder.build_scene(
        state,
        question="Write a file into HDFS",
        teddy_response="HDFS stores the file as blocks."
    )

    assert scene["scene_type"] == "hdfs"

    node_ids = [
        node["id"]
        for node in scene["nodes"]
    ]

    assert "namenode" in node_ids
    assert "dn-1" in node_ids
    assert "dn-2" in node_ids
    assert "blk-1" in node_ids

    assert scene["metadata"]["datanode_count"] == 2
    assert scene["metadata"]["block_count"] == 1


def test_failed_datanode_scene():

    state = {
        "cluster": {
            "data_nodes": [
                {
                    "node_id": "dn-1",
                    "status": "failed",
                },
                {
                    "node_id": "dn-2",
                    "status": "active",
                },
            ],
            "files": [],
        }
    }

    builder = VisualizationSceneBuilder()

    scene = builder.build_scene(state)

    assert scene["metadata"]["failed_datanode_count"] == 1

    failure_events = [
        event
        for event in scene["events"]
        if event["type"] == "datanode_failure"
    ]

    assert len(failure_events) == 1
    assert "dn-1" in failure_events[0]["nodes"]
