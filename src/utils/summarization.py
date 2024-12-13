from transformers import pipeline

# Initialize summarizer
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_document(content, max_length_ratio=0.5, min_length_ratio=0.2):
    """
    Summarize a document for better LLM context with dynamic length adjustment.
    Handles both string and list input for content.
    """
    try:
        # Ensure content is a string
        if isinstance(content, list):
            content = "\n".join(content)
        
        # Split content into chunks for better summarization
        chunk_size = 1024  # Adjust based on model token limit
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

        summaries = []
        for chunk in chunks:
            input_length = len(chunk.split())  # Calculate input token length
            max_length = int(input_length * max_length_ratio)  # Set max length dynamically
            min_length = int(input_length * min_length_ratio)  # Set min length dynamically

            # Ensure lengths are within valid range
            max_length = max(min_length + 1, min(max_length, 300))  # Max capped at 300
            min_length = min(min_length, max_length - 1)

            # Generate summary
            summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
            summaries.append(summary[0]["summary_text"])

        # Combine all summaries
        final_summary = " ".join(summaries)
        return final_summary
    except Exception as e:
        print(f"Error in summarize_document: {e}")
        return f"Error summarizing content: {e}"