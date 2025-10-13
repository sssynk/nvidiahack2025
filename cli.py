"""
Command-line interface for the Class AI Agent
"""
import argparse
import sys
from class_agent import ClassAIAgent
from typing import Optional


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_section(text: str):
    """Print a section header"""
    print(f"\n--- {text} ---\n")


def add_transcript_interactive(agent: ClassAIAgent):
    """Interactive mode for adding a transcript"""
    print_header("Add New Class Transcript")
    
    class_id = input("Enter Class ID (e.g., 'cs101-lecture1'): ").strip()
    title = input("Enter Class Title (optional): ").strip() or None
    
    print("\nEnter the transcript (press Ctrl+D or Ctrl+Z when done):")
    print("(You can paste multi-line text)")
    
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    transcript = "\n".join(lines)
    
    if not transcript.strip():
        print("Error: Transcript cannot be empty")
        return
    
    print("\nProcessing transcript...")
    result = agent.add_class_transcript(class_id, transcript, title)
    
    print(f"\n✓ Transcript added successfully!")
    print(f"  Class ID: {result['class_id']}")
    print(f"  Title: {result['title']}")
    
    if result.get('summary'):
        print_section("Auto-generated Summary")
        print(result['summary'])


def list_classes(agent: ClassAIAgent):
    """List all classes"""
    print_header("Available Classes")
    
    classes = agent.list_classes()
    
    if not classes:
        print("No classes found.")
        return
    
    for i, cls in enumerate(classes, 1):
        print(f"{i}. {cls['title']}")
        print(f"   ID: {cls['class_id']}")
        print(f"   Date: {cls['timestamp']}")
        print(f"   Has Summary: {'Yes' if cls.get('summary') else 'No'}")
        print()


def ask_question_interactive(agent: ClassAIAgent):
    """Interactive mode for asking questions"""
    print_header("Ask a Question")
    
    classes = agent.list_classes()
    if not classes:
        print("No classes available. Please add a transcript first.")
        return
    
    print("Available classes:")
    for i, cls in enumerate(classes, 1):
        print(f"  {i}. {cls['title']} (ID: {cls['class_id']})")
    
    print("\nOptions:")
    print("  - Enter a class number to ask about a specific class")
    print("  - Enter 'all' to search across all classes")
    
    choice = input("\nYour choice: ").strip()
    
    if choice.lower() == 'all':
        class_id = None
    elif choice.isdigit() and 1 <= int(choice) <= len(classes):
        class_id = classes[int(choice) - 1]['class_id']
    else:
        print("Invalid choice")
        return
    
    question = input("\nEnter your question: ").strip()
    if not question:
        print("Error: Question cannot be empty")
        return
    
    print_section("Answer")
    
    try:
        if class_id:
            response = agent.ask_question(class_id, question, stream=True)
        else:
            response = agent.ask_across_classes(question, stream=True)
        
        for chunk in response:
            print(chunk, end='', flush=True)
        print("\n")
    except Exception as e:
        print(f"Error: {e}")


def view_summary(agent: ClassAIAgent):
    """View or generate summary for a class"""
    print_header("View/Generate Summary")
    
    classes = agent.list_classes()
    if not classes:
        print("No classes available. Please add a transcript first.")
        return
    
    print("Available classes:")
    for i, cls in enumerate(classes, 1):
        summary_status = "✓" if cls.get('summary') else "✗"
        print(f"  {i}. [{summary_status}] {cls['title']} (ID: {cls['class_id']})")
    
    choice = input("\nEnter class number: ").strip()
    
    if not choice.isdigit() or not (1 <= int(choice) <= len(classes)):
        print("Invalid choice")
        return
    
    class_id = classes[int(choice) - 1]['class_id']
    cls_info = agent.get_class_info(class_id)
    
    if cls_info.get('summary'):
        print_section(f"Summary for: {cls_info['title']}")
        print(cls_info['summary'])
        
        regenerate = input("\nRegenerate summary? (y/n): ").strip().lower()
        if regenerate == 'y':
            print("\nRegenerating summary...")
            summary = agent.summarize_transcript(class_id)
            print_section("New Summary")
            print(summary)
    else:
        print(f"\nNo summary exists for '{cls_info['title']}'")
        generate = input("Generate summary now? (y/n): ").strip().lower()
        if generate == 'y':
            print("\nGenerating summary...")
            summary = agent.summarize_transcript(class_id)
            print_section("Summary")
            print(summary)


def interactive_mode(agent: ClassAIAgent):
    """Run the interactive CLI"""
    print_header("Class AI Agent - Interactive Mode")
    
    while True:
        print("\nWhat would you like to do?")
        print("  1. Add a new class transcript")
        print("  2. List all classes")
        print("  3. Ask a question")
        print("  4. View/Generate summary")
        print("  5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            add_transcript_interactive(agent)
        elif choice == '2':
            list_classes(agent)
        elif choice == '3':
            ask_question_interactive(agent)
        elif choice == '4':
            view_summary(agent)
        elif choice == '5':
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def main():
    parser = argparse.ArgumentParser(description="Class AI Agent - Transcript Summarization and Q&A")
    parser.add_argument("--api-key", help="NVIDIA API key (or set NVIDIA_API_KEY env variable)")
    parser.add_argument("--storage", default="transcripts", help="Path to store transcripts")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add transcript command
    add_parser = subparsers.add_parser("add", help="Add a class transcript")
    add_parser.add_argument("class_id", help="Class ID")
    add_parser.add_argument("--title", help="Class title")
    add_parser.add_argument("--file", help="Path to transcript file")
    add_parser.add_argument("--text", help="Transcript text")
    
    # List classes command
    list_parser = subparsers.add_parser("list", help="List all classes")
    
    # Ask question command
    ask_parser = subparsers.add_parser("ask", help="Ask a question")
    ask_parser.add_argument("class_id", help="Class ID (or 'all' for all classes)")
    ask_parser.add_argument("question", help="Question to ask")
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="View or generate summary")
    summary_parser.add_argument("class_id", help="Class ID")
    summary_parser.add_argument("--regenerate", action="store_true", help="Regenerate summary")
    
    args = parser.parse_args()
    
    try:
        agent = ClassAIAgent(api_key=args.api_key, storage_path=args.storage)
        
        if not args.command:
            # Run interactive mode
            interactive_mode(agent)
        elif args.command == "add":
            if args.file:
                with open(args.file, 'r') as f:
                    transcript = f.read()
            elif args.text:
                transcript = args.text
            else:
                print("Error: Either --file or --text is required")
                sys.exit(1)
            
            result = agent.add_class_transcript(args.class_id, transcript, args.title)
            print(f"✓ Transcript added: {result['title']}")
            if result.get('summary'):
                print(f"\nSummary:\n{result['summary']}")
        
        elif args.command == "list":
            classes = agent.list_classes()
            if not classes:
                print("No classes found.")
            else:
                for cls in classes:
                    print(f"- {cls['title']} (ID: {cls['class_id']})")
        
        elif args.command == "ask":
            if args.class_id.lower() == 'all':
                response = agent.ask_across_classes(args.question, stream=True)
            else:
                response = agent.ask_question(args.class_id, args.question, stream=True)
            
            for chunk in response:
                print(chunk, end='', flush=True)
            print()
        
        elif args.command == "summary":
            cls_info = agent.get_class_info(args.class_id)
            if not cls_info:
                print(f"Error: Class '{args.class_id}' not found")
                sys.exit(1)
            
            if args.regenerate or not cls_info.get('summary'):
                summary = agent.summarize_transcript(args.class_id)
            else:
                summary = cls_info['summary']
            
            print(summary)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

