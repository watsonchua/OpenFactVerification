

from factcheck import FactCheck
from factcheck.utils.utils import load_yaml
from pathlib import Path
import pandas as pd
import json
from tqdm.auto import tqdm


def main(api_config_path="../api_config.yaml", start_index=0, end_index=None):
    api_config = load_yaml(api_config_path)
    output_path = Path("/home/watso/sls-assistant-evaluation/data/analysis/ofv_results_wiki_retriever.json")
    
    # use chatgpt_wiki_prompt for wikipedia searches
    factcheck_instance = FactCheck(
            default_model="gpt-4o-eastus", client=None, api_config=api_config, prompt="chatgpt_wiki_prompt", retriever="wikipedia"
        )
    
    df = pd.read_csv("/home/watso/sls-assistant-evaluation/data/analysis/hd_fc_by_record.csv")
    df_fc_fail = df[(df["hd_score"] ==  "FAIL") & (df["fc_score"] ==  "FAIL")]

    # new_results = []
    if end_index is None:
        end_index = len(df_fc_fail)

    df_eval = df_fc_fail[start_index:end_index]
    for index, row in tqdm(df_eval.iterrows(), total=len(df_eval)):
        statement = row["statement"]
        try:        
            results = factcheck_instance.check_text(statement)
        except AttributeError as e:
            print(f"Error: {e}")
            continue
        # new_results.append({**row, "ofv_results": results})

        with output_path.open("a") as f:
            f.write(json.dumps({**row, "ofv_results": results}))
            f.write("\n")




if __name__ == "__main__":
    main()