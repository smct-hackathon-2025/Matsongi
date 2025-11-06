import pandas as pd
import pickle
import numpy as np

def load_flavorgraph(node_csv_path, embedding_pickle_path):
    print("🔄 FlavorGraph 데이터 로드 중...")

    nodes_df = pd.read_csv(node_csv_path)
    name_to_node_id = pd.Series(nodes_df.node_id.values, index=nodes_df.name).to_dict()

    with open(embedding_pickle_path, "rb") as f:
        node_id_to_vec = pickle.load(f)

    name_to_vec = {}
    for name, node_id in name_to_node_id.items():
        node_id_str = str(node_id)
        if node_id_str in node_id_to_vec:
            name_to_vec[name] = np.array(node_id_to_vec[node_id_str])

    print(f"✅ FlavorGraph 로드 완료: {len(name_to_vec)}개 재료")
    return name_to_vec
