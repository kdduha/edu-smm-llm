from langchain_openai import ChatOpenAI
import toml


def config() -> tuple[dict, dict, dict]:
    cfg = toml.load("src/.streamlit/config.toml")
    return cfg["llm"], cfg["openai"], cfg["ui"]


def model(llm_cfg: dict, openai_cfg: dict) -> ChatOpenAI:
    return ChatOpenAI(
        openai_api_base=openai_cfg["api_base"],
        openai_api_key=openai_cfg["api_key"],
        model_name=llm_cfg["model_name"],
    )
