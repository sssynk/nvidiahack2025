"""
Demo script showing how to use the Class AI Agent programmatically
"""
from class_agent import ClassAIAgent
import os


def main():
    # Initialize the agent (make sure NVIDIA_API_KEY is set)
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("Please set NVIDIA_API_KEY environment variable")
        print("Example: export NVIDIA_API_KEY='your_key_here'")
        return
    
    agent = ClassAIAgent(api_key=api_key)
    
    # Example transcript
    transcript_text = """
In today's lecture, we covered the fundamentals of machine learning.

We started with supervised learning, where the algorithm learns from labeled data. 
The main types are classification and regression. Classification predicts categories, 
while regression predicts continuous values.

For example, predicting whether an email is spam or not spam is a classification problem. 
Predicting house prices is a regression problem.

Next, we discussed unsupervised learning, which finds patterns in unlabeled data. 
Common techniques include clustering and dimensionality reduction.

Key takeaways:
1. Always split your data into training and test sets to avoid overfitting
2. Feature engineering is crucial for model performance
3. Start simple before trying complex models

Homework: Implement a linear regression model on the housing dataset.
"""
    
    # Add a class transcript
    print("=" * 60)
    print("DEMO: Adding Class Transcript")
    print("=" * 60)
    
    result = agent.add_class_transcript(
        class_id="ml101-demo",
        transcript=transcript_text,
        title="Introduction to Machine Learning",
        auto_summarize=True
    )
    
    print(f"\n✓ Added: {result['title']}")
    print(f"  Class ID: {result['class_id']}")
    
    if result.get('summary'):
        print("\n--- Auto-generated Summary ---")
        print(result['summary'])
    
    # Ask a question
    print("\n" + "=" * 60)
    print("DEMO: Asking a Question")
    print("=" * 60)
    
    question = "What are the key differences between supervised and unsupervised learning?"
    print(f"\nQuestion: {question}\n")
    print("Answer: ", end='', flush=True)
    
    for chunk in agent.ask_question("ml101-demo", question, stream=True):
        print(chunk, end='', flush=True)
    
    print("\n\n" + "=" * 60)
    print("DEMO: Complete!")
    print("=" * 60)
    print("\nYou can now:")
    print("1. Run the interactive CLI: python cli.py")
    print("2. List classes: python cli.py list")
    print("3. Ask more questions: python cli.py ask ml101-demo 'your question'")


if __name__ == "__main__":
    main()

