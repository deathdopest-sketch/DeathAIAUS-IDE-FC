import { Workflow } from './types';

export const ALL_LANGUAGES = [
    'Python', 'JavaScript', 'TypeScript', 'C++', 'C', 'C#', 'Go', 'Rust', 'Java', 'Kotlin',
    'Swift', 'PHP', 'Ruby', 'Perl', 'Lua', 'R', 'Julia', 'Scala', 'Haskell', 'Elixir',
    'Erlang', 'Clojure', 'F#', 'Dart', 'Groovy', 'Nim', 'Crystal', 'D', 'Zig', 'OCaml',
    'Racket', 'Scheme', 'Common Lisp', 'Fortran', 'COBOL', 'Pascal', 'Ada', 'Assembly (x86)',
    'BASIC', 'Visual Basic', 'SQL', 'HTML', 'CSS', 'SCSS', 'SASS', 'LESS', 'Shell', 'Batch',
    'PowerShell', 'Makefile', 'CMake', 'Dockerfile', 'YAML', 'JSON', 'XML', 'TOML', 'Markdown',
    'LaTeX', 'MATLAB', 'Octave', 'Mathematica', 'VimScript', 'Emacs Lisp', 'AWK', 'Sed', 'Tcl',
    'Prolog', 'Verilog', 'VHDL', 'Solidity', 'Move', 'Cairo', 'Vyper', 'WebAssembly', 'GraphQL',
    'Protocol Buffers', 'Thrift'
];

export const AVAILABLE_MODELS = [
    'THANATOS-DeathAIAUS-22B-Q4_K_M.gguf',
    'ANUBIS-DeathAIAUS-1.2B-Q8_0.gguf',
    'MORRIGAN-DeathAIAUS-7B-Q4_0.gguf',
    'AZRAEL-DeathAIAUS-8B-Q4_0.gguf',
    'IZANAMI-DeathAIAUS-1.5B-Q4_0.gguf',
    'YAMA-DeathAIAUS-13B-Q5_K_M.gguf',
    'ODIN-DeathAIAUS-13B-Q5_K_M.gguf',
    'HEL-DeathAIAUS-22B-Q4_0.gguf',
    'gemini-2.5-flash'
];

export const WORKFLOWS: Workflow[] = [
    {
        id: 'coding',
        name: 'Coding Workflow',
        steps: [
            { id: 'coding_generate', name: 'Generate' },
            { id: 'coding_analyze', name: 'Analyze' },
            { id: 'coding_validate', name: 'Validate' },
        ],
    },
    {
        id: 'large_projects',
        name: 'Large Projects',
        steps: [
            { id: 'large_plan', name: 'Plan' },
            { id: 'large_implement', name: 'Implement' },
            { id: 'large_review', name: 'Review' },
        ],
    },
    {
        id: 'quick_tasks',
        name: 'Quick Tasks',
        steps: [
            { id: 'quick_prototype', name: 'Prototype' },
            { id: 'quick_task', name: 'Task' },
            { id: 'quick_logic', name: 'Logic' },
        ],
    },
    {
        id: 'security_audit',
        name: 'Security Audit',
        steps: [
            { id: 'security_detect', name: 'Detect' },
            { id: 'security_destroy', name: 'Destroy' },
            { id: 'security_test', name: 'Test' },
        ],
    },
];
