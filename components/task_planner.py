"""
Task Planner - AI proposes step-by-step plan, you approve each step

Features:
- Breaks complex tasks into manageable steps
- Shows estimated time per step
- You approve/reject each step
- Tracks progress
- Can modify plan mid-execution

No more "AI does everything at once and breaks stuff"!

Part of DeathAIAUS IDE FC - The Honest AI IDE
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime
from components import death_theme as T


class TaskPlan:
    """Represents a multi-step task plan"""
    
    def __init__(self, task_description):
        self.task_description = task_description
        self.steps = []
        self.current_step = 0
        self.status = "pending"  # pending, in_progress, completed, cancelled
        self.created_at = datetime.now()
        self.completed_at = None
    
    def add_step(self, description, estimated_time=None, dependencies=None):
        """Add a step to the plan"""
        step = {
            'id': len(self.steps),
            'description': description,
            'estimated_time': estimated_time or "Unknown",
            'dependencies': dependencies or [],
            'status': 'pending',  # pending, in_progress, completed, skipped, failed
            'actual_time': None,
            'result': None,
            'error': None
        }
        self.steps.append(step)
        return step
    
    def get_next_step(self):
        """Get next pending step"""
        for step in self.steps:
            if step['status'] == 'pending':
                # Check if dependencies are met
                deps_met = all(
                    self.steps[dep_id]['status'] == 'completed'
                    for dep_id in step['dependencies']
                    if dep_id < len(self.steps)
                )
                if deps_met:
                    return step
        return None
    
    def mark_step_complete(self, step_id, actual_time=None, result=None):
        """Mark step as completed"""
        if 0 <= step_id < len(self.steps):
            self.steps[step_id]['status'] = 'completed'
            self.steps[step_id]['actual_time'] = actual_time
            self.steps[step_id]['result'] = result
    
    def mark_step_failed(self, step_id, error=None):
        """Mark step as failed"""
        if 0 <= step_id < len(self.steps):
            self.steps[step_id]['status'] = 'failed'
            self.steps[step_id]['error'] = error
    
    def is_complete(self):
        """Check if all steps are complete"""
        return all(step['status'] in ['completed', 'skipped'] for step in self.steps)
    
    def get_progress(self):
        """Get completion percentage"""
        if not self.steps:
            return 0
        completed = sum(1 for step in self.steps if step['status'] in ['completed', 'skipped'])
        return (completed / len(self.steps)) * 100
    
    def to_dict(self):
        """Convert to dictionary for saving"""
        return {
            'task_description': self.task_description,
            'steps': self.steps,
            'current_step': self.current_step,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Load from dictionary"""
        plan = cls(data['task_description'])
        plan.steps = data['steps']
        plan.current_step = data['current_step']
        plan.status = data['status']
        plan.created_at = datetime.fromisoformat(data['created_at'])
        if data['completed_at']:
            plan.completed_at = datetime.fromisoformat(data['completed_at'])
        return plan


class TaskPlannerPanel(tk.Toplevel):
    """UI for creating and managing task plans"""
    
    def __init__(self, parent, ide_instance):
        super().__init__(parent)
        self.ide = ide_instance
        self.current_plan = None
        
        self.title("Task Planner")
        self.geometry("1000x700")
        self.configure(bg=T.BG)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        # Header
        header = tk.Frame(self, bg=T.BG2, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📋 Task Planner",
                font=(T.UI, 14, 'bold'),
                fg=T.BILE, bg=T.BG2).pack(side=tk.LEFT, padx=20, pady=15)
        
        # Action buttons
        btn_frame = tk.Frame(header, bg=T.BG2)
        btn_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Button(btn_frame, text="➕ New Plan",
                 command=self.create_new_plan,
                 bg=T.HOVER, fg=T.TEXT,
                 font=(T.UI, 10),
                 relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="💾 Save Plan",
                 command=self.save_plan,
                 bg=T.BILE, fg=T.TEXT,
                 font=(T.UI, 10),
                 relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="📂 Load Plan",
                 command=self.load_plan,
                 bg=T.AMBER, fg=T.TEXT,
                 font=(T.UI, 10),
                 relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Main content
        content = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=T.BG)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left: Plan creation
        left_frame = tk.LabelFrame(content, text="Plan Details",
                                   bg=T.BG2, fg=T.TEXT,
                                   font=(T.UI, 10, 'bold'))
        content.add(left_frame)
        
        # Task description
        tk.Label(left_frame, text="Task Description:",
                bg=T.BG2, fg=T.TEXT,
                font=(T.UI, 10)).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.task_input = scrolledtext.ScrolledText(
            left_frame,
            height=4,
            wrap=tk.WORD,
            font=(T.UI, 10),
            bg=T.BG,
            fg=T.TEXT,
            relief=tk.FLAT,
            padx=5,
            pady=5
        )
        self.task_input.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Generate Plan button
        tk.Button(left_frame, text="🤖 Generate Plan (AI)",
                 command=self.generate_plan_with_ai,
                 bg=T.BLOOD, fg=T.TEXT,
                 font=(T.UI, 11, 'bold'),
                 relief=tk.FLAT, padx=20, pady=10,
                 cursor='hand2').pack(pady=10)
        
        # Or manual steps
        tk.Label(left_frame, text="Or Add Steps Manually:",
                bg=T.BG2, fg=T.TEXT,
                font=(T.UI, 10)).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        step_input_frame = tk.Frame(left_frame, bg=T.BG2)
        step_input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.step_input = tk.Entry(step_input_frame,
                                   bg=T.BG, fg=T.TEXT,
                                   font=(T.UI, 10),
                                   relief=tk.FLAT)
        self.step_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(step_input_frame, text="➕",
                 command=self.add_manual_step,
                 bg=T.HOVER, fg=T.TEXT,
                 font=(T.UI, 10),
                 relief=tk.FLAT, padx=10).pack(side=tk.RIGHT)
        
        # Right: Steps list and execution
        right_frame = tk.LabelFrame(content, text="Steps",
                                    bg=T.BG2, fg=T.TEXT,
                                    font=(T.UI, 10, 'bold'))
        content.add(right_frame)
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(right_frame, variable=self.progress_var,
                                           maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=10)
        
        self.progress_label = tk.Label(right_frame, text="No plan loaded",
                                       bg=T.BG2, fg=T.TEXT,
                                       font=(T.UI, 9))
        self.progress_label.pack(anchor=tk.W, padx=10)
        
        # Steps list
        list_frame = tk.Frame(right_frame, bg=T.BG2)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.steps_listbox = tk.Listbox(
            list_frame,
            bg=T.BG,
            fg=T.TEXT,
            selectbackground=T.HOVER,
            font=(T.MONO, 10),
            bd=0,
            yscrollcommand=scrollbar.set
        )
        self.steps_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.steps_listbox.yview)
        
        # Execution buttons
        exec_frame = tk.Frame(right_frame, bg=T.BG2)
        exec_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.execute_btn = tk.Button(exec_frame, text="▶️ Execute Next Step",
                                     command=self.execute_next_step,
                                     bg=T.BLOOD, fg=T.TEXT,
                                     font=(T.UI, 10, 'bold'),
                                     relief=tk.FLAT, padx=20, pady=8,
                                     cursor='hand2', state='disabled')
        self.execute_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(exec_frame, text="⏭️ Skip Step",
                 command=self.skip_step,
                 bg=T.AMBER, fg=T.TEXT,
                 font=(T.UI, 10),
                 relief=tk.FLAT, padx=20, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
    
    def create_new_plan(self):
        """Create a new empty plan"""
        task = self.task_input.get('1.0', tk.END).strip()
        if not task:
            messagebox.showwarning("No Task", "Please enter a task description")
            return
        
        self.current_plan = TaskPlan(task)
        self.current_plan.status = 'in_progress'
        self.update_display()
        messagebox.showinfo("Plan Created", "New task plan created. Add steps manually or generate with AI.")
    
    def generate_plan_with_ai(self):
        """Use AI to generate task plan"""
        task = self.task_input.get('1.0', tk.END).strip()
        if not task:
            messagebox.showwarning("No Task", "Please enter a task description")
            return
        
        # Create plan
        self.current_plan = TaskPlan(task)
        
        # Send to AI (placeholder - would use actual AI integration)
        messagebox.showinfo("AI Planning", 
                          "This would send task to AI and get breakdown.\n\n"
                          "For now, add steps manually.\n\n"
                          "In production: AI analyzes task and suggests steps with time estimates.")
        
        # Example steps (in production, AI would generate these)
        self.current_plan.add_step("Analyze requirements", "5-10 min")
        self.current_plan.add_step("Design structure", "10-15 min", [0])
        self.current_plan.add_step("Implement core logic", "20-30 min", [1])
        self.current_plan.add_step("Add error handling", "10-15 min", [2])
        self.current_plan.add_step("Test and debug", "15-20 min", [3])
        
        self.current_plan.status = 'in_progress'
        self.update_display()
        self.execute_btn.config(state='normal')
    
    def add_manual_step(self):
        """Add step manually"""
        if not self.current_plan:
            self.create_new_plan()
        
        step_text = self.step_input.get().strip()
        if not step_text:
            return
        
        self.current_plan.add_step(step_text)
        self.step_input.delete(0, tk.END)
        self.update_display()
        self.execute_btn.config(state='normal')
    
    def update_display(self):
        """Update steps display"""
        if not self.current_plan:
            return
        
        # Update progress
        progress = self.current_plan.get_progress()
        self.progress_var.set(progress)
        
        completed = sum(1 for s in self.current_plan.steps if s['status'] in ['completed', 'skipped'])
        total = len(self.current_plan.steps)
        self.progress_label.config(text=f"Progress: {completed}/{total} steps ({progress:.1f}%)")
        
        # Update steps list
        self.steps_listbox.delete(0, tk.END)
        for step in self.current_plan.steps:
            status_icon = {
                'pending': '⏸️',
                'in_progress': '▶️',
                'completed': '✅',
                'skipped': '⏭️',
                'failed': '❌'
            }.get(step['status'], '❓')
            
            line = f"{status_icon} {step['id']+1}. {step['description']} ({step['estimated_time']})"
            self.steps_listbox.insert(tk.END, line)
    
    def execute_next_step(self):
        """Execute next step"""
        if not self.current_plan:
            return
        
        next_step = self.current_plan.get_next_step()
        if not next_step:
            if self.current_plan.is_complete():
                messagebox.showinfo("Complete", "All steps completed!")
                self.current_plan.status = 'completed'
                self.current_plan.completed_at = datetime.now()
            else:
                messagebox.showinfo("Blocked", "No available steps (dependencies not met)")
            return
        
        # Show confirmation
        result = messagebox.askyesno("Execute Step",
                                     f"Execute step {next_step['id']+1}?\n\n"
                                     f"{next_step['description']}\n\n"
                                     f"Estimated time: {next_step['estimated_time']}")
        
        if result:
            next_step['status'] = 'in_progress'
            self.update_display()
            
            # In production: actually execute the step with AI
            messagebox.showinfo("Executing",
                              "Step would be executed here.\n\n"
                              "In production: AI performs the step,\n"
                              "you review results, then mark complete.")
            
            # Mark complete
            self.current_plan.mark_step_complete(next_step['id'], 
                                                actual_time="Simulated",
                                                result="Success")
            self.update_display()
    
    def skip_step(self):
        """Skip current step"""
        if not self.current_plan:
            return
        
        next_step = self.current_plan.get_next_step()
        if not next_step:
            return
        
        result = messagebox.askyesno("Skip Step",
                                     f"Skip step {next_step['id']+1}?\n\n"
                                     f"{next_step['description']}")
        
        if result:
            next_step['status'] = 'skipped'
            self.update_display()
    
    def save_plan(self):
        """Save plan to file"""
        if not self.current_plan:
            messagebox.showwarning("No Plan", "No plan to save")
            return
        
        filename = f"task_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.ide.workspace_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.current_plan.to_dict(), f, indent=2)
            messagebox.showinfo("Saved", f"Plan saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save plan:\n{e}")
    
    def load_plan(self):
        """Load plan from file"""
        from tkinter import filedialog
        
        filepath = filedialog.askopenfilename(
            initialdir=self.ide.workspace_path,
            title="Load Task Plan",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.current_plan = TaskPlan.from_dict(data)
            self.task_input.delete('1.0', tk.END)
            self.task_input.insert('1.0', self.current_plan.task_description)
            self.update_display()
            self.execute_btn.config(state='normal')
            messagebox.showinfo("Loaded", "Plan loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load plan:\n{e}")
