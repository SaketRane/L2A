import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import remarkGfm from 'remark-gfm';

interface AlternativeLatexRendererProps {
  text: string;
}

const AlternativeLatexRenderer: React.FC<AlternativeLatexRendererProps> = ({ text }) => {
  // Pre-process the text to fix common LaTeX issues
  const preprocessText = (rawText: string): string => {
    let processedText = rawText;
    
    // Removed debug logging to prevent Fast Refresh issues
    
    // Fix common double-escaping issues
    processedText = processedText.replace(/\\\\([a-zA-Z]+)/g, '\\$1');
    
    // Fix specific LaTeX commands that might be escaped
    processedText = processedText.replace(/\\\\frac/g, '\\frac');
    processedText = processedText.replace(/\\\\langle/g, '\\langle');
    processedText = processedText.replace(/\\\\rangle/g, '\\rangle');
    processedText = processedText.replace(/\\\\sqrt/g, '\\sqrt');
    processedText = processedText.replace(/\\\\hat/g, '\\hat');
    processedText = processedText.replace(/\\\\partial/g, '\\partial');
    processedText = processedText.replace(/\\\\hbar/g, '\\hbar');
    processedText = processedText.replace(/\\\\begin/g, '\\begin');
    processedText = processedText.replace(/\\\\end/g, '\\end');
    
    // Fix angle bracket notation - convert \angle and \rangle patterns
    processedText = processedText.replace(/\\angle/g, '\\langle');
    
    // Fix matrix-specific issues based on the error patterns
    // Replace problematic sequences that cause parse errors
    processedText = processedText.replace(/3ea_0/g, '3E_0');
    processedText = processedText.replace(/3ea/g, '3E');
    processedText = processedText.replace(/eEa_0/g, 'E_0');
    processedText = processedText.replace(/eEz/g, '');
    processedText = processedText.replace(/-3eEa_0/g, '-3E_0');
    
    // Fix ampersand escaping in matrices - don't escape them
    processedText = processedText.replace(/\\\&/g, '&');
    
    // Fix matrix delimiters - completely rewrite this approach
    // First, handle inline math that contains matrices
    processedText = processedText.replace(/\$([^$]*\\begin\{[pb]matrix\}[^$]*\\end\{[pb]matrix\}[^$]*)\$/g, '$$$$1$$$$');
    
    // Handle cases where matrices are already wrapped with single $
    processedText = processedText.replace(/\$\\begin\{([pb]matrix)\}/g, '$$\\begin{$1}');
    processedText = processedText.replace(/\\end\{([pb]matrix)\}\$/g, '\\end{$1}$$');
    
    // Handle bare matrix environments and wrap them properly
    processedText = processedText.replace(/\\begin\{([pb]matrix)\}/g, '$$\\begin{$1}');
    processedText = processedText.replace(/\\end\{([pb]matrix)\}/g, '\\end{$1}$$');
    
    // Fix matrix row separators
    processedText = processedText.replace(/\\\\\s*/g, ' \\\\\\\\ ');
    
    // Fix specific quantum mechanics notation patterns
    processedText = processedText.replace(/\\langle\s*\\psi_\{([^}]+)\}\s*\|\s*\\hat\{([^}]+)\}\s*\|\s*\\psi_\{([^}]+)\}\s*\\rangle/g, '\\langle \\psi_{$1} | \\hat{$2} | \\psi_{$3} \\rangle');
    
    // Fix matrix element notation
    processedText = processedText.replace(/\\langle\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^>]+)\s*\\rangle/g, '\\langle $1 | $2 | $3 \\rangle');
    
    // Fix matrix environments
    processedText = processedText.replace(/\\\\pmatrix/g, '\\pmatrix');
    processedText = processedText.replace(/\\\\bmatrix/g, '\\bmatrix');
    processedText = processedText.replace(/\\\\matrix/g, '\\matrix');
    processedText = processedText.replace(/\\\\vmatrix/g, '\\vmatrix');
    processedText = processedText.replace(/\\\\Vmatrix/g, '\\Vmatrix');
    
    // Fix Greek letters
    processedText = processedText.replace(/\\\\(alpha|beta|gamma|delta|epsilon|theta|lambda|mu|nu|pi|rho|sigma|tau|omega|Omega|psi|Psi|phi|Phi)/g, '\\$1');
    
    // Fix trigonometric functions
    processedText = processedText.replace(/\\\\(cos|sin|tan|cot|sec|csc)/g, '\\$1');
    
    // Fix quantum mechanics operators and symbols
    processedText = processedText.replace(/\\\\Delta/g, '\\Delta');
    processedText = processedText.replace(/\\\\nabla/g, '\\nabla');
    processedText = processedText.replace(/\\\\int/g, '\\int');
    processedText = processedText.replace(/\\\\sum/g, '\\sum');
    processedText = processedText.replace(/\\\\prod/g, '\\prod');
    
    // Fix subscripts and superscripts in matrices
    processedText = processedText.replace(/W_\{([^}]+)\}/g, 'W_{$1}');
    processedText = processedText.replace(/([a-zA-Z]+)_\{([^}]+)\}/g, '$1_{$2}');
    processedText = processedText.replace(/([a-zA-Z]+)\^\{([^}]+)\}/g, '$1^{$2}');
    
    // Ensure proper spacing around | in bra-ket notation
    processedText = processedText.replace(/\|([^|$]+)\|/g, '| $1 |');
    
    // Fix specific matrix notation issues
    processedText = processedText.replace(/\{\\([^}]+)\}/g, '{\\$1}');
    
    // Clean up excessive newlines and ensure proper paragraph spacing
    processedText = processedText.replace(/\n{3,}/g, '\n\n');
    
    // Fix common matrix delimiters
    processedText = processedText.replace(/\\\[\s*\\begin\{/g, '$$\\begin{');
    processedText = processedText.replace(/\\end\{[^}]+\}\s*\\\]/g, (match) => match.replace(/\\\]/, '$$'));
    
    // Better LaTeX delimiter fixing
    processedText = processedText.replace(/\\\(/g, '$');
    processedText = processedText.replace(/\\\)/g, '$');
    
    // Fix standalone matrix expressions that should be display math
    processedText = processedText.replace(/\$\\begin\{/g, '$$\\begin{');
    processedText = processedText.replace(/\\end\{([pb]matrix)\}\$/g, '\\end{$1}$$');
    
    // Fix equation assignments with matrices
    processedText = processedText.replace(/([A-Z])\s*=\s*\$\$\\begin\{([pb]matrix)\}/g, '$1 = $$\\begin{$2}');
    processedText = processedText.replace(/([A-Z]')\s*=\s*\$\$\\begin\{([pb]matrix)\}/g, '$1 = $$\\begin{$2}');
    
    // Fix any remaining single $ around matrices
    processedText = processedText.replace(/\$\\begin\{([pb]matrix)\}/g, '$$\\begin{$1}');
    processedText = processedText.replace(/\\end\{([pb]matrix)\}\$/g, '\\end{$1}$$');
    
    // Fix specific problematic patterns from the error message
    // Remove any remaining invalid characters or sequences
    processedText = processedText.replace(/[^\x00-\x7F\u00A0-\uFFFF]/g, '');
    
    // Fix matrix elements spacing
    processedText = processedText.replace(/(\d+)\s*&\s*(\d+)/g, '$1 & $2');
    processedText = processedText.replace(/([a-zA-Z_0-9]+)\s*&\s*([a-zA-Z_0-9]+)/g, '$1 & $2');
    
    // Ensure proper escaping of special characters within LaTeX
    processedText = processedText.replace(/(?<!\\)\{([^}]*(?:\\.[^}]*)*)\}/g, (match, content) => {
      // Don't escape if already properly formatted
      if (content.includes('\\')) return match;
      return `{${content}}`;
    });
    
    // Fix common LaTeX errors in quantum mechanics expressions
    processedText = processedText.replace(/\\psi_\{([0-9]+)\}/g, '\\psi_{$1}');
    processedText = processedText.replace(/E_n\^\{([^}]+)\}/g, 'E_n^{($1)}');
    
    // Removed debug logging to prevent Fast Refresh issues
    
    return processedText;
  };

  const processedText = preprocessText(text);
  
  return (
    <div className="text-gray-100 leading-normal">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[
          [rehypeKatex, {
            strict: false,
            trust: true,
            throwOnError: false,
            errorColor: '#ff6b6b',
            displayMode: false,
            macros: {
              // Quantum mechanics macros
              '\\ket': '\\left|#1\\right\\rangle',
              '\\bra': '\\left\\langle#1\\right|',
              '\\braket': '\\left\\langle#1\\right\\rangle',
              '\\expval': '\\left\\langle#1\\right\\rangle',
              '\\ketbra': '\\left|#1\\right\\rangle\\left\\langle#2\\right|',
              // Matrix shortcuts
              '\\mat': '\\begin{pmatrix}#1\\end{pmatrix}',
              '\\det': '\\begin{vmatrix}#1\\end{vmatrix}',
              // Common operators
              '\\Tr': '\\mathrm{Tr}',
              '\\Re': '\\mathrm{Re}',
              '\\Im': '\\mathrm{Im}',
              // Fix angle commands
              '\\angle': '\\langle',
            },
            fleqn: false,
            output: 'html',
            // More permissive error handling
            maxSize: Infinity,
            maxExpand: 1000,
            // Enable matrix environments
            delimiters: [
              {left: '$$', right: '$$', display: true},
              {left: '$', right: '$', display: false},
              {left: '\\[', right: '\\]', display: true},
              {left: '\\(', right: '\\)', display: false}
            ]
          }]
        ]}
        components={{
          ul: ({ node, ...props }) => (
            <ul className="list-disc pl-6 mb-4 space-y-1 marker:text-purple-400" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="mb-1" {...props} />
          ),
          p: ({ node, ...props }) => (
            <p className="mb-4 leading-relaxed text-gray-100" {...props} />
          ),
          strong: ({ node, ...props }) => (
            <strong className="font-semibold text-purple-300" {...props} />
          ),
          h1: ({ node, ...props }) => (
            <h1 className="text-2xl font-bold text-purple-200 mb-6 mt-8 border-b-2 border-purple-700 pb-3" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-xl font-bold text-purple-300 mb-4 mt-6 border-b border-purple-800 pb-2" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-lg font-semibold text-purple-400 mb-3 mt-5" {...props} />
          ),
          h4: ({ node, ...props }) => (
            <h4 className="text-base font-medium text-purple-500 mb-2 mt-4" {...props} />
          ),
          blockquote: ({ node, ...props }) => (
            <blockquote className="border-l-4 border-purple-500 pl-4 py-3 my-4 bg-gray-800/30 rounded-r italic" {...props} />
          ),
          code: ({ node, className, children, ...props }: any) => {
            const inline = !className?.includes('language-');
            return inline ? (
              <code className="bg-gray-700 px-2 py-1 rounded text-sm font-mono text-purple-200" {...props}>
                {children}
              </code>
            ) : (
              <code className="block bg-gray-800 p-4 rounded text-sm font-mono overflow-x-auto border border-gray-700" {...props}>
                {children}
              </code>
            );
          },
          pre: ({ node, ...props }) => (
            <pre className="bg-gray-800 p-4 rounded my-4 overflow-x-auto border border-gray-700" {...props} />
          ),
        }}
      >
        {processedText}
      </ReactMarkdown>
    </div>
  );
};

export default AlternativeLatexRenderer;
