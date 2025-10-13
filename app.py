"""
Gradio Web UI for Class AI Agent with Video Transcription
"""
import gradio as gr
from integrated_agent import IntegratedClassAgent
import os
from typing import List, Tuple
import json


# Initialize the agent
api_key = os.getenv("NVIDIA_API_KEY")
agent = IntegratedClassAgent(api_key=api_key)


def process_video(video_file, class_id: str, title: str, auto_summarize: bool, progress=gr.Progress()):
    """Process uploaded video"""
    try:
        if not video_file:
            return "❌ Please upload a video file", "", "", ""
        
        if not class_id or not class_id.strip():
            return "❌ Please provide a Class ID", "", "", ""
        
        progress(0.2, desc="Extracting audio...")
        
        # Use provided title or generate from filename
        if not title or not title.strip():
            title = None
        
        progress(0.4, desc="Transcribing audio...")
        result = agent.process_video(
            video_path=video_file,
            class_id=class_id.strip(),
            title=title.strip() if title else None,
            auto_summarize=auto_summarize
        )
        
        progress(1.0, desc="Complete!")
        
        status = f"✅ Successfully processed: **{result['title']}**\n\nClass ID: `{result['class_id']}`"
        transcript = result['transcript']
        summary = result.get('summary', 'No summary generated')
        
        # Update class list dropdown
        classes = agent.list_classes()
        class_choices = [f"{c['title']} ({c['class_id']})" for c in classes]
        
        return status, transcript, summary, gr.Dropdown(choices=class_choices, value=class_choices[-1] if class_choices else None)
        
    except Exception as e:
        return f"❌ Error: {str(e)}", "", "", gr.Dropdown()


def get_class_list():
    """Get list of available classes"""
    classes = agent.list_classes()
    if not classes:
        return []
    return [f"{c['title']} ({c['class_id']})" for c in classes]


def extract_class_id(class_selection: str) -> str:
    """Extract class ID from dropdown selection"""
    if not class_selection:
        return ""
    # Format is "Title (class_id)"
    if '(' in class_selection and ')' in class_selection:
        return class_selection.split('(')[-1].strip(')')
    return class_selection


def chat_with_class(message: str, history: List[Tuple[str, str]], class_selection: str):
    """Chat with a specific class"""
    if not message or not message.strip():
        return history, ""
    
    if not class_selection:
        history.append((message, "❌ Please select a class first"))
        return history, ""
    
    class_id = extract_class_id(class_selection)
    
    try:
        response = ""
        for chunk in agent.ask_question(class_id, message, stream=True):
            response += chunk
        
        history.append((message, response))
        return history, ""
    except Exception as e:
        history.append((message, f"❌ Error: {str(e)}"))
        return history, ""


def chat_across_all(message: str, history: List[Tuple[str, str]]):
    """Chat across all classes"""
    if not message or not message.strip():
        return history, ""
    
    try:
        classes = agent.list_classes()
        if not classes:
            history.append((message, "❌ No classes available. Please add some transcripts first."))
            return history, ""
        
        response = ""
        for chunk in agent.ask_across_classes(message, stream=True):
            response += chunk
        
        history.append((message, response))
        return history, ""
    except Exception as e:
        history.append((message, f"❌ Error: {str(e)}"))
        return history, ""


def view_class_details(class_selection: str):
    """View details of a selected class"""
    if not class_selection:
        return "Please select a class", "", ""
    
    class_id = extract_class_id(class_selection)
    
    try:
        info = agent.get_class_info(class_id)
        if not info:
            return "Class not found", "", ""
        
        details = f"""
**Title:** {info['title']}  
**Class ID:** `{info['class_id']}`  
**Date:** {info['timestamp']}  
**Has Summary:** {'✅ Yes' if info.get('summary') else '❌ No'}
"""
        transcript = info['content']
        summary = info.get('summary', 'No summary available')
        
        return details, transcript, summary
    except Exception as e:
        return f"Error: {str(e)}", "", ""


def regenerate_summary(class_selection: str):
    """Regenerate summary for a class"""
    if not class_selection:
        return "Please select a class first"
    
    class_id = extract_class_id(class_selection)
    
    try:
        summary = agent.summarize_transcript(class_id)
        return summary
    except Exception as e:
        return f"Error: {str(e)}"


# Custom CSS for better styling
custom_css = """
.gradio-container {
    max-width: 1200px !important;
    margin: auto;
}

.header {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    margin-bottom: 20px;
}

.tab-nav {
    background-color: #f8f9fa;
}

footer {
    display: none !important;
}
"""

# Build the Gradio interface
with gr.Blocks(css=custom_css, theme=gr.themes.Soft(), title="Class AI Agent") as demo:
    
    gr.HTML("""
    <div class="header">
        <h1>🎓 Class AI Agent</h1>
        <p>Upload videos, get AI-powered transcripts and summaries, ask questions about your classes</p>
    </div>
    """)
    
    with gr.Tabs():
        
        # Tab 1: Upload Video
        with gr.Tab("📹 Upload Video"):
            gr.Markdown("### Upload a class video for automatic transcription")
            
            with gr.Row():
                with gr.Column(scale=1):
                    video_input = gr.Video(label="Upload Video or Audio File")
                    class_id_input = gr.Textbox(
                        label="Class ID",
                        placeholder="e.g., cs101-lecture1",
                        info="Unique identifier for this class"
                    )
                    title_input = gr.Textbox(
                        label="Class Title (Optional)",
                        placeholder="e.g., Introduction to Python",
                        info="Will be auto-generated from filename if left empty"
                    )
                    auto_summarize = gr.Checkbox(
                        label="Auto-generate summary",
                        value=True,
                        info="Automatically create an AI summary after transcription"
                    )
                    process_btn = gr.Button("🚀 Process Video", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    status_output = gr.Markdown(label="Status")
                    
            with gr.Accordion("📝 Transcript", open=False):
                transcript_output = gr.Textbox(label="Generated Transcript", lines=10, max_lines=20)
            
            with gr.Accordion("📋 Summary", open=True):
                summary_output = gr.Textbox(label="AI-Generated Summary", lines=8, max_lines=15)
            
            class_list_state = gr.State([])
        
        # Tab 2: Ask Questions
        with gr.Tab("💬 Ask Questions"):
            gr.Markdown("### Ask questions about your classes")
            
            with gr.Row():
                with gr.Column(scale=1):
                    class_dropdown = gr.Dropdown(
                        label="Select Class",
                        choices=get_class_list(),
                        interactive=True,
                        info="Choose a specific class to ask questions about"
                    )
                    refresh_btn = gr.Button("🔄 Refresh Class List", size="sm")
                    
                    gr.Markdown("---")
                    gr.Markdown("**Or ask across all classes:**")
                    all_classes_mode = gr.Checkbox(
                        label="Search all classes",
                        value=False,
                        info="Answer questions using all available transcripts"
                    )
                
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(
                        label="Chat",
                        height=500,
                        show_label=True,
                        avatar_images=(None, "https://cdn-icons-png.flaticon.com/512/6134/6134346.png")
                    )
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="Your Question",
                            placeholder="Ask a question about the class...",
                            scale=4,
                            show_label=False
                        )
                        send_btn = gr.Button("Send", variant="primary", scale=1)
                    
                    gr.Examples(
                        examples=[
                            "What are the main topics covered in this class?",
                            "Can you summarize the key takeaways?",
                            "What homework was assigned?",
                            "Explain the most important concept from this lecture",
                        ],
                        inputs=msg_input
                    )
        
        # Tab 3: View Classes
        with gr.Tab("📚 View Classes"):
            gr.Markdown("### Browse and manage your classes")
            
            with gr.Row():
                with gr.Column(scale=1):
                    view_class_dropdown = gr.Dropdown(
                        label="Select Class",
                        choices=get_class_list(),
                        interactive=True
                    )
                    view_refresh_btn = gr.Button("🔄 Refresh", size="sm")
                    view_btn = gr.Button("👁️ View Details", variant="primary")
                    regenerate_btn = gr.Button("🔄 Regenerate Summary", variant="secondary")
                
                with gr.Column(scale=2):
                    class_details = gr.Markdown(label="Class Details")
            
            with gr.Accordion("📝 Full Transcript", open=False):
                view_transcript = gr.Textbox(label="Transcript", lines=10, max_lines=20)
            
            with gr.Accordion("📋 Summary", open=True):
                view_summary = gr.Textbox(label="Summary", lines=8, max_lines=15)
    
    # Event handlers
    
    # Upload tab
    process_btn.click(
        fn=process_video,
        inputs=[video_input, class_id_input, title_input, auto_summarize],
        outputs=[status_output, transcript_output, summary_output, class_dropdown]
    )
    
    # Ask Questions tab
    def ask_question_handler(message, history, class_selection, all_classes):
        if all_classes:
            return chat_across_all(message, history)
        else:
            return chat_with_class(message, history, class_selection)
    
    msg_input.submit(
        fn=ask_question_handler,
        inputs=[msg_input, chatbot, class_dropdown, all_classes_mode],
        outputs=[chatbot, msg_input]
    )
    
    send_btn.click(
        fn=ask_question_handler,
        inputs=[msg_input, chatbot, class_dropdown, all_classes_mode],
        outputs=[chatbot, msg_input]
    )
    
    refresh_btn.click(
        fn=lambda: gr.Dropdown(choices=get_class_list()),
        outputs=class_dropdown
    )
    
    # View Classes tab
    view_btn.click(
        fn=view_class_details,
        inputs=[view_class_dropdown],
        outputs=[class_details, view_transcript, view_summary]
    )
    
    view_refresh_btn.click(
        fn=lambda: gr.Dropdown(choices=get_class_list()),
        outputs=view_class_dropdown
    )
    
    regenerate_btn.click(
        fn=regenerate_summary,
        inputs=[view_class_dropdown],
        outputs=[view_summary]
    )


if __name__ == "__main__":
    print("="*60)
    print("🎓 Starting Class AI Agent Web Interface")
    print("="*60)
    
    if not api_key:
        print("\n⚠️  WARNING: NVIDIA_API_KEY not set!")
        print("Please set your API key:")
        print("  export NVIDIA_API_KEY='your_key_here'\n")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

