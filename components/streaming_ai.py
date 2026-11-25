"""
Streaming AI Responses
Real-time streaming responses from AI models
"""
import tkinter as tk
from tkinter import scrolledtext
import threading
import queue
import time
import json
from components import death_theme as T


class StreamingAIResponse:
    """Handles streaming AI responses with real-time display"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.stream_queue = queue.Queue()
        self.is_streaming = False
        self.current_response = ""
        self.stop_requested = False

    def stream_response(self, display_widget, prompt, system_prompt="", on_complete=None):
        """Stream AI response to display widget"""
        self.is_streaming = True
        self.stop_requested = False
        self.current_response = ""

        # Clear display
        if isinstance(display_widget, (tk.Text, scrolledtext.ScrolledText)):
            display_widget.config(state='normal')
            display_widget.delete('1.0', 'end')

        # Start streaming thread
        thread = threading.Thread(
            target=self._streaming_thread,
            args=(display_widget, prompt, system_prompt, on_complete),
            daemon=True
        )
        thread.start()

        # Start display update loop
        self._update_display_loop(display_widget, on_complete)

    def _streaming_thread(self, display_widget, prompt, system_prompt, on_complete):
        """Background thread for getting AI response"""
        try:
            # Check if model supports streaming
            if hasattr(self.ide, '_call_model_streaming'):
                # Use native streaming if available
                for chunk in self.ide._call_model_streaming(
                    self.ide.coder_model.get() if hasattr(self.ide, 'coder_model') else 'default',
                    system_prompt,
                    prompt,
                    120
                ):
                    if self.stop_requested:
                        break
                    self.stream_queue.put(('chunk', chunk))
                    self.current_response += chunk
            else:
                # Simulate streaming for non-streaming models
                self._simulate_streaming(display_widget, prompt, system_prompt)

            # Signal completion
            self.stream_queue.put(('complete', self.current_response))

        except Exception as e:
            self.stream_queue.put(('error', str(e)))

        finally:
            self.is_streaming = False

    def _simulate_streaming(self, display_widget, prompt, system_prompt):
        """Simulate streaming by chunking response"""
        try:
            # Get full response
            if hasattr(self.ide, '_call_model'):
                response = self.ide._call_model(
                    self.ide.coder_model.get() if hasattr(self.ide, 'coder_model') else 'default',
                    system_prompt,
                    prompt,
                    120
                )

                # Stream word by word
                words = response.split()
                for i, word in enumerate(words):
                    if self.stop_requested:
                        break

                    chunk = word + (' ' if i < len(words) - 1 else '')
                    self.stream_queue.put(('chunk', chunk))
                    self.current_response += chunk
                    time.sleep(0.05)  # Simulate streaming delay

        except Exception as e:
            self.stream_queue.put(('error', str(e)))

    def _update_display_loop(self, display_widget, on_complete):
        """Update display with streamed content"""
        try:
            # Process all queued items
            while True:
                try:
                    event_type, data = self.stream_queue.get_nowait()

                    if event_type == 'chunk':
                        # Append chunk to display
                        if isinstance(display_widget, (tk.Text, scrolledtext.ScrolledText)):
                            display_widget.config(state='normal')
                            display_widget.insert('end', data)
                            display_widget.see('end')
                            display_widget.config(state='disabled')

                    elif event_type == 'complete':
                        # Streaming complete
                        if on_complete:
                            on_complete(data)
                        return

                    elif event_type == 'error':
                        # Error occurred
                        if isinstance(display_widget, (tk.Text, scrolledtext.ScrolledText)):
                            display_widget.config(state='normal')
                            display_widget.insert('end', f"\n\nError: {data}", 'error')
                            display_widget.config(state='disabled')
                        return

                except queue.Empty:
                    break

            # Schedule next update
            if self.is_streaming:
                display_widget.after(50, self._update_display_loop, display_widget, on_complete)

        except Exception as e:
            print(f"Display update error: {e}")

    def stop_streaming(self):
        """Stop current streaming"""
        self.stop_requested = True


class StreamingChatWidget(tk.Frame):
    """Chat widget with streaming responses"""

    def __init__(self, parent, ide_instance):
        super().__init__(parent, bg=T.BG3)
        self.ide = ide_instance
        self.streaming_ai = StreamingAIResponse(ide_instance)
        self.conversation_history = []

        self.setup_ui()

    def setup_ui(self):
        """Setup streaming chat UI"""
        # Header
        header = tk.Frame(self, bg=T.BG, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="💬 Streaming AI Chat", font=(T.UI, 11, 'bold'),
                fg=T.BILE, bg=T.BG).pack(side=tk.LEFT, padx=10, pady=10)

        # Stop button
        self.stop_btn = tk.Button(
            header,
            text="⬛ Stop",
            command=self.stop_streaming,
            bg=T.BLOOD,
            fg=T.TEXT,
            relief=tk.FLAT,
            state='disabled'
        )
        self.stop_btn.pack(side=tk.RIGHT, padx=10)

        # Chat display
        chat_frame = tk.Frame(self, bg=T.BG)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=(T.UI, 10),
            bg=T.BG,
            fg=T.TEXT,
            state='disabled'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Configure tags
        self.chat_display.tag_configure("user", foreground=T.BILE, font=(T.UI, 10, 'bold'))
        self.chat_display.tag_configure("ai", foreground=T.SIGNAL, font=(T.UI, 10, 'bold'))
        self.chat_display.tag_configure("error", foreground=T.BLOOD_LIGHT)
        self.chat_display.tag_configure("streaming", foreground=T.TEXT)

        # Input area
        input_frame = tk.Frame(self, bg=T.BG3)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.input_field = tk.Text(
            input_frame,
            height=3,
            font=(T.UI, 10),
            bg=T.BG,
            fg=T.TEXT,
            insertbackground=T.TEXT,
            wrap=tk.WORD
        )
        self.input_field.pack(fill=tk.BOTH, expand=True, pady=5)
        self.input_field.bind('<Control-Return>', lambda e: self.send_message())

        # Send button
        tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg=T.BLOOD,
            fg=T.TEXT,
            font=(T.UI, 10, 'bold'),
            relief=tk.FLAT,
            padx=20
        ).pack(pady=5)

    def send_message(self):
        """Send message and get streaming response"""
        message = self.input_field.get('1.0', 'end-1c').strip()
        if not message:
            return

        # Clear input
        self.input_field.delete('1.0', 'end')

        # Add user message to display
        self.chat_display.config(state='normal')
        self.chat_display.insert('end', '\n' if self.conversation_history else '')
        self.chat_display.insert('end', 'You: ', 'user')
        self.chat_display.insert('end', f"{message}\n\n")
        self.chat_display.insert('end', 'AI: ', 'ai')
        self.chat_display.config(state='disabled')

        # Store user message
        self.conversation_history.append({
            'role': 'user',
            'content': message
        })

        # Get cursor position for AI response
        ai_response_start = self.chat_display.index('end-1c')

        # Enable stop button
        self.stop_btn.config(state='normal')

        # Stream response
        system_prompt = "You are a helpful AI coding assistant. Provide clear, concise responses."

        def on_complete(response):
            # Store AI response
            self.conversation_history.append({
                'role': 'assistant',
                'content': response
            })
            # Disable stop button
            self.stop_btn.config(state='disabled')

        # Create temporary display widget for streaming
        self._stream_to_chat_display(message, system_prompt, on_complete)

    def _stream_to_chat_display(self, message, system_prompt, on_complete):
        """Stream response directly to chat display"""
        self.streaming_ai.is_streaming = True
        self.streaming_ai.stop_requested = False
        self.streaming_ai.current_response = ""

        # Start streaming thread
        thread = threading.Thread(
            target=self._chat_streaming_thread,
            args=(message, system_prompt, on_complete),
            daemon=True
        )
        thread.start()

        # Start display update loop
        self._chat_display_loop(on_complete)

    def _chat_streaming_thread(self, message, system_prompt, on_complete):
        """Background thread for chat streaming"""
        try:
            # Simulate streaming (replace with actual streaming API)
            if hasattr(self.ide, '_call_model'):
                response = self.ide._call_model(
                    self.ide.coder_model.get() if hasattr(self.ide, 'coder_model') else 'default',
                    system_prompt,
                    message,
                    120
                )

                # Stream word by word
                words = response.split()
                for i, word in enumerate(words):
                    if self.streaming_ai.stop_requested:
                        break

                    chunk = word + (' ' if i < len(words) - 1 else '')
                    self.streaming_ai.stream_queue.put(('chunk', chunk))
                    self.streaming_ai.current_response += chunk
                    time.sleep(0.03)  # Streaming delay

            # Signal completion
            self.streaming_ai.stream_queue.put(('complete', self.streaming_ai.current_response))

        except Exception as e:
            self.streaming_ai.stream_queue.put(('error', str(e)))

        finally:
            self.streaming_ai.is_streaming = False

    def _chat_display_loop(self, on_complete):
        """Update chat display with streamed content"""
        try:
            updated = False

            # Process queued items
            while True:
                try:
                    event_type, data = self.streaming_ai.stream_queue.get_nowait()

                    if event_type == 'chunk':
                        # Append chunk
                        self.chat_display.config(state='normal')
                        self.chat_display.insert('end', data)
                        self.chat_display.see('end')
                        self.chat_display.config(state='disabled')
                        updated = True

                    elif event_type == 'complete':
                        # Complete
                        self.chat_display.config(state='normal')
                        self.chat_display.insert('end', '\n')
                        self.chat_display.config(state='disabled')
                        if on_complete:
                            on_complete(data)
                        return

                    elif event_type == 'error':
                        # Error
                        self.chat_display.config(state='normal')
                        self.chat_display.insert('end', f"\n\nError: {data}\n", 'error')
                        self.chat_display.config(state='disabled')
                        return

                except queue.Empty:
                    break

            # Schedule next update
            if self.streaming_ai.is_streaming:
                self.after(50, self._chat_display_loop, on_complete)

        except Exception as e:
            print(f"Chat display error: {e}")

    def stop_streaming(self):
        """Stop current streaming"""
        self.streaming_ai.stop_streaming()
        self.stop_btn.config(state='disabled')


class StreamingCodeGenerator:
    """Streaming code generation with real-time file updates"""

    def __init__(self, ide_instance):
        self.ide = ide_instance
        self.streaming_ai = StreamingAIResponse(ide_instance)

    def generate_code_streaming(self, prompt, target_editor, on_complete=None):
        """Generate code with streaming updates to editor"""
        # Clear editor
        target_editor.delete('1.0', 'end')

        # Show loading indicator
        target_editor.insert('1.0', '// Generating code...\n')

        # Build prompt
        system_prompt = """You are a code generator. Generate ONLY code, no explanations or markdown."""

        # Stream to editor
        def stream_complete(response):
            # Clean up loading indicator
            target_editor.delete('1.0', 'end')
            target_editor.insert('1.0', response)

            # Highlight syntax
            if hasattr(target_editor, 'highlight_syntax'):
                target_editor.highlight_syntax()

            if on_complete:
                on_complete(response)

        self.streaming_ai.stream_response(
            target_editor,
            prompt,
            system_prompt,
            stream_complete
        )


class ProgressiveResponseWidget(tk.Frame):
    """Widget showing progressive AI response"""

    def __init__(self, parent):
        super().__init__(parent, bg=T.BG3)

        # Progress bar
        self.progress = tk.Label(
            self,
            text="⏳ Thinking...",
            bg=T.BG3,
            fg=T.SIGNAL,
            font=(T.UI, 9)
        )
        self.progress.pack(padx=10, pady=5)

        # Animation
        self.animation_running = False
        self.animation_frame = 0

    def start_animation(self):
        """Start thinking animation"""
        self.animation_running = True
        self._animate()

    def _animate(self):
        """Animate thinking indicator"""
        if not self.animation_running:
            return

        frames = ['⏳', '⌛']
        self.animation_frame = (self.animation_frame + 1) % len(frames)
        self.progress.config(text=f"{frames[self.animation_frame]} Thinking...")

        self.after(500, self._animate)

    def stop_animation(self):
        """Stop animation"""
        self.animation_running = False
        self.progress.config(text="✓ Complete", fg=T.BILE)

    def show_error(self, message):
        """Show error"""
        self.animation_running = False
        self.progress.config(text=f"✗ Error: {message}", fg=T.BLOOD_LIGHT)
