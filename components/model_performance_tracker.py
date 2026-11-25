"""
Model Performance Tracker - Track which AI models actually deliver

Tracks:
- Success/failure rates per model
- Average response time
- Task completion rates
- Error rates
- User satisfaction (optional ratings)

Part of DeathAIAUS IDE FC - The Honest AI IDE
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from collections import defaultdict
from components import death_theme as T


class ModelPerformanceTracker:
    """Tracks AI model performance metrics"""
    
    def __init__(self, workspace_path):
        self.workspace_path = workspace_path
        self.stats_file = os.path.join(workspace_path, '.model_stats.json')
        self.stats = self.load_stats()
        
    def load_stats(self):
        """Load stats from file"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._empty_stats()
        return self._empty_stats()
    
    def _empty_stats(self):
        """Return empty stats structure"""
        return {
            'models': {},  # {model_name: {attempts, successes, failures, total_time, errors}}
            'tasks': [],   # [{timestamp, model, task_type, success, duration, error}]
            'version': '1.0'
        }
    
    def save_stats(self):
        """Save stats to file"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Failed to save model stats: {e}")
    
    def record_attempt(self, model_name, task_type, success, duration=0, error_msg=None):
        """Record a model attempt"""
        # Initialize model stats if needed
        if model_name not in self.stats['models']:
            self.stats['models'][model_name] = {
                'attempts': 0,
                'successes': 0,
                'failures': 0,
                'total_time': 0,
                'errors': []
            }
        
        # Update model stats
        model = self.stats['models'][model_name]
        model['attempts'] += 1
        model['total_time'] += duration
        
        if success:
            model['successes'] += 1
        else:
            model['failures'] += 1
            if error_msg:
                model['errors'].append({
                    'timestamp': datetime.now().isoformat(),
                    'message': error_msg
                })
        
        # Record task
        self.stats['tasks'].append({
            'timestamp': datetime.now().isoformat(),
            'model': model_name,
            'task_type': task_type,
            'success': success,
            'duration': duration,
            'error': error_msg
        })
        
        # Limit task history to last 1000
        if len(self.stats['tasks']) > 1000:
            self.stats['tasks'] = self.stats['tasks'][-1000:]
        
        # Limit errors per model to last 50
        if len(model['errors']) > 50:
            model['errors'] = model['errors'][-50:]
        
        self.save_stats()
    
    def get_model_stats(self, model_name):
        """Get stats for a specific model"""
        if model_name not in self.stats['models']:
            return None
        
        model = self.stats['models'][model_name]
        success_rate = (model['successes'] / model['attempts'] * 100) if model['attempts'] > 0 else 0
        avg_time = (model['total_time'] / model['attempts']) if model['attempts'] > 0 else 0
        
        return {
            'attempts': model['attempts'],
            'successes': model['successes'],
            'failures': model['failures'],
            'success_rate': success_rate,
            'avg_time': avg_time,
            'recent_errors': model['errors'][-10:]
        }
    
    def get_all_models_ranked(self):
        """Get all models ranked by performance"""
        ranked = []
        for model_name, stats in self.stats['models'].items():
            success_rate = (stats['successes'] / stats['attempts'] * 100) if stats['attempts'] > 0 else 0
            avg_time = (stats['total_time'] / stats['attempts']) if stats['attempts'] > 0 else 0
            
            ranked.append({
                'name': model_name,
                'attempts': stats['attempts'],
                'success_rate': success_rate,
                'avg_time': avg_time,
                'failures': stats['failures']
            })
        
        # Sort by success rate, then by attempts (more data = more reliable)
        ranked.sort(key=lambda x: (x['success_rate'], x['attempts']), reverse=True)
        return ranked
    
    def get_best_model(self, min_attempts=5):
        """Get the best performing model (with enough data)"""
        ranked = self.get_all_models_ranked()
        for model in ranked:
            if model['attempts'] >= min_attempts:
                return model['name']
        # If no model has enough attempts, return the one with most attempts
        if ranked:
            return max(ranked, key=lambda x: x['attempts'])['name']
        return None
    
    def clear_stats(self):
        """Clear all stats"""
        self.stats = self._empty_stats()
        self.save_stats()


class ModelPerformancePanel(tk.Toplevel):
    """UI panel to view model performance"""
    
    def __init__(self, parent, tracker):
        super().__init__(parent)
        self.tracker = tracker
        self.title("Model Performance Tracker")
        self.geometry("900x600")
        self.configure(bg=T.BG)
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self, bg=T.BG2, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📊 Model Performance Tracker",
                font=(T.UI, 14, 'bold'),
                fg=T.BILE, bg=T.BG2).pack(side=tk.LEFT, padx=20, pady=15)
        
        # Refresh button
        tk.Button(header, text="🔄 Refresh",
                 command=self.refresh_data,
                 bg=T.HOVER, fg=T.TEXT,
                 font=(T.UI, 10),
                 relief=tk.FLAT, padx=15, pady=5).pack(side=tk.RIGHT, padx=10)
        
        # Clear button
        tk.Button(header, text="🗑️ Clear Stats",
                 command=self.clear_stats,
                 bg=T.BLOOD, fg=T.TEXT,
                 font=(T.UI, 10),
                 relief=tk.FLAT, padx=15, pady=5).pack(side=tk.RIGHT, padx=5)
        
        # Main content
        content = tk.Frame(self, bg=T.BG)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Summary section
        summary_frame = tk.LabelFrame(content, text="Summary", 
                                     bg=T.BG2, fg=T.TEXT,
                                     font=(T.UI, 11, 'bold'))
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.summary_text = tk.Text(summary_frame, height=4,
                                   bg=T.BG, fg=T.TEXT,
                                   font=(T.MONO, 10),
                                   relief=tk.FLAT, padx=10, pady=10)
        self.summary_text.pack(fill=tk.X, padx=10, pady=10)
        
        # Models table
        table_frame = tk.LabelFrame(content, text="Model Rankings",
                                   bg=T.BG2, fg=T.TEXT,
                                   font=(T.UI, 11, 'bold'))
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('rank', 'model', 'attempts', 'success_rate', 'avg_time', 'failures')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.tree.heading('rank', text='Rank')
        self.tree.heading('model', text='Model')
        self.tree.heading('attempts', text='Attempts')
        self.tree.heading('success_rate', text='Success Rate')
        self.tree.heading('avg_time', text='Avg Time (s)')
        self.tree.heading('failures', text='Failures')
        
        # Define column widths
        self.tree.column('rank', width=50)
        self.tree.column('model', width=300)
        self.tree.column('attempts', width=100)
        self.tree.column('success_rate', width=120)
        self.tree.column('avg_time', width=120)
        self.tree.column('failures', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 10))
        
        # Double-click to see details
        self.tree.bind('<Double-1>', self.show_model_details)
    
    def refresh_data(self):
        """Refresh the displayed data"""
        self.tracker.load_stats()
        
        # Update summary
        self.summary_text.delete('1.0', tk.END)
        ranked = self.tracker.get_all_models_ranked()
        total_attempts = sum(m['attempts'] for m in ranked)
        
        if ranked:
            best = ranked[0]
            worst = ranked[-1]
            summary = f"""Total Attempts: {total_attempts}
Best Model: {best['name']} ({best['success_rate']:.1f}% success, {best['attempts']} attempts)
Worst Model: {worst['name']} ({worst['success_rate']:.1f}% success, {worst['attempts']} attempts)
Tracked Models: {len(ranked)}"""
        else:
            summary = "No model performance data yet.\nUse AI features to start tracking!"
        
        self.summary_text.insert('1.0', summary)
        
        # Update table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for rank, model in enumerate(ranked, 1):
            # Color code by performance
            if model['success_rate'] >= 80:
                tag = 'excellent'
            elif model['success_rate'] >= 60:
                tag = 'good'
            elif model['success_rate'] >= 40:
                tag = 'fair'
            else:
                tag = 'poor'
            
            self.tree.insert('', tk.END, values=(
                f"#{rank}",
                model['name'],
                model['attempts'],
                f"{model['success_rate']:.1f}%",
                f"{model['avg_time']:.2f}s",
                model['failures']
            ), tags=(tag,))
        
        # Configure tags
        self.tree.tag_configure('excellent', background=T.BILE_DEEP)
        self.tree.tag_configure('good', background=T.SIGNAL_DEEP)
        self.tree.tag_configure('fair', background=T.BILE_DEEP)
        self.tree.tag_configure('poor', background=T.BLOOD_DEEP)
    
    def show_model_details(self, event):
        """Show detailed stats for selected model"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        model_name = item['values'][1]
        
        stats = self.tracker.get_model_stats(model_name)
        if not stats:
            return
        
        # Create detail dialog
        dialog = tk.Toplevel(self)
        dialog.title(f"Details: {model_name}")
        dialog.geometry("600x400")
        dialog.configure(bg=T.BG)
        
        # Header
        tk.Label(dialog, text=f"📊 {model_name}",
                font=(T.UI, 12, 'bold'),
                bg=T.BG, fg=T.BILE).pack(pady=10)
        
        # Stats
        stats_text = tk.Text(dialog, bg=T.BG2, fg=T.TEXT,
                           font=(T.MONO, 10), relief=tk.FLAT)
        stats_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        details = f"""Performance Summary:
─────────────────────────────────────────
Total Attempts: {stats['attempts']}
Successes: {stats['successes']}
Failures: {stats['failures']}
Success Rate: {stats['success_rate']:.1f}%
Average Time: {stats['avg_time']:.2f}s
─────────────────────────────────────────

Recent Errors:
"""
        
        if stats['recent_errors']:
            for i, error in enumerate(stats['recent_errors'], 1):
                timestamp = error['timestamp'][:19].replace('T', ' ')
                msg = error['message'][:100]
                details += f"\n{i}. [{timestamp}] {msg}"
        else:
            details += "\nNo recent errors! 🎉"
        
        stats_text.insert('1.0', details)
        stats_text.config(state='disabled')
        
        # Close button
        tk.Button(dialog, text="Close", command=dialog.destroy,
                 bg=T.HOVER, fg=T.TEXT, font=(T.UI, 10),
                 relief=tk.FLAT, padx=30, pady=8).pack(pady=(0, 20))
    
    def clear_stats(self):
        """Clear all statistics"""
        result = messagebox.askyesno("Clear Stats",
                                     "Are you sure you want to clear all model performance statistics?\n\n"
                                     "This cannot be undone.")
        if result:
            self.tracker.clear_stats()
            self.refresh_data()
            messagebox.showinfo("Stats Cleared", "All model performance statistics have been cleared.")
