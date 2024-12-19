from g4f.client import Client
import gradio as gr
import pytesseract
from PIL import Image
import pyttsx3
import PyPDF2
import docx
import speech_recognition as sr
import pyperclip  # To handle copying the response to clipboard

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

client = Client()

# Function to process text from image (OCR)
def process_image(image: Image.Image):
    try:
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Error processing image: {str(e)}"

# Function to convert text to speech
def text_to_speech(text, language="en"):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)
    voices = engine.getProperty('voices')
    
    # Set voices based on the selected language
    if language == "en":
        engine.setProperty('voice', voices[0].id)  # English voice
    elif language == "fr":
        engine.setProperty('voice', voices[1].id)  # French voice (if available)
    else:
        engine.setProperty('voice', voices[0].id)  # Kiswahili handled by English voice
    
    # Save the audio to a file
    audio_path = "response_audio.mp3"
    engine.save_to_file(text, audio_path)
    engine.runAndWait()
    return audio_path

# Function to handle audio input and convert it to text
def audio_to_text(audio_file):
    recognizer = sr.Recognizer()
    audio = sr.AudioFile(audio_file)
    with audio as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except Exception as e:
        return str(e)

# Function to process PDF files
def process_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to process Word documents
def process_word(file):
    doc = docx.Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text
    return text

# Main chatbot function
def chatbot_response(user_input, file=None, language="en", response_type="text"):
    try:
        if file:
            if file.name.endswith('.pdf'):
                user_input = process_pdf(file)
            elif file.name.endswith('.docx'):
                user_input = process_word(file)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}],
        )
        ai_response = response.choices[0].message.content

        # If response_type is audio, convert response to speech and return the audio path
        if response_type == "audio":
            audio_path = text_to_speech(ai_response, language)
            return ai_response, audio_path
        else:
            return ai_response, None
    except Exception as e:
        return f"Error: {str(e)}", None

# Function to copy AI response to clipboard
def copy_to_clipboard(text):
    pyperclip.copy(text)
    return text

# Gradio interface with improved design
def create_interface():
    with gr.Blocks() as interface:
        # Custom background and styling (blue background gradient)
        gr.Markdown("""
            <style>
                .gradio-container {
                    background: linear-gradient(to right, #1E90FF, #87CEEB); /* Blue gradient background */
                    padding: 15px;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    width: 100%;
                    max-width: 600px; /* Reduced width for smaller system */
                    margin: auto;
                    height: auto; /* Adjusted to be more compact */
                }
                .gradio-input {
                    background-color: #e6f7ff;
                    border-radius: 8px;
                    padding: 8px;
                    width: 100%;
                    max-width: 350px; /* Smaller width for inputs */
                }
                .gradio-button {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 8px;
                    padding: 8px;
                    width: 100%;
                    font-size: 14px; /* Reduced font size */
                    height: 20px; /* Smaller height for button */
                    max-width: 100px; /* Limit button width */
                    margin: auto;
                }
                .gradio-button:hover {
                    background-color: #45a049;
                }
                .gradio-column {
                    padding: 10px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .gradio-textbox {
                    background-color: #f9f9f9;
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    padding: 8px;
                    width: 100%;
                    max-width: 350px;
                    height: 100px; /* Minimized height */
                    resize: none;
                }
                .gradio-dropdown {
                    background-color: rgb(14, 225, 38);
                    border-radius: 8px;
                    padding: 8px;
                    width: 100%;
                }
                .gradio-file {
                    border-radius: 8px;
                    width: 100%;
                    max-width: 350px; /* Smaller file upload size */
                }
                .gradio-row {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px; /* Reduced gap between rows */
                }
                .gradio-row .gradio-column {
                    width: 48%; /* Each column takes 48% of the row width */
                }
                .gradio-textbox, .gradio-file, .gradio-button {
                    margin-bottom: 10px;
                }
                .gradio-audio {
                    max-width: 350px;
                }
                .title {
                    text-align: center;
                    font-size: 60px; /* Increased font size */
                    font-weight: bold;
                    text-transform: uppercase;
                    color:rgb(67, 13, 243) ;
                    margin-bottom: 20px;
                    align-item:center;
                    display:flex;
                    justify-content:center;
                    position:relative;
                    
                }
                .copy-icon {
                    font-size: 18px; /* Small icon size */
                    color: #4CAF50;
                    cursor: pointer;
                    margin-top: 5px;
                    display: inline-block;
                    margin-left: 10px;
                }
            </style>
        """)

        # Title in center with capitalized text
        gr.Markdown('<div class="title">SMARTECH AI ASSISTANT</div>')

        with gr.Row():
            with gr.Column():
                # Text input on the left side with minimized size
                text_input = gr.Textbox(label="Enter your question", placeholder="message SMARTECH AI...design by senior ceo", lines=2, max_lines=2)
                
                # Submit button between the text input and file input
                submit_button = gr.Button("Submit", elem_id="submit_button", variant="primary")

            with gr.Column():
                # File upload section on the right side with minimized size
                file_input = gr.File(label="Upload PDF/Word Document")

        # Below both input sections, display the AI response
        with gr.Row():
            with gr.Column():
                # Language selection dropdown on the left side
                language_select = gr.Dropdown(
                    choices=["en", "sw", "fr"], 
                    label="Select Language", 
                    value="en",  # Default to English
                    interactive=True
                )
                
            with gr.Column():
                # Response type dropdown on the right side (text/audio)
                response_type = gr.Dropdown(choices=["text", "audio"], label="Response Type", value="text", interactive=True)

        # Below the language and response type, display the output
        with gr.Row():
            with gr.Column():
                # Output text box for the AI response (copyable)
                output_text = gr.Textbox(label="AI Response", interactive=False, elem_id="response_box", value="", lines=3, max_lines=5)

                # Small icon button to copy the response text
                copy_button = gr.HTML("""
                    <span class="copy-icon" onclick="navigator.clipboard.writeText(document.getElementById('response_box').value)">
                        &#128203; <!-- Copy Icon -->
                    </span>
                """)
                
            with gr.Column():
                # Audio response (if selected)
                output_audio = gr.Audio(label="AI Audio Response", interactive=False)

        # Handling the submit button click event
        submit_button.click(
            chatbot_response,
            inputs=[text_input, file_input, language_select, response_type],
            outputs=[output_text, output_audio],
        )

    return interface

# Run the interface
if __name__ == "__main__":
    create_interface().launch()
