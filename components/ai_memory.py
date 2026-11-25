"""
AI Conversation Memory
Persistent AI memory across sessions with context retention
"""
import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import datetime
import hashlib
from components import death_theme as T


class ConversationMemory:
    """Stores and retrieves AI conversation history"""

    def __init__(self, workspace_path=None):
        self.workspace_path = workspace_path
        self.memory_file = self._get_memory_file()
        self.conversations = []  # List of conversation sessions
        self.current_session = None
        self.session_summaries = {}  # session_id -> summary

        self.load_memory()

    def _get_memory_file(self):
        """Get memory file path"""
        if self.workspace_path:
            # Project-specific memory
            project_hash = hashlib.md5(self.workspace_path.encode()).hexdigest()[:8]
            memory_dir = os.path.join(os.path.expanduser('~'), '.deathaius_memory')
            os.makedirs(memory_dir, exist_ok=True)
            return os.path.join(memory_dir, f'memory_{project_hash}.json')
        else:
            # Global memory
            return os.path.join(os.path.expanduser('~'), '.deathaius_memory', 'global_memory.json')

    def load_memory(self):
        """Load conversation memory from disk"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversations = data.get('conversations', [])
                    self.session_summaries = data.get('summaries', {})
            except Exception as e:
                print(f"Failed to load memory: {e}")

    def save_memory(self):
        """Save conversation memory to disk"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)

            data = {
                'conversations': self.conversations[-100:],  # Keep last 100 sessions
                'summaries': self.session_summaries,
                'last_updated': datetime.now().isoformat()
            }

            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save memory: {e}")

    def start_session(self):
        """Start a new conversation session"""
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.current_session = {
            'id': session_id,
            'started': datetime.now().isoformat(),
            'messages': [],
            'context': {}
        }
        return session_id

    def add_message(self, role, content, context=None):
        """Add message to current session"""
        if not self.current_session:
            self.start_session()

        message = {
            'role': role,  # 'user' or 'assistant'
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }

        self.current_session['messages'].append(message)

    def end_session(self, summary=None):
        """End current session and save"""
        if not self.current_session:
            return

        self.current_session['ended'] = datetime.now().isoformat()

        # Generate summary if not provided
        if not summary:
            summary = self._generate_summary(self.current_session)

        self.session_summaries[self.current_session['id']] = summary
        self.conversations.append(self.current_session)

        self.save_memory()
        self.current_session = None

    def _generate_summary(self, session):
        """Generate session summary"""
        if not session['messages']:
            return "Empty session"

        # Count messages
        user_msgs = sum(1 for m in session['messages'] if m['role'] == 'user')
        ai_msgs = sum(1 for m in session['messages'] if m['role'] == 'assistant')

        # Get first user message
        first_msg = next((m['content'] for m in session['messages'] if m['role'] == 'user'), "")
        first_msg_preview = first_msg[:50] + "..." if len(first_msg) > 50 else first_msg

        return f"{first_msg_preview} ({user_msgs} questions, {ai_msgs} responses)"

    def get_relevant_context(self, query, max_messages=10):
        """Get relevant context from past conversations"""
        relevant = []

        # Search recent conversations
        for session in reversed(self.conversations[-20:]):  # Last 20 sessions
            for message in session['messages']:
                if self._is_relevant(query, message['content']):
                    relevant.append({
                        'content': message['content'],
                        'role': message['role'],
                        'timestamp': message['timestamp'],
                        'session': session['id']
                    })

                if len(relevant) >= max_messages:
                    break
            if len(relevant) >= max_messages:
                break

        return relevant

    def _is_relevant(self, query, content):
        """Check if content is relevant to query"""
        # Simple keyword matching
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        # Check for common words (excluding common stopwords)
        common = query_words & content_words
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why'}
        common = common - stopwords

        return len(common) >= 2  # At least 2 common meaningful words

    def get_conversation_summary(self):
        """Get summary of all conversations"""
        total_sessions = len(self.conversations)
        total_messages = sum(len(s['messages']) for s in self.conversations)

        return {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'recent_sessions': self.conversations[-5:] if self.conversations else []
        }

    def search_conversations(self, query):
        """Search through all conversations"""
        results = []

        for session in self.conversations:
            for message in session['messages']:
                if query.lower() in message['content'].lower():
                    results.append({
                        'session_id': session['id'],
                        'role': message['role'],
                        'content': message['content'],
                        'timestamp': message['timestamp']
                    })

        return results

    def clear_memory(self):
        """Clear all conversation memory"""
        self.conversations = []
        self.session_summaries = {}
        self.current_session = None
        self.save_memory()


class MemoryEnhancedChat:
    """Chat interface with conversation memory"""

    def __init__(self, parent, ide_instance):
        self.ide = ide_instance
        self.memory = ConversationMemory(
            ide_instance.workspace_path if hasattr(ide_instance, 'workspace_path') else None
        )

        # Start new session
        self.memory.start_session()

    def send_message_with_memory(self, user_message, ai_chat_instance):
        """Send message with memory context"""
        # Add to memory
        self.memory.add_message('user', user_message)

        # Get relevant context
        relevant = self.memory.get_relevant_context(user_message, max_messages=5)

        # Build enhanced prompt with context
        context_str = ""
        if relevant:
            context_str = "\n\nRelevant past conversation:\n"
            for ctx in relevant:
                context_str += f"- {ctx['role']}: {ctx['content'][:100]}...\n"

        # Send with context (you would integrate this with your AI chat)
        # ai_chat_instance.send_with_context(user_message, context_str)

    def on_ai_response(self, response):
        """Called when AI responds"""
        self.memory.add_message('assistant', response)

    def end_session(self):
        """End current conversation session"""
        self.memory.end_session()


class MemoryViewer(tk.Toplevel):
    """UI for viewing conversation history"""

    def __init__(self, parent, conversation_memory):
        super().__init__(parent)
        self.memory = conversation_memory
        self.title("Conversation Memory")
        self.geometry("900x700")
        self.configure(bg=T.BG3)

        self.setup_ui()
        self.load_sessions()

    def setup_ui(self):
        """Setup memory viewer UI"""
        # Header
        header = tk.Frame(self, bg=T.BG, height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="🧠 Conversation Memory", font=(T.UI, 12, 'bold'),
                fg=T.BILE, bg=T.BG).pack(side=tk.LEFT, padx=10, pady=15)

        # Stats
        summary = self.memory.get_conversation_summary()
        tk.Label(header,
                text=f"Sessions: {summary['total_sessions']} | Messages: {summary['total_messages']}",
                bg=T.BG, fg=T.TEXT2, font=(T.UI, 9)).pack(side=tk.LEFT, padx=20)

        # Clear button
        tk.Button(header, text="🗑 Clear All", command=self.clear_memory,
                 bg=T.BLOOD, fg=T.TEXT, relief=tk.FLAT).pack(side=tk.RIGHT, padx=10)

        # Search
        search_frame = tk.Frame(self, bg=T.BG3)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(search_frame, text="Search:", bg=T.BG3, fg=T.TEXT).pack(side=tk.LEFT, padx=5)

        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, bg=T.BG, fg=T.TEXT,
                font=(T.UI, 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        tk.Button(search_frame, text="🔍", command=self.search,
                 bg=T.HOVER, fg=T.TEXT, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)

        # Main paned window
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: Sessions list
        left_frame = tk.Frame(main_paned, bg=T.BG3)
        main_paned.add(left_frame, weight=1)

        tk.Label(left_frame, text="Sessions:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 10, 'bold')).pack(anchor='w', padx=5, pady=5)

        list_frame = tk.Frame(left_frame, bg=T.BG)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.session_list = tk.Listbox(
            list_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.UI, 9),
            selectbackground=T.HOVER,
            yscrollcommand=scrollbar.set
        )
        self.session_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.session_list.yview)

        self.session_list.bind('<<ListboxSelect>>', self.on_session_select)

        # Right: Messages
        right_frame = tk.Frame(main_paned, bg=T.BG3)
        main_paned.add(right_frame, weight=2)

        tk.Label(right_frame, text="Messages:", bg=T.BG3, fg=T.TEXT,
                font=(T.UI, 10, 'bold')).pack(anchor='w', padx=5, pady=5)

        msg_frame = tk.Frame(right_frame, bg=T.BG)
        msg_frame.pack(fill=tk.BOTH, expand=True)

        msg_scrollbar = tk.Scrollbar(msg_frame)
        msg_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.message_text = tk.Text(
            msg_frame,
            bg=T.BG,
            fg=T.TEXT,
            font=(T.UI, 10),
            wrap=tk.WORD,
            state='disabled',
            yscrollcommand=msg_scrollbar.set
        )
        self.message_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        msg_scrollbar.config(command=self.message_text.yview)

        # Configure tags
        self.message_text.tag_configure("user", foreground=T.BILE, font=(T.UI, 10, 'bold'))
        self.message_text.tag_configure("assistant", foreground=T.SIGNAL, font=(T.UI, 10, 'bold'))
        self.message_text.tag_configure("timestamp", foreground=T.TEXT2, font=(T.UI, 8))

    def load_sessions(self):
        """Load sessions into list"""
        self.session_list.delete(0, tk.END)

        for session in reversed(self.memory.conversations):
            session_id = session['id']
            summary = self.memory.session_summaries.get(session_id, "No summary")

            # Format date
            started = datetime.fromisoformat(session['started'])
            date_str = started.strftime('%Y-%m-%d %H:%M')

            display = f"{date_str} - {summary}"
            self.session_list.insert(tk.END, display)

    def on_session_select(self, event=None):
        """Handle session selection"""
        selection = self.session_list.curselection()
        if not selection:
            return

        idx = len(self.memory.conversations) - 1 - selection[0]  # Reverse index
        session = self.memory.conversations[idx]

        # Display messages
        self.message_text.config(state='normal')
        self.message_text.delete('1.0', 'end')

        for message in session['messages']:
            # Timestamp
            timestamp = datetime.fromisoformat(message['timestamp']).strftime('%H:%M:%S')
            self.message_text.insert('end', f"[{timestamp}] ", 'timestamp')

            # Role
            role_tag = message['role']
            role_text = "You: " if message['role'] == 'user' else "AI: "
            self.message_text.insert('end', role_text, role_tag)

            # Content
            self.message_text.insert('end', f"{message['content']}\n\n")

        self.message_text.config(state='disabled')

    def search(self):
        """Search conversations"""
        query = self.search_var.get().strip()
        if not query:
            return

        results = self.memory.search_conversations(query)

        # Display results
        self.message_text.config(state='normal')
        self.message_text.delete('1.0', 'end')

        self.message_text.insert('end', f"Search results for '{query}':\n\n", 'timestamp')

        for result in results[:50]:  # Limit to 50 results
            timestamp = datetime.fromisoformat(result['timestamp']).strftime('%Y-%m-%d %H:%M')
            self.message_text.insert('end', f"[{timestamp}] ", 'timestamp')

            role_tag = result['role']
            role_text = "You: " if result['role'] == 'user' else "AI: "
            self.message_text.insert('end', role_text, role_tag)

            self.message_text.insert('end', f"{result['content']}\n\n")

        self.message_text.config(state='disabled')

    def clear_memory(self):
        """Clear all memory"""
        from tkinter import messagebox
        confirm = messagebox.askyesno(
            "Confirm Clear",
            "Clear all conversation memory? This cannot be undone."
        )

        if confirm:
            self.memory.clear_memory()
            self.load_sessions()
            messagebox.showinfo("Success", "Memory cleared")


class SmartContextBuilder:
    """Builds smart context using conversation memory"""

    def __init__(self, conversation_memory):
        self.memory = conversation_memory

    def build_context(self, current_query, current_file_content="", project_files=None):
        """Build comprehensive context for AI"""
        context_parts = []

        # 1. Relevant past conversations
        relevant = self.memory.get_relevant_context(current_query, max_messages=3)
        if relevant:
            context_parts.append("=== RELEVANT PAST CONVERSATIONS ===")
            for ctx in relevant:
                context_parts.append(f"{ctx['role']}: {ctx['content'][:200]}")
            context_parts.append("")

        # 2. Current file
        if current_file_content:
            context_parts.append("=== CURRENT FILE ===")
            context_parts.append(current_file_content[:1000])  # First 1000 chars
            context_parts.append("")

        # 3. Project context
        if project_files:
            context_parts.append("=== PROJECT FILES ===")
            context_parts.append(", ".join(project_files[:20]))
            context_parts.append("")

        return "\n".join(context_parts)
