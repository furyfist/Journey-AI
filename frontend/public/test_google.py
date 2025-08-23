import os
from dotenv import load_dotenv
from portia import Config, Portia, LLMProvider

load_dotenv()

print("Attempting to run Portia with Google Gemini...")

try:

    config = Config.from_default(
        llm_provider=LLMProvider.GOOGLE,
        default_model="google/gemini-1.5-flash" 
    )

    portia = Portia(config=config)

    task = "add 1 + 2"
    plan_run = portia.run(task)

    print("\n--- SUCCESS ---")
    print(f"The result is: {plan_run.outputs.final_output}")

except Exception as e:
    print(f"\n--- AN ERROR OCCURRED ---")
    print(f"Error details: {e}")
    print("\nPlease double-check that your GOOGLE_API_KEY is set correctly in the .env file.")