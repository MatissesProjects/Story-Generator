import llm
import random
import config

SPARK_TEMPLATES = [
    "Generate a brief, compelling premise for a fantasy story involving a lost artifact and an unlikely hero.",
    "Generate a sci-fi story hook about a space station that discovers a signal from an ancient civilization.",
    "Generate a mystery premise set in a fog-drenched Victorian city where something is stealing shadows.",
    "Generate a post-apocalyptic story seed about a group of survivors finding a lot, green oasis in the middle of a desert.",
    "Generate a cyberpunk hook about a hacker who finds a ghost in the machine of a mega-corporation."
]

async def generate_spark(genre=None, model=config.FAST_MODEL):
    if genre:
        prompt = f"Generate a brief, compelling {genre} story premise."
    else:
        prompt = random.choice(SPARK_TEMPLATES)

    print(f"Generating spark with prompt: {prompt}")

    spark_content = ""
    async for chunk in llm.generate_story_segment(prompt, model=model):
        spark_content += chunk

    return spark_content

if __name__ == "__main__":
    print("--- Spark Generator Test ---")
    print(generate_spark())