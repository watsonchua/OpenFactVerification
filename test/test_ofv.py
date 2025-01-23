

from factcheck import FactCheck
from factcheck.utils.utils import load_yaml
from pathlib import Path




def main(api_config_path="../api_config.yaml"):
    api_config = load_yaml(api_config_path)

    
    factcheck_instance = FactCheck(
            default_model="gpt-4o-eastus", client=None, api_config=api_config, prompt="chatgpt_prompt", retriever="serper"
        )
    



    # Example text
    text = "Climate change refers to long-term changes in temperature and weather patterns, primarily caused by human activities like burning fossil fuels and deforestation. These actions release greenhouse gases, which trap heat in the atmosphere. As for cows, they produce methane, a potent greenhouse gas, during digestion. So, while they can't literally talk, they do play a role in climate change!"

    # Run the fact-check pipeline
    results = factcheck_instance.check_text(text)
    print(results)


if __name__ == "__main__":
    main()