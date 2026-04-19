import asyncio
import random
import llm
import config

class PromptMatrix:
    """A compositional engine for generating unique story sparks."""
    
    def __init__(self):
        self.formats = [
            "a brief, compelling premise",
            "a gripping story hook",
            "a mysterious flash fiction seed",
            "an action-packed elevator pitch",
            "a slow-burn narrative outline",
            "a surreal, dream-like introduction",
            "a tense, mid-action cold open",
            "a world-building heavy lore fragment",
            "a philosophical dialogue snippet"
        ]
        
        self.genres = [
            "fantasy", "sci-fi", "cyberpunk", "Victorian mystery",
            "post-apocalyptic", "urban fantasy", "space opera", "noir",
            "techno-thriller", "cosmic horror", "steampunk", "biopunk",
            "silkpunk", "grimdark", "hopepunk", "weird fiction", "magical realism",
            "solarpunk", "gothic horror", "political thriller", "high fantasy",
            "hard sci-fi", "dieselpunk", "mythic fiction"
        ]
        
        self.settings = [
            "a fog-drenched city", 
            "an abandoned orbital space station",
            "a lush, hidden oasis in a radioactive desert", 
            "a mega-corporation's subterranean data-vault",
            "a clockwork metropolis suspended over a void", 
            "a neon-lit labyrinth of floating islands",
            "a virtual realm where rogue algorithms roam",
            "a decaying underwater research facility",
            "a library that contains every book never written",
            "a massive train that never stops moving across a frozen world",
            "the inside of a gargantuan, dying biological entity",
            "a village where people trade their voices for survival",
            "an archipelago of clouds connected by silver threads",
            "a forest where the trees grow crystal instead of wood",
            "a moon where the gravity changes based on your heart rate"
        ]
        
        self.protagonists = [
            "an unlikely hero", "a cynical hacker", "a disgraced detective",
            "a runaway AI", "a retired assassin", "a lowly cartographer",
            "a genetic engineer with a terrible secret", "an exiled aristocrat",
            "a sentient collection of nanites", "a time-traveling archivist",
            "a blind seer who sees the future in sound", "a rebel against a hive-mind",
            "a chef who can cook emotions into food", "a pilot of a ship powered by dreams",
            "a scavenger in the ruins of a digital afterlife", "a linguist deciphering a god's heartbeat"
        ]
        
        self.catalysts = [
            "discovers a signal from an ancient civilization",
            "finds a lost artifact that bends time",
            "is framed for a crime they didn't commit",
            "must escort a highly unstable entity across enemy lines",
            "wakes up in a synthetic body that isn't theirs",
            "accidentally unleashes a dormant, self-replicating virus",
            "inherits a haunted skyscraper in a city that doesn't exist",
            "receives a letter written by their future self",
            "breaks a fundamental law of reality by accident",
            "is chosen by a dying star to carry its final message",
            "discovers their entire reality is a simulation being deleted",
            "finds a door in their house that leads to 10,000 other worlds"
        ]

        self.themes = [
            "of sacrifice and redemption", "of the cost of immortality",
            "of the blurred line between human and machine", "of the nature of truth in a post-fact world",
            "of the weight of ancestral sins", "of the beauty in entropy",
            "of finding connection in a vast, cold universe", "of the corrupting nature of absolute power",
            "of the struggle between tradition and progress", "of the price of knowledge"
        ]
        
        self.twists = [
            "where something is actively stealing people's memories.",
            "where the laws of physics shift unpredictably every sunset.",
            "but the ghosts in the machine are starting to leak into physical reality.",
            "and their only ally is the villain's right-hand.",
            "while a massive, world-ending anomaly rapidly approaches.",
            "only to realize they are the antagonist of the story.",
            "where words have physical weight and can crush the unwary.",
            "and the sun is actually a giant, unblinking eye.",
            "but every time they succeed, a piece of their past vanishes.",
            "while the shadows of the dead are starting to take on a life of their own.",
            "only to discover that they are the one they've been hunting.",
            "where reality itself is starting to peel away at the edges like old wallpaper."
        ]

    def build_prompt(self, genre=None):
        """Assembles a prompt from the compositional matrices."""
        story_format = random.choice(self.formats)
        chosen_genre = genre if genre else random.choice(self.genres)
        setting = random.choice(self.settings)
        protagonist = random.choice(self.protagonists)
        catalyst = random.choice(self.catalysts)
        theme = random.choice(self.themes)
        twist = random.choice(self.twists)

        return (f"Generate {story_format} for a {chosen_genre} story set in {setting}. "
                f"It explores themes {theme}. "
                f"It follows {protagonist} who {catalyst}, {twist}")


async def generate_spark(genre=None, model=config.FAST_MODEL):
    # 1. Initialize the matrix and build the dynamic prompt
    matrix = PromptMatrix()
    prompt = matrix.build_prompt(genre=genre)

    print(f"Generating spark with prompt:\n> {prompt}\n")

    spark_content = ""
    
    # 2. Call your actual LLM tool exactly as requested
    async for chunk in llm.generate_story_segment(prompt, model=model):
        spark_content += chunk

    return spark_content

async def main():
    print("--- Spark Generator Test ---\n")
    
    # Generate a completely random spark
    random_spark = await generate_spark()
    print("Result:")
    print(random_spark)
    print("\n" + "-"*40 + "\n")
    
    # Generate a spark locked to a specific genre
    cyberpunk_spark = await generate_spark(genre="cyberpunk")
    print("Result:")
    print(cyberpunk_spark)

if __name__ == "__main__":
    # Because generate_spark is an async function, it must be run inside an event loop
    asyncio.run(main())