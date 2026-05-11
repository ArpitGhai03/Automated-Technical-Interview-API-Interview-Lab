import MonacoEditor from "@monaco-editor/react";

interface EditorProps {
  value: string;
  language: string;
  onChange: (value: string) => void;
}

export function Editor({ value, language, onChange }: EditorProps) {
  return (
    <div className="editor-wrapper">
      <MonacoEditor
        height="100%"
        language={language}
        theme="vs-dark"
        value={value}
        onChange={(v) => onChange(v ?? "")}
        options={{
          fontSize: 14,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 4,
        }}
      />
    </div>
  );
}
