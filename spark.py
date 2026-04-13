import llm
import random

SPARK_TEMPLATES = [
    "Generate a brief, compelling premise for a fantasy story involving a lost artifact and an unlikely hero.",
    "Generate a sci-fi story hook about a space station that discovers a signal from an ancient civilization.",
    "Generate a mystery premise set in a fog-drenched Victorian city where something is stealing shadows.",
    "Generate a post-apocalyptic story seed about a group of survivors finding a lush, green oasis in the middle of a desert.",
    "Generate a cyberpunk hook about a hacker who finds a ghost in the machine of a mega-corporation."
]

def generate_spark(genre=None):
    if genre:
        prompt = f"Generate a brief, compelling {genre} story premise."
    else:
        prompt = random.choice(SPARK_TEMPLATES)
    
    print(f"Generating spark with prompt: {prompt}")
    
    spark_content = ""
    for chunk in llm.generate_story_segment(prompt):
        spark_content += chunk
    
    return spark_content

if __name__ == "__main__":
    print("--- Spark Generator Test ---")
    print(generate_spark())